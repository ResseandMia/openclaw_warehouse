---
name: youtube-notes
description: Generate detailed study notes from YouTube videos. Use when user sends a YouTube link and wants a Markdown file with key knowledge points and detailed explanations.
---

# YouTube Video Notes Generator

## Prerequisites

**Required tools:**
```bash
# Install yt-dlp for video info and subtitle extraction
pip install yt-dlp

# Or via apt (Ubuntu/Debian)
sudo apt install yt-dlp
```

## Workflow

### Step 1: Get Video Info and Subtitles

```bash
# Get video metadata (title, duration, description)
yt-dlp --dump-json "VIDEO_URL" | jq '{title, description, duration_string, uploader}'

# Download subtitles (auto-detect language, prefer en/zh-Hans)
yt-dlp --write-subs --sub-langs "en,zh-Hans" --skip-download "VIDEO_URL" -o "%(title)s.%(ext)s"
```

### Step 2: Generate Notes

1. Read the subtitle file (.vtt or .srt)
2. Identify key topics using LLM analysis:
   - recurring concepts
   - tutorial steps
   - important definitions
   - actionable takeaways
3. Structure into markdown with:
   - Video metadata header
   - Table of contents (if 5+ sections)
   - Organized knowledge points
   - Relevant details under each point

### Step 3: Output

Save to: `notes/[video-title-slug]-[date].md`

```markdown
---
title: "Video Title"
source: https://youtube.com/watch?v=...
date: YYYY-MM-DD
duration: HH:MM:SS
---

# Video Title

## Overview
Brief summary...

## Key Knowledge Points

### 1. First Topic
Detail...

### 2. Second Topic
Detail...
```

## Handling Missing Subtitles

If no subtitles available:
1. Warn user: "Video has no subtitles, notes will be based on title/description only"
2. Optionally use `--write-auto-subs` for auto-generated captions
3. If still nothing, generate minimal notes from description + metadata

## Output Options

### Option 1: Telegram Direct Send (Default)
Generate notes and send directly to user via current chat.

```markdown
# [Video Title]

**Source:** https://youtube.com/watch?v=...
**Date:** YYYY-MM-DD
**Duration:** HH:MM:SS

---

## Overview
Brief summary...

## Key Knowledge Points

### 1. First Topic
Detail...

### 2. Second Topic
Detail...
```

### Option 2: Save to File (Optional)
Save markdown file to: `/root/.openclaw/workspace/notes/`

### Option 3: Feishu (Future)
Coming soon - requires Feishu API credentials.
