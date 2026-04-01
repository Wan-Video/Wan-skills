#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Upload to OSS - 文件上传工具

将本地文件或 base64 图片数据上传到阿里云百炼临时 OSS 存储，获取 oss:// URL。

使用场景：
- 图生图/图像编辑/图生组图时需要上传参考图
- 任何需要本地文件或 base64 数据作为模型输入的场景

使用方法：
    # 方式 1: 从文件路径上传
    python file_to_oss.py --file /path/to/image.jpg --model wan2.7-image
    
    # 方式 2: 从 base64 数据上传
    python file_to_oss.py --base64 "<base64_data>" --model wan2.7-image

输出：
    oss://dashscope-instant/xxx/2024-07-18/xxx/cat.png

环境变量：
    DASHSCOPE_API_KEY: 必需，阿里云百炼 API Key
"""

import os
import sys
import base64
import requests
from pathlib import Path
from typing import Optional


def upload_file_to_oss(api_key: str, model_name: str, file_path: str = None, 
                       base64_data: str = None, filename: str = None) -> str:
    """
    上传文件到临时 OSS 存储
    
    Args:
        api_key: 阿里云百炼 API Key
        model_name: 模型名称（如 wan2.7-image）
        file_path: 本地文件路径（可选，与 base64_data 二选一）
        base64_data: base64 编码的图片数据（可选，与 file_path 二选一）
        filename: 当使用 base64_data 时，指定文件名（可选，默认 image.png）
        
    Returns:
        oss:// 格式的临时 URL
        
    Raises:
        ValueError: 未提供 file_path 或 base64_data
        FileNotFoundError: 文件不存在
        Exception: 上传失败
    """
    
    # 检查输入：必须有 file_path 或 base64_data
    if not file_path and not base64_data:
        raise ValueError("必须提供 file_path 或 base64_data")
    
    if file_path and base64_data:
        raise ValueError("file_path 和 base64_data 只能提供一个")
    
    # 如果是文件路径，读取文件内容
    if file_path:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")
        with open(file_path, 'rb') as f:
            file_content = f.read()
        file_name = Path(file_path).name
    else:
        # 如果是 base64 数据，解码
        try:
            # 处理可能的 data URI 格式
            if ',' in base64_data:
                base64_data = base64_data.split(',', 1)[1]
            file_content = base64.b64decode(base64_data)
        except Exception as e:
            raise Exception(f"base64 解码失败：{e}")
        file_name = filename or "image.png"
    
    # Step 1: 获取上传凭证
    upload_url = "https://dashscope.aliyuncs.com/api/v1/uploads"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "action": "getPolicy",
        "model": model_name
    }
    
    try:
        response = requests.get(upload_url, headers=headers, params=params)
        if response.status_code != 200:
            raise ValueError(f"Failed to get upload policy: {response.text}")
        
        policy_data = response.json()['data']
    except Exception as e:
        raise Exception(f"获取上传凭证失败：{e}")
    
    # Step 2: 上传文件到 OSS
    key = f"{policy_data['upload_dir']}/{file_name}"
    
    files = {
        'OSSAccessKeyId': (None, policy_data['oss_access_key_id']),
        'Signature': (None, policy_data['signature']),
        'policy': (None, policy_data['policy']),
        'x-oss-object-acl': (None, policy_data['x_oss_object_acl']),
        'x-oss-forbid-overwrite': (None, policy_data['x_oss_forbid_overwrite']),
        'key': (None, key),
        'success_action_status': (None, '200'),
        'file': (file_name, file_content)
    }
    
    try:
        response = requests.post(policy_data['upload_host'], files=files)
        if response.status_code != 200:
            raise Exception(f"上传失败：{response.text}")
    except Exception as e:
        raise Exception(f"文件上传失败：{e}")
    
    return f"oss://{key}"


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='文件上传到 OSS 工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 方式 1: 从文件路径上传
  python file_to_oss.py --file /path/to/image.jpg --model wan2.7-image
  
  # 方式 2: 从 base64 数据上传
  python file_to_oss.py --base64 "<base64_data>" --model wan2.7-image
        """
    )
    
    parser.add_argument('--file', '-f', help='本地文件路径')
    parser.add_argument('--base64', '-b', help='base64 编码的图片数据')
    parser.add_argument('--model', '-m', required=True, help='模型名称（如 wan2.7-image）')
    parser.add_argument('--filename', help='当使用 base64 时，指定文件名（默认 image.png）')
    
    args = parser.parse_args()
    
    # 检查输入
    if not args.file and not args.base64:
        print("❌ 错误：请提供 --file、--base64 之一")
        print("   使用 --help 查看帮助")
        sys.exit(1)
    
    # 获取 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：请先设置 DASHSCOPE_API_KEY 环境变量")
        print("请设置环境变量：")
        print("如果使用bash")
        print("echo 'export DASHSCOPE_API_KEY=\"your-api-key-here\"' >> ~/.bashrc && source ~/.bashrc")
        print("如果使用zsh")
        print("echo 'export DASHSCOPE_API_KEY=\"your-api-key-here\"' >> ~/.zshrc && source ~/.zshrc")
        sys.exit(1)
    
    try:
        # 从参数获取 base64
        if args.base64:
            oss_url = upload_file_to_oss(api_key, args.model, base64_data=args.base64, 
                                        filename=args.filename)
        # 从文件路径
        else:
            oss_url = upload_file_to_oss(api_key, args.model, file_path=args.file)
        
        print(oss_url)
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
