---
name: podcast-to-notion-workflow
description: |
  一键处理 YouTube 播客视频：字幕提取 → 内容摘要 → AI生图 → Notion保存
  完整6步工作流：youtube-feed → transcript → content-digest → markdown-to-image → Notion
  触发词：「处理播客」「一键摘要」「播客工作流」
---

# 播客工作流 v3.0

## 快速开始

```bash
# 1. 设置环境变量
export NOTION_TOKEN="ntn_..."
export TRANSCRIPT_API_KEY="sk_..."
export NANOBANANA_KEY="RS3onk9L9pkY237VGMRsJIWsXG"

# 2. 一键处理
python3 scripts/workflow.py --url "https://youtube.com/watch?v=xxx"
```

## 完整6步工作流

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: youtube-feed    → 监控25位META博主                  │
│  Step 2: Notion Queue    → 待处理队列管理                    │
│  Step 3: Transcript      → 字幕提取                          │
│  Step 4: content-digest  → 四阶段分析摘要 ⭐                 │
│  Step 5: markdown-to-image → Nano Banana生图 ⭐              │
│  Step 6: notion-wiki     → 保存到知识库                      │
└──────────────────────────────────────────────────────────────┘
```

## 核心特性

- ✅ **四阶段分析**: 穷举→过滤→策展→输出
- ✅ **双语内容**: 中文正文 + 英文术语
- ✅ **小红书生图**: 封面+内容页+尾页（3:4比例）
- ✅ **批量处理**: 每日自动处理2-3个高优先级视频
- ✅ **队列管理**: Notion待处理队列，状态跟踪

## 25位META博主监控

| 优先级 | 博主 |
|:---|:---|
| 🔥 高 | Alex Hormozi, Sabri Suby, Tiana Asperjan, William Kast, Jeremy Haynes, Fraser Cottrell, Perpetual Traffic |
| ⭐ 中 | 其他18位博主 |

## 技术栈

| 组件 | 技术 |
|:---|:---|
| 字幕提取 | TranscriptAPI |
| 内容摘要 | 四阶段分析框架 (GPT) |
| 图片生成 | 速创 Nano Banana API |
| 图片存储 | ImgBB |
| 数据存储 | Notion Database |
| 定时任务 | OpenClaw Cron |

## 详细文档

📄 **[完整文档](README.md)** - 包含完整工作流程、API配置、使用指南

## 相关Skills

- [content-digest](../content-digest/) - 内容摘要
- [markdown-to-image](../markdown-to-image/) - 图片生成
- [youtube-feed](../youtube-feed/) - 监控发现

---

*Version: 3.0* | *Updated: 2026-02-09*
