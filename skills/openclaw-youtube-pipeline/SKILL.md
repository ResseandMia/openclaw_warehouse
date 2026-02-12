---
name: openclaw-youtube-pipeline
description: |
  YouTube 播客内容一站式处理工作流。
  每日监控关注的 YouTube 频道更新 → 新视频存入待处理队列 →
  每天定时取 2 篇处理 → 获取字幕 → 内容消化（结构化存档 + 二创文章）→
  AI 生成配图 → 图文合并存入 Notion → 存入微信草稿。
  触发词："获取播客更新"、"处理播客队列"、"处理这个播客"、"有什么新播客"、"播客工作流"
---

# OpenClaw YouTube Pipeline

从 YouTube 频道监控到微信发布的一站式内容处理流程。

---

## 整体架构

```
youtube-monitor → 新视频全部存入「待处理队列」→ 通知用户新增数量
                                                        ↓
                              每天定时取 2 篇（或用户手动选择）
                                                        ↓
                  youtube-transcript → content-digest → image-gen
                                                           ↓
                                                     ┌─────┼─────┐
                                                     ↓     ↓     ↓
                                                  notion  wechat  队列状态更新
```

## 子技能一览

| # | 子技能 | 职责 | 成本 |
|---|--------|------|------|
| 1 | youtube-monitor | 监控频道更新，存入待处理队列 | 免费 |
| 1.5 | queue-manager | 管理待处理队列，每日取 2 篇处理 | 免费 |
| 2 | youtube-transcript | 获取视频字幕 | 1 credit/视频 |
| 3 | content-digest | 内容消化：存档版 + 二创版 + 图片 prompt | LLM token |
| 4 | image-generation | 生成封面图 + 配图 + 图文卡片 | ¥0.09/篇 |
| 5 | notion-storage | 图文合并写入 Notion | 免费 |
| 6 | wechat-draft | 存入微信公众号草稿 | 免费（OpenClaw 已有 skill） |

---

## 使用方式

### 模式 1：每日自动流程（推荐）
```
每日定时:
  1. youtube-monitor 检查所有频道更新 → 新视频存入待处理队列
  2. queue-manager 从队列取 2 篇 → 自动执行完整流程（Step 2-6）
  3. 通知用户处理结果
```

### 模式 2：手动获取更新
```
用户: "获取播客更新" / "有什么新播客"
→ 执行 youtube-monitor，存入队列
→ 展示新增数量和队列概况
```

### 模式 3：手动处理队列
```
用户: "处理队列" / "处理播客队列"
用户: "处理队列里的第 3 条"
用户: "处理 Alex Hormozi 那条"
用户: "今天多处理 2 条"
→ 从队列取指定内容，进入 Step 2-6 处理流程
```

### 模式 4：直接处理链接（跳过队列）
```
用户: "处理这个播客 https://youtube.com/watch?v=..."
→ 跳过 Step 1 和 Step 1.5，直接进入 Step 2 字幕提取
→ 后续流程相同，同样存入 Notion 知识库
```

---

## 环境变量 / 密钥

| 变量名 | 用途 | 说明 |
|--------|------|------|
| `TRANSCRIPT_API_KEY` | TranscriptAPI | 字幕提取 + 频道监控 |
| `NANO_BANANA_API_KEY` | Nano Banana Pro | AI 图片生成 |
| `IMGBB_API_KEY` | ImgBB 图床 | 图片永久托管 |

所有密钥通过环境变量管理，不硬编码在 skill 文件中。

---

## Notion 数据库参考

### 📺 播客监听清单
- Database ID: `30083d24986d81fd81a9dd941383aea2`
- Data Source ID: `30083d24-986d-81ff-a393-000be67370f7`
- 字段:
  - 博主名称 (title) — 频道名
  - Channel ID (text) — YouTube channel ID
  - Handle (text) — @handle，如 @AlexHormozi
  - YouTube 链接 (url) — 频道主页链接
  - 优先级 (select) — 高 / 中 / 低
  - 分类 (select) — 如 Marketing, AI 教育, META 等
  - 状态 (select) — 监听中 / 暂停
  - 备注 (text)

