# Wan 2.7 Image Generation & Editing（图像生成与编辑）

## Overview

wan2.7-image，支持**文生图**、**文生组图**、**图生组图**、**图像编辑**和**多图参考生成**。

**Model:**  `wan2.7-image` （固定） 

### Core Features

- **图像生成**：文生图、文生组图
- **图像编辑**：基于参考图的编辑、风格迁移、多图融合
- **组图生成**：文生组图、图生组图（一次生成多张关联的图片，最多 12 张）

---

## Three Operation Modes

### Mode 1: 图像生成（文生图）

**用途：** 纯文本生成单张图像

**示例1：**
```bash
python3 scripts/image-generation-editing.py \
    --user_requirement "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵" \
    --n 1 \
    --size 1K
```

**要点：**
- 无需参考图
- `user_requirement` 是用户的文生图需求
- `n` 控制生成数量 [1-4]，按张计费，默认为1
- `size`: 支持 `1K`、`2K` 或自定义分辨率（如 `1280*1280`）
关于输出图片分辨率参数，支持以下两种方式，不可混用：
**方式一：参考输入图比例（推荐）**
1K：分辨率1024*1024
2K：分辨率2048*2048
**方式二：指定生成图像的宽高像素值**
总像素在 [768*768, 2048*2048] 之间，且宽高比范围为 [1:8, 8:1]
**分辨率转换：** 当用户即指定分辨率又指定宽高比时，使用 `scripts/parse_resolution.py` 脚本自动转换（详见文末 Resolution Script 章节）

---

### Mode 2: 图像编辑

**用途：** 基于 1-9 张参考图像进行编辑、风格迁移或主体一致性生成

**示例1：**
```bash
python3 scripts/image-generation-editing.py \
    --user_requirement "把图 2 的涂鸦喷绘在图 1 的汽车上" \
    --input_images "图 1 URL" "图 2 URL" \
    --n 1 \
    --size 1K
```

**要点：**
- 必须提供至少 1 张参考图
- 最多支持 9 张参考图
- `user_requirement` 是用户的图片编辑/风格转换/融合需求，在`user_requirement`中对图片的指代用图X，这种方式，其中X表示是`input_images`参数中的第几张图，从1开始
- `input_images` 是用户提供的参考图列表，该参数按顺序填充参考图的url链接
- `n` 控制生成数量 [1-4]，按张计费，默认为1
- `size`: 支持 `1K`、`2K` 或自定义分辨率（如 `1280*1280`）
关于输出图片分辨率参数，支持以下两种方式，不可混用：
**方式一：参考输入图比例（推荐）** 输出的图片输出宽高比与输入图像（多图输入时为最后一张）一致，并缩放到相应的分辨率。
1K：分辨率1024*1024
2K：分辨率2048*2048
**方式二：指定生成图像的宽高像素值**
总像素在 [768*768, 2048*2048] 之间，且宽高比范围为 [1:8, 8:1]
**分辨率转换：** 当用户即指定分辨率又指定宽高比时，使用 `scripts/parse_resolution.py` 脚本自动转换（详见文末 Resolution Script 章节）

**参考图 本地文件上传流程：**
```bash
# Step 1: 上传本地文件到 OSS（文件路径方式）
oss_url=$(python scripts/file_to_oss.py --file /path/to/image.jpg --model wan2.7-image)

# Step 1: 上传 base64 图片到 OSS（如Claw chat框粘贴场景）
oss_url=$(python scripts/file_to_oss.py --base64 "<base64_data>" --model wan2.7-image)

# Step 2: 在脚本调用中使用
# --input_images "$oss_url"
```

---

### Mode 3: 组图生成

**用途：** 根据文本描述生成系列图像（一次生成多张关联的图片，教程、故事等）可以对输入图片进行参考

**示例1：**
```bash
python3 scripts/image-generation-editing.py \
    --user_requirement "给我一个 3 张图辣椒炒肉教程" \
    --n 3 \
    --size 1K \
    --enable_sequential
```

**示例2：**
```bash
python3 scripts/image-generation-editing.py \
    --user_requirement "生成一个5张图的绘本图片，角色参考图1和图2" \
    --input_images "图 1 URL" "图 2 URL" \
    --n 5 \
    --size 1K \
    --enable_sequential
```

