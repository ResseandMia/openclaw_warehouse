---
name: podcast-to-notion-workflow
description: |
  一键处理 YouTube 播客视频：字幕提取 → 内容摘要 → AI生图 → Notion保存
  触发词：「处理播客」「一键摘要」「播客工作流」
---

# 一键播客工作流 v2.0

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    播客工作流系统 v2.0                        │
├─────────────────────────────────────────────────────────────┤
│  阶段1: 发现                                                │
│  ├── 定时检查25位META博主 (每天 9:00)                        │
│  └── 发现新视频 → 添加到Notion待处理队列                     │
├─────────────────────────────────────────────────────────────┤
│  阶段2: 队列管理 (Notion数据库)                              │
│  ├── 📥 播客待处理队列                                       │
│  │   ├── 状态: 🆕待处理 / 📋已提取字幕 / ✍️处理中 / ✅已完成  │
│  │   ├── 优先级: 🔥高 / ⭐中 / 📌低                          │
│  │   └── 字段: 视频标题/博主/链接/发布日期/发现日期/分类标签   │
│  └── 优势: 分批处理，避免一次性处理过多视频                  │
├─────────────────────────────────────────────────────────────┤
│  阶段3: 每日处理 (每天 10:00)                                │
│  ├── 从队列取2-3个🔥高优先级视频                             │
│  ├── 字幕提取 (TranscriptAPI)                                │
│  ├── 内容摘要 (content-digest)                               │
│  ├── AI生图 (Nano Banana - 小红书卡片)                       │
│  ├── 保存到🎙️播客知识库 V3                                   │
│  └── 更新状态为✅已完成                                       │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 监控脚本
**文件**: `skills/youtube-feed/scripts/check_meta_v2.py`

**功能**:
- 检查25位META博主YouTube更新
- 获取Channel ID列表（内置）
- 解析RSS feed获取最近视频
- 将新视频添加到Notion待处理队列

**运行**:
```bash
python3 skills/youtube-feed/scripts/check_meta_v2.py
```

### 2. 待处理队列数据库
**Notion Database**: `📥 播客待处理队列`  
**ID**: `30183d24-986d-81cd-b25f-cd31bd9d87ba`  
**链接**: https://www.notion.so/30183d24986d81cdb25fcd31bd9d87ba

**字段说明**:
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| 视频标题 | Title | 视频标题 |
| 博主 | Select | 频道名称 |
| 视频链接 | URL | YouTube链接 |
| 发布日期 | Date | 视频发布日期 |
| 发现日期 | Date | 系统发现日期 |
| 状态 | Select | 🆕/📋/✍️/✅/❌ |
| 优先级 | Select | 🔥/⭐/📌 |
| 分类标签 | Multi-select | 内容分类 |
| 备注 | Rich text | 处理备注 |

**状态流程**:
```
🆕 待处理 → 📋 已提取字幕 → ✍️ 处理中 → ✅ 已完成
     ↓
   ❌ 跳过
```

### 3. 每日处理脚本
**文件**: `skills/youtube-feed/scripts/process_daily_queue.py`

**功能**:
- 查询🔥高优先级且🆕待处理的视频
- 每天最多处理3个
- 按发现日期排序（先入先出）
- 提取字幕、生成摘要、保存到知识库
- 更新状态

**运行**:
```bash
python3 skills/youtube-feed/scripts/process_daily_queue.py
```

### 4. 工作流脚本
**文件**: `skills/podcast-to-notion-workflow/scripts/workflow.py`

**功能**:
- 单视频完整处理流程
- 字幕提取 → 摘要 → 生图 → Notion保存

**使用**:
```bash
python3 scripts/workflow.py --url "YOUTUBE_URL" --channel "博主名"
```

## 定时任务配置

### 任务1: 每日播客检查
```json
{
  "name": "播客更新检查-META",
  "schedule": "0 9 * * *",
  "timezone": "Asia/Shanghai",
  "action": "运行 check_meta_v2.py 检查更新"
}
```

### 任务2: 每日播客处理
```json
{
  "name": "每日播客处理",
  "schedule": "0 10 * * *",
  "timezone": "Asia/Shanghai",
  "action": "运行 process_daily_queue.py 处理3个视频"
}
```

## 25位META博主列表

