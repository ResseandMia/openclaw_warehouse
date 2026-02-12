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

## ⚠️ 强制规则（每次执行必须遵守）

1. **模型要求：** 所有 LLM 生成任务（内容消化、图片 prompt）必须使用 **Kimi K2.5** 模型。禁止使用 MiniMax、其他模型或简化处理。如果 Kimi K2.5 不可用，立即报错停止，不要静默降级。

2. **字幕来源：** 必须通过 **TranscriptAPI** 获取完整字幕原文。禁止使用视频摘要、视频描述、或自行生成总结来替代字幕。如果 TranscriptAPI 返回错误，报错停止，不要用其他方式替代。

3. **图片 Prompt 必须包含 Base Style：** 每段图片 prompt 必须以指定的 base style 前缀开头（见 Step 3 详细规范）。这是硬编码的，不由 LLM 自由发挥。

4. **状态报告必须准确：** 每个步骤完成后，报告的状态必须与实际执行结果一致。如果图片生成失败用了降级方案，必须明确告知用户"图片生成失败，已使用缩略图替代"，不要说"已成功生成图片"。

5. **Notion 写入必须完整：** 如果内容较长，必须分段写入（见 Step 5 分段策略）。写入后必须验证内容完整性。

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
| 3 | content-digest | 内容消化：存档版 + 二创版 + 图片 prompt | LLM token（Kimi K2.5） |
| 4 | image-generation | 生成封面图 + 配图 + 图文卡片 | ¥0.09/篇 |
| 5 | notion-storage | 图文合并写入 Notion（分段写入） | 免费 |
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

### ✅ Step 1 质量门禁
- [ ] 至少成功查询了 1 个频道的更新
- [ ] 所有写入队列的记录都有完整字段（标题、链接、博主、优先级、状态）
- [ ] 无重复录入
- 如果全部频道查询失败 → 停止流程，通知用户 "频道更新检查失败，请检查 API 密钥"

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

| 用户指令 | 行为 |
|---------|------|
| "处理队列里的第 3 条" | 按默认排序的第 3 条 |
| "处理 Alex Hormozi 那条" | 按博主名匹配 |
| "今天多处理 2 条" | 在当日已处理的基础上再取 2 条 |
| "跳过第 1 条" | 将第 1 条状态改为 ❌ 跳过 |

### 错误处理
- 某条视频处理失败 → 保持当前状态不变，在 `备注` 字段写入具体错误原因
- 继续处理下一条，不因单条失败中断整个批次

### 完成通知

```
✅ 今日播客处理完成

已处理 2 篇：
1. ✅ Alex Hormozi — "How I Made $100M" → 已存入知识库 + 微信草稿
2. ✅ Fraser Cottrell — "Meta Ads Strategy 2026" → 已存入知识库 + 微信草稿

队列剩余：{remaining} 条待处理
```

如有失败：
```
⚠️ 今日播客处理完成（有异常）

1. ✅ Alex Hormozi — "How I Made $100M" → 已存入知识库 + 微信草稿
2. ❌ Fraser Cottrell — "Meta Ads Strategy 2026" → 字幕提取失败（该视频无可用字幕）

队列剩余：{remaining} 条待处理（含 1 条失败未处理）
```

---

## Step 2: youtube-transcript

### 触发
queue-manager 选定视频后自动进入。

### ⚠️ 强制要求
**必须调用 TranscriptAPI 获取真实字幕。禁止以下替代方案：**
- ❌ 用视频标题/描述猜测内容
- ❌ 用其他摘要 API 替代
- ❌ 用 LLM 直接生成"大概内容"
- ❌ 只获取部分字幕

**如果 TranscriptAPI 不可用或该视频无字幕 → 立即停止该视频的处理，在队列备注写明原因，跳到下一条。**

### 执行流程

