---
name: podcast-workflow
description: |
  播客处理一站式工作流。支持两种入口：
  (1) 直接处理：提供 YouTube 链接，直接进入处理流程
  (2) 更新检查：获取关注博主的最新更新，用户挑选后处理
  功能：字幕提取 → content-digest 处理 → 自动保存飞书知识库。
  触发词："获取播客更新"、"处理这个播客"、"播客工作流"、"有什么新播客"。
---

# 播客处理工作流

从 YouTube 到飞书发布的一站式播客处理流程。

## 两种入口

### 入口 A：获取播客更新（推荐）

用户说"获取播客更新"或"有什么新播客"时：

```
获取更新 → 展示列表 → 用户选择 → 字幕提取 → [询问] → Content-Digest → 飞书
```

### 入口 B：直接处理链接

用户提供 YouTube 链接时：

```
YouTube 链接 → 字幕提取 → [询问] → Content-Digest → 飞书
```

## 使用方式

**获取播客更新：**
```
"获取播客更新"
"有什么新播客"
```

**直接处理链接：**
```
"处理这个播客 https://youtube.com/watch?v=..."
"播客工作流 https://youtube.com/..."
```

## 依赖的 Skills

- `youtube-feed`：获取博主更新
- `youtube-transcript-cn`：字幕提取
- `content-digest`：内容处理
- `feishu-integration`：飞书写入
- `markdown-to-image`：转换为图片海报（可选）

## 配置

| 配置项 | 值 |
|--------|-----|
| 本地保存路径 | `/root/.openclaw/workspace/notes/` |
| 关注的频道 | 22 个（见 youtube-feed） |
| 观点数量 | 10-15 条 |
| 更新检查天数 | 2 天 |
