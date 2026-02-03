---
name: yt-subtitles-downloader
description: |
  Download YouTube video subtitles in bulk. Supports single videos, playlists, and channels.
  Output to Markdown (for LLM/RAG) or SRT (subtitle files).
  Trigger: "下载字幕" / "YouTube 字幕"
---

# YouTube Subtitles Downloader

Download subtitles from YouTube videos, playlists, or channels.

## Installation

```bash
# Install dependencies
pip install yt-dlp youtube-transcript-api
```

## Usage

### Download single video

```bash
python3 scripts/download.py --url "YOUTUBE_URL" --format md
```

### Download with SRT format

```bash
python3 scripts/download.py --url "YOUTUBE_URL" --format srt --output ./srt_files
```

## Trigger Words

- 下载字幕
- YouTube 字幕
- 下载 YouTube 字幕
- 提取字幕

## Example

**User says:**
> 下载这个字幕 https://www.youtube.com/watch?v=VcqQmrGqthg

**Agent executes:**
```bash
python3 scripts/download.py --url "https://www.youtube.com/watch?v=VcqQmrGqthg" --format md
```

**Output:**
```
Video ID: VcqQmrGqthg
Title: Content Masterclass: The Most Valuable 3 Hours
Downloading subtitle...
✓ Saved: ./subtitles/Content Masterclass_The Most Valuable 3 Hours.md
  Language: English
  Characters: 15000
```

## Output Files

| Format | Description | Use Case |
|--------|-------------|----------|
| Markdown (.md) | Single file with TOC | LLM/RAG, NotebookLM |
| SRT (.srt) | Timestamped subtitles | Video editing, translation |

## Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| --url | -u | YouTube URL or video ID |
| --format | -f | Output format: md or srt (default: md) |
| --output | -o | Output directory (default: ./subtitles) |

## Advanced Features

**From original project (yt-bulk-subtitles-downloader):**
- Bulk download entire channels/playlists
- Multi-threaded parallel downloads
- Proxy rotation to prevent rate limiting
- Progress saving and resume capability

These features require the full project installation.

## Source

Based on: https://github.com/ResseandMia/yt-bulk-subtitles-downloader

## Dependencies

- `yt-dlp` - Video metadata extraction
- `youtube-transcript-api` - Transcript fetching