```
1. 从队列记录获取视频链接
2. 更新队列状态 → 📋 已提取字幕（注意：这里先更新状态再调 API，表示已进入此阶段）
3. 调用 TranscriptAPI 获取完整字幕
4. 验证字幕完整性（见质量门禁）
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

```json
{
  "title": "视频标题",
  "channel_name": "频道名",
  "duration": 1234,
  "thumbnail": "https://i.ytimg.com/vi/xxx/maxresdefault.jpg",
  "transcript": "完整的纯文本字幕内容..."
}
```

- `duration`：秒数，需转换为分钟 → `Math.round(duration / 60)`
- `transcript`：完整字幕文本

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

### ✅ Step 2 质量门禁
- [ ] `transcript` 字段非空
- [ ] 字幕文本长度 > 500 字符（低于此值说明字幕不完整或提取失败）
- [ ] `duration` 字段有值（用于 Step 3 动态长度控制）
- 如果任一条件不满足 → 队列备注写入 "字幕提取不完整：{具体原因}"，跳过此视频

---

## Step 3: content-digest

这是整个工作流的核心智能步骤。接收字幕原文，产出三项内容：版本 A（存档版）、版本 B（二创版）、3 段图片 prompt。

### ⚠️ 强制要求
- **必须使用 Kimi K2.5 模型**，不要使用其他模型
- **必须基于 Step 2 返回的完整字幕原文**生成内容，不要基于摘要或自行理解
- **版本 B 文章必须严格遵循写作风格要求**（见下方 prompt），不要生成通稿式教科书文体

### 触发
Step 2 字幕提取完成后自动进入。同时更新队列状态 → `✍️ 处理中`。

### 输入
- `transcript_text`：来自 Step 2 的完整字幕纯文本
- `metadata`：标题、频道、时长（分钟）、链接、缩略图、发布日期

### 长度动态控制

根据 `metadata.duration_minutes` 选择对应档位：

| 视频时长 | 版本 A 观点提取数 | 版本 B 字数目标 |
|---------|-----------------|---------------|
| < 10 min | 3-5 条 | 600-800 字 |
| 10-20 min | 5-8 条 | 800-1000 字 |
| 20-40 min | 8-12 条 | 1000-1200 字 |
| > 40 min | 10-15 条 | 1200-1500 字 |

---

### 输出 1：版本 A — Notion 存档版

#### Prompt（发送给 Kimi K2.5）

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
用 20-30 个中文字概括这个视频的核心内容。要精准、有信息量。
✅ 好的例子："分享了 3 种低预算下冷启动 Meta 广告的投放策略和素材制作方法"
❌ 差的例子："讨论了关于广告投放的一些方法"

### 核心要点
提炼 3-5 条 key takeaways，每条 1-2 句话。这是"如果只能记住几件事"的那几件事。

### 观点提取
提取 {viewpoint_count} 条独立观点或知识点。每条包含：
- 观点标题（10 字以内，加粗）
- 观点内容（2-3 句话展开说明）
- 如果原文有具体数据、案例、方法论步骤，必须保留原始细节，不要模糊概括

### 金句引用
从原文中提取 2-3 句最有价值的原话。
格式：英文原文 + 中文翻译。
选择标准：有洞察力、有记忆点、能独立传播的句子。不要选平淡的过渡句。

### 行动建议
提炼 2-3 条可执行的 action items。动词开头，具体可操作。
✅ 好的例子："在下一次广告测试中，先用 3 个不同 hook 测试 CTR，再对胜出的 hook 迭代 body copy"
❌ 差的例子："优化你的广告策略"
```

#### 输出格式

```markdown
### 一句话总结
{tl_dr}

### 核心要点
1. {takeaway_1}
2. {takeaway_2}
3. {takeaway_3}

### 观点提取
**{观点标题1}**
{观点内容1}

**{观点标题2}**
{观点内容2}

### 金句引用
> "{英文原文1}" — {speaker}
> 翻译：{中文翻译1}

> "{英文原文2}" — {speaker}
> 翻译：{中文翻译2}

### 行动建议
1. {action_1}
2. {action_2}
3. {action_3}
```