### 📥 播客待处理队列
- Database ID: `30183d24986d81cdb25fcd31bd9d87ba`
- Data Source ID: `30183d24-986d-811c-8b41-000be90b0c13`
- 字段:
  - 视频标题 (title)
  - 视频链接 (url)
  - 博主 (select)
  - 分类标签 (multi_select)
  - 优先级 (select) — 🔥 高 / ⭐ 中 / 📌 低
  - 发布日期 (date)
  - 发现日期 (date)
  - 状态 (select) — 🆕 待处理 / 📋 已提取字幕 / ✍️ 处理中 / ✅ 已完成 / ❌ 跳过
  - 备注 (text)

### 🎙️ 播客知识库 V3
- Database ID: `30083d24986d81aab0bac4c5a29baceb`
- Data Source ID: `30083d24-986d-81d9-931d-000bef515098`
- 字段:
  - 名称 (title) — 视频标题
  - 日期 (date) — 视频发布日期
  - 频道 (text) — 博主/频道名
  - 链接 (url) — YouTube 视频链接
  - 一句话总结 (text)
  - 视频时长 (number) — 分钟
  - 缩略图 (url) — 图文卡片的 ImgBB URL
  - 标签 (multi_select) — 手动打标，不自动生成
  - 状态 (select) — 待处理 / 已消化 / 已发布
  - 发布状态 (select) — 未发布 / 微信已发 / 小红书已发 / 全部已发

---
---

# 子技能详细规范

---

## Step 1: youtube-monitor

### 触发
- 每日自动检查
- 用户说 "获取播客更新" / "有什么新播客" / "检查频道更新"

### 执行流程

```
1. 查询 Notion「播客监听清单」，筛选 状态=监听中 的频道
2. 遍历每个频道：
   a. 如果 Handle 有值但 Channel ID 为空 → 调用 resolve API 补全
   b. 调用 channel/latest API 获取最近 15 条视频
   c. 筛选发布时间在过去 2 天内的视频
3. 汇总所有新视频
4. 去重：查询「待处理队列」已有的视频链接，跳过已存在的
5. 批量写入「待处理队列」
6. 通知用户结果
```

### API 调用详情

#### API 1: 自动补全 Channel ID（免费，仅需要时调用）

场景：用户在监听清单只填了 Handle（如 @AlexHormozi），没填 Channel ID。

```http
GET https://transcriptapi.com/api/v2/youtube/channel/resolve?input={handle}
Authorization: Bearer {{TRANSCRIPT_API_KEY}}
```

响应示例：
```json
{
  "channel_id": "UCo1qWBDj_yXOKxJq5INNDLA",
  "channel_name": "Alex Hormozi",
  "channel_url": "https://www.youtube.com/channel/UCo1qWBDj_yXOKxJq5INNDLA"
}
```

处理：
- 将 `channel_id` 回写到 Notion 监听清单的 `Channel ID` 字段
- 后续直接使用 Channel ID，不再重复 resolve

#### API 2: 获取频道最新视频（免费）

```http
GET https://transcriptapi.com/api/v2/youtube/channel/latest?channel={channel_id}
Authorization: Bearer {{TRANSCRIPT_API_KEY}}
```

响应示例：
```json
{
  "channel_id": "UCo1qWBDj_yXOKxJq5INNDLA",
  "channel_name": "Alex Hormozi",
  "videos": [
    {
      "video_id": "abc123",
      "title": "How I Made $100M",
      "published": "2026-02-10T14:30:00Z",
      "link": "https://www.youtube.com/watch?v=abc123",
      "thumbnail": "https://i.ytimg.com/vi/abc123/hqdefault.jpg"
    }
  ]
}
```

处理：
- 筛选 `published` 在当前时间 - 48 小时内的视频
- 提取：video_id, title, published, link

### 写入待处理队列

对每条新视频，写入 Notion「📥 播客待处理队列」：

```
视频标题 = video.title
视频链接 = video.link
博主 = 频道名称（从监听清单的「博主名称」字段继承）
分类标签 = 从监听清单的「分类」字段继承（映射为 multi_select）
优先级 = 从监听清单的「优先级」字段继承（高→🔥 高，中→⭐ 中，低→📌 低）
date:发布日期:start = video.published（ISO 日期）
date:发布日期:is_datetime = 0
date:发现日期:start = 今天日期
date:发现日期:is_datetime = 0
状态 = "🆕 待处理"
```

