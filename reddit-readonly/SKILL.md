---
name: reddit-readonly
description: |
  Browse and search Reddit in read-only mode using public JSON endpoints. Supports subreddit listings, post searches, comment threads, and permalink shortlists. No authentication required.
---

# Reddit (Read-Only)

Reddit 浏览工具 - 只读模式，无需认证

## Features

- 🔍 **子版块浏览** - 查看任意 subreddit 的帖子列表
- 📝 **帖子搜索** - 按关键词搜索帖子
- 💬 **评论查看** - 获取帖子评论和讨论
- 🔗 **链接清单** - 整理 permalink 清单
- 🚫 **严格只读** - 不发帖、不回复、不投票、不管理

## Usage

**浏览子版块：**
```
"查看 Reddit r/programming"
"列出 r/ai 的热门帖子"
```

**搜索帖子：**
```
"搜索 Reddit Python 教程"
"在 Reddit 找机器学习相关讨论"
```

**查看评论：**
```
"查看这个 Reddit 帖子的评论"
"获取 r/technology 的最新帖子"
```

## Commands

### List Subreddit Posts

```bash
python3 scripts/reddit.py listing --subreddit programming --sort hot --limit 25
```

**Sort options:** hot, new, rising, top, controversial

### Search Posts

```bash
python3 scripts/reddit.py search --query "Python tutorial" --subreddit learnpython
```

### Get Post Comments

```bash
python3 scripts/reddit.py comments --post-id POST_ID --limit 50
```

### Build Permalink Shortlist

```bash
python3 scripts/reddit.py shortlist --subreddit technology --limit 10
```

## Reddit JSON API

All data comes from public endpoints:

| Endpoint | Description |
|----------|-------------|
| `reddit.com/r/{sub}/hot.json` | Hot posts |
| `reddit.com/r/{sub}/new.json` | New posts |
| `reddit.com/r/{sub}/search.json` | Search results |
| `reddit.com/r/{sub}/comments/{id}.json` | Comments |

## Output Format

All commands return standardized JSON:

```json
{
  "success": true,
  "data": [...],
  "meta": {
    "subreddit": "programming",
    "count": 25
  }
}
```

## Error Handling

- Subreddit not found → Return empty list with error
- Rate limited → Retry after delay
- Invalid post ID → Error message
- Network issues → Retry 3 times

## Rate Limits

Reddit has implicit rate limits. Commands include:
- Automatic delays between requests
- Respect for `Retry-After` headers
- Error recovery for 429 responses

## Examples

### Get Top Posts Today

```bash
python3 scripts/reddit.py listing --subreddit all --sort top --time day --limit 50
```

### Search Multiple Subreddits

```bash
python3 scripts/reddit.py search --query "AI news" --subreddits technology,science,ai
```

### Get Comment Thread

```bash
python3 scripts/reddit.py comments --post-id "15abcde" --sort top
```

## Limitations (By Design)

- ❌ Cannot post content
- ❌ Cannot vote (upvote/downvote)
- ❌ Cannot comment/reply
- ❌ Cannot send messages
- ❌ Cannot manage subreddits
- ❌ Cannot access private content

This is intentional - read-only mode for safe browsing.

## Source

Skill from ClawHub by @buksan1950
- ClawHub: https://www.clawhub.ai/buksan1950/reddit-readonly

## Note

Reddit API may be restricted in some server environments (HTTP 403). If this occurs:

1. Use browser-based access via OpenClaw browser tool
2. Or use a proxy/VPN if available
3. The tool will still function normally when used in a non-restricted environment

## Installation# Install dependencies

```bash
pip install requests

# Make script (if needed)
 executable
chmod +x scripts/reddit.py
```
