---
name: podcast-to-notion-workflow
description: |
  一键处理 YouTube 播客视频：字幕提取 → 内容摘要 → AI生图 → Notion保存
  完整6步工作流：youtube-feed → transcript → content-digest → markdown-to-image → Notion
  触发词：「处理播客」「一键摘要」「播客工作流」
---

# 一键播客工作流 v2.5

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      播客工作流系统 v2.5（完整6步）                        │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 1: 发现 (youtube-feed)                                            │
│  ├── 定时检查25位META博主 (每天 9:00)                                     │
│  └── 发现新视频 → 添加到Notion待处理队列 (🆕待处理)                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 2: 队列管理 (Notion)                                               │
│  ├── 📥 播客待处理队列                                                    │
│  │   ├── 状态: 🆕待处理 / 📋已提取字幕 / ✍️处理中 / ✅已完成 / ❌跳过       │
│  │   └── 优先级: 🔥高 / ⭐中 / 📌低                                       │
│  └── 优势: 分批处理，避免一次性处理过多视频                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 3: 每日处理 (每天 10:00)                                           │
│  ├── 从队列取2-3个🔥高优先级视频                                          │
│  ├── 字幕提取 (TranscriptAPI / youtube-transcript)                        │
│  ├── 📝 内容摘要 (content-digest)                                         │
│  │   ├── 四阶段分析: 穷举→过滤→策展→输出                                 │
│  │   ├── 输出: 短文(10-15条) + 长文(叙事精编)                              │
│  │   └── 格式: 中文正文 + 英文术语保留                                    │
│  ├── 🎨 生成图片 (markdown-to-image)                                      │
│  │   ├── 解析content-digest格式                                          │
│  │   ├── 生成: 封面 + 内容页 + 尾页                                       │
│  │   └── 输出: 1080×1440 PNG (小红书3:4)                                  │
│  ├── 💾 保存到🎙️播客知识库 V3 (Notion)                                     │
│  └── ✅ 更新状态为已完成                                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 核心 Skills

### 1. youtube-feed（监控发现）
**文件**: `skills/youtube-feed/scripts/check_meta_v2.py`

**功能**:
- 检查25位META博主YouTube更新
- 解析RSS feed获取最近视频
- 将新视频添加到Notion待处理队列

**运行**:
```bash
python3 skills/youtube-feed/scripts/check_meta_v2.py
```

---

### 2. content-digest（内容摘要）⭐ 新增
**文件**: `skills/content-digest/`

**功能**:
- **四阶段深度分析**：穷举→过滤→策展→输出
- **双语处理**：中文正文 + 英文术语保留
- **输出两版**：
  - **短文**：10-15条编号观点（小红书格式）
  - **长文**：叙事性精编文章（公众号/Notion）

**输入格式**:
```markdown
# MMDD：嘉宾 X 栏目：核心观点

嘉宾背景介绍（2-3句，含具体数据）...

1、**加粗关键词** — 观点文本。逻辑推理解释。
2、...
```

**输出格式**:
- 短文：编号观点列表（顿号分隔、每条2-4句）
- 长文：Style B 编辑精编（#01 #02 主题段）

**运行**:
```bash
# 在播客工作流中自动调用
# 或手动: python3 skills/content-digest/scripts/digest.py -f transcript.md
```

**参考文档**:
- `SKILL.md` - 完整工作流程
- `references/style-guide.md` - 写作规范
- `references/examples.md` - 输出示例

---

### 3. markdown-to-image（图片生成）⭐ 新增
**文件**: `skills/markdown-to-image/scripts/md_to_image.py`

**功能**:
- 解析content-digest输出格式
- 生成多页图片海报：
  - **封面页**：嘉宾名 × 栏目名 + 核心观点
  - **内容页**：编号观点列表（自适应字体大小）
  - **尾页**：THE END + 互动引导
- **智能分页**：按字数而非固定条目数
- **主题自动匹配**：AI/Marketing/Startup/Product/Engineering/Growth/Open Source/Podcast

**输入格式契约**（来自content-digest）:
```markdown
# MMDD：嘉宾 X 栏目：核心观点

1、**关键词** — 观点文本...
2、...
```

**输出**:
```
output_dir/
├── page_1.png ← 封面页 (1080×1440)
├── page_2.png ← 内容页1
├── page_3.png ← 内容页2
└── page_N.png ← 尾页
```

**运行**:
```bash
python3 skills/markdown-to-image/scripts/md_to_image.py \
  -f content-digest-output.md \
  -o /mnt/user-data/outputs/poster \
  -t default
```

**参数**:
| 参数 | 说明 | 默认 |
|:---|:---|:---|
| `-f` | 输入Markdown文件 | 必填 |
| `-o` | 输出目录 | attachments/MMDD |
| `-t` | 主题: default/warm/dark | default |
| `--no-cover` | 不生成封面 | false |
| `--no-end` | 不生成尾页 | false |

**参考文档**:
- `SKILL.md` - 完整使用指南
- `scripts/md_to_image_v2_reference.py` - 完整功能参考代码