**去重逻辑：** 写入前，用 Notion search/query 检查队列中是否已存在相同 `视频链接` 的记录。如果已存在则跳过该视频。

### 通知用户

```
📺 今日频道更新检查完成

新增 {N} 条视频已存入待处理队列：
- [AI 教育] Alex Hormozi — "How I Made $100M"
- [META] Fraser Cottrell — "Meta Ads Strategy 2026"
- [Marketing] Sam Piliero — "Hook Framework That Works"

当前队列：共 {total} 条待处理
今日将自动处理 2 篇（优先级高的优先）
```

如果没有新视频：
```
📺 今日频道更新检查完成
过去 2 天没有新视频更新。
当前队列仍有 {total} 条待处理。
```

### 错误处理
- 某个频道 API 调用失败 → 跳过该频道，继续处理其他频道，最后报告失败的频道
- Channel ID resolve 失败 → 在监听清单备注字段写入 "Channel ID 解析失败，请检查 Handle"

---

## Step 1.5: queue-manager

### 触发
- **自动：** 在 youtube-monitor 完成后立即执行
- **手动：** 用户说 "处理队列" / "处理播客队列" / "今天处理几条播客"

### 执行流程

```
1. 查询 Notion「播客待处理队列」，筛选 状态=🆕 待处理
2. 排序规则：
   a. 优先级：🔥 高 → ⭐ 中 → 📌 低
   b. 同优先级：按 发布日期 升序（先发布的先处理）
3. 取前 2 条（或用户指定的数量）
4. 对每条视频，按顺序执行 Step 2 → Step 3 → Step 4 → Step 5 → Step 6
5. 每完成一条，更新队列状态为 ✅ 已完成
6. 全部完成后，汇总通知用户
```

### 状态流转（处理过程中实时更新）

```
🆕 待处理
  ↓ 开始 Step 2 字幕提取
📋 已提取字幕
  ↓ 开始 Step 3 内容消化
✍️ 处理中
  ↓ Step 3-6 全部完成
✅ 已完成
```

更新方式：每进入新阶段，立即更新该记录的 `状态` 字段。

### 手动指定处理

用户可以跳过自动排序，手动指定：

| 用户指令 | 行为 |
|---------|------|
| "处理队列里的第 3 条" | 按默认排序的第 3 条 |
| "处理 Alex Hormozi 那条" | 按博主名匹配 |
| "今天多处理 2 条" | 在当日已处理的基础上再取 2 条 |
| "跳过第 1 条" | 将第 1 条状态改为 ❌ 跳过 |

### 错误处理
- 某条视频处理失败（如字幕提取失败）→ 保持当前状态不变，在 `备注` 字段写入错误原因
- 继续处理下一条，不因单条失败中断整个批次

### 完成通知

```
✅ 今日播客处理完成

已处理 2 篇：
1. ✅ Alex Hormozi — "How I Made $100M" → 已存入知识库 + 微信草稿
2. ✅ Fraser Cottrell — "Meta Ads Strategy 2026" → 已存入知识库 + 微信草稿

队列剩余：{remaining} 条待处理
```

---

## Step 2: youtube-transcript

### 触发
queue-manager 选定视频后自动进入。

### 执行流程

```
1. 从队列记录获取视频链接
2. 更新队列状态 → 📋 已提取字幕
3. 调用 TranscriptAPI 获取字幕
4. 解析响应，提取字幕文本和元数据
5. 将结果传递给 Step 3
```

### API 调用

```http
GET https://transcriptapi.com/api/v2/youtube/transcript?video_url={video_url}&format=text&include_timestamp=false&send_metadata=true
Authorization: Bearer {{TRANSCRIPT_API_KEY}}
```

| 参数 | 值 | 原因 |
|------|-----|------|
| video_url | 完整 YouTube 链接或 video ID | 支持两种格式 |
| format | `text` | 纯文本，方便后续消化处理 |
| include_timestamp | `false` | 播客内容不需要逐句时间戳 |
| send_metadata | `true` | 获取标题、频道名、缩略图、时长等 |

### 响应解析

响应中需要提取的字段：

