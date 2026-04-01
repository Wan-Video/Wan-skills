#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Resolution Parser for Wan 2.7 Image Generation

解析用户输入的分辨率描述，转换为 API 所需的 size 参数。

使用示例：
    python parse_resolution.py "2K 3:4"
    python parse_resolution.py "1K 16:9"
    python parse_resolution.py "2048*2048"

输出：
    1536*2048
    1696*960
    2048*2048
"""

import re
import sys


"""
**语法：** `{K 值} {宽}:{高}`
| 输入 | 输出 | 说明 |
|------|------|------|
| `1K 1:1` | 1024*1024 | 标准正方形 |
| `1K 3:4` | 896*1194 | 竖向图片 |
| `1K 4:3` | 1194*896 | 横向图片 |
| `1K 16:9` | 1364*768 | 宽屏 |
| `1K 9:16` | 768*1364 | 手机竖屏 |
| `2K 3:4` | 1774*2364 | 2K 竖向 |
| `2K 16:9` | 2730*1536 | 2K 宽屏 |
| `2K 1:1` | 2048*2048 | 2K 正方形 |
"""

def parse_resolution(input_str):
    """
    解析分辨率输入字符串
    
    Args:
        input_str: 用户输入，支持以下格式：
            - "2K 3:4", "1K 16:9" (K + 比例)
            - "2K", "1K" (仅 K 值，默认 1:1)
            - "1280*1280", "2048*2048" (直接指定分辨率)
            - "1280x1280" (x 分隔符)
    
    Returns:
        str: 格式化的分辨率字符串，如 "1536*2048"
    
    Raises:
        ValueError: 输入格式不正确或超出范围
    """
    
    input_str = input_str.strip().lower()
    
    # 模式 1: 直接指定分辨率 (如 "1280*1280" 或 "1280x1280")
    direct_pattern = r'^(\d+)[*x](\d+)$'
    match = re.match(direct_pattern, input_str)
    if match:
        width = int(match.group(1))
        height = int(match.group(2))
        
        # 验证范围
        if not (768*768 <= width * height <= 2048*2048):
            raise ValueError(f"总像素数必须在 [768*768, 2048*2048] 即 [{768*768}, {2048*2048}] 范围内，当前：{width}*{height}: {width*height}")
        
        aspect_ratio = width / height
        if not (1/8 <= aspect_ratio <= 8):
            raise ValueError(f"宽高比必须在 [1:8, 8:1] 范围内，当前：{aspect_ratio:.2f}")
        
        return f"{width}*{height}"
    
    # 模式 2: K + 比例 (如 "2K 3:4", "1K 16:9")
    k_ratio_pattern = r'^([124])k\s*(\d+):(\d+)$'
    match = re.match(k_ratio_pattern, input_str)
    if match:
        k_value = int(match.group(1))
        ratio_w = int(match.group(2))
        ratio_h = int(match.group(3))
        
        # 计算总像素
        total_pixels = min(max((k_value * 1024) ** 2, 1024*1024), 2048*2048)
        
        # 根据比例计算宽高
        base_unit = (total_pixels / (ratio_w * ratio_h)) ** 0.5
        
        width = int(round(base_unit * ratio_w))
        height = int(round(base_unit * ratio_h))

        # 确保是偶数（某些模型要求）
        width = width if width % 2 == 0 else width - 1
        height = height if height % 2 == 0 else height - 1

        # 验证范围
        if not (768*768 <= width * height <= 2048*2048):
            raise ValueError(f"总像素数必须在 [768*768, 2048*2048] 即 [{768*768}, {2048*2048}] 范围内，计算的分辨率超出范围：{width}*{height}: {width*height}")
        
        aspect_ratio = width / height
        if not (1/8 <= aspect_ratio <= 8):
            raise ValueError(f"宽高比必须在 [1:8, 8:1] 范围内，当前：{aspect_ratio:.2f}")
        
        return f"{width}*{height}"
    
    # 模式 3: 仅 K 值 (如 "1K", "2K")，默认 1:1 比例
    k_only_pattern = r'^([12])k$'
    match = re.match(k_only_pattern, input_str)
    if match:
        k_value = int(match.group(1))
        size = k_value * 1024
        return f"{size}*{size}"
    
    # 不支持的格式
    raise ValueError(
        f"不支持的输入格式：'{input_str}'\n"
        f"支持的格式：\n"
        f"  - K + 比例：'2K 3:4', '1K 16:9', '2K 1:1'\n"
        f"  - 仅 K 值：'1K', '2K' (默认 1:1)\n"
        f"  - 直接指定：'1280*1280', '2048*2048'"
    )


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python parse_resolution.py '<输入>'")
        print("")
        print("示例:")
        print("  python parse_resolution.py '2K 3:4'")
        print("  python parse_resolution.py '1K 16:9'")
        print("  python parse_resolution.py '2048*2048'")
        print("")
        print("输出:")
        print("  1536*2048")
        print("  1696*960")
        print("  2048*2048")
        sys.exit(1)
    
    input_str = sys.argv[1]
    
    try:
        result = parse_resolution(input_str)
        print(result)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