---

### 输出 2：版本 B — 微信/小红书二创版

#### Prompt（发送给 Kimi K2.5 — 这是最关键的 prompt）

```
你是一个擅长内容二创的中文博主。你的读者是做跨境电商和数字营销的中国从业者。

请根据以下视频字幕，写一篇适合在微信公众号和小红书发布的中文文章。

## 视频信息
- 标题：{title}
- 频道：{channel}
- 时长：{duration_minutes} 分钟

## 字幕原文
{transcript_text}

## 写作风格（极其重要，必须严格遵守，违反任何一条都算失败）

### 语气和人设
你在分享你看了一个很棒的视频后的心得。像在微信群里给做电商的朋友安利一个好视频，带有自己的吐槽和点评。不是在写公众号"专业文章"，是在跟朋友唠嗑。

### 用词标准
四五年级就能看懂的中文。禁止使用以下词汇：赋能、底层逻辑、认知升维、范式转移、打法、抓手、颗粒度、闭环、对齐、拉齐、沉淀、心智、势能、链路。说人话。

### 段落格式
- 短段落，每段 2-4 句话最多
- 段落之间自然过渡，禁止"首先...其次...最后..."结构
- 像发微信消息一样自然

### 绝对禁止的格式
- ❌ emoji 做段落装饰（全文最多 2-3 个 emoji）
- ❌ bullet point / 编号列表罗列知识点
- ❌ 加粗标题做段落分隔（如 **第一点：XXXX**）
- ❌ 表格
- ❌ "一、二、三" 或 "第一点、第二点" 分段
- ❌ 每段结尾都带感叹号
- ✅ 用连贯的自然段落讲述

### 英文术语处理
自然嵌入，不刻意翻译。
✅ "他提到的这个 hook framework 其实挺简单的"
❌ "他提到的这个钩子框架（hook framework）其实挺简单的"

### 开头要求
必须抓人，前 2 句话就要让人想继续读。
✅ 允许的开头方式：反常识、痛点共鸣、场景带入、数据冲击、直接提问
❌ 绝对禁止的开头：
  - "今天给大家分享..."
  - "最近看了一个视频..."
  - "大家好，今天我们来聊聊..."
  - "在数字营销领域..."
  - "随着XXX的发展..."

✅ 好的开头示例：
  - "花了 5000 块投广告，转化了 0 单——这事儿你经历过吧？"
  - "你知道那些月销百万的 Shopify 店铺，广告素材其实都长一个样吗？"
  - "上周我把一个广告的 hook 换了一句话，ROAS 从 1.2 直接飙到 3.8。"

### 结尾要求
带互动引导，抛出一个具体的、让人有回复冲动的问题。
✅ "你们投 Meta 广告的时候，一般第一轮测几个素材？评论区聊聊"
❌ "希望这篇文章对大家有所帮助，欢迎点赞转发"

### 干货与观点比例
60% 干货（具体方法/案例/数据）+ 40% 个人观点（你自己的解读、延伸、吐槽）

### 个人观点（必须包含，这是区别于 AI 总结的关键）
至少包含 3 处个人点评，自然嵌入正文中。可以是：
- "说实话这一点我不太同意，因为国内的情况是..."
- "我觉得这个方法如果用在独立站上，可能要调整一下..."
- "这让我想到之前看过的一个案例..."
- "坦白讲这个操作门槛还挺高的，一般小团队估计..."

### 真实感
写出来要像真人写的。可以有口语化表达、不确定的语气、偶尔跑题再拉回。不要每段都完美工整。

## 文章结构（灵活参考，根据内容自然组织，不要死板套用）

[IMAGE:cover]

{抓人开头 — 1-2 段}

{核心内容展开 — 围绕视频中最有价值的 2-3 个点，用故事、案例、比喻串联。像讲故事一样推进，不是罗列知识点。}

[IMAGE:inline]

{延伸思考/个人点评 — 结合国内跨境电商/营销实际情况}

{结尾互动引导}

## 图片占位符规则
- [IMAGE:cover] 固定放在文章最开头第一行
- [IMAGE:inline] 放在文章中间你认为最合适的话题转折点
- 每个占位符单独占一行，前后各空一行
- 不要在文章末尾放图片

## 字数要求
{word_count_range} 字（不含图片占位符行）

## 输出
只输出文章正文（包含两个图片占位符）。不要输出标题、前缀、后缀。直接输出内容。
```

