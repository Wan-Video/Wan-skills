#!/usr/bin/env python3

# Copyright 2025-2026 The Alibaba Wan Team Authors. All rights reserved.

"""
PPTX Generator - Generate PowerPoint images using DashScope API
"""

import os
import sys
import re
import json
import argparse
import urllib.request
from http import HTTPStatus
from pathlib import Path
import dashscope
from openai import OpenAI
from datetime import datetime
import requests
# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# Log file path - use script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "pptx_generator.log")

# Output directory (can be overridden via --output-dir parameter)
OUTPUT_DIR = None


def log_print(*args, **kwargs):
    """Print function that outputs to both console and log file"""
    message = " ".join(str(arg) for arg in args)
    print(message, **kwargs)
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[Log Error] {e}", file=sys.stderr)


def clear_log():
    """Clear log file"""
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("")
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[Clear Log Error] {e}", file=sys.stderr)


def save_outline(outline_text, output_dir):
    """Save outline to content.md immediately after receiving it"""
    try:
        filepath = os.path.join(output_dir, "content.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("## PPT Outline\n\n")
            f.write(outline_text)
            f.flush()
            os.fsync(f.fileno())
        log_print(f"📝 Outline saved: {filepath}")
    except Exception as e:
        log_print(f"❌ Failed to save outline: {e}")


def download_image(page_num, url, output_dir):
    """Download a single image and save as {page_num}.jpg"""
    try:
        filepath = os.path.join(output_dir, f"{page_num}.jpg")
        log_print(f"⬇️  Downloading image for page {page_num}...")
        urllib.request.urlretrieve(url, filepath)
        file_size = os.path.getsize(filepath)
        log_print(f"✅ Page {page_num} saved: {filepath} ({file_size / 1024:.1f} KB)")
    except Exception as e:
        log_print(f"❌ Failed to download image for page {page_num}: {e}")


def download_pptx(url, output_dir, name="presentation"):
    """Download the final PPTX file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_dir, f"{name}_{timestamp}.pptx")
        log_print(f"⬇️  Downloading PPTX file...")
        urllib.request.urlretrieve(url, filepath)
        file_size = os.path.getsize(filepath)
        log_print(f"✅ PPTX saved: {filepath} ({file_size / 1024:.1f} KB)")
        return filepath
    except Exception as e:
        log_print(f"❌ Failed to download PPTX: {e}")
        return None


def should_upload_file(file_path):
    """Determine if file needs to be uploaded to DashScope for intelligent parsing"""
    upload_extensions = {
        '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.txt'
    }
    text_extensions = {'.md', '.json', '.csv', '.py', '.js', '.html', '.xml'}
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in upload_extensions:
        return True
    elif file_ext in text_extensions:
        return False
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(100)
            return False
        except:
            return True


def read_file_content(file_path: str):
    """Read file content"""
    try:
        log_print(f"📖 Reading file content: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        log_print(f"✅ File read successfully, content length: {len(content)} characters")
        return content
    except Exception as e:
        log_print(f"❌ Failed to read file: {e}")
        return None


def get_upload_policy(api_key, model_name):
    """Get file upload credentials"""
    url = "https://dashscope.aliyuncs.com/api/v1/uploads"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "action": "getPolicy",
        "model": model_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get upload policy: {response.text}")
    
    return response.json()['data']

def upload_file_to_oss(policy_data, file_path):
    """Upload file to temporary storage OSS"""
    file_name = Path(file_path).name
    key = f"{policy_data['upload_dir']}/{file_name}"
    
    with open(file_path, 'rb') as file:
        files = {
            'OSSAccessKeyId': (None, policy_data['oss_access_key_id']),
            'Signature': (None, policy_data['signature']),
            'policy': (None, policy_data['policy']),
            'x-oss-object-acl': (None, policy_data['x_oss_object_acl']),
            'x-oss-forbid-overwrite': (None, policy_data['x_oss_forbid_overwrite']),
            'key': (None, key),
            'success_action_status': (None, '200'),
            'file': (file_name, file)
        }
        
        response = requests.post(policy_data['upload_host'], files=files)
        if response.status_code != 200:
            raise Exception(f"Failed to upload file: {response.text}")
    
    return f"oss://{key}"

def upload_file_and_get_url(api_key, file_path):
    """Upload file and get URL"""
    # 1. Get upload credentials, upload credential interface has rate limiting, exceeding the limit will cause request failure
    policy_data = get_upload_policy(api_key, "qwen-doc-turbo") 
    # 2. Upload file to OSS
    oss_url = upload_file_to_oss(policy_data, file_path)
    
    return oss_url



def generate_ppt(content=None, query=None, mode="creative", api_key=None, file_path=None, output_dir=None):
    """
    Generate PPT images, save outline and images to output_dir in real-time
    """
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    
    if not api_key:
        api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        return {"success": False, "error": "API key not provided."}
    
    # Process file input
    file_url = None
    file_content = None
    
    if file_path:
        log_print(f"📁 File input detected: {file_path}")
        if should_upload_file(file_path):
            file_url = upload_file_and_get_url(api_key, file_path)
            if not file_url:
                return {"success": False, "error": f"File upload failed: {file_path}"}
        else:
            file_content = read_file_content(file_path)
            if not file_content:
                return {"success": False, "error": f"File read failed: {file_path}"}
    
    if not query:
        return {"success": False, "error": "Query parameter must be provided"}
    
    # Build messages
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    if file_url:
        messages.append({"role": "user", "content": [{"text": query, "type": "text"}, {"type": "doc_url", "doc_url": [file_url], "file_parsing_strategy": "auto"}]})
    elif file_content:
        messages.append({"role": "system", "content": file_content})
        messages.append({"role": "user", "content": query})
    else:
        if not content:
            return {"success": False, "error": "Must provide either content text or file path"}
        messages.append({"role": "system", "content": content})
        messages.append({"role": "user", "content": query})
    
    skill = [{"type": "ppt", "mode": mode}]
    
    try:
        log_print(f"📊 Starting PPT generation (mode: {mode})...")
        log_print(f"💬 User query: {query}")
        if file_url:
            log_print(f"📁 Using file upload mode (file_url: {file_url})")
        elif file_content:
            log_print(f"📖 Using file read mode (content length: {len(file_content)} characters)")
        if content:
            log_print(f"📝 Additional content: {content}")
        log_print()
        
        responses = dashscope.Generation.call(
            api_key=api_key,
            model='qwen-doc-turbo',
            messages=messages,
            skill=skill,
            stream=True,
            incremental_output=True
        )
        
        all_content = []
        all_reasoning = []
        outline_content = ""
        page_images = []
        final_pptx_url = ""
        
        for idx, resp in enumerate(responses, start=1):
            if resp.status_code == HTTPStatus.OK:
                try:
                    choice = resp.output["choices"][0]
                    message = choice["message"]
                    
                    content_chunk = message.get("content", "")
                    reasoning_content = message.get("reasoning_content", "")
                    
                    log_print(f"\n{'─'*60}")
                    log_print(f"Response #{idx}")
                    log_print(f"{'─'*60}")
                    
                    if reasoning_content:
                        log_print("\n🤔 Reasoning Content:")
                        log_print(reasoning_content)
                        all_reasoning.append(reasoning_content)
                        
                        # First response: outline → save content.md immediately
                        if idx == 1:
                            outline_content = reasoning_content
                            log_print(f"\n📋 [First Response] Received outline and strategy content")
                            if output_dir:
                                save_outline(outline_content, output_dir)
                        
                        # Second response: page image links → download each image immediately
                        elif "<page-" in reasoning_content:
                            page_matches = re.findall(r'<page-(\d+)>(.*?)</page-\1>', reasoning_content)
                            log_print(f"\n🖼️  Received {len(page_matches)} page image links")
                            for page_num, url in page_matches:
                                page_images.append({"page": int(page_num), "url": url})
                                if output_dir and url.startswith("http"):
                                    download_image(int(page_num), url, output_dir)
                    
                    if content_chunk:
                        log_print("\n✅ Content:")
                        log_print(content_chunk)
                        all_content.append(content_chunk)
                        
                        # Extract PPT download link → download PPTX immediately
                        url_pattern = r'(https?://[^\s<>"\']+)'
                        url_matches = re.findall(url_pattern, content_chunk)
                        if url_matches:
                            pptx_url = next((u for u in url_matches if 'pptx' in u.lower()), None)
                            if pptx_url:
                                final_pptx_url = pptx_url
                                log_print(f"\n📎 Received complete PPT download link: {final_pptx_url}")
                                if output_dir:
                                    download_pptx(final_pptx_url, output_dir)
                            elif not final_pptx_url:
                                final_pptx_url = url_matches[0]
                                log_print(f"\n📎 Received download link: {final_pptx_url}")
                
                except KeyError as e:
                    log_print(f"❌ Error parsing response: {e}")
                    continue
            else:
                log_print(f"❌ API call failed: {resp.code} - {resp.message}")
                return {"success": False, "error": f"API call failed: {resp.code} - {resp.message}"}
        
        log_print(f"\n{'='*60}")
        log_print("🎉 PPT generation completed!")
        log_print(f"{'='*60}")
        
        return {
            "success": True,
            "content": "\n".join(all_content),
            "reasoning": "\n".join(all_reasoning),
            "outline": outline_content,
            "page_images": page_images,
            "pptx_download_url": final_pptx_url,
        }
        
    except Exception as e:
        log_print(f"❌ Error during generation: {e}")
        return {"success": False, "error": f"Error during generation: {e}"}


def main():
    clear_log()
    
    parser = argparse.ArgumentParser(description="Generate PowerPoint images using DashScope API")
    parser.add_argument("-c", "--content", type=str, help="PPT content text")
    parser.add_argument("-f", "--file", type=str, help="Input file path")
    parser.add_argument("-q", "--query", type=str, required=True, help="User query content")
    parser.add_argument("-m", "--mode", type=str, choices=["creative"], default="creative", help="Generation mode")
    parser.add_argument("-o", "--output-dir", type=str, help="Output directory (to save content.md, images, PPTX)")
    
    args = parser.parse_args()
    
    if not args.content and not args.file:
        log_print("❌ Error: Must provide either --content or --file parameter")
        sys.exit(1)
    
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        log_print("❌ Error: DASHSCOPE_API_KEY not set")
        log_print("Please set environment variable:")
        log_print("echo 'export DASHSCOPE_API_KEY=\"your-api-key-here\"' >> ~/.bashrc && source ~/.bashrc")
        sys.exit(1)
    
    # Set output directory
    output_dir = args.output_dir
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        log_print(f"📂 Output directory: {output_dir}")
    
    try:
        log_print("🚀 PPTX Generator started")
        log_print(f"💬 Query: {args.query}")
        log_print(f"🎨 Mode: {args.mode}")
        if args.file:
            log_print(f"📁 File: {args.file}")
        if args.content:
            log_print(f"📝 Content: {args.content[:100]}{'...' if len(args.content) > 100 else ''}")
        
        result = generate_ppt(
            content=args.content,
            query=args.query,
            mode=args.mode,
            api_key=api_key,
            file_path=args.file,
            output_dir=output_dir
        )
        
        if result["success"]:
            log_print("\n🎉 Generation successful!")
        else:
            log_print(f"\n❌ Generation failed: {result['error']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        log_print("\n\n⚠️  User interrupted operation")
        sys.exit(0)
    except Exception as e:
        log_print(f"\n❌ Program execution error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()