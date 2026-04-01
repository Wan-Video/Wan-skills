# Wan-skills
> 基于Wan的AI Agent Skills —— 让你的 AI Agent 轻松调用 Wan 的 AIGC 能力。
---
## 🌟 核心能力
**Wan-skills** 是一组面向 AI Agent 的技能包（Skills），通过调用API接口的方式赋予 AI Agent 相关 AIGC 能力。

**技能列表**

| 技能 | 描述 | 脚本 | 参考 |
|------|------|------|------|
| **wan2.7-image-skill** | 通过wan2.7-image模型的图像生成和编辑能力进行创作 | `image-generation-editing.py` `file_to_oss.py` `parse_resolution.py` `check_wan_task_status.py` | `common.md` `image-generation-editing.md` |

将持续更新多种技能到技能列表。

---

## 🚀 快速开始

### Step 1: 获取 API Key

**前提条件：** 需要阿里云账号

1. **注册阿里云账号**
   - 访问 https://www.aliyun.com/
   - 完成账号注册和实名认证

2. **开通百炼服务**
   - 访问 https://bailian.console.aliyun.com/
   - 开通百炼服务

3. **创建 API Key**
   - 进入百炼控制台 → API-KEY管理
   - 创建新的 API Key

### Step 2: 配置环境变量

```bash
export DASHSCOPE_API_KEY="your-access-key"
```

**地域选择**

根据所在地域选择合适的`DASHSCOPE_BASE_URL`
```bash
# 中国大陆（北京）- 默认
export DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/api/v1/"

# 新加坡（取消注释使用）
# export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/api/v1/"
```

### Step 3: 安装

clone本项目后，在AI Agent的对话框，指定安装对应的skill，以wan2.7-image-skill为例：

clone本项目
```bash
git clone https://github.com/Wan-Video/Wan-skills.git
```

在AI Agent对话框指定skill路径进行安装，其中`/path/to/`是用户本地真实路径地址。

```
安装这个目录下的skill  /path/to/Wan-skills/skills/wan2.7-image-skill
```

## 📂 项目结构

```
Wan-skills/
├── README.md
├── LICENSE
└── skills/
    └── wan2.7-image-skill/                     # wan2.7-image图像生成编辑技能
        ├── references
        │   ├── common.md                       # 通用配置文档
        │   └── image-generation-editing.md     # 详细用法文档
        ├── scripts
        │   ├── check_wan_task_status.py        # 异步任务查询脚本
        │   ├── file_to_oss.py                  # 文件上传脚本
        │   ├── image-generation-editing.py     # 核心生成脚本
        │   └── parse_resolution.py             # 分辨率解析脚本
        └── SKILL.md                            # 技能描述文件
```

---

## API 参考文档
[万相-图像生成与编辑2.7](https://bailian.console.aliyun.com/cn-beijing?tab=api#/api/?type=model&url=3026980)