```json
{
  "title": "视频标题",
  "channel_name": "频道名",
  "duration": 1234,
  "thumbnail": "https://i.ytimg.com/vi/xxx/maxresdefault.jpg",
  "transcript": "完整的纯文本字幕内容..."
}
```

- `duration`：秒数，转为分钟后传给 Step 3 用于动态长度控制
- `transcript`：完整字幕文本，作为 Step 3 的输入

### 费用
1 credit / 视频

### 输出（传递给 Step 3）

```yaml
transcript_text: 完整字幕纯文本
metadata:
  title: 视频标题
  channel: 频道名
  duration_minutes: 时长（分钟）
  thumbnail: 缩略图 URL
  video_url: YouTube 链接
  published: 发布日期
```

### 错误处理
- 字幕不可用（如无字幕的视频）→ 在队列备注写入 "该视频无可用字幕"，跳过此视频
- API 超时或 5xx → 重试 1 次，仍失败则跳过并记录错误

---

## Step 3: content-digest

这是整个工作流的核心智能步骤。接收字幕原文，产出三项内容：版本 A（存档版）、版本 B（二创版）、3 段图片 prompt。

### 触发
Step 2 字幕提取完成后自动进入。同时更新队列状态 → `✍️ 处理中`。

### 输入
- `transcript_text`：完整字幕纯文本
- `metadata`：标题、频道、时长（分钟）、链接、缩略图、发布日期

### 长度动态控制

根据视频时长自动调整输出规模：

| 视频时长 | 版本 A 观点提取数 | 版本 B 字数 |
|---------|-----------------|------------|
| < 10 min | 3-5 条 | 600-800 字 |
| 10-20 min | 5-8 条 | 800-1000 字 |
| 20-40 min | 8-12 条 | 1000-1200 字 |
| > 40 min | 10-15 条 | 1200-1500 字 |

### 输出 1：版本 A — Notion 存档版（结构化摘要）

#### Prompt

```
你是一个内容消化助手。请根据以下视频字幕，生成结构化的内容摘要。

## 视频信息
- 标题：{title}
- 频道：{channel}
- 时长：{duration_minutes} 分钟
- 链接：{video_url}

## 字幕原文
{transcript_text}

## 输出要求

请严格按以下结构输出，使用中文。英文专业术语保留原文并用括号标注中文含义（如 "hook framework（钩子框架）"）。

### 一句话总结
用 20-30 个中文字概括这个视频的核心内容。要求精准、有信息量，不要泛泛而谈。
例如好的："分享了 3 种低预算下冷启动 Meta 广告的投放策略和素材制作方法"
例如差的："讨论了关于广告投放的一些方法"

### 核心要点
提炼 3-5 条 key takeaways，每条 1-2 句话。这是"如果只能记住几件事"的那几件事。

### 观点提取
提取 {viewpoint_count} 条独立观点或知识点。每条包含：
- 观点标题（10 字以内，加粗）
- 观点内容（2-3 句话展开说明）
- 如果原文有具体数据、案例、方法论步骤，必须保留原始细节

### 金句引用
从原文中提取 2-3 句最有价值、最有洞察力的原话。
格式：英文原文 + 中文翻译
选择标准：有洞察力、有记忆点、值得反复回味的句子。不要选平淡的陈述句。

### 行动建议
提炼 2-3 条可执行的 action items。
要求：具体、可操作，动词开头。
例如好的："在下一次广告测试中，先用 3 个不同 hook 测试 CTR，再对胜出的 hook 迭代 body copy"
例如差的："优化你的广告策略"
```

#### 输出格式

```markdown
### 一句话总结
{tl_dr}

### 核心要点
1. {takeaway_1}
2. {takeaway_2}
3. {takeaway_3}
...

### 观点提取
**{观点标题1}**
{观点内容1}

**{观点标题2}**
{观点内容2}
...

### 金句引用
> "{英文原文1}" — {speaker}
> 翻译：{中文翻译1}

> "{英文原文2}" — {speaker}
> 翻译：{中文翻译2}
...

### 行动建议
1. {action_1}
2. {action_2}
3. {action_3}
```

---

### 输出 2：版本 B — 微信/小红书二创版（~1000 字自然文章）

#### Prompt（核心 prompt，决定文章质量）