| # | 博主 | Handle | Channel ID |
|:---|:---|:---|:---|
| 1 | Mark Builds Brands | @markbuildsbrands | UCkRbLkvUX5zuwnKOBwFHOjg |
| 2 | Anthony V Camacho | @anthonyvcamacho | UCRWXCice10Mc8Q03F12n0lg |
| 3 | Ale Cordeddu | @alecordeddu | UC4EhDIzjoucaGo_DSbsc09Q |
| 4 | Tiana Asperjan | @TianaAsperjan | UCMGOWVTVf-Ifmqo2o-xhlaw |
| 5 | Jeremy Haynes Training | @JeremyHaynesTraining | UCuzbImxdBNTUeolGXpLVL0A |
| 6 | Adam Griffinn | @AdamGriffinn | UCdPol0HT-LRJZ2e0BTlk8TQ |
| 7 | Manel Gomez Official | @ManelGomezOfficial | UC1vPamoNz06tgbfkmSuA_eg |
| 8 | William Kast | @WilliamKast_ | UCcWoNjTgGubStM0znmnUa1A |
| 9 | Sabri Suby | @SabriSubyOfficial | UCAxUtcgLiq_gopO87VaZM5w |
| 10 | Blake Jones | @blakejonesecom | UCg3xYiZQj8-uQL2v0S_ahMg |
| 11 | Evan Seech | @EvanSeech12 | UCH-ujTCpi2D4ScwCgcXzT0w |
| 12 | Fernando Oliver | @FernandoOliver11 | UCft_4WI2teohQzVUUc4fQlQ |
| 13 | Timpano Dante | @TimpanoDante | UCe_YpLjZwTpXIWXiV1LK2aQ |
| 14 | Brando Monetti | @brandomonetti | UCYlLHxZs2uyK9-v__BTwJVg |
| 15 | Alex Hormozi | @AlexHormozi | UCUyDOdBWhC1MCxEjC46d-zw |
| 16 | Marcus Zanquila | @marcuszanquila | UCI5kGYUAdjFxW1dmrJet22w |
| 17 | Fraser Cottrell | @FraserCottrell | UC8xkoDqgLjJq_lfi2DBfAQA |
| 18 | Sam Piliero | @SamPiliero | UCFFCa4tMjhj9g_xKlvqFWxg |
| 19 | Digital Ad Guide | @digitaladguide | UCJtOmNBW_XuV-F0Z3ydfYHQ |
| 20 | Adam Taylor | @adamtaylorl | UCtBK_brawRM-Lo1beeHWzwA |
| 21 | D2C Diaries | @d2cdiaries | UCaB1dzAwsxDp6vWqaH7ZNLg |
| 22 | Stuff About Advertising | @StuffAboutAdvertising | UCErPUEJHpFwrTH-BDakPOZw |
| 23 | Ecomm Moose | @ecommmoose | UCSNj6DwyGL9qhG_8KPyeXYw |
| 24 | Tier11 | @Tier11 | UCaJKpcYpU3xxvEj9N_lLH8A |
| 25 | Perpetual Traffic | @perpetual_traffic | UCBHuj4q2Gxv7vSVaDrlpLeA |

## API Keys (环境变量)

```bash
# Notion
export NOTION_TOKEN="ntn_..."

# TranscriptAPI (YouTube字幕)
export TRANSCRIPT_API_KEY="sk_..."

# Nano Banana (AI生图)
export NANOBANANA_KEY="..."

# 可选: YouTube Data API (备用方案)
export YOUTUBE_API_KEY="..."
```

## Notion数据库

| 数据库 | 用途 | ID |
|:---|:---|:---|
| 📺 播客监听清单 | 25位博主信息 | 30083d24986d81fd81a9dd941383aea2 |
| 📥 播客待处理队列 | 待处理视频 | 30183d24986d81cdb25fcd31bd9d87ba |
| 🎙️ 播客知识库 V3 | 已完成内容 | 30083d24986d81aab0bac4c5a29baceb |

## 工作流程图

```
Day 1: 发现更新
├─ 9:00 AM 定时检查
├─ 发现34个新视频
└─ 添加到Notion待处理队列（全部🆕待处理）

Day 1+: 每日处理
├─ 10:00 AM 定时处理
├─ 取3个🔥高优先级视频
├─ 字幕提取 → 摘要 → 生图 → 保存
└─ 更新状态为✅已完成

预计完成时间: 34个视频 / 每天3个 ≈ 12天
```

## 手动操作

### 立即处理单个视频
```bash
# 从队列中取一个视频处理
python3 skills/youtube-feed/scripts/process_daily_queue.py --limit 1

# 或者直接处理指定URL
python3 skills/podcast-to-notion-workflow/scripts/workflow.py \
  --url "https://www.youtube.com/watch?v=..." \
  --channel "博主名"
```

### 查看队列状态
打开Notion: https://www.notion.so/30183d24986d81cdb25fcd31bd9d87ba

### 调整优先级
在Notion中直接修改"优先级"字段

## 扩展功能 (TODO)

- [ ] 微信公众号自动发布
- [ ] 小红书图片自动生成
- [ ] 多语言翻译 (英文→中文)
- [ ] 视频内容标签自动分类
- [ ] 处理完成通知 (Telegram)

## 文件结构

```
skills/
├── podcast-to-notion-workflow/
│   ├── SKILL.md (本文档)
│   └── scripts/
│       └── workflow.py
├── youtube-feed/
│   └── scripts/
│       ├── check_meta_v2.py      # 每日检查
│       └── process_daily_queue.py # 每日处理
├── content-digest/
├── youtube-transcript-cn/
├── markdown-to-image/
└── wechat-publisher/
```

## 版本历史

- v1.0: 基础工作流，单视频处理
- v2.0: 添加队列系统，支持批量管理和分批处理

---
*Generated by kimi大总管 v2.0*