**要点：**
- 可以无参考图（纯文生组图）或最多 9 张参考图
- `user_requirement` 是用户的图片编辑/风格转换/融合需求，在`user_requirement`中对图片的指代用图X，这种方式，其中X表示是`input_images`参数中的第几张图，从1开始
- `input_images` 是用户提供的参考图列表，如果没有参考图时，调用的命令行中不要出现这个参数。需要参考图时，该参数按顺序填充参考图的url链接
- `n` 控制最大生成数量 [1-12]，实际数量由模型决定
- `size`: 支持 `1K`、`2K` 或自定义分辨率（如 `1280*1280`）
关于输出图片分辨率参数，支持以下两种方式，不可混用：
**方式一：参考输入图比例（推荐）** 
1K：分辨率1024*1024
2K：分辨率2048*2048
**方式二：指定生成图像的宽高像素值**
总像素在 [768*768, 2048*2048] 之间，且宽高比范围为 [1:8, 8:1]
**分辨率转换：** 当用户即指定分辨率又指定宽高比时，使用 `scripts/parse_resolution.py` 脚本自动转换（详见文末 Resolution Script 章节）

**参考图 本地文件上传流程：**
```bash
# Step 1: 上传本地文件到 OSS（文件路径方式）
oss_url=$(python scripts/file_to_oss.py --file /path/to/image.jpg --model wan2.7-image)

# Step 1: 上传 base64 图片到 OSS（如Claw chat框粘贴场景）
oss_url=$(python scripts/file_to_oss.py --base64 "<base64_data>" --model wan2.7-image)

# Step 2: 在脚本调用中使用
# --input_images "$oss_url"
```

---

## Image Input

### 支持的格式

- **格式：** JPEG, JPG, PNG(不支持透明通道), BMP, WEBP
- **分辨率：** [240, 8000] 像素
- **大小：** ≤ 20MB
- **宽高比：** [1:8, 8:1]

### 输入方式

#### 方式 1: 公网 URL（推荐）

直接使用已有的图片 URL：
```
http://wanx.alicdn.com/material/xxx.jpeg
```

#### 方式 2: 本地文件上传（使用脚本）

**本地文件 → OSS URL 转换：**

```bash
# 方式 1: 从文件路径上传
python scripts/file_to_oss.py --file <文件路径> --model <模型名称>

# 方式 2: 从 base64 数据上传（OpenClaw 场景）
python scripts/file_to_oss.py --base64 "<base64_data>" --model <模型名称>

# 示例
python scripts/file_to_oss.py --file /path/to/image.jpg wan2.7-image
python scripts/file_to_oss.py --base64 "iVBORw0KGgoAAAANSUhEUgAA..." --model wan2.7-image

# 输出
oss://dashscope-instant/xxx/2024-07-18/xxx/cat.png
```

**在脚本调用中使用：**

```
--input_images oss://dashscope-instant/xxx/2024-07-18/xxx/cat.png
```

📖 **详细文档：** [file_to_oss.py](../scripts/file_to_oss.py)

---

## Common Use Cases

### Case 1: 文生图

```bash
python3 scripts/image-generation-editing.py \
    --user_requirement "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵" \
    --n 1 \
    --size 1K
```

### Case 2: 图像编辑（多图融合）

```bash
python3 scripts/image-generation-editing.py \
    --user_requirement "把图 2 的涂鸦喷绘在图 1 的汽车上" \
    --input_images "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20251229/pjeqdf/car.webp" "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20251229/xsunlm/paint.webp" \
    --n 1 \
    --size 1K
```

### Case 3: 组图生成（教程）

```bash
python3 scripts/image-generation-editing.py \
    --user_requirement "给我一个 3 张图辣椒炒肉教程" \
    --n 3 \
    --size 1K \
    --enable_sequential
```

---

## Resolution Script

**脚本位置：** `scripts/parse_resolution.py`

**用途：** 当用户即对分辨率有要求又对宽高比有要求时，解析用户输入的分辨率描述，转换为生成脚本所需的 size 参数。

**使用方法：**
```bash
python scripts/parse_resolution.py "<输入>"
```

**支持的输入格式：**
- K + 比例：`"2K 3:4"`, `"1K 16:9"`
- 仅 K 值：`"1K"`, `"2K"`（默认 1:1）
- 直接指定：`"1280*1280"`, `"2048*2048"`

**输出：** 格式化的分辨率字符串（如 `1536*2048`）