```
你是一个擅长内容二创的中文博主。你的读者是做跨境电商和数字营销的中国从业者。

请根据以下视频字幕，写一篇适合在微信公众号和小红书发布的中文文章。

## 视频信息
- 标题：{title}
- 频道：{channel}
- 时长：{duration_minutes} 分钟

## 字幕原文
{transcript_text}

## 写作风格（极其重要，必须严格遵守）

1. **语气**：像跟朋友聊天，不是写教科书。你在分享你看了一个很棒的视频后的心得和感悟，带有自己的吐槽和点评。想象你在微信群里给做电商的朋友安利一个好视频。

2. **阅读水平**：四五年级就能看懂的中文。不用"赋能""底层逻辑""认知升维""范式转移"这类大词。说人话。用最简单直白的方式表达。

3. **段落**：短段落，每段 2-4 句话最多。段落之间自然过渡，不要用"首先...其次...最后..."这种机械结构。像聊天一样自然地转换话题。

4. **格式禁忌**：
   - ❌ 不要用 emoji 做段落装饰（全文最多出现 2-3 个 emoji）
   - ❌ 不要用 bullet point / 编号列表罗列知识点
   - ❌ 不要用加粗标题做段落分隔
   - ❌ 不要用表格
   - ❌ 不要用 "一、二、三" 或 "第一点、第二点" 分段
   - ✅ 用连贯的自然段落讲述，就像微信上给朋友发长消息

5. **英文术语**：自然嵌入，不刻意翻译。
   - ✅ "他提到的这个 hook framework 其实挺简单的"
   - ❌ "他提到的这个钩子框架（hook framework）其实挺简单的"

6. **开头**：必须抓人。可以用反常识、痛点共鸣、场景带入、数据冲击、提问等方式。
   - ❌ 绝对禁止："今天给大家分享..."、"最近看了一个视频..."、"大家好，今天我们来聊聊..."
   - ✅ 好的开头示例："花了 5000 块投广告，转化了 0 单——这事儿你经历过吧？"
   - ✅ 好的开头示例："你知道那些月销百万的 Shopify 店铺，广告素材其实都长一个样吗？"

7. **结尾**：带互动引导。问读者一个具体的问题，或邀请他们分享经验，让人有回复的冲动。
   - ✅ "你们投 Meta 广告的时候，一般第一轮测几个素材？评论区聊聊"
   - ❌ "希望这篇文章对大家有所帮助，欢迎点赞转发"

8. **干货密度**：有实质内容，有具体方法/案例/数据。但不是干巴巴罗列知识点——要有你自己的解读、延伸思考和吐槽。大概 60% 干货 + 40% 个人观点。

9. **个人观点**：必须包含。这是区别于"AI 总结"的关键。
   - "说实话这一点我不太同意，因为国内的情况是..."
   - "我觉得这个方法如果用在独立站上，可能要调整一下..."
   - "这让我想到之前看过的一个案例..."
   - "坦白讲这个操作门槛还挺高的，一般小团队估计..."

10. **真实感**：写出来的东西要像一个真人写的。可以有口语化表达、可以有不确定的语气、可以有偶尔的跑题和拉回。不要每一段都完美工整。

## 文章结构（灵活参考，不是固定模板，根据内容自然组织）

[IMAGE:cover]

{抓人开头 — 1-2 段，用痛点/反常识/提问/场景把读者拉进来}

{核心内容展开 — 围绕视频中最有价值的 2-3 个点，用故事、案例、比喻串联。不是"第一点...第二点..."的罗列，是像讲故事一样自然推进。每个点之间用自然的口语化过渡连接。}

[IMAGE:inline]

{延伸思考/个人点评 — 你对这些观点的看法，结合国内跨境电商/营销的实际情况做延伸。可以表达不同意的地方、补充自己的经验、或分析在不同场景下的适用性。}

{结尾互动引导 — 抛出一个具体的、让人有回复冲动的问题}

## 图片占位符规则
- `[IMAGE:cover]` 固定放在文章最开头（第一个位置）
- `[IMAGE:inline]` 放在文章中间，你认为最合适的话题转折点或视觉停顿点
- 两个占位符各自单独占一行，前后各空一行
- 不要在文章末尾放图片

## 字数要求
{word_count_range} 字（不含图片占位符行）

## 输出
只输出文章正文（包含两个图片占位符）。
不要输出标题。不要输出任何前缀如"以下是文章"。不要输出任何后缀。直接输出文章内容。
```