---

### 4. Notion 数据库（存储管理）

#### 📥 播客待处理队列
**ID**: `30183d24-986d-81cd-b25f-cd31bd9d87ba`  
**链接**: https://www.notion.so/30183d24986d81cdb25fcd31bd9d87ba

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| 视频标题 | Title | YouTube视频标题 |
| 博主 | Select | 频道名称（25位META博主之一）|
| 视频链接 | URL | YouTube链接 |
| 发布日期 | Date | 视频发布日期 |
| 发现日期 | Date | 系统发现日期 |
| 状态 | Select | 🆕/📋/✍️/✅/❌ |
| 优先级 | Select | 🔥高 / ⭐中 / 📌低 |
| 分类标签 | Multi-select | AI/Marketing/Startup等 |
| 备注 | Rich text | 处理备注 |

**状态流程**:
```
🆕 待处理 → 📋 已提取字幕 → ✍️ 处理中 → ✅ 已完成
     ↓
   ❌ 跳过
```

#### 🎙️ 播客知识库 V3（已完成内容存储）
**ID**: `30083d24986d81aab0bac4c5a29baceb`

存储：
- 视频元信息（标题、博主、链接）
- content-digest 输出（短文+长文）
- markdown-to-image 生成的图片
- 标签分类

---

## 完整工作流程

### 阶段1: 发现（自动）
```
每天 9:00 AM
    ↓
youtube-feed 检查25位博主
    ↓
发现新视频 → 添加到Notion待处理队列（状态：🆕待处理）
```

### 阶段2: 处理（自动/手动）
```
每天 10:00 AM（或手动触发）
    ↓
从队列取2-3个🔥高优先级视频
    ↓
Step 3: 字幕提取（TranscriptAPI）
    ↓
Step 4: 内容摘要（content-digest）
    ├── 四阶段分析
    ├── 生成短文（10-15条观点）
    └── 生成长文（叙事精编）
    ↓
Step 5: 图片生成（markdown-to-image）
    ├── 解析content-digest格式
    ├── 生成封面+内容页+尾页
    └── 输出1080×1440 PNG
    ↓
Step 6: 保存到Notion知识库
    ├── 保存文本摘要
    ├── 上传图片
    └── 更新状态为✅已完成
```

---

## 定时任务配置

| 任务 | 时间 | 功能 | 命令 |
|:---|:---|:---|:---|
| **播客更新检查** | 9:00 AM | 检查25位博主新视频 | `check_meta_v2.py` |
| **每日播客处理** | 10:00 AM | 处理2-3个高优先级视频 | `process_daily_queue.py` |

---

## 25位META博主列表

| # | 博主 | Handle | Channel ID | 优先级 |
|:---|:---|:---|:---|:---:|
| 1 | Mark Builds Brands | @markbuildsbrands | UCkRbLkvUX5zuwnKOBwFHOjg | ⭐ |
| 2 | Anthony V Camacho | @anthonyvcamacho | UCRWXCice10Mc8Q03F12n0lg | ⭐ |
| 3 | Ale Cordeddu | @alecordeddu | UC4EhDIzjoucaGo_DSbsc09Q | ⭐ |
| 4 | Tiana Asperjan | @TianaAsperjan | UCMGOWVTVf-Ifmqo2o-xhlaw | 🔥 |
| 5 | Jeremy Haynes Training | @JeremyHaynesTraining | UCuzbImxdBNTUeolGXpLVL0A | 🔥 |
| 6 | Adam Griffinn | @AdamGriffinn | UCdPol0HT-LRJZ2e0BTlk8TQ | ⭐ |
| 7 | Manel Gomez Official | @ManelGomezOfficial | UC1vPamoNz06tgbfkmSuA_eg | ⭐ |
| 8 | William Kast | @WilliamKast_ | UCcWoNjTgGubStM0znmnUa1A | 🔥 |
| 9 | Sabri Suby | @SabriSubyOfficial | UCAxUtcgLiq_gopO87VaZM5w | 🔥 |
| 10 | Blake Jones | @blakejonesecom | UCg3xYiZQj8-uQL2v0S_ahMg | ⭐ |
| 11 | Evan Seech | @EvanSeech12 | UCH-ujTCpi2D4ScwCgcXzT0w | ⭐ |
| 12 | Fernando Oliver | @FernandoOliver11 | UCft_4WI2teohQzVUUc4fQlQ | ⭐ |
| 13 | Timpano Dante | @TimpanoDante | UCe_YpLjZwTpXIWXiV1LK2aQ | ⭐ |
| 14 | Brando Monetti | @brandomonetti | UCYlLHxZs2uyK9-v__BTwJVg | ⭐ |
| 15 | Alex Hormozi | @AlexHormozi | UCUyDOdBWhC1MCxEjC46d-zw | 🔥 |
| 16 | Marcus Zanquila | @marcuszanquila | UCI5kGYUAdjFxW1dmrJet22w | ⭐ |
| 17 | Fraser Cottrell | @FraserCottrell | UC8xkoDqgLjJq_lfi2DBfAQA | 🔥 |
| 18 | Sam Piliero | @SamPiliero | UCFFCa4tMjhj9g_xKlvqFWxg | ⭐ |
| 19 | Digital Ad Guide | @digitaladguide | UCJtOmNBW_XuV-F0Z3ydfYHQ | ⭐ |
| 20 | Adam Taylor | @adamtaylorl | UCtBK_brawRM-Lo1beeHWzwA | ⭐ |
| 21 | D2C Diaries | @d2cdiaries | UCaB1dzAwsxDp6vWqaH7ZNLg | 🔥 |
| 22 | Stuff About Advertising | @StuffAboutAdvertising | UCErPUEJHpFwrTH-BDakPOZw | ⭐ |
| 23 | Ecomm Moose | @ecommmoose | UCSNj6DwyGL9qhG_8KPyeXYw | ⭐ |
| 24 | Tier11 | @Tier11 | UCaJKpcYpU3xxvEj9N_lLH8A | ⭐ |
| 25 | Perpetual Traffic | @perpetual_traffic | UCBHuj4q2Gxv7vSVaDrlpLeA | 🔥 |

