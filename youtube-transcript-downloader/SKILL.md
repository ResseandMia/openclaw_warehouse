---
name: youtube-transcript-downloader
description: |
  Download YouTube transcripts via TranscriptAPI.com. Supports transcript extraction, YouTube search, and multiple output formats (JSON, text, SRT, VTT, Markdown). Use when asked to download, extract, or save YouTube video transcripts.
---

# YouTube Transcript Downloader

Download YouTube video transcripts using the [TranscriptAPI.com](https://transcriptapi.com) REST API.

## Features

- Transcript extraction with timestamps and metadata
- YouTube video search with type and result limit filtering
- Multiple output formats: JSON, text, SRT, VTT, Markdown
- Save transcripts to files or print to stdout
- Batch download from a list of URLs
- Paragraph grouping for readable text output

## Setup

### API Key

Get a free API key (100 credits) at [transcriptapi.com/signup](https://transcriptapi.com/signup).

Set it as an environment variable:

```bash
export TRANSCRIPTAPI_KEY="sk_your_api_key_here"
```

Or pass it via `--api-key` on every command.

### Dependencies

```bash
pip install requests
```

## Commands

### Get Transcript

Fetch transcript for a single video:

```bash
python3 scripts/transcript_downloader.py transcript --url "https://youtube.com/watch?v=VIDEO_ID"
```

With timestamps and metadata:

```bash
python3 scripts/transcript_downloader.py transcript \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --timestamps \
  --metadata
```

Plain text output:

```bash
python3 scripts/transcript_downloader.py transcript \
  --url "dQw4w9WgXcQ" \
  --format text
```

### Download Transcript to File

Save as SRT:

```bash
python3 scripts/transcript_downloader.py download \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --format srt \
  --output subtitles.srt
```

Save as Markdown:

```bash
python3 scripts/transcript_downloader.py download \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --format markdown \
  --output transcript.md
```

Save as VTT:

```bash
python3 scripts/transcript_downloader.py download \
  --url "https://youtube.com/watch?v=VIDEO_ID" \
  --format vtt \
  --output subtitles.vtt
```

### Search YouTube

Search for videos:

```bash
python3 scripts/transcript_downloader.py search \
  --query "machine learning tutorial" \
  --type video \
  --limit 5
```

### Batch Download

Download transcripts from a file containing URLs (one per line):

```bash
python3 scripts/transcript_downloader.py batch \
  --file urls.txt \
  --format markdown \
  --output-dir ./transcripts
```

## Trigger Words

- download transcript
- YouTube transcript
- get transcript
- save subtitles
- extract transcript

## Output Formats

| Format | Extension | Description | Use Case |
|--------|-----------|-------------|----------|
| json | .json | Structured segments with timestamps | Data processing, APIs |
| text | .txt | Plain text transcript | Reading, LLM input |
| srt | .srt | SubRip subtitle format | Video editing |
| vtt | .vtt | WebVTT subtitle format | Web video players |
| markdown | .md | Formatted with metadata header | Documentation, RAG |

## Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| --api-key | -k | TranscriptAPI key (or set TRANSCRIPTAPI_KEY env var) |
| --url | -u | YouTube URL or video ID |
| --format | -f | Output format: json, text, srt, vtt, markdown |
| --output | -o | Output file path |
| --timestamps | -t | Include timestamps in output |
| --metadata | -m | Include video metadata in response |
| --query | -q | Search query (for search command) |
| --type | | Search type: video, channel, playlist |
| --limit | -l | Max search results (for search command) |
| --file | | File with URLs for batch download |
| --output-dir | -d | Output directory for batch downloads |

## Example Workflow

**User says:**
> Download the transcript for https://www.youtube.com/watch?v=dQw4w9WgXcQ

**Agent executes:**
```bash
python3 scripts/transcript_downloader.py download \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --format markdown \
  --output transcript.md
```

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request | Check parameters |
| 401 | Invalid API key | Verify TRANSCRIPTAPI_KEY |
| 402 | No credits remaining | Top up at transcriptapi.com |
| 404 | Video not found | Verify URL |
| 422 | Unprocessable | Check video has captions |

## API Reference

- Base URL: `https://transcriptapi.com/api/v2`
- Auth: Bearer token (`Authorization: Bearer sk_xxx`)
- Docs: [transcriptapi.com/docs/api](https://transcriptapi.com/docs/api/)
- Credits: 1 credit per API call, 100 free to start

## Source

Built on [TranscriptAPI.com](https://transcriptapi.com) REST API.
Inspired by [yt-dlp](https://github.com/yt-dlp/yt-dlp) CLI patterns.