---

### 输出 3：图片 Prompt

#### ⚠️ 图片 Prompt 生成规则（硬编码）

**Base Style 前缀（以下文本必须原样出现在每个 prompt 的开头，不可修改、不可省略、不可替换）：**

```
cute kawaii-style digital illustration, warm beige/cream background, soft pastel colors, rounded cartoon elements, cheerful decorative details like confetti and banners, clean layout, friendly and professional, flat design with subtle shadows,
```

**生成方式：不要让 LLM 自由发挥整段 prompt。而是用以下拼接方式：**

```
PROMPT_COVER = BASE_STYLE + {LLM 生成的主题视觉描述} + ", wide banner composition with space for title text on the right side, 16:9 aspect ratio"

PROMPT_INLINE = BASE_STYLE + {LLM 生成的核心概念视觉描述} + ", centered icon with cute character illustration, square composition, 1:1 aspect ratio"

PROMPT_CARD = BASE_STYLE + {LLM 生成的主题视觉元素} + ", with prominent Chinese text reading '{card_title}', vertical card layout, large bold readable text overlay, 3:4 aspect ratio"
```

#### Prompt（发送给 Kimi K2.5，只让它生成中间变量部分）

```
Based on this video content, I need you to generate components for 3 image prompts.

Video title: {title}
One-line summary: {tl_dr}

Generate exactly the following 4 items. Each should be 10-30 English words describing specific visual objects/scenes (NO abstract concepts, NO style words like "kawaii" or "pastel"):

TOPIC_VISUAL: A visual metaphor or scene that represents the video's main topic. Use specific objects.
Example: "a laptop showing rising graph charts surrounded by shopping bags and megaphone"

CONCEPT_VISUAL: A visual representation of the single most important method or concept discussed. Show a cute character doing something related.
Example: "a cute character with magnifying glass examining three different advertisement cards"

CARD_VISUAL: Topic-related decorative elements that would frame text nicely.
Example: "rocket ships, target icons, and coins scattered around a central text area"

CARD_TITLE: A catchy Chinese title of 6-10 characters that captures the video's core message. Punchy and shareable.
Example: "三步写出爆款广告"

Output EXACTLY in this format, nothing else:
TOPIC_VISUAL: {text}
CONCEPT_VISUAL: {text}
CARD_VISUAL: {text}
CARD_TITLE: {Chinese text}
```

#### 拼接最终 Prompt（在代码中完成，不交给 LLM）

```python
BASE_STYLE = "cute kawaii-style digital illustration, warm beige/cream background, soft pastel colors, rounded cartoon elements, cheerful decorative details like confetti and banners, clean layout, friendly and professional, flat design with subtle shadows, "

PROMPT_COVER = BASE_STYLE + topic_visual + ", wide banner composition with space for title text on the right side, 16:9 aspect ratio"

PROMPT_INLINE = BASE_STYLE + concept_visual + ", centered icon with cute character illustration, square composition, 1:1 aspect ratio"

PROMPT_CARD = BASE_STYLE + card_visual + ", with prominent Chinese text reading '" + card_title + "', vertical card layout, large bold readable text overlay, 3:4 aspect ratio"
```

---

### Step 3 完整输出

