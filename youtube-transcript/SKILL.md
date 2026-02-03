---
name: youtube-transcript
description: |
  Fetch and summarize YouTube video transcripts. Use when asked to summarize, transcribe, or extract content from YouTube videos. Handles transcript fetching via residential IP proxy to bypass YouTube's cloud IP blocks.
---

# YouTube Transcript

YouTube 字幕提取工具 - 支持代理和摘要生成

## Features

- 🎬 **字幕提取** - 获取 YouTube 视频字幕
- 📝 **内容摘要** - 自动生成视频摘要
- 🌍 **代理支持** - 住宅 IP 代理绕过云 IP 封锁
- 📄 **多格式输出** - Markdown、SRT、TXT
- 🔍 **自动检测** - 智能选择字幕语言
- 💾 **本地缓存** - 避免重复请求

## Usage

**提取字幕：**
```
"提取这个 YouTube 视频的字幕"
"下载 YouTube 字幕"
```

**生成摘要：**
```
"总结这个 YouTube 视频"
"视频内容摘要"
```

**指定语言：**
```
"获取英文字幕"
"中日双语字幕"
```

## Configuration

Required environment variables:
```bash
# 代理配置（可选）
PROXY_URL=http://residential-proxy:port
PROXY_USERNAME=xxx
PROXY_PASSWORD=xxx

# 缓存配置
CACHE_DIR=./cache

# API 配置（可选，用于摘要）
OPENAI_API_KEY=your_key
```

## Commands

### Get Transcript

```bash
python3 scripts/transcript.py get --url "https://youtube.com/watch?v=VIDEO_ID"
```

### Get with Language

```bash
python3 scripts/transcript.py get \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --lang en
```

### Get All Transcripts

```bash
python3 scripts/transcript.py get-all \
  --url "https://youtube.com/watch?v=VIDEO_ID"
```

### Download as SRT

```bash
python3 scripts/transcript.py download \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --format srt \
  --output subtitles.srt
```

### Generate Summary

```bash
python3 scripts/transcript.py summarize \
  --url "https://youtube.com/watch?v=VIDEO_ID"
```

### List Cached

```bash
python3 scripts/transcript.py list-cache
```

### Clear Cache

```bash
python3 scripts/transcript.py clear-cache --video VIDEO_ID
```

## Output Formats

### Markdown (Default)

```markdown
# Video Title

**Duration:** 10:30
**Language:** English

## Transcript

[Full transcript text...]

## Summary

[AI-generated summary...]
```

### SRT Format

```
1
00:00:01,000 --> 00:00:05,000
First line of subtitle

2
00:00:05,000 --> 00:00:10,000
Second line of subtitle
```

### TXT Format

```
[00:00] First line of subtitle
[00:05] Second line of subtitle
```

## Proxy Configuration

The skill supports residential proxies to bypass YouTube's IP blocks:

### Environment Variables

```bash
# HTTP Proxy
export PROXY_URL="http://user:pass@proxy:port"

# Or with authentication
export PROXY_USERNAME="your_username"
export PROXY_PASSWORD="your_password"
```

### Supported Proxy Types

- HTTP/HTTPS proxies
- SOCKS5 proxies
- Residential proxy networks
- Rotating proxies

## Error Handling

- No transcript available → Try auto-generated captions
- Proxy blocked → Switch proxy or retry
- Video private → Return error
- Rate limited → Wait and retry

## Automation Examples

### Batch Extract Transcripts

```bash
#!/bin/bash
# Extract transcripts from playlist

while read url; do
  python3 scripts/transcript.py get \
    --url "$url" \
    --format markdown \
    --output "transcripts/$(echo $url | grep -oP 'v=\K[^&]+').md"
done < playlist.txt
```

### Daily Video Summary

```bash
#!/bin/bash
# Summarize new videos from channel

CHANNEL_URL="https://youtube.com/channel/UCxxx"

# Get latest video
LATEST=$(python3 scripts/transcript.py latest --channel "$CHANNEL_URL")

# Generate summary
python3 scripts/transcript.py summarize --url "$LATEST" > "summaries/$(date +%Y-%m-%d).md"
```

### Export to Notion

```bash
#!/bin/bash
# Extract and save to Notion

VIDEO_URL=$1
TRANSCRIPT=$(python3 scripts/transcript.py get --url "$VIDEO_URL" --format markdown)

# Send to Notion via Notion API
curl -X POST "https:///v1/pagesapi.notion.com" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "'$NOTION_DB'"},
    "properties": {"title": {"title": [{"text": {"content": "'"$VIDEO_URL"'"}}]}},
    "children": '"$(echo $TRANSCRIPT | jq -Rs '.')"'
  }'
```

## Limitations

- YouTube may block data center IPs
- Some videos have disabled captions
- Auto-generated captions may be inaccurate
- Long videos may timeout

## Links

- YouTube API: https://developers.google.com/youtube/v3
- YouTube Transcript API: https://github.com/jdepoix/youtube-transcript-api

## Source

Skill from ClawHub by @xthezealot
- ClawHub: https://www.clawhub.ai/xthezealot/youtube-transcript
