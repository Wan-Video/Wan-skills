---
name: wan-pptx-generator
description: 基于阿里云 qwen-doc-turbo 与 Wan2.7-Image 模型，支持将文档、文本或主题描述自动转换为带有 AI 生成图片的专业 PPT 幻灯片。主要覆盖以下场景：1、文档转 PPT——直接传入 PDF、DOCX、TXT、MD 等格式文件生成演示文稿；2、文本转 PPT——根据用户输入的文字内容或主题描述生成幻灯片；3、风格化生成——指定视觉风格（如"哆啦A梦风格"）和叙事风格（如"TED 演讲风格"）生成 PPT。触发条件：只要用户意图涉及创建、生成、制作 PPT 或演示文稿——无论是直接指令（如"帮我做个 PPT"）、文件驱动（如"把这份文档转成幻灯片"）还是主题驱动（如"做一个关于人工智能的演示文稿"）——均应激活本技能。
metadata:
  version: 0.1.0
---

# Wan PPT Generator（图片PPT 生成技能）

使用qwen-doc-turbo，通过直接 API 调用生成 AI 驱动的 PPT 幻灯片图片，背后调度wan2.7-image模型。

## Quick Start

**1. 配置环境变量** `DASHSCOPE_API_KEY`
**2. 了解能力** → 阅读下文核心能力介绍
**3. 准备输入** → 文件路径或文本内容二选一
**4. 运行脚本** → `scripts/pptx_generator.py`

**核心能力：**
- ✅ **文档转 PPT**：直接传入文件，自动解析并生成幻灯片
- ✅ **文本转 PPT**：根据文字内容或主题描述生成演示文稿
- ✅ **风格化生成**：支持指定视觉风格与叙事风格
- ✅ **AI 图片渲染**：每页幻灯片由 Wan2.7-Image 模型生成高质量配图

> 🎉 **限时优惠**：当前通过 qwen-doc-turbo 调用 Wan2.7-Image 图片生成**限时免费**，仅计算文本 Token 费用，欢迎体验！

## 环境变量配置

使用前需设置 DashScope API Key：

**获取 API Key**：
- 访问阿里云百炼控制台：https://bailian.console.aliyun.com/
- 登录后在 API Key 管理页面创建或获取您的 API Key

运行脚本前，请先检查 `DASHSCOPE_API_KEY` 是否已在环境配置


## 风格选择引导
如果用户已经明确说了风格，跳过此菜单直接生成。

当用户没有指定风格，或者说"帮我选一个"、"你来决定"、"有什么风格"时，
主动展示风格菜单供用户选择，格式如下：

---

🎨 **请选择您喜欢的 PPT 风格：**

**🎌 日漫 / 动漫风**
> 哆啦A梦 / 宫崎骏 / 鸟山明 / 龙珠 / 火影忍者 / 海贼王 / 鬼灭之刃
> 死神 / 灌篮高手 / 一拳超人 / 美少女战士 / 樱桃小丸子 / 银魂
> 圣斗士 / 阿童木 / 蜡笔小新 / JOJO的奇妙冒险 / 罗小黑 / 3渲2

**🦸 欧美漫画风**
> 漫威 / DC / 蝙蝠侠 / X战警 / 罪恶之城 / 地狱男爵 / 美式漫画

**🇨🇳 中国风 / 国漫**
> 新中式国潮 / 水墨风 / 敦煌风 / 工笔画 / 浮世绘 / 剪纸风
> 三毛流浪记 / 老夫子 / 朱德庸 / 镖人 / 风云雄霸天下

**🎮 游戏 / 像素风**
> 原神 / 塞尔达 / 我的世界(Minecraft) / 赛博朋克 / 街机 / 像素风
> 低面建模 / 积木风 / 2.5D / 3D

**✏️ 插画 / 设计风**
> MBE插画 / 扁平化 / 波普艺术 / 孟菲斯 / 包豪斯 / 苹果设计
> 材质设计 / 新拟物 / 黏土拟物 / 手绘 / 草图 / 文具手帐

**🖼️ 艺术 / 绘画风**
> 油画 / 水彩 / 版画 / 木刻 / 彩绘玻璃 / 超写实 / 超现实
> 梵高 / 莫奈 / 达芬奇 / 蒙德里安 / 立体主义 / 欧普艺术

**🌈 潮流 / 特效风**
> 蒸汽波 / 蒸汽朋克 / 赛璐璐 / 酸性设计 / 故障美学 / 科技未来
> 哥特风 / 重工业 / 定格动画