```yaml
version_a:
  tl_dr: "一句话总结文本"
  full_text: "完整版本 A markdown（所有 section）"

version_b:
  full_text: "完整版本 B 文章（含 [IMAGE:cover] 和 [IMAGE:inline]）"

image_prompts:
  cover: "完整拼接后的封面图 prompt"
  inline: "完整拼接后的配图 prompt"
  card: "完整拼接后的卡片 prompt"
  card_title: "6-10 字中文卡片标题"

metadata:
  title: "视频标题"
  channel: "频道名"
  duration_minutes: 时长分钟数
  video_url: "YouTube 链接"
  thumbnail: "原始缩略图 URL"
  published: "发布日期"
```

### ✅ Step 3 质量门禁

**版本 A 检查：**
- [ ] 一句话总结字数在 20-30 字之间
- [ ] 核心要点数量 ≥ 3 条
- [ ] 观点提取数量符合时长档位要求
- [ ] 金句引用包含英文原文
- [ ] 行动建议以动词开头

**版本 B 检查：**
- [ ] 字数在目标范围内（±20%）
- [ ] 包含 `[IMAGE:cover]` 和 `[IMAGE:inline]` 两个占位符
- [ ] 开头不是 "今天给大家分享" / "最近看了" / "大家好" 等禁止套路
- [ ] 全文 emoji 数量 ≤ 3 个
- [ ] 不包含编号列表（1. 2. 3. 或 - 开头的列表段落）
- [ ] 至少有 3 处个人观点表达（如 "我觉得"、"说实话"、"坦白讲"）
- [ ] 结尾是互动提问

**图片 Prompt 检查：**
- [ ] 3 个 prompt 都以 "cute kawaii-style digital illustration" 开头
- [ ] CARD_TITLE 是 6-10 个中文字

**如果版本 B 不通过质量门禁 → 用 Kimi K2.5 重新生成一次（最多重试 1 次），附上具体不合格项作为额外指令。**

---

## Step 4: image-generation

### 触发
Step 3 content-digest 完成后自动进入。

### 执行流程

```
1. 接收 3 段已拼接好的图片 prompt（cover / inline / card）
2. 向 Nano Banana Pro 提交 3 个异步生成请求
3. 用正确的 /api/async/detail 接口轮询状态
4. 对每张成功的图片，上传到 ImgBB 获取永久 URL
5. 用永久 URL 替换版本 B 中的占位符
6. 传递给 Step 5
```

### API 1: Nano Banana Pro — 提交异步生成

**⚠️ 注意 Authorization header 的值是 API 密钥本身，不带 Bearer 前缀。**

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

**响应示例：**
```json
{
  "code": 200,
  "msg": "成功",
  "data": {
    "id": "image_4d39239e-776a-4cbd-a8eb-e2d9b4816829",
    "count": 10
  },
  "exec_time": 0.290186,
  "ip": "119.6.176.239"
}
```

记录每个请求的 `data.id`。

### API 2: Nano Banana Pro — 轮询状态

**⚠️ 正确接口地址（之前用的 /api/img/drawDetail 是错的，会 404）：**

```http
GET https://api.wuyinkeji.com/api/async/detail?id={id}
Authorization: {{NANO_BANANA_API_KEY}}
Content-Type: application/x-www-form-urlencoded;charset:utf-8;
```

**轮询规则：**
- 每 **5 秒** 查询一次
- 最多轮询 **60 次**（5 分钟超时）
- 3 张图可以并行轮询

**状态判断：**
```
data.status = 0 → 初始化，继续等待
data.status = 1 → 进行中，继续等待
data.status = 2 → ✅ 成功，从 data 中提取图片 URL
data.status = 3 → ❌ 失败，data.message 包含错误信息
```

**成功响应中提取图片 URL：** 查看 `data` 对象中的图片链接字段（通常为 `data.image_url` 或 `data.url` 或 `data.output`，以实际返回为准）。

### API 3: ImgBB — 上传图床获取永久 URL

```http
POST https://api.imgbb.com/1/upload
Content-Type: multipart/form-data

key={{IMGBB_API_KEY}}
image={Nano Banana 返回的图片 URL}
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

### 输出

```yaml
images:
  cover_url: "https://i.ibb.co/xxx/cover.png"     # 或降级值
  inline_url: "https://i.ibb.co/xxx/inline.png"    # 或降级值
  card_url: "https://i.ibb.co/xxx/card.png"        # 或降级值

