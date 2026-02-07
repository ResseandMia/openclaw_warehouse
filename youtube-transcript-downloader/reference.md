# YouTube Transcript Downloader - Reference Guide

Advanced reference for the TranscriptAPI.com integration, response schemas, output format details, and troubleshooting.

## API Reference

### Base URL

```
https://transcriptapi.com/api/v2
```

### Authentication

All requests use Bearer token authentication:

```
Authorization: Bearer sk_your_api_key_here
```

API keys:
- Prefixed with `sk_`
- Never expire (unless manually revoked)
- Get yours at [transcriptapi.com/signup](https://transcriptapi.com/signup)

### Endpoints

#### GET /youtube/transcript

Fetch the transcript for a YouTube video.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_url` | string | Yes | YouTube URL or bare video ID |
| `format` | string | No | `json` (default) or `text` |
| `include_timestamp` | boolean | No | Include timestamps (default: true) |
| `send_metadata` | boolean | No | Include video metadata (default: false) |

**Response (format=json):**

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "title": "Video Title",
  "duration": "3:32",
  "transcript": [
    {
      "text": "First segment of text",
      "start": 0.0,
      "duration": 4.12
    },
    {
      "text": "Second segment of text",
      "start": 4.12,
      "duration": 3.5
    }
  ]
}
```

**Response (format=text):**

```
First segment of text Second segment of text...
```

**Notes:**
- `title` and `duration` fields only appear when `send_metadata=true`
- Transcript segments may appear under `transcript` or `segments` key
- 1 credit deducted per successful call

#### GET /youtube/search

Search YouTube for videos, channels, or playlists.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `type` | string | No | `video` (default), `channel`, or `playlist` |
| `limit` | integer | No | Max results to return (default: 10) |

**Response:**

```json
{
  "results": [
    {
      "video_id": "abc123",
      "title": "Video Title",
      "channel": "Channel Name",
      "url": "https://youtube.com/watch?v=abc123"
    }
  ]
}
```

**Notes:**
- 1 credit deducted per search call
- Results include video metadata for discovery

### Error Responses

All errors return JSON with an error message:

```json
{
  "error": "Description of what went wrong"
}
```

| Status | Code | Meaning | Retryable |
|--------|------|---------|-----------|
| 400 | Bad Request | Invalid parameters | No - fix request |
| 401 | Unauthorized | Bad API key | No - check key |
| 402 | Payment Required | Credits exhausted | No - top up account |
| 404 | Not Found | Video doesn't exist | No - check URL |
| 422 | Unprocessable | No captions available | No - different video |
| 429 | Rate Limited | Too many requests | Yes - wait and retry |
| 500 | Server Error | API internal error | Yes - retry after delay |

### Credits

- 100 free credits on signup
- 1 credit per successful API call (transcript or search)
- Credits NOT deducted on errors
- Monitor usage at [transcriptapi.com dashboard](https://transcriptapi.com)

## Output Format Details

### JSON Format

Raw structured segments directly from the API:

```json
[
  {"text": "Hello world", "start": 0.0, "duration": 2.5},
  {"text": "Welcome to this video", "start": 2.5, "duration": 3.1}
]
```

### SRT Format (SubRip)

Standard subtitle format used by most video editors:

```
1
00:00:00,000 --> 00:00:02,500
Hello world

2
00:00:02,500 --> 00:00:05,600
Welcome to this video
```

**Timestamp format:** `HH:MM:SS,mmm` (comma before milliseconds)

### VTT Format (WebVTT)

Web standard subtitle format for HTML5 video:

```
WEBVTT

00:00:00.000 --> 00:00:02.500
Hello world

00:00:02.500 --> 00:00:05.600
Welcome to this video
```

**Timestamp format:** `HH:MM:SS.mmm` (dot before milliseconds)

### Text Format

Plain text output. With `--timestamps`:

```
[00:00:00] Hello world
[00:00:02] Welcome to this video
```

Without timestamps:

```
Hello world
Welcome to this video
```

### Markdown Format

Formatted document with metadata header and paragraph-grouped transcript:

```markdown
# Video Title

- **Video ID:** dQw4w9WgXcQ
- **Language:** en
- **Duration:** 3:32
- **Downloaded:** 2026-02-07 12:00:00

## Transcript

**[00:00:00]**

Hello world. Welcome to this video. Today we're going to talk about...

**[00:01:00]**

Moving on to the next topic. Let me show you how this works...
```

**Paragraph grouping:** Segments are merged into ~60-second blocks for readability. Each block starts with a bold timestamp.

## Script Architecture

### Class: TranscriptAPIClient

The API client handles authentication, HTTP requests, and error mapping.

```python
client = TranscriptAPIClient(api_key="sk_xxx")

# Fetch transcript
result = client.get_transcript(
    video_url="https://youtube.com/watch?v=VIDEO_ID",
    fmt="json",              # "json" or "text"
    include_timestamp=True,  # include start/duration in segments
    send_metadata=True,      # include title, duration in response
)

# Search YouTube
result = client.search(
    query="machine learning",
    search_type="video",     # "video", "channel", "playlist"
    limit=10,
)
```

**Return format:** All methods return a dict with `"success": True/False`. On failure, includes `"error"` message.

### Utility Functions

| Function | Purpose |
|----------|---------|
| `extract_video_id(url)` | Extract 11-char video ID from any YouTube URL format |
| `format_timestamp(seconds)` | Convert float seconds to `HH:MM:SS` |
| `format_srt_timestamp(seconds)` | Convert to `HH:MM:SS,mmm` (SRT) |
| `format_vtt_timestamp(seconds)` | Convert to `HH:MM:SS.mmm` (VTT) |
| `convert_to_srt(segments)` | Segments list to SRT string |
| `convert_to_vtt(segments)` | Segments list to VTT string |
| `convert_to_text(segments)` | Segments list to plain text |
| `convert_to_markdown(segments, metadata)` | Segments to Markdown with headers |
| `sanitize_filename(name)` | Clean string for safe filenames |
| `get_segments(data)` | Extract segment list from API response |

### Extending the Script

To add a new output format:

1. Create a `convert_to_FORMAT(segments)` function
2. Add the format to the `choices` list in `p_download` and `p_batch` argparse
3. Add the conversion case in `cmd_download()` and `cmd_batch()`
4. Add the extension mapping in `cmd_batch()`'s `ext_map`

## Troubleshooting

### "Connection failed. Check your network."

- Verify internet connectivity
- Check if a corporate proxy/firewall is blocking `transcriptapi.com`
- If behind a proxy, configure `HTTP_PROXY`/`HTTPS_PROXY` env vars

### "Invalid API key."

- Verify `TRANSCRIPTAPI_KEY` is set: `echo $TRANSCRIPTAPI_KEY`
- Key must start with `sk_`
- Check the key hasn't been revoked at transcriptapi.com dashboard

### "No credits remaining."

- Check credit balance at transcriptapi.com
- Credits are only deducted on successful calls

### "Video not found or no transcript available."

- Verify the video URL works in a browser
- Video may be private, deleted, or age-restricted
- Some videos have captions disabled by the uploader

### "No transcript segments found."

- The API returned data but no parseable segments
- Try `--format text` which uses a different API response path
- The video may only have auto-generated captions in an unsupported format

### Batch download stops midway

- Progress is printed to stderr for each video
- Already-downloaded files are NOT overwritten on re-run (manually delete to re-download)
- Failed videos are reported but don't stop the batch

## Integration with Other Skills

This skill pairs well with:

- **content-digest** - Summarize downloaded transcripts
- **notion-api-skill** - Save transcripts to Notion pages
- **feishu-integration** - Post transcripts to Feishu/Lark
- **markdown-to-image** - Convert transcript to shareable image
- **youtube-feed** - Monitor channels, then download new transcripts
