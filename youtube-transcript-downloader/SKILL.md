---
name: youtube-transcript-downloader
description: |
  Download YouTube video transcripts via TranscriptAPI.com REST API. Use when the user wants to:
  - Download or extract a YouTube video transcript/subtitles
  - Search YouTube for videos, channels, or playlists
  - Save subtitles as SRT, VTT, Markdown, or plain text
  - Batch download transcripts from multiple URLs
  - Get structured transcript data with timestamps
  Trigger phrases: "download transcript", "get subtitles", "YouTube transcript", "extract captions", "save transcript"
---

# YouTube Transcript Downloader

Download YouTube video transcripts using the [TranscriptAPI.com](https://transcriptapi.com) REST API. Supports single video transcripts, YouTube search, batch downloads, and 5 output formats.

## When to Use This Skill

Use this skill when the user wants to:

- Extract or download a transcript from a YouTube video
- Save subtitles/captions to a file (SRT, VTT, Markdown, text, JSON)
- Search YouTube for videos on a topic
- Batch download transcripts from a list of URLs
- Get structured transcript data for LLM processing or RAG pipelines

## Setup

### 1. Get API Key

Sign up for a free API key (100 credits) at [transcriptapi.com/signup](https://transcriptapi.com/signup).

### 2. Set Environment Variable

```bash
export TRANSCRIPTAPI_KEY="sk_your_api_key_here"
```

Or pass `--api-key sk_xxx` on every command.

### 3. Install Dependencies

```bash
pip install requests
```

## Quick Start

```bash
# Get transcript as JSON
python3 scripts/transcript_downloader.py transcript --url "https://youtube.com/watch?v=VIDEO_ID"

# Download as Markdown file
python3 scripts/transcript_downloader.py download --url "VIDEO_ID" --format markdown --output transcript.md

# Search YouTube
python3 scripts/transcript_downloader.py search --query "machine learning" --limit 5
```

## Commands

### transcript - Fetch and print transcript

Fetch a video's transcript and print structured JSON to stdout.

```bash
# Basic usage
python3 scripts/transcript_downloader.py transcript --url "https://youtube.com/watch?v=VIDEO_ID"

# With video metadata (title, duration, etc.)
python3 scripts/transcript_downloader.py transcript \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --metadata

# Without timestamps
python3 scripts/transcript_downloader.py transcript \
  --url "dQw4w9WgXcQ" \
  --no-timestamps
```

**Output:** JSON to stdout with `video_id`, `language`, `transcript` segments.

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--url` | `-u` | required | YouTube URL or video ID |
| `--timestamps` | `-t` | true | Include timestamps |
| `--no-timestamps` | | | Exclude timestamps |
| `--metadata` | `-m` | false | Include video metadata |

### download - Save transcript to file

Fetch transcript and convert to a specific format. Writes to file or stdout.

```bash
# Save as SRT subtitles
python3 scripts/transcript_downloader.py download \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --format srt \
  --output subtitles.srt

# Save as Markdown (default format)
python3 scripts/transcript_downloader.py download \
  --url "VIDEO_ID" \
  --output transcript.md

# Save as WebVTT
python3 scripts/transcript_downloader.py download \
  --url "VIDEO_ID" \
  --format vtt \
  --output subtitles.vtt

# Print plain text to stdout
python3 scripts/transcript_downloader.py download \
  --url "VIDEO_ID" \
  --format text

# Save as JSON segments
python3 scripts/transcript_downloader.py download \
  --url "VIDEO_ID" \
  --format json \
  --output data.json
```

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--url` | `-u` | required | YouTube URL or video ID |
| `--format` | `-f` | markdown | json, text, srt, vtt, markdown |
| `--output` | `-o` | stdout | Output file path |
| `--timestamps` | `-t` | true | Include timestamps (text format) |

### search - Search YouTube

Search for videos, channels, or playlists. Returns JSON results.

```bash
# Search videos
python3 scripts/transcript_downloader.py search \
  --query "python tutorial" \
  --limit 5

# Search channels
python3 scripts/transcript_downloader.py search \
  --query "Andrej Karpathy" \
  --type channel

# Search playlists
python3 scripts/transcript_downloader.py search \
  --query "deep learning course" \
  --type playlist \
  --limit 3
```

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--query` | `-q` | required | Search query |
| `--type` | | video | video, channel, playlist |
| `--limit` | `-l` | 10 | Max number of results |

### batch - Batch download from URL list

Download transcripts for multiple videos from a text file (one URL per line). Lines starting with `#` are treated as comments.

```bash
# Batch download as Markdown
python3 scripts/transcript_downloader.py batch \
  --file urls.txt \
  --format markdown \
  --output-dir ./transcripts

# Batch download as SRT
python3 scripts/transcript_downloader.py batch \
  --file urls.txt \
  --format srt \
  --output-dir ./subtitles
```

**urls.txt example:**

```
# AI lectures
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
dQw4w9WgXcQ
```

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--file` | | required | Text file with URLs (one per line) |
| `--format` | `-f` | markdown | json, text, srt, vtt, markdown |
| `--output-dir` | `-d` | ./transcripts | Output directory |

## Output Formats

| Format | Extension | Description | Best For |
|--------|-----------|-------------|----------|
| json | .json | Structured segments with start/duration/text | Data processing, APIs, pipelines |
| text | .txt | Plain text, optionally timestamped | LLM input, reading, RAG |
| srt | .srt | SubRip subtitle format | Video editing, translation |
| vtt | .vtt | WebVTT subtitle format | Web video players, HTML5 |
| markdown | .md | Metadata header + paragraph-grouped text | Documentation, Notion, notes |

## Supported URL Formats

The tool accepts any of these URL formats:

- `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `https://youtu.be/dQw4w9WgXcQ`
- `https://youtube.com/embed/dQw4w9WgXcQ`
- `https://youtube.com/shorts/dQw4w9WgXcQ`
- `https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120`
- `dQw4w9WgXcQ` (bare video ID)

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `TRANSCRIPTAPI_KEY` | Yes | API key from transcriptapi.com (prefix: `sk_`) |

## Workflow Examples

### Extract transcript for LLM analysis

```bash
# User: "Summarize this YouTube video for me"
python3 scripts/transcript_downloader.py download \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --format text \
  --output /tmp/transcript.txt

# Then feed the text to Claude or another LLM for summarization
```

### Research a topic via YouTube

```bash
# Step 1: Search for relevant videos
python3 scripts/transcript_downloader.py search \
  --query "transformer architecture explained" \
  --limit 5

# Step 2: Download transcripts for selected videos
python3 scripts/transcript_downloader.py download \
  --url "VIDEO_ID_FROM_SEARCH" \
  --format markdown \
  --output research/transformers.md
```

### Build a transcript corpus

```bash
# Step 1: Create a URL list
cat > urls.txt << 'EOF'
# Andrej Karpathy lectures
https://www.youtube.com/watch?v=VIDEO_1
https://www.youtube.com/watch?v=VIDEO_2
https://www.youtube.com/watch?v=VIDEO_3
EOF

# Step 2: Batch download all transcripts
python3 scripts/transcript_downloader.py batch \
  --file urls.txt \
  --format markdown \
  --output-dir ./corpus
```

## Error Handling

| HTTP Code | Meaning | Resolution |
|-----------|---------|------------|
| 400 | Bad request | Check URL format and parameters |
| 401 | Invalid API key | Verify `TRANSCRIPTAPI_KEY` is set correctly |
| 402 | Credits exhausted | Top up credits at transcriptapi.com |
| 404 | Video not found | Verify the video URL exists and is public |
| 422 | Unprocessable | Video may not have captions/subtitles |

## Limitations

- Requires a TranscriptAPI.com API key (100 free credits on signup)
- 1 credit consumed per successful API call
- Videos without captions/auto-generated subtitles will return errors
- Private or age-restricted videos may not be accessible

## Source

- API: [TranscriptAPI.com](https://transcriptapi.com) | [API docs](https://transcriptapi.com/docs/api/)
- CLI patterns inspired by [yt-dlp](https://github.com/yt-dlp/yt-dlp)