---

### 输出 3：图片 Prompt（3 段英文 prompt）

#### Prompt

```
Based on the video content below, generate 3 image prompts for AI image generation (Nano Banana Pro model).

Video title: {title}
One-line summary: {tl_dr}
Key concepts: {从核心要点中提取 3-5 个关键词}

All 3 prompts MUST start with this exact base style prefix:
"cute kawaii-style digital illustration, warm beige/cream background, soft pastel colors, rounded cartoon elements, cheerful decorative details like confetti and banners, clean layout, friendly and professional, flat design with subtle shadows, "

Then append topic-specific content for each:

PROMPT_COVER: [base style] + a visual metaphor that represents the video's main topic, showing relevant objects/scenes + "wide banner composition with space for title text on the right side, 16:9 aspect ratio"

PROMPT_INLINE: [base style] + a visual representation of the single most important concept or method discussed in the video, with a cute character demonstrating or interacting with it + "centered composition, square format, 1:1 aspect ratio"

PROMPT_CARD: [base style] + topic-related visual elements arranged around prominent Chinese text that reads "{card_title}" + "vertical card layout, large bold readable Chinese text as the main focal point, decorative elements framing the text, 3:4 aspect ratio"

For {card_title}: Generate a catchy Chinese title of 6-10 characters that captures the video's core message. This text will appear ON the image.

Rules:
- Keep prompts under 200 words each
- Be specific about objects and scenes, avoid abstract descriptions
- Do not mention any real people, brands, or logos
- The card title Chinese text should be punchy and shareable

Output EXACTLY in this format (no other text before or after):
PROMPT_COVER: {full prompt including base style}
PROMPT_INLINE: {full prompt including base style}
PROMPT_CARD: {full prompt including base style}
CARD_TITLE: {6-10 Chinese characters}
```

---

### Step 3 完整输出（传递给后续步骤）

```yaml
version_a:
  tl_dr: "一句话总结文本"
  full_text: |
    完整版本 A markdown 文本，包含所有 section：
    一句话总结 / 核心要点 / 观点提取 / 金句引用 / 行动建议

version_b:
  full_text: |
    完整版本 B 文章正文
    包含 [IMAGE:cover] 和 [IMAGE:inline] 两个占位符
    纯中文自然段落，无格式标记

image_prompts:
  cover: "完整的封面图 prompt（含 base style）"
  inline: "完整的配图 prompt（含 base style）"
  card: "完整的卡片 prompt（含 base style）"
  card_title: "6-10 字中文卡片标题"

metadata:
  title: "视频标题"
  channel: "频道名"
  duration_minutes: 时长分钟数
  video_url: "YouTube 链接"
  thumbnail: "原始缩略图 URL"
  published: "发布日期 ISO"
```

---

## Step 4: image-generation

### 触发
Step 3 content-digest 完成后自动进入。

### 执行流程

```
1. 接收 3 段图片 prompt（cover / inline / card）
2. 向 Nano Banana Pro 提交 3 个异步生成请求
3. 轮询每个请求的状态，直到全部完成或超时
4. 对每张成功的图片，上传到 ImgBB 获取永久 URL
5. 用永久 URL 替换版本 B 中的 [IMAGE:cover] 和 [IMAGE:inline] 占位符
6. 将 3 个 URL + 替换后的版本 B 传递给 Step 5
```

### API 1: Nano Banana Pro — 提交异步生成

对每张图片分别调用：

```http
POST https://api.wuyinkeji.com/api/async/image_nanoBanana_pro
Authorization: {{NANO_BANANA_API_KEY}}
Content-Type: application/x-www-form-urlencoded;charset:utf-8;

prompt={image_prompt}&imageSize=1K&aspectRatio={ratio}
```

3 张图的参数：