image_status:
  cover: "success" | "fallback_thumbnail" | "failed"
  inline: "success" | "fallback_thumbnail" | "failed"
  card: "success" | "fallback_thumbnail" | "failed"

version_b_with_images: "版本 B 完整文本（占位符已替换）"
```

### 降级策略（按优先级）

```
图片生成成功 → 上传 ImgBB → 使用 ImgBB URL         ✅ 最佳
ImgBB 上传失败 → 直接使用 Nano Banana 原始 URL       ⚠️ 可能过期
图片生成失败 → 使用视频原始缩略图 URL                  ⚠️ 降级方案
全部 3 张都失败 → 移除版本 B 中的占位符行              ❌ 最差情况
```

### ⚠️ 状态报告规则（必须准确）

向用户报告时，必须如实反映每张图的实际状态：
- 如果 3 张都成功："✅ 已生成 3 张配图并上传图床"
- 如果部分降级："⚠️ 封面图和配图已生成，图文卡片生成失败，已使用视频缩略图替代"
- 如果全部失败："❌ 图片生成全部失败，文章中未插入图片"

**禁止说"已生成图片"但实际用的是占位图/缩略图。**

### 成本
每张 ¥0.03，每篇 3 张 = **¥0.09/篇**

### ✅ Step 4 质量门禁
- [ ] 至少 1 张图片成功生成（cover 优先）
- [ ] 成功的图片已上传 ImgBB 获得永久 URL
- [ ] 版本 B 中的占位符已被替换（或已移除）
- [ ] image_status 准确反映每张图的实际状态

---

## Step 5: notion-storage

### 触发
Step 4 图片生成完成后自动进入。

### ⚠️ 分段写入策略（解决内容缩水问题）

Notion API 单次写入有长度限制。当内容较长时，必须分段写入：

```
1. 先创建页面，写入属性（properties）+ 存档版内容（版本 A）
2. 再用 append/update 追加二创文章（版本 B with images）
3. 最后追加素材 URL 区域
```

**每段写入后，验证是否成功再继续下一段。**

### 执行流程

```
1. 创建 Notion 页面，写入属性 + 存档版（版本 A）
2. 验证页面创建成功
3. 追加写入二创文章（版本 B with images）
4. 验证追加成功
5. 追加写入素材 URL
6. 更新待处理队列状态 → ✅ 已完成
```

### Step 5.1: 创建页面 + 写入属性 + 存档版

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

content (第一段):
  ## 📋 存档版

  {version_a.full_text 完整内容}

  ---
```

### Step 5.2: 追加二创文章

使用 Notion update page 的 `insert_content_after` 命令，在存档版 `---` 分割线之后追加：

```markdown
## ✍️ 二创文章

{version_b_with_images — 完整版本 B，图片已插入}

---
```

### Step 5.3: 追加素材区

继续追加：

```markdown
## 🖼️ 素材

封面图（16:9）：{images.cover_url}
文章配图（1:1）：{images.inline_url}
图文卡片（3:4）：{images.card_url}

图片状态：{image_status 的中文描述}
```

### 更新队列状态

知识库页面创建并写入完成后，更新「📥 播客待处理队列」中对应记录：
```
状态 → "✅ 已完成"
```

### ✅ Step 5 质量门禁
- [ ] Notion 页面创建成功（返回了 page_id）
- [ ] 所有属性字段已写入
- [ ] 存档版内容写入成功
- [ ] 二创文章追加成功
- [ ] 素材 URL 追加成功
- [ ] 队列状态已更新为 ✅ 已完成

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
段落文本       → <p style="margin:0 0 16px 0;line-height:1.8;color:#333;font-size:16px;">{text}</p>
图片 ![x](url) → <p style="text-align:center;margin:20px 0;"><img src="{url}" style="width:100%;border-radius:8px;" /></p>
空行           → 忽略（已通过 <p> 的 margin 控制间距）
```

不使用 H1-H6 标签。不使用粗体/斜体标签。保持朴素排版。

### 转换示例

版本 B 原文：
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

## 每篇处理完成后的汇总报告模板

每处理完一篇视频，向用户发送以下格式的报告（必须如实填写每项状态）：

```
📝 处理报告：{video_title}

