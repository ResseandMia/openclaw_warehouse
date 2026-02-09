# 播客工作流完整文档 v3.0

## 📋 目录
1. [系统架构](#系统架构)
2. [完整工作流程](#完整工作流程)
3. [Skills 详解](#skills-详解)
4. [API 配置](#api-配置)
5. [使用指南](#使用指南)
6. [文件结构](#文件结构)
7. [更新日志](#更新日志)

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     播客工作流系统 v3.0（完整6步）                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 1: 发现监控 (youtube-feed)                                        │
│  ├── 定时检查25位META博主 (每天 9:00)                                     │
│  └── 发现新视频 → 添加到Notion待处理队列                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 2: 队列管理 (Notion)                                               │
│  └── 📥 播客待处理队列                                                    │
│      ├── 状态: 🆕待处理 → 📋已提取字幕 → ✍️处理中 → ✅已完成              │
│      └── 优先级: 🔥高 / ⭐中 / 📌低                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 3: 字幕提取 (youtube-transcript)                                   │
│  └── 使用 TranscriptAPI 获取 YouTube 视频字幕                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 4: 内容摘要 (content-digest) ⭐ 核心                               │
│  └── 四阶段分析 → 短文(12条观点) + 长文(叙事精编)                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 5: 图片生成 (markdown-to-image) ⭐ 核心                             │
│  └── 速创 Nano Banana API 生成小红书风格图片                              │
│      └── 封面 + 内容页(5条/页) + 尾页                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  Step 6: 保存发布 (notion-wiki)                                          │
│  └── 保存到🎙️播客知识库 V3 (Notion)                                       │
│      └── 文字摘要 + 图片 + 标签分类                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 完整工作流程

### 阶段1: 发现（自动，每天9:00）
```
 youtube-feed 检查25位META博主
         ↓
 发现新视频
         ↓
 添加到 Notion 待处理队列（状态：🆕待处理）
```

### 阶段2: 处理（自动，每天10:00）
```
 从队列取2-3个🔥高优先级视频
         ↓
 字幕提取（TranscriptAPI）
         ↓
 内容摘要（content-digest）
    ├── 穷举阶段：识别所有潜在洞察
    ├── 过滤阶段：筛选非共识洞察
    ├── 策展阶段：构建叙事弧线
    └── 输出阶段：短文+长文双语格式
         ↓
 图片生成（markdown-to-image）
    ├── 封面页：日期+嘉宾+栏目+核心观点
    ├── 内容页1：观点1-5 + 图标
    ├── 内容页2：观点6-10 + 图标
    └── 尾页：THE END + 互动引导
         ↓
 保存到 Notion 播客知识库
    ├── 元信息（标题、博主、链接）
    ├── 文字摘要（12条观点完整版）
    └── 图片（4张小红书风格）
         ↓
 更新状态为 ✅已完成
```

---

## Skills 详解

### 1️⃣ youtube-feed（发现监控）

**文件**: `skills/youtube-feed/scripts/check_meta_v2.py`

**功能**:
- 检查25位META博主YouTube更新
- 解析RSS feed获取最近视频
- 将新视频添加到Notion待处理队列

**运行**:
```bash
python3 skills/youtube-feed/scripts/check_meta_v2.py
```

**输出示例**:
```
🎬 Mark Builds Brands: "How to Scale Your Brand" (2026-02-08)
🎬 Alex Hormozi: "The VSSL Framework" (2026-02-08)
✅ 发现2个新视频，已添加到队列
```

---

### 2️⃣ content-digest（内容摘要）⭐ 核心

**文件**: `skills/content-digest/`

**四阶段分析框架**:
1. **Enumerate** - 穷举所有值得注意的点
2. **Filter** - 筛选有价值的非共识洞察
3. **Curate** - 构建叙事弧线
4. **Output** - 双语输出（中文正文+英文术语）

**输出格式**:

**短文版（小红书）**:
```markdown
# MMDD：嘉宾 X 栏目：核心观点

1、**加粗关键词** — 观点核心。详细解释。
2、...
```

**长文版（公众号/Notion）**:
```markdown
# Style B：叙事精编

## #01 主题一
内容段落...

## #02 主题二
内容段落...
```

**运行**:
```bash
python3 skills/content-digest/scripts/digest.py -f transcript.md -o output.md
```

---

### 3️⃣ markdown-to-image（图片生成）⭐ 核心 ⭐

**文件**: `skills/markdown-to-image/scripts/md_to_image_nano.py`

**技术方案**: 速创 Nano Banana API（第三方）

**优势**:
- ✅ 无需安装 Chromium
- ✅ 云端渲染，速度快
- ✅ 跨平台兼容
- ✅ 小红书3:4标准比例

**API配置**:
```bash
export NANOBANANA_KEY="RS3onk9L9pkY237VGMRsJIWsXG"
export NANOBANANA_API_URL="https://api.wuyinkeji.com/api/img/nanoBanana-pro"
```

**运行**:
```bash
cd skills/markdown-to-image

# 设置API Key
export NANOBANANA_KEY="RS3onk9L9pkY237VGMRsJIWsXG"

# 生成图片
python3 scripts/md_to_image_nano.py \
  -f content-digest-output.md \
  -o /tmp/output
```

**输出**:
```
/tmp/output/
├── page_1_cover.png      # 封面 (1792×2400)
├── page_2_content.png    # 内容页1
├── page_3_content.png    # 内容页2
└── page_4_end.png        # 尾页
```

**设计风格**:
- **封面**: 暖色调渐变 + 大标题 + 几何装饰
- **内容页**: 编号列表 + 图标 + 珊瑚红配色
- **尾页**: THE END + 收藏/点赞/转发引导

---

### 4️⃣ Notion 数据库

#### 📥 播客待处理队列
**ID**: `30183d24-986d-81cd-b25f-cd31bd9d87ba`

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| 视频标题 | Title | YouTube视频标题 |
| 博主 | Select | 频道名称 |
| 视频链接 | URL | YouTube链接 |
| 状态 | Select | 🆕/📋/✍️/✅/❌ |
| 优先级 | Select | 🔥高 / ⭐中 / 📌低 |
| 标签 | Multi-select | AI/Marketing/Startup等 |

**状态流程**:
```
🆕 待处理 → 📋 已提取字幕 → ✍️ 处理中 → ✅ 已完成
     ↓
   ❌ 跳过
```

#### 🎙️ 播客知识库 V3（已完成内容）
**ID**: `30083d24-986d-81aa-b0ba-c4c5a29baceb`

存储：
- 视频元信息
- content-digest 输出（短文+长文）
- 4张小红书风格图片
- 标签分类

---

## API 配置

### 必需 API Keys

```bash
# Notion
export NOTION_TOKEN="ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# TranscriptAPI (YouTube字幕)
export TRANSCRIPT_API_KEY="sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 速创 Nano Banana (图片生成)
export NANOBANANA_KEY="your_nano_banana_key_here"
export NANOBANANA_API_URL="https://api.wuyinkeji.com/api/img/nanoBanana-pro"

# ImgBB (图片上传)
export IMGBB_API_KEY="your_imgbb_key_here"
```

**注**: 实际API Key请查看 TOOLS.md 或环境变量配置

### 依赖安装

```bash
# Python依赖
pip3 install requests

# 可选：Playwright（备用方案）
pip3 install playwright
playwright install chromium
```

---

## 使用指南

### 完整处理流程

#### 步骤1: 获取字幕
```bash
# 使用 TranscriptAPI
python3 skills/youtube-transcript-cn/scripts/get_transcript.py \
  --url "https://youtube.com/watch?v=xxx" \
  --output /tmp/transcript.md
```

#### 步骤2: 内容摘要
```bash
python3 skills/content-digest/scripts/digest.py \
  -f /tmp/transcript.md \
  -o /tmp/digest.md
```

#### 步骤3: 生成图片
```bash
export NANOBANANA_KEY="RS3onk9L9pkY237VGMRsJIWsXG"

python3 skills/markdown-to-image/scripts/md_to_image_nano.py \
  -f /tmp/digest.md \
  -o /tmp/xhs_images
```

#### 步骤4: 上传到图床
```bash
# 使用 ImgBB
curl -s -X POST "https://api.imgbb.com/1/upload?key=$IMGBB_API_KEY" \
  -F "image=@/tmp/xhs_images/page_1_cover.png"
```

#### 步骤5: 保存到 Notion
```bash
python3 skills/podcast-to-notion-workflow/scripts/save_to_notion.py \
  --title "0208：Tiana VSSL" \
  --content /tmp/digest.md \
  --images /tmp/xhs_images/
```

---

## 25位META博主列表

| # | 博主 | Handle | 优先级 |
|:---|:---|:---|:---:|
| 1 | Mark Builds Brands | @markbuildsbrands | ⭐ |
| 2 | Tiana Asperjan | @TianaAsperjan | 🔥 |
| 3 | Jeremy Haynes Training | @JeremyHaynesTraining | 🔥 |
| 4 | William Kast | @WilliamKast_ | 🔥 |
| 5 | Sabri Suby | @SabriSubyOfficial | 🔥 |
| 6 | Alex Hormozi | @AlexHormozi | 🔥 |
| 7 | Fraser Cottrell | @FraserCottrell | 🔥 |
| 8 | D2C Diaries | @d2cdiaries | 🔥 |
| 9 | Perpetual Traffic | @perpetual_traffic | 🔥 |
| 10-25 | 其他16位博主 | ... | ⭐ |

---

## 文件结构

```
skills/
├── podcast-to-notion-workflow/     # 主工作流
│   ├── SKILL.md                    # 本文档
│   └── scripts/
│       ├── workflow.py             # 一键处理脚本
│       └── save_to_notion.py       # Notion保存
│
├── youtube-feed/                   # Step 1: 发现
│   └── scripts/
│       └── check_meta_v2.py        # 25位博主监控
│
├── content-digest/                 # Step 4: 摘要 ⭐
│   ├── SKILL.md
│   └── scripts/
│       └── digest.py
│
├── markdown-to-image/              # Step 5: 图片 ⭐
│   ├── SKILL.md
│   └── scripts/
│       ├── md_to_image_nano.py     # Nano Banana API版 ⭐
│       └── md_to_image.py          # Playwright版（备用）
│
└── youtube-transcript-cn/          # Step 3: 字幕
    └── scripts/
        └── get_transcript.py
```

---

## 更新日志

### v3.0 (2026-02-09)
- ✅ **新增速创 Nano Banana API 图片生成方案**
- ✅ 替代 Playwright，无需本地 Chromium
- ✅ 完成 Tiana VSSL 测试（4张图片生成成功）
- ✅ 更新 TOOLS.md 保存 API 配置
- ✅ 完善完整工作流程文档

### v2.5 (2026-02-08)
- ✅ 新增 content-digest 四阶段分析框架
- ✅ 新增 markdown-to-image 图片生成
- ✅ 25位META博主队列系统
- ✅ 每日自动处理2-3个视频

### v2.0 (2026-02-07)
- ✅ 播客待处理队列（Notion）
- ✅ 分批处理机制

### v1.0 (2026-02-06)
- ✅ 基础工作流，单视频处理

---

*文档版本: v3.0*  
*更新时间: 2026-02-09*  
*维护者: kimi大总管* 🐾