---

## Skill 间格式契约

### content-digest → markdown-to-image

**标题格式**:
```
# MMDD：嘉宾 X 栏目：核心观点文本
```

**列表格式**:
```markdown
1、**加粗关键词** — 观点文本。逻辑推理解释。
2、...
```

**编码**: UTF-8, Unix 换行符（LF）

**关键字段**:
- `MMDD`: 日期（用于文件命名）
- `嘉宾`: 用于封面页大标题
- `栏目`: 用于封面页副标题
- `核心观点`: 用于封面页主文案

---

## API Keys & 依赖

```bash
# Notion
export NOTION_TOKEN="ntn_..."

# TranscriptAPI (YouTube字幕)
export TRANSCRIPT_API_KEY="sk_..."

# Playwright (markdown-to-image依赖)
pip3 install playwright
playwright install chromium

# 系统字体 (Linux)
apt install fonts-noto-cjk  # 或 yum install google-noto-sans-cjk-fonts
```

---

## 文件结构

```
skills/
├── podcast-to-notion-workflow/          # 本工作流
│   ├── SKILL.md                         # 本文档
│   └── scripts/
│       └── workflow.py                  # 单视频处理脚本
│
├── youtube-feed/                        # Step 1: 监控发现
│   └── scripts/
│       ├── check_meta_v2.py             # 每日检查25位博主
│       └── process_daily_queue.py       # 每日处理队列
│
├── content-digest/                      # Step 4: 内容摘要 ⭐ NEW
│   ├── SKILL.md
│   ├── references/
│   │   ├── style-guide.md               # 写作规范
│   │   └── examples.md                  # 输出示例
│   └── scripts/
│       └── digest.py
│
├── markdown-to-image/                   # Step 5: 图片生成 ⭐ NEW
│   ├── SKILL.md
│   └── scripts/
│       ├── md_to_image.py               # v1.0 基础版
│       └── md_to_image_v2_reference.py  # v2.0 完整参考
│
└── [其他辅助skills]
    ├── youtube-transcript-cn/           # 字幕提取
    ├── wechat-publisher/                # 公众号发布
    └── notion-wiki/                     # Notion存储
```

---

## 手动操作指南

### 处理单个视频（完整流程）
```bash
# 1. 获取字幕（手动）
# 使用 TranscriptAPI 或其他方式获取transcript

# 2. 内容摘要
cd skills/content-digest
python3 scripts/digest.py -f transcript.md -o digest-output.md

# 3. 生成图片
cd skills/markdown-to-image
python3 scripts/md_to_image.py \
  -f ../../content-digest/digest-output.md \
  -o /mnt/user-data/outputs/poster \
  -t default

# 4. 保存到Notion（手动或脚本）
```

### 查看队列状态
打开Notion: https://www.notion.so/30183d24986d81cdb25fcd31bd9d87ba

### 调整视频优先级
在Notion待处理队列中直接修改"优先级"字段

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|:---|:---|:---|
| v1.0 | 2024-02-07 | 基础工作流，单视频处理 |
| v2.0 | 2024-02-08 | 添加队列系统，支持批量管理和分批处理 |
| **v2.5** | **2024-02-08** | **新增 content-digest 和 markdown-to-image，完整6步工作流** |

---

## 待办优化 (TODO)

- [ ] 微信公众号自动发布 (wechat-publisher)
- [ ] 小红书自动发布 (auto-redbook-skills)
- [ ] 多语言翻译 (英文→中文 自动化)
- [ ] 视频内容标签自动分类
- [ ] 处理完成 Telegram 通知
- [ ] markdown-to-image v2.0 功能迁移（智能分页、SVG主题、配色系统）

---

*Generated by kimi大总管 v2.5*  
*Last Updated: 2024-02-08*
