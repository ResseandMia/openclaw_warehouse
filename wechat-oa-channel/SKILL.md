---
name: wechat-oa-channel
description: |
  WeChat Official Account Draft Box management tool. Create and manage graphic draft articles via WeChat API, supporting text and images. Automatically extracts the first paragraph as summary. Supports draft creation, listing, publishing, and deletion.
  微信公众号素材管理工具。通过微信API创建和管理图文草稿箱，支持文字和图片。自动提取第一段作为摘要。支持草稿创建、列表、发布和删除。
---

# WeChat OA Channel

微信公众号素材管理工具 / WeChat Official Account Draft Box Management

## Features

- 📝 **创建草稿** - 从文本或文件创建图文草稿
- 🖼️ **图片上传** - 支持封面图片和内容图片
- 📋 **草稿列表** - 查看和管理现有草稿
- ✅ **发布草稿** - 将草稿发布到公众号
- 🗑️ **删除草稿** - 清理不需要的草稿
- 🤖 **自动摘要** - 自动提取文章第一段作为摘要

## Usage

**创建草稿：**
```
"创建微信草稿"
"在公众号发布新文章"
```

**管理草稿：**
```
"列出所有草稿"
"删除草稿 XXX"
"发布草稿 XXX"
```

## Prerequisites

1. WeChat Official Account (公众号)
2. AppID and AppSecret (应用ID和密钥)
3. WeChat API access token

## Configuration

Required environment variables:
```bash
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
WECHAT_ACCESS_TOKEN=your_access_token  # or get automatically
```

## Core Workflows

### Create Draft from Text

```bash
python3 scripts/channel.py create \
  --title "文章标题" \
  --content "文章内容..." \
  --author "作者名" \
  --cover "cover_image_url"
```

### Create Draft from File

```bash
python3 scripts/channel.py create \
  --file article.md \
  --author "作者名" \
  --cover "cover_image_url"
```

### List Drafts

```bash
python3 scripts/channel.py list
```

### Publish Draft

```bash
python3 scripts/channel.py publish --id DRAFT_ID
```

### Delete Draft

```python scripts/channel.py delete --id DRAFT_ID
```

## Output Format

All commands return JSON:
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}
```

## Error Handling

- Missing credentials → Prompt user to configure
- API rate limit → Retry with backoff
- Invalid content → Return detailed error
- Network issues → Retry 3 times

## Automation Examples

**Batch publish workflow:**
```bash
# List all drafts
python3 scripts/channel.py list --format json > drafts.json

# Filter and publish
for draft in $(cat drafts.json | jq -r '.[].id'); do
  python3 scripts/channel.py publish --id $draft
done
```

**Scheduled publishing:**
```bash
# Cron job to publish daily
0 9 * * * python3 /path/to/channel.py publish --id TODAYS_DRAFT
```

## Links

- WeChat Official Account Platform: https://mp.weixin.qq.com
- WeChat API Documentation: https://developers.weixin.qq.com/doc/offiaccount/en

## Source

Skill from ClawHub by @AlphaFactor
- ClawHub: https://www.clawhub.ai/AlphaFactor/channel
