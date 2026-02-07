#!/usr/bin/env python3
"""
YouTube Transcript Downloader - Download transcripts via TranscriptAPI.com

Commands:
    transcript  Fetch transcript and print structured JSON
    download    Save transcript to file in SRT/VTT/Markdown/text/JSON
    search      Search YouTube for videos, channels, or playlists
    batch       Batch download transcripts from a URL list file

Setup:
    export TRANSCRIPTAPI_KEY="sk_your_api_key"
    pip install requests
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "requests library required. Install with: pip install requests",
    }))
    sys.exit(1)


API_BASE_URL = "https://transcriptapi.com/api/v2"


# ── API Client ──────────────────────────────────────────────────────────────


class TranscriptAPIClient:
    """Client for TranscriptAPI.com REST API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        })

    def _request(self, endpoint: str, params: dict = None) -> Dict:
        """Make a GET request to the API and return a standardized result dict."""
        url = f"{API_BASE_URL}{endpoint}"
        try:
            resp = self.session.get(url, params=params, timeout=60)

            error_map = {
                401: "Invalid API key. Check your TRANSCRIPTAPI_KEY.",
                402: "No credits remaining. Top up at transcriptapi.com.",
                404: "Video not found or no transcript available.",
                422: "Unprocessable request. The video may not have captions.",
            }
            if resp.status_code in error_map:
                return {"success": False, "error": error_map[resp.status_code],
                        "status_code": resp.status_code}
            if resp.status_code >= 400:
                return {"success": False, "status_code": resp.status_code,
                        "error": f"API error {resp.status_code}: {resp.text[:200]}"}

            data = resp.json()
            data["success"] = True
            return data

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out. The video may be very long."}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Connection failed. Check your network."}
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON response: {resp.text[:200]}"}

    def get_transcript(self, video_url: str, fmt: str = "json",
                       include_timestamp: bool = True,
                       send_metadata: bool = False) -> Dict:
        """Fetch transcript for a YouTube video.

        Args:
            video_url: YouTube URL or bare video ID.
            fmt: Response format - "json" (structured segments) or "text" (plain).
            include_timestamp: Whether segments include start/duration.
            send_metadata: Whether to include title, duration, etc.
        """
        params = {
            "video_url": video_url,
            "format": fmt,
            "include_timestamp": str(include_timestamp).lower(),
        }
        if send_metadata:
            params["send_metadata"] = "true"
        return self._request("/youtube/transcript", params)

    def search(self, query: str, search_type: str = "video",
               limit: int = 10) -> Dict:
        """Search YouTube for videos, channels, or playlists.

        Args:
            query: Search query string.
            search_type: One of "video", "channel", "playlist".
            limit: Maximum number of results.
        """
        params = {
            "q": query,
            "type": search_type,
            "limit": limit,
        }
        return self._request("/youtube/search", params)


# ── Helpers ─────────────────────────────────────────────────────────────────