| 图片 | prompt 来源 | aspectRatio | 用途 |
|------|------------|------------|------|
| 封面图 | image_prompts.cover | `16:9` | 文章顶部 + 微信封面 |
| 文章配图 | image_prompts.inline | `1:1` | 文章中间插图 |
| 图文卡片 | image_prompts.card | `3:4` | 小红书独立分享 |

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": "img_abc123"
  }
}
```

记录每个请求的 `id`。

### API 2: Nano Banana Pro — 轮询状态

```http
GET https://api.wuyinkeji.com/api/img/drawDetail?id={id}
Authorization: {{NANO_BANANA_API_KEY}}
Content-Type: application/json;charset:utf-8;
```

**轮询规则：**
- 每 **5 秒** 查询一次
- 最多轮询 **60 次**（5 分钟超时）
- 3 张图可以并行轮询

**状态判断：**
```
status=0 → 排队中，继续等待
status=1 → 生成中，继续等待
status=2 → ✅ 成功，提取 data.image_url
status=3 → ❌ 失败，记录错误信息
```

### API 3: ImgBB — 上传图床获取永久 URL

对每张成功生成的图片：

```http
POST https://api.imgbb.com/1/upload
Content-Type: multipart/form-data

key={{IMGBB_API_KEY}}
image={Nano Banana 返回的 image_url}
name={描述性文件名，如 cover_alex-hormozi_20260211}
```

**响应：**
```json
{
  "data": {
    "url": "https://i.ibb.co/xxxxx/cover.png",
    "display_url": "https://i.ibb.co/xxxxx/cover.png"
  },
  "success": true
}
```

提取 `data.display_url` 作为永久图片链接。

### 替换版本 B 占位符

```
版本 B 原文中：
  [IMAGE:cover]  → ![封面图]({cover_imgbb_url})
  [IMAGE:inline] → ![配图]({inline_imgbb_url})
```

### 输出（传递给 Step 5 和 Step 6）

```yaml
images:
  cover_url: "https://i.ibb.co/xxx/cover.png"
  inline_url: "https://i.ibb.co/xxx/inline.png"
  card_url: "https://i.ibb.co/xxx/card.png"

version_b_with_images: |
  版本 B 完整文本（[IMAGE:cover] 和 [IMAGE:inline] 已替换为实际图片 markdown）
```

### 成本
每张 ¥0.03，每篇 3 张 = **¥0.09/篇**

### 错误处理
- 单张图片生成失败 → 用视频原始缩略图 URL 替代该位置，继续流程
- ImgBB 上传失败 → 直接使用 Nano Banana Pro 返回的原始 URL（可能过期，但不阻断流程）
- 全部 3 张都失败 → 移除版本 B 中的占位符行（删除该行），使用缩略图作为封面，继续流程

---

## Step 5: notion-storage

### 触发
Step 4 图片生成完成后自动进入。

### 执行流程

```
1. 在 Notion「播客知识库 V3」创建新页面
2. 写入页面属性（properties）
3. 写入页面正文（body content）
4. 更新「待处理队列」中该记录的状态 → ✅ 已完成
```

### 写入页面属性

```
parent: { data_source_id: "30083d24-986d-81d9-931d-000bef515098" }

properties:
  名称: "{metadata.title}"
  date:日期:start: "{metadata.published}"
  date:日期:is_datetime: 0
  频道: "{metadata.channel}"
  链接: "{metadata.video_url}"
  一句话总结: "{version_a.tl_dr}"
  视频时长: {metadata.duration_minutes}
  缩略图: "{images.card_url}"
  状态: "已消化"
  发布状态: "未发布"
```

注意：`标签` (multi_select) 留空，由用户手动打标。

### 写入页面正文

使用 Notion enhanced markdown 格式：

```markdown
## 📋 存档版

{version_a.full_text}

---

## ✍️ 二创文章

{version_b_with_images}

---

## 🖼️ 素材

封面图（16:9）：{images.cover_url}
文章配图（1:1）：{images.inline_url}
图文卡片（3:4）：{images.card_url}
```

### 更新队列状态

知识库页面创建成功后，更新「📥 播客待处理队列」中对应记录：
```
状态 → "✅ 已完成"
```

---

## Step 6: wechat-draft

### 触发
Step 5 Notion 存储完成后自动进入。

### 职责
将版本 B 二创文章 + 图片存入微信公众号草稿箱。

**此步骤调用 OpenClaw 已有的微信草稿 skill。** 本工作流只需传递以下参数：

### 传递参数

```yaml
title: "{metadata.title} | {metadata.channel}"

