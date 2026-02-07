#!/usr/bin/env python3
"""
YouTube Transcript Downloader - Download transcripts via TranscriptAPI.com

Usage:
    python3 transcript_downloader.py transcript --url "https://youtube.com/watch?v=VIDEO_ID"
    python3 transcript_downloader.py search --query "topic" --limit 5
    python3 transcript_downloader.py download --url "VIDEO_URL" --format srt --output out.srt
    python3 transcript_downloader.py batch --file urls.txt --format markdown --output-dir ./transcripts
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


API_BASE_URL = "https://transcriptapi.com/api/v2"


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
        """Make a GET request to the API."""
        url = f"{API_BASE_URL}{endpoint}"
        try:
            resp = self.session.get(url, params=params, timeout=60)
            if resp.status_code == 401:
                return {"success": False, "error": "Invalid API key. Check your TRANSCRIPTAPI_KEY."}
            if resp.status_code == 402:
                return {"success": False, "error": "No credits remaining. Top up at transcriptapi.com."}
            if resp.status_code == 404:
                return {"success": False, "error": "Video not found or no transcript available."}
            if resp.status_code == 422:
                return {"success": False, "error": "Unprocessable request. The video may not have captions."}
            if resp.status_code >= 400:
                return {"success": False, "error": f"API error {resp.status_code}: {resp.text[:200]}"}
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
        """Fetch transcript for a YouTube video."""
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
        """Search YouTube for videos, channels, or playlists."""
        params = {
            "q": query,
            "type": search_type,
            "limit": limit,
        }
        return self._request("/youtube/search", params)


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from a YouTube URL or return the ID if already bare."""
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
    """Format seconds as HH:MM:SS,mmm for SRT."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_vtt_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS.mmm for WebVTT."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def convert_to_srt(segments: List[Dict]) -> str:
    """Convert transcript segments to SRT format."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = seg.get("start", 0)
        duration = seg.get("duration", 0)
        end = start + duration
        text = seg.get("text", "")
        lines.append(f"{i}")
        lines.append(f"{format_srt_timestamp(start)} --> {format_srt_timestamp(end)}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def convert_to_vtt(segments: List[Dict]) -> str:
    """Convert transcript segments to WebVTT format."""
    lines = ["WEBVTT", ""]
    for seg in segments:
        start = seg.get("start", 0)
        duration = seg.get("duration", 0)
        end = start + duration
        text = seg.get("text", "")
        lines.append(f"{format_vtt_timestamp(start)} --> {format_vtt_timestamp(end)}")
        lines.append(text)
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
    """Convert transcript segments to Markdown format."""
    lines = []

    # Header with metadata
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

    # Group segments into paragraphs (~60 second blocks)
    paragraph = []
    para_start = 0
    for seg in segments:
        start = seg.get("start", 0)
        text = seg.get("text", "")
        if not paragraph:
            para_start = start
        if start - para_start > 60 and paragraph:
            ts = format_timestamp(para_start)
            lines.append(f"**[{ts}]**")
            lines.append("")
            lines.append(" ".join(paragraph))
            lines.append("")
            paragraph = [text]
            para_start = start
        else:
            paragraph.append(text)

    # Flush remaining
    if paragraph:
        ts = format_timestamp(para_start)
        lines.append(f"**[{ts}]**")
        lines.append("")
        lines.append(" ".join(paragraph))
        lines.append("")

    return "\n".join(lines)


def sanitize_filename(name: str, max_len: int = 100) -> str:
    """Sanitize a string for use as a filename."""
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = name.replace(' ', '_')
    return name[:max_len]


def get_segments(data: Dict) -> List[Dict]:
    """Extract transcript segments from API response, handling different response shapes."""
    # The API may return segments under different keys
    if "transcript" in data and isinstance(data["transcript"], list):
        return data["transcript"]
    if "segments" in data and isinstance(data["segments"], list):
        return data["segments"]
    # If the response is text-only (format=text), there are no segments
    return []


# ── Command handlers ────────────────────────────────────────────────────────


def cmd_transcript(client: TranscriptAPIClient, args):
    """Handle the 'transcript' command."""
    result = client.get_transcript(
        video_url=args.url,
        fmt="json",
        include_timestamp=args.timestamps,
        send_metadata=args.metadata,
    )
    if not result.get("success"):
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    # Print JSON to stdout
    result.pop("success", None)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_download(client: TranscriptAPIClient, args):
    """Handle the 'download' command."""
    fmt = args.format

    # Always fetch JSON from API so we have structured segments
    result = client.get_transcript(
        video_url=args.url,
        fmt="json",
        include_timestamp=True,
        send_metadata=True,
    )
    if not result.get("success"):
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    segments = get_segments(result)
    if not segments:
        # Fallback: try text format from API
        text_result = client.get_transcript(
            video_url=args.url,
            fmt="text",
            include_timestamp=False,
        )
        if text_result.get("success"):
            raw_text = text_result.get("transcript", text_result.get("text", ""))
            if isinstance(raw_text, str) and raw_text.strip():
                content = raw_text
                if args.output:
                    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Saved to {args.output} ({len(content)} chars)", file=sys.stderr)
                else:
                    print(content)
                return
        print("Error: No transcript segments found.", file=sys.stderr)
        sys.exit(1)

    metadata = {k: result.get(k) for k in ("video_id", "title", "language", "duration")}

    # Convert to requested format
    if fmt == "json":
        content = json.dumps(segments, ensure_ascii=False, indent=2)
    elif fmt == "text":
        content = convert_to_text(segments, with_timestamps=args.timestamps)
    elif fmt == "srt":
        content = convert_to_srt(segments)
    elif fmt == "vtt":
        content = convert_to_vtt(segments)
    elif fmt == "markdown":
        content = convert_to_markdown(segments, metadata)
    else:
        print(f"Error: Unknown format '{fmt}'", file=sys.stderr)
        sys.exit(1)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved to {args.output} ({len(content)} chars)", file=sys.stderr)
    else:
        print(content)


def cmd_search(client: TranscriptAPIClient, args):
    """Handle the 'search' command."""
    result = client.search(
        query=args.query,
        search_type=args.type,
        limit=args.limit,
    )
    if not result.get("success"):
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    result.pop("success", None)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_batch(client: TranscriptAPIClient, args):
    """Handle the 'batch' command - download transcripts for multiple URLs."""
    if not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    with open(args.file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        print("Error: No URLs found in file.", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output_dir or "./transcripts"
    os.makedirs(output_dir, exist_ok=True)
    fmt = args.format

    ext_map = {
        "json": ".json",
        "text": ".txt",
        "srt": ".srt",
        "vtt": ".vtt",
        "markdown": ".md",
    }
    ext = ext_map.get(fmt, ".txt")

    success_count = 0
    fail_count = 0

    for i, url in enumerate(urls, 1):
        video_id = extract_video_id(url)
        label = video_id or url[:40]
        print(f"[{i}/{len(urls)}] Processing {label}...", file=sys.stderr)

        result = client.get_transcript(
            video_url=url,
            fmt="json",
            include_timestamp=True,
            send_metadata=True,
        )

        if not result.get("success"):
            print(f"  FAILED: {result.get('error', 'Unknown error')}", file=sys.stderr)
            fail_count += 1
            continue

        segments = get_segments(result)
        metadata = {k: result.get(k) for k in ("video_id", "title", "language", "duration")}

        # Build filename
        title = result.get("title") or video_id or f"video_{i}"
        filename = sanitize_filename(title) + ext
        filepath = os.path.join(output_dir, filename)

        if fmt == "json":
            content = json.dumps(segments, ensure_ascii=False, indent=2)
        elif fmt == "text":
            content = convert_to_text(segments)
        elif fmt == "srt":
            content = convert_to_srt(segments)
        elif fmt == "vtt":
            content = convert_to_vtt(segments)
        elif fmt == "markdown":
            content = convert_to_markdown(segments, metadata)
        else:
            content = convert_to_text(segments)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  Saved: {filepath} ({len(content)} chars)", file=sys.stderr)
        success_count += 1

    print(f"\nDone. {success_count} succeeded, {fail_count} failed.", file=sys.stderr)


# ── CLI entry point ─────────────────────────────────────────────────────────


def main():
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

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── transcript ──
    p_transcript = subparsers.add_parser("transcript", help="Fetch transcript and print as JSON")
    p_transcript.add_argument("--url", "-u", required=True, help="YouTube URL or video ID")
    p_transcript.add_argument("--timestamps", "-t", action="store_true", default=True,
                              help="Include timestamps (default: true)")
    p_transcript.add_argument("--no-timestamps", dest="timestamps", action="store_false",
                              help="Exclude timestamps")
    p_transcript.add_argument("--metadata", "-m", action="store_true",
                              help="Include video metadata")

    # ── download ──
    p_download = subparsers.add_parser("download", help="Download transcript in a specific format")
    p_download.add_argument("--url", "-u", required=True, help="YouTube URL or video ID")
    p_download.add_argument("--format", "-f", default="markdown",
                            choices=["json", "text", "srt", "vtt", "markdown"],
                            help="Output format (default: markdown)")
    p_download.add_argument("--output", "-o", help="Output file path (default: stdout)")
    p_download.add_argument("--timestamps", "-t", action="store_true", default=True,
                            help="Include timestamps for text format")
    p_download.add_argument("--no-timestamps", dest="timestamps", action="store_false")

    # ── search ──
    p_search = subparsers.add_parser("search", help="Search YouTube videos, channels, or playlists")
    p_search.add_argument("--query", "-q", required=True, help="Search query")
    p_search.add_argument("--type", default="video",
                          choices=["video", "channel", "playlist"],
                          help="Result type (default: video)")
    p_search.add_argument("--limit", "-l", type=int, default=10,
                          help="Max results (default: 10)")

    # ── batch ──
    p_batch = subparsers.add_parser("batch", help="Batch download transcripts from a URL list file")
    p_batch.add_argument("--file", required=True, help="File with URLs (one per line)")
    p_batch.add_argument("--format", "-f", default="markdown",
                         choices=["json", "text", "srt", "vtt", "markdown"],
                         help="Output format (default: markdown)")
    p_batch.add_argument("--output-dir", "-d", default="./transcripts",
                         help="Output directory (default: ./transcripts)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not args.api_key:
        print("Error: API key required. Set TRANSCRIPTAPI_KEY env var or use --api-key.", file=sys.stderr)
        sys.exit(1)

    client = TranscriptAPIClient(args.api_key)

    commands = {
        "transcript": cmd_transcript,
        "download": cmd_download,
        "search": cmd_search,
        "batch": cmd_batch,
    }

    commands[args.command](client, args)


if __name__ == "__main__":
    main()