def extract_video_id(url: str) -> Optional[str]:
    """Extract 11-character video ID from any YouTube URL format, or return
    the input if it is already a bare video ID."""
    if re.match(r'^[0-9A-Za-z_-]{11}$', url):
        return url
    patterns = [
        r'(?:v=)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be/)([0-9A-Za-z_-]{11})',
        r'(?:youtube\.com/embed/)([0-9A-Za-z_-]{11})',
        r'(?:youtube\.com/shorts/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_srt_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS,mmm (SRT standard)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_vtt_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS.mmm (WebVTT standard)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def sanitize_filename(name: str, max_len: int = 100) -> str:
    """Remove characters unsafe for filenames and truncate."""
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = name.replace(' ', '_')
    return name[:max_len]


def get_segments(data: Dict) -> List[Dict]:
    """Extract transcript segments from API response.

    The API may return segments under "transcript" or "segments" key.
    Returns an empty list if the response is text-only.
    """
    if "transcript" in data and isinstance(data["transcript"], list):
        return data["transcript"]
    if "segments" in data and isinstance(data["segments"], list):
        return data["segments"]
    return []


def _now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _output_json(data: Dict) -> None:
    """Print a dict as formatted JSON to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _fail(error: str, meta: Dict = None) -> None:
    """Print a standardized error JSON and exit."""
    result = {"success": False, "error": error}
    if meta:
        result["meta"] = meta
    _output_json(result)
    sys.exit(1)


# ── Format converters ───────────────────────────────────────────────────────


def convert_to_srt(segments: List[Dict]) -> str:
    """Convert transcript segments to SRT subtitle format."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = seg.get("start", 0)
        duration = seg.get("duration", 0)
        end = start + duration
        lines.append(str(i))
        lines.append(f"{format_srt_timestamp(start)} --> {format_srt_timestamp(end)}")
        lines.append(seg.get("text", ""))
        lines.append("")
    return "\n".join(lines)


def convert_to_vtt(segments: List[Dict]) -> str:
    """Convert transcript segments to WebVTT subtitle format."""
    lines = ["WEBVTT", ""]
    for seg in segments:
        start = seg.get("start", 0)
        duration = seg.get("duration", 0)
        end = start + duration
        lines.append(f"{format_vtt_timestamp(start)} --> {format_vtt_timestamp(end)}")
        lines.append(seg.get("text", ""))
        lines.append("")
    return "\n".join(lines)


def convert_to_text(segments: List[Dict], with_timestamps: bool = False) -> str:
    """Convert transcript segments to plain text."""
    lines = []
    for seg in segments:
        text = seg.get("text", "")
        if with_timestamps:
            ts = format_timestamp(seg.get("start", 0))
            lines.append(f"[{ts}] {text}")
        else:
            lines.append(text)
    return "\n".join(lines)


def convert_to_markdown(segments: List[Dict], metadata: Dict = None) -> str:
    """Convert transcript segments to Markdown with metadata header
    and ~60-second paragraph grouping for readability."""
    lines = []

    title = "YouTube Transcript"
    if metadata:
        title = metadata.get("title", title)
    lines.append(f"# {title}")
    lines.append("")

    if metadata:
        if metadata.get("video_id"):
            lines.append(f"- **Video ID:** {metadata['video_id']}")
        if metadata.get("language"):
            lines.append(f"- **Language:** {metadata['language']}")
        if metadata.get("duration"):
            lines.append(f"- **Duration:** {metadata['duration']}")
        lines.append(f"- **Downloaded:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

    lines.append("## Transcript")
    lines.append("")

    # Group segments into ~60-second paragraphs
    paragraph: List[str] = []
    para_start = 0.0
    for seg in segments:
        start = seg.get("start", 0)
        text = seg.get("text", "")
        if not paragraph:
            para_start = start
        if start - para_start > 60 and paragraph:
            lines.append(f"**[{format_timestamp(para_start)}]**")
            lines.append("")
            lines.append(" ".join(paragraph))
            lines.append("")
            paragraph = [text]
            para_start = start
        else:
            paragraph.append(text)

    if paragraph:
        lines.append(f"**[{format_timestamp(para_start)}]**")
        lines.append("")
        lines.append(" ".join(paragraph))
        lines.append("")

    return "\n".join(lines)


def _convert(fmt: str, segments: List[Dict], metadata: Dict = None,
             timestamps: bool = True) -> str:
    """Dispatch to the appropriate format converter."""
    converters = {
        "json": lambda: json.dumps(segments, ensure_ascii=False, indent=2),
        "text": lambda: convert_to_text(segments, with_timestamps=timestamps),
        "srt": lambda: convert_to_srt(segments),
        "vtt": lambda: convert_to_vtt(segments),
        "markdown": lambda: convert_to_markdown(segments, metadata),
    }
    fn = converters.get(fmt)
    if not fn:
        _fail(f"Unknown format: {fmt}")
    return fn()


# ── Command handlers ────────────────────────────────────────────────────────


def cmd_transcript(client: TranscriptAPIClient, args):
    """Fetch transcript and print structured JSON to stdout."""
    result = client.get_transcript(
        video_url=args.url,
        fmt="json",
        include_timestamp=args.timestamps,
        send_metadata=args.metadata,
    )
    if not result.get("success"):
        _fail(result.get("error", "Unknown error"),
              meta={"command": "transcript", "url": args.url})

    video_id = result.get("video_id") or extract_video_id(args.url)
    segments = get_segments(result)

    _output_json({
        "success": True,
        "data": {
            "video_id": video_id,
            "language": result.get("language"),
            "title": result.get("title"),
            "duration": result.get("duration"),
            "segment_count": len(segments),
            "transcript": segments,
        },
        "meta": {
            "command": "transcript",
            "timestamp": _now_iso(),
            "url": args.url,
        },
    })


def cmd_download(client: TranscriptAPIClient, args):
    """Download transcript and convert to requested format."""
    fmt = args.format

    result = client.get_transcript(
        video_url=args.url,
        fmt="json",
        include_timestamp=True,
        send_metadata=True,
    )
    if not result.get("success"):
        _fail(result.get("error", "Unknown error"),
              meta={"command": "download", "url": args.url, "format": fmt})

    segments = get_segments(result)

    # Fallback: if no structured segments, try the text endpoint
    if not segments:
        text_result = client.get_transcript(
            video_url=args.url, fmt="text", include_timestamp=False)
        if text_result.get("success"):
            raw = text_result.get("transcript", text_result.get("text", ""))
            if isinstance(raw, str) and raw.strip():
                _write_output(raw, args.output)
                return
        _fail("No transcript segments found.",
              meta={"command": "download", "url": args.url})

    metadata = {k: result.get(k) for k in ("video_id", "title", "language", "duration")}
    content = _convert(fmt, segments, metadata, timestamps=args.timestamps)
    _write_output(content, args.output)


def cmd_search(client: TranscriptAPIClient, args):
    """Search YouTube and print results as JSON."""
    result = client.search(
        query=args.query,
        search_type=args.type,
        limit=args.limit,
    )
    if not result.get("success"):
        _fail(result.get("error", "Unknown error"),
              meta={"command": "search", "query": args.query})

    result.pop("success", None)
    _output_json({
        "success": True,
        "data": result,
        "meta": {
            "command": "search",
            "timestamp": _now_iso(),
            "query": args.query,
            "type": args.type,
            "limit": args.limit,
        },
    })


def cmd_batch(client: TranscriptAPIClient, args):
    """Batch download transcripts from a file of URLs."""
    if not os.path.isfile(args.file):
        _fail(f"File not found: {args.file}",
              meta={"command": "batch", "file": args.file})

    with open(args.file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        _fail("No URLs found in file.",
              meta={"command": "batch", "file": args.file})

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    fmt = args.format

    ext_map = {"json": ".json", "text": ".txt", "srt": ".srt",
               "vtt": ".vtt", "markdown": ".md"}
    ext = ext_map.get(fmt, ".txt")

    results = []

    for i, url in enumerate(urls, 1):
        video_id = extract_video_id(url)
        label = video_id or url[:40]
        print(f"[{i}/{len(urls)}] Processing {label}...", file=sys.stderr)

        result = client.get_transcript(
            video_url=url, fmt="json", include_timestamp=True, send_metadata=True)

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            print(f"  FAILED: {error_msg}", file=sys.stderr)
            results.append({"url": url, "success": False, "error": error_msg})
            continue

        segments = get_segments(result)
        metadata = {k: result.get(k) for k in ("video_id", "title", "language", "duration")}

        title = result.get("title") or video_id or f"video_{i}"
        filename = sanitize_filename(title) + ext
        filepath = os.path.join(output_dir, filename)

        content = _convert(fmt, segments, metadata)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  Saved: {filepath} ({len(content)} chars)", file=sys.stderr)
        results.append({
            "url": url,
            "success": True,
            "video_id": video_id,
            "output": filepath,
            "chars": len(content),
            "segments": len(segments),
        })

    succeeded = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    print(f"\nDone. {succeeded} succeeded, {failed} failed.", file=sys.stderr)

    _output_json({
        "success": True,
        "data": {"results": results},
        "meta": {
            "command": "batch",
            "timestamp": _now_iso(),
            "total": len(urls),
            "succeeded": succeeded,
            "failed": failed,
            "format": fmt,
            "output_dir": output_dir,
        },
    })


# ── Output helpers ──────────────────────────────────────────────────────────


def _write_output(content: str, output_path: Optional[str]) -> None:
    """Write content to a file or stdout."""
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(json.dumps({
            "success": True,
            "meta": {"output": output_path, "chars": len(content)},
        }))
    else:
        print(content)


# ── CLI entry point ─────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        description="YouTube Transcript Downloader - powered by TranscriptAPI.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s transcript --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s download --url "dQw4w9WgXcQ" --format srt --output subtitles.srt
  %(prog)s search --query "python tutorial" --limit 5
  %(prog)s batch --file urls.txt --format markdown --output-dir ./transcripts
""",
    )

    parser.add_argument(
        "--api-key", "-k",
        default=os.environ.get("TRANSCRIPTAPI_KEY"),
        help="TranscriptAPI key (default: TRANSCRIPTAPI_KEY env var)",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── transcript ──
    p = sub.add_parser("transcript", help="Fetch transcript and print as JSON")
    p.add_argument("--url", "-u", required=True, help="YouTube URL or video ID")
    p.add_argument("--timestamps", "-t", action="store_true", default=True,
                   help="Include timestamps (default: true)")
    p.add_argument("--no-timestamps", dest="timestamps", action="store_false",
                   help="Exclude timestamps")
    p.add_argument("--metadata", "-m", action="store_true",
                   help="Include video metadata (title, duration)")

    # ── download ──
    p = sub.add_parser("download", help="Download transcript in a specific format")
    p.add_argument("--url", "-u", required=True, help="YouTube URL or video ID")
    p.add_argument("--format", "-f", default="markdown",
                   choices=["json", "text", "srt", "vtt", "markdown"],
                   help="Output format (default: markdown)")
    p.add_argument("--output", "-o", help="Output file path (default: stdout)")
    p.add_argument("--timestamps", "-t", action="store_true", default=True,
                   help="Include timestamps for text format")
    p.add_argument("--no-timestamps", dest="timestamps", action="store_false")

    # ── search ──
    p = sub.add_parser("search", help="Search YouTube videos, channels, or playlists")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--type", default="video",
                   choices=["video", "channel", "playlist"],
                   help="Result type (default: video)")
    p.add_argument("--limit", "-l", type=int, default=10,
                   help="Max results (default: 10)")

    # ── batch ──
    p = sub.add_parser("batch", help="Batch download transcripts from a URL list file")
    p.add_argument("--file", required=True, help="File with URLs (one per line)")
    p.add_argument("--format", "-f", default="markdown",
                   choices=["json", "text", "srt", "vtt", "markdown"],
                   help="Output format (default: markdown)")
    p.add_argument("--output-dir", "-d", default="./transcripts",
                   help="Output directory (default: ./transcripts)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not args.api_key:
        _fail("API key required. Set TRANSCRIPTAPI_KEY env var or use --api-key.",
              meta={"command": args.command})

    client = TranscriptAPIClient(args.api_key)

    handlers = {
        "transcript": cmd_transcript,
        "download": cmd_download,
        "search": cmd_search,
        "batch": cmd_batch,
    }
    handlers[args.command](client, args)


if __name__ == "__main__":
    main()
