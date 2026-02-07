---
name: podcast-to-notion-workflow
description: |
  一键处理 YouTube 播客视频：字幕提取 → 内容摘要 → AI生图 → Notion保存
  触发词：「处理播客」「一键摘要」「播客工作流」
---

# 一键播客工作流

## 功能
1. 字幕提取 (TranscriptAPI)
2. 内容摘要 (content-digest)
3. AI生图 (Nano Banana)
4. Notion保存

## 使用
```bash
python3 scripts/workflow.py --url "..." --channel "..."
```

## 监听清单
24位META博主 + 13位默认频道 = 37个频道
每日UTC 9:00自动检查

## API Keys (环境变量)
- TRANSCRIPT_API_KEY
- NANOBANANA_KEY
- NOTION_TOKEN
