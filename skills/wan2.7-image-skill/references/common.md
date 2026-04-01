# Common Configuration（通用配置）

本文档包含所有 Skill 共享的基础配置和环境变量。

---

## Quick Setup（快速配置）

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

**Region Selection（地域选择）**
```bash
# 中国大陆（北京）- 默认
export DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/api/v1/"

# 新加坡（取消注释使用）
# export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/api/v1/"
```

---

## Related Documents

- 📖 [SKILL.md](../SKILL.md) - 整体工作流和技能列表
- 📖 [image-generation-editing.md](image-generation-editing.md) - 文生图/图生图/编辑/组图生成的细节和例子的说明文档
- 🐍 [file_to_oss.py](../scripts/file_to_oss.py) - 本地文件上传脚本
- 🐍 [parse_resolution.py](../scripts/parse_resolution.py) - 解析用户输入的分辨率的脚本
- 🐍 [image-generation-editing.py](../scripts/image-generation-editing.py) - 文生图/图生图/编辑/组图生成的脚本
