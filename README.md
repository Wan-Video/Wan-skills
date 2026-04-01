# Wan-skills
> AI Agent Skills for Wan — Enable your AI Agent to easily leverage Wan's AIGC capabilities.
---
## 🌟 Core Capabilities
**Wan-skills** is a suite of skills designed for AI Agents, empowering them with AIGC capabilities through API calls.

**Skills List**

| name | description | scripts | refenence |
|------|------|------|------|
| **wan2.7-image-skill** | Create content using the image generation and editing capabilities of the wan2.7-image model. | `image-generation-editing.py` `file_to_oss.py` `parse_resolution.py` `check_wan_task_status.py` | `common.md` `image-generation-editing.md` |

Continuously update the skill list with a variety of new skills.

---

## 🚀 Quick Start

### Step 1: Get API Key

**Prerequisites:** An Alibaba Cloud account is required

1. **Sign up for an Alibaba Cloud account**
   - visit https://www.aliyun.com/
   - Complete account registration

2. **Activate ModelStudio Service**
   - visit https://modelstudio.console.aliyun.com/
   - Activate the ModelStudio service

3. **create API Key**
   - Go to the ModelStudio Console → API Key Management
   - create new API Key

### Step 2: Configure environment variables

```bash
export DASHSCOPE_API_KEY="your-access-key"
```

**Region selection**

Select the appropriate `DASHSCOPE_BASE_URL` based on your region.
```bash
# Chinese Mainland (Beijing) - default
export DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/api/v1/"

# Singapore (Uncomment to use)
# export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/api/v1/"
```

### Step 3: Install skill

After cloning this repo, specify the installation of the corresponding skill in the AI Agent's chat interface, using wan2.7-image-skill as an example:

clone this repo
```bash
git clone https://github.com/Wan-Video/Wan-skills.git
```

Specify the skill path in the AI Agent chat interface for installation, where `/path/to/` is the actual local path on the user's machine.

```
Install the skill from this directory  /path/to/Wan-skills/skills/wan2.7-image-skill
```

## 📂 Project Structure

```
Wan-skills/
├── README.md
├── LICENSE
└── skills/
    └── wan2.7-image-skill/                     # wan2.7-image image generation and editing skill
        ├── references
        │   ├── common.md                       # General configuration documentation
        │   └── image-generation-editing.md     # Detailed usage documentation
        ├── scripts
        │   ├── check_wan_task_status.py        # Asynchronous task status query script
        │   ├── file_to_oss.py                  # File upload script
        │   ├── image-generation-editing.py     # Core generation script
        │   └── parse_resolution.py             # Resolution parsing script
        └── SKILL.md                            # Skill description file
```

---

## API Reference Documentation
[Wan2.7 - image generation and editing](https://modelstudio.console.alibabacloud.com/ap-southeast-1?tab=api#/api/?type=model&url=3026980)
[万相-图像生成与编辑2.7](https://bailian.console.aliyun.com/cn-beijing?tab=api#/api/?type=model&url=3026980)
