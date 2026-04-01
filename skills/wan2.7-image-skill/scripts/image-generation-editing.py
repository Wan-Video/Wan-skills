#!/usr/bin/env python3
"""
image-generation-editing - 使用 DashScope API 进行图片生成/图片编辑/组图生成
"""

import os
import sys
import argparse
from http import HTTPStatus
from pathlib import Path
import requests
import time

def _poll_wan_task_status(task_id: str, headers: dict[str, str]) -> str:
    """Poll task status until completion"""

    dashscope_base_url = os.environ.get("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/")
    check_url = f"{dashscope_base_url}tasks/{task_id}"
    
    status = "PENDING"
    check_count = 0
    while status not in ("SUCCEEDED", "FAILED", "CANCELLED"):
        if check_count >= 15:
            return {"status": status, "content": []}
        print(
            f"Polling Dashscope generation {task_id}, current status: {status} ...")
        time.sleep(3)  # Wait 3 seconds between polls
        poll_response = requests.get(check_url, headers=headers)
        if poll_response.status_code != 200:
            try:
                error_data = poll_response.json()
                error_message = error_data.get(
                    "error", f"HTTP {poll_response.status_code}")
            except Exception:
                error_message = f"HTTP {poll_response.status_code}"
            raise Exception(
                f"poll Dashscope failed: {error_message}")
        
        poll_res = poll_response.json()
        status = poll_res.get("output", {}).get("task_status")
        if status == "SUCCEEDED":
            output = poll_res.get("output", {}).get("choices", [])[0].get("message", None).get("content", None)
            if output and isinstance(output, list):
                return {"status": status, "content": output}
            else:
                raise Exception(
                    "No image URL found in successful response")
        elif status == "FAILED":
            failed_code = poll_res.get("output", {}).get("code", "")
            failed_message = poll_res.get("output", {}).get("message", "")
            detail_error = f"Task failed with code: {failed_code}  message: {failed_message}"
            raise Exception(
                f"Dashscope image generation failed: {detail_error}")
        check_count += 1
    raise Exception(f"Task polling failed with final status: {status}")
    

def generate(user_requirement: str, input_images: list[str] = [], n: int = 1, size: str = '1K', enable_sequential: bool = False):
    """
    使用 DashScope API 进行图片生成/图片编辑/组图生成

    Args:
        user_requirement: 用户的图片生成/图片编辑/组图生成需求
        input_images: 输入的参考图片
        n: 生成图片的数量
        size: 生成图片的分辨率
        enable_sequential: 是否开启组图生成
        
    Returns:
        dict: 包含 success, content 等的结果字典
    """

    try:
        # 获取 API Key
        api_key = os.environ.get("DASHSCOPE_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "API key not provided. Set DASHSCOPE_API_KEY environment variable"
            }
        # 获取Base URL
        dashscope_base_url = os.environ.get("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/")
        api_url = f"{dashscope_base_url}services/aigc/image-generation/generation"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-DashScope-Async": "enable",
            "X-DashScope-OssResourceResolve": "enable"
        }
        payload = {
            "model": "wan2.7-image",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": f"{user_requirement}"}
                        ]
                    }
                ]
            },
            "parameters": {
                "size": f"{size}",
                "n": n,
                "watermark": False,
                "enable_sequential": enable_sequential
            }
        }
        if input_images:
            for img_url in input_images:
                payload['input']['messages'][0]['content'].append({"image": f"{img_url}"})
        response = requests.post(api_url, headers=headers, json=payload)

        # post request
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_message = error_data.get(
                    "error", f"HTTP {response.status_code}")
            except Exception:
                error_message = f"HTTP {response.status_code}"
            raise Exception(
                f"Dashscope task creation failed: {error_message}")
        result = response.json()
        task_id = result.get("output", {}).get("task_id", None)
        print('Dashscope TASK_ID: ', task_id)

        # check results
        check_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        poll_rst = _poll_wan_task_status(task_id, check_headers)
        status = poll_rst['status']
        content = poll_rst['content']
        if status == 'SUCCEEDED':
            for rst_idx, rst_item in enumerate(content):
                rst_type = rst_item.get('type', '')
                if rst_type == 'image':
                    print(f'第{rst_idx}个结果：', rst_item['image'])

            return {
                "success": True,
                "content": content,
                "error": ""
            }
        elif status == 'RUNNING':
            return {
                "success": False,
                "content": content,
                "task_id": task_id,
                "error": "still running"
            }

    except Exception as e:
        print(f"❌ 生成过程中出错: {e}")
        return {
            "success": False,
            "error": f"生成过程中出错: {e}"
        }


def main():
    parser = argparse.ArgumentParser(description="使用 DashScope API 进行图片生成/图片编辑/组图生成")
    
    # 必需参数
    parser.add_argument("--user_requirement", type=str, required=True, help="用户的图片生成/图片编辑/组图生成需求")
    
    # 其他参数
    parser.add_argument("--input_images", nargs='*', default=[], help="输入的参考图片")
    parser.add_argument("--n", type=int, default=1, help="生成图片的数量")
    parser.add_argument("--size", type=str, default='1K', help="生成图片的分辨率")
    parser.add_argument("--enable_sequential", action="store_true", help="是否开启组图生成")
    
    args = parser.parse_args()
    
    # 检查 API Key
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 DASHSCOPE_API_KEY")
        print("请设置环境变量：")
        print("如果使用bash")
        print("echo 'export DASHSCOPE_API_KEY=\"your-api-key-here\"' >> ~/.bashrc && source ~/.bashrc")
        print("如果使用zsh")
        print("echo 'export DASHSCOPE_API_KEY=\"your-api-key-here\"' >> ~/.zshrc && source ~/.zshrc")
        sys.exit(1)
    
    dashscope_base_url = os.environ.get("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/")
    api_url = f"{dashscope_base_url}services/aigc/image-generation/generation"

    try:
        result = generate(
            user_requirement=args.user_requirement,
            input_images=args.input_images,
            n=args.n,
            size=args.size,
            enable_sequential=args.enable_sequential
        )
        
        if result["success"]:
            print("\n🎉 生成成功！")
        else:
            if result['error'] == 'still running':
                print(f"\n还在生成中，该任务是异步生成任务，后续可以通过task_id: {result['task_id']}进行查询。")
            else:
                print(f"\n❌ 生成失败: {result['error']}")
                sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()