cover_image_url: "{images.cover_url}"

content_html: |
  # 将版本 B with images（Markdown）转换为微信兼容 HTML
  # 转换规则见下方

digest: "{version_a.tl_dr}"
```

### Markdown → 微信 HTML 转换规则

```
段落文本     → <p style="margin:0 0 16px 0;line-height:1.8;color:#333;font-size:16px;">{text}</p>
图片 ![x](url) → <p style="text-align:center;margin:20px 0;"><img src="{url}" style="width:100%;border-radius:8px;" /></p>
空行         → 忽略（已通过 <p> 的 margin 控制间距）
```

不使用 H1-H6 标签。不使用粗体/斜体标签。保持朴素排版。

### 转换示例

版本 B 原文（占位符已替换）：
```
![封面图](https://i.ibb.co/xxx/cover.png)

你有没有发现，花在广告上的钱越来越多，效果却越来越差？

这不是你的问题。

![配图](https://i.ibb.co/xxx/inline.png)

说到底，问题出在 creative fatigue。
```

转换后 HTML：
```html
<p style="text-align:center;margin:20px 0;"><img src="https://i.ibb.co/xxx/cover.png" style="width:100%;border-radius:8px;" /></p>

<p style="margin:0 0 16px 0;line-height:1.8;color:#333;font-size:16px;">你有没有发现，花在广告上的钱越来越多，效果却越来越差？</p>

<p style="margin:0 0 16px 0;line-height:1.8;color:#333;font-size:16px;">这不是你的问题。</p>

<p style="text-align:center;margin:20px 0;"><img src="https://i.ibb.co/xxx/inline.png" style="width:100%;border-radius:8px;" /></p>

<p style="margin:0 0 16px 0;line-height:1.8;color:#333;font-size:16px;">说到底，问题出在 creative fatigue。</p>
```

### 完成后更新

微信草稿创建成功后，更新 Notion「播客知识库 V3」中该记录：
```
发布状态 → "微信已发"
```

---

## 成本估算

| 项目 | 单价 | 说明 |
|------|------|------|
| 频道监控 | 免费 | TranscriptAPI channel/latest + channel/resolve |
| 字幕提取 | 1 credit/视频 | TranscriptAPI transcript |
| 内容消化 | LLM token | Claude/GPT API |
| 图片生成 | ¥0.09/篇 | 3 张 × ¥0.03 |
| 图床 | 免费 | ImgBB |
| Notion | 免费 | Notion API |
| 微信草稿 | 免费 | 微信公众号 API |

**每篇总成本 ≈ 1 credit + LLM token + ¥0.09**
**每日成本（2 篇）≈ 2 credits + LLM tokens + ¥0.18**

---

## 完整流程时间线示例

```
08:00  youtube-monitor 启动
       → 检查 12 个频道，发现 4 条新视频
       → 去重后 3 条写入待处理队列
       → 通知："新增 3 条，当前队列共 7 条待处理"

08:01  queue-manager 启动
       → 取优先级最高的 2 条
       → 开始第 1 条：Alex Hormozi "How I Made $100M"

08:01  Step 2 字幕提取
       → TranscriptAPI → 获得 45 分钟字幕文本
       → 队列状态 → 📋 已提取字幕

08:02  Step 3 内容消化
       → 版本 A：15 条观点 + 3 条金句 + 3 条行动建议
       → 版本 B：1300 字二创文章（含 2 个图片占位符）
       → 3 段图片 prompt
       → 队列状态 → ✍️ 处理中

08:03  Step 4 图片生成
       → 提交 3 张图生成请求（并行）
       → 轮询 ~30-60 秒等待完成
       → 上传 ImgBB → 3 个永久 URL
       → 替换版本 B 占位符

08:04  Step 5 Notion 存储
       → 创建知识库页面（属性 + 正文）
       → 队列状态 → ✅ 已完成

08:04  Step 6 微信草稿
       → Markdown → HTML → 存入草稿箱
       → 发布状态 → 微信已发

08:05  开始第 2 条：Fraser Cottrell "Meta Ads Strategy 2026"
       → 重复 Step 2-6...

08:10  全部完成
       → 通知："已处理 2 篇，队列剩余 5 条"
```