**📸 复古 / 生活风**
> 胶片复古 / 做旧风 / 怀旧风 / 北欧风 / 奶油风 / 和风侘寂
> 韦斯安德森 / 宜家 / 维多利亚 / 新艺术 / 大字报 / 杂志排版

**🎤 演讲 / 商务风**
> TED风

---

直接回复风格名称即可，或者"日漫里选一个最适合的"，如果您无法选择，我将自行为您选择最合适的风格制作PPT。
## Workflow：PPT 生成流程

1. **判断输入类型** - 根据用户提供的是文件还是文本，选择对应输入方式
2. **调用生成脚本** - 调用 `scripts/pptx_generator.py`，传入内容、查询指令和输出目录
3. **生成脚本会实时保存结果**：
   - 收到大纲 → 保存为 `content.md`
   - 收到每页图片 URL → 逐页下载保存为 `1.jpg`、`2.jpg`...
   - 收到 PPTX 下载链接 → 下载保存为 `presentation_{timestamp}.pptx`
4. **展示结果** - 在用户交互界面中显示页面图片预览
5. **提示保存** - 告知用户图片链接有效期为 24 小时，建议指定目录长期保存

## Command Line Arguments（命令行参数）

| 参数 | 简写 | 必填 | 说明 |
|------|------|------|------|
| --content | -c | 否* | PPT 文本内容 |
| --file | -f | 否* | 输入文件路径（支持 pdf、docx、txt、md 等） |
| --query | -q | 是 | 风格与需求描述，如"用哆啦A梦视觉风格和 TED 叙事风格生成 PPT" |
| --mode | -m | 否 | 生成模式，默认为 creative |
| --output-dir | -o | 否 | 输出目录，指定后自动保存大纲、页面图片和 PPTX 文件 |

*注：`--content` 和 `--file` 至少需要提供一个

## Output Files（输出文件）

当指定 `--output-dir` 时，脚本会**实时**将结果保存到输出目录：

| 文件 | 生成时机 | 说明 |
|------|----------|------|
| `content.md` | 收到大纲时（第 1 次返回） | PPT 大纲与分镜脚本 |
| `1.jpg`, `2.jpg`, ... `N.jpg` | 收到每页图片 URL 时（逐页返回） | 由 Wan2.7-Image 渲染的每页幻灯片预览图，按页码命名 |
| `presentation_{timestamp}.pptx` | 收到 PPTX 下载链接时（最后返回） | 完整的 PowerPoint 文件 |

## Usage Examples（使用示例）

### 示例 1：传入文件生成 PPT

```bash
python3 scripts/pptx_generator.py \
  -f ~/Downloads/document.pdf \
  -q "用哆啦A梦视觉风格和TED叙事风格生成PPT" \
  -m creative \
  -o /path/to/output/dir
```

### 示例 2：传入文本内容生成 PPT

```bash

python3 scripts/pptx_generator.py \
  -c "产品名称：智能助手。核心功能：自然语言处理、任务自动化、多平台支持。" \
  -q "用极简商务风格和TED叙事风格生成PPT，共5页" \
  -m creative \
  -o /path/to/output/dir
```

## 生成任务耗时过长及进度追踪

通过日志文件 `scripts/pptx_generator.log` 实时追踪进度。每次运行会先清空日志，再逐条写入带时间戳的日志记录。

**重要原则：** 若任务长时间未返回结果，告知用户当前进度并建议稍后查看输出目录。绝对不要私自修改用户需求，例如减少页数或降低生成质量。

## Error Handling（错误处理）

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| API key not provided | 未设置 API Key | 设置 `DASHSCOPE_API_KEY` 环境变量
| 请求失败：code=XXX | API 调用失败 | 检查网络连接、API Key 有效性、模型可用性 |
| 解析响应失败 | 响应格式异常 | 查看 `scripts/pptx_generator.log` 获取详细信息 |
| 必须提供 content 或 file | 未提供输入内容 | 使用 `-c` 或 `-f` 参数提供内容 |
| BalanceError | 账户余额不足或后端服务异常 | 检查阿里云账户余额，稍后重试 |

详细错误码参考：[DashScope 错误码文档](https://help.aliyun.com/zh/model-studio/developer-reference/error-code)


## 相关文件

- 🐍 [pptx_generator.py](scripts/pptx_generator.py) - PPT 生成主脚本
- 📄 [pptx_generator.log](scripts/pptx_generator.log) - 实时运行日志