🎬 字幕提取：✅ 成功（{duration_minutes} 分钟，{transcript_char_count} 字符）
📝 内容消化：✅ 版本 A（{viewpoint_count} 条观点）+ 版本 B（{word_count} 字）
🖼️ 图片生成：
  - 封面图：{✅ 成功 / ⚠️ 使用缩略图替代 / ❌ 失败}
  - 文章配图：{✅ 成功 / ⚠️ 使用缩略图替代 / ❌ 失败}
  - 图文卡片：{✅ 成功 / ⚠️ 使用缩略图替代 / ❌ 失败}
📓 Notion：✅ 已写入知识库（{notion_page_url}）
📱 微信草稿：✅ 已存入草稿箱

总耗时：{elapsed_time}
```

---

## 成本估算

| 项目 | 单价 | 说明 |
|------|------|------|
| 频道监控 | 免费 | TranscriptAPI channel/latest + channel/resolve |
| 字幕提取 | 1 credit/视频 | TranscriptAPI transcript |
| 内容消化 | LLM token | Kimi K2.5 |
| 图片生成 | ¥0.09/篇 | 3 张 × ¥0.03 |
| 图床 | 免费 | ImgBB |
| Notion | 免费 | Notion API |
| 微信草稿 | 免费 | 微信公众号 API |

**每篇总成本 ≈ 1 credit + Kimi token + ¥0.09**
**每日成本（2 篇）≈ 2 credits + Kimi tokens + ¥0.18**

---

## 完整流程时间线示例

```
08:00  youtube-monitor 启动
       → 检查 12 个频道，发现 4 条新视频
       → 去重后 3 条写入待处理队列
       → 通知："新增 3 条，当前队列共 7 条待处理"

08:01  queue-manager 启动
       → 取优先级最高的 2 条

--- 第 1 条：Alex Hormozi "How I Made $100M" ---

08:01  Step 2 字幕提取
       → 调用 TranscriptAPI（不是其他 API！）
       → 获得 45 分钟完整字幕文本（32,000 字符）
       → 队列状态 → 📋 已提取字幕
       → ✅ 质量门禁：字幕 > 500 字符 ✓

08:02  Step 3 内容消化（使用 Kimi K2.5，不是其他模型！）
       → 版本 A：15 条观点 + 3 条金句 + 3 条行动建议
       → 版本 B：1300 字二创文章（含占位符）
       → 图片 prompt：3 段（base style 拼接，不是 LLM 自由生成！）
       → 队列状态 → ✍️ 处理中
       → ✅ 质量门禁：版本 B 无禁止套路开头 ✓，emoji ≤ 3 ✓

08:03  Step 4 图片生成
       → POST /api/async/image_nanoBanana_pro ×3
       → GET /api/async/detail 轮询（不是 /api/img/drawDetail！）
       → 3 张全部成功 → 上传 ImgBB
       → 替换版本 B 占位符
       → 状态报告："✅ 已生成 3 张配图"（不是说成功但用的占位图！）

08:04  Step 5 Notion 存储（分段写入）
       → 第 1 段：创建页面 + 属性 + 存档版 ✓
       → 第 2 段：追加二创文章 ✓
       → 第 3 段：追加素材 URL ✓
       → 队列状态 → ✅ 已完成

08:04  Step 6 微信草稿
       → Markdown → HTML → 存入草稿箱
       → 发布状态 → 微信已发

--- 第 2 条开始 ---

08:05  Step 2-6 重复...

08:10  全部完成
       → 汇总通知："已处理 2 篇，队列剩余 5 条"
```
