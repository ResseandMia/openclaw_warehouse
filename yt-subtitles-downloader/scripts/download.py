#!/usr/bin/env python3
"""
YouTube Subtitles Downloader - Bulk download subtitles from YouTube
Usage: python3 download.py --url "YOUTUBE_URL" [--format md|srt] [--threads N]
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Try to import dependencies
try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp not installed. Run: pip install yt-dlp")
    sys.exit(1)

try:
    from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
except ImportError:
    print("Error: youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
    sys.exit(1)

try:
    from youtube_transcript_api.formatters import SRTFormatter
except ImportError:
    print("Error: Formatter not available")
    sys.exit(1)


def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    import re
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_info(url):
    """Get video title using yt-dlp."""
    ydl_opts = {'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'id': info.get('id'),
                'title': info.get('title', 'Unknown'),
                'uploader': info.get('uploader', 'Unknown')
            }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None


def download_subtitle(video_id, output_dir):
    """Download subtitle for a single video."""
    try:
        ytt = YouTubeTranscriptApi()
        transcript_list = ytt.list(video_id)
        
        # Try English first
        try:
            transcript = transcript_list.find_transcript(["en"])
            lang_info = "English"
        except NoTranscriptFound:
            # Try any available
            available = list(transcript_list)
            if available:
                transcript = available[0]
                lang_info = transcript.language
            else:
                return None
        
        # Fetch transcript
        fetched = transcript.fetch()
        text = ' '.join(snippet.text for snippet in fetched)
        
        return {
            'id': video_id,
            'transcript': text,
            'fetched': fetched,
            'language': lang_info
        }
    except Exception as e:
        print(f"Error downloading {video_id}: {e}")
        return None


def save_markdown(video_info, output_dir):
    """Save as Markdown file."""
    title = sanitize_filename(video_info['title'])
    filename = os.path.join(output_dir, f"{title}.md")
    
    content = f"# {video_info['title']}\n\n"
    content += f"**Video ID:** {video_info['id']}\n"
    content += f"**URL:** https://www.youtube.com/watch?v={video_info['id']}\n"
    content += f"**Downloaded:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    content += "---\n\n"
    content += "## Transcript\n\n"
    content += video_info.get('transcript', 'No transcript available.')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename


def save_srt(video_info, output_dir):
    """Save as SRT file."""
    title = sanitize_filename(video_info['title'])
    filename = os.path.join(output_dir, f"{title}.srt")
    
    formatter = SRTFormatter()
    if video_info.get('fetched'):
        srt_content = formatter.format_transcript(video_info['fetched'])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        return filename
    return None


def sanitize_filename(name):
    """Remove invalid characters from filename."""
    import re
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized[:100] if len(sanitized) > 100 else sanitized


def main():
    parser = argparse.ArgumentParser(description='Download YouTube subtitles')
    parser.add_argument('--url', '-u', required=True, help='YouTube URL or video ID')
    parser.add_argument('--format', '-f', default='md', choices=['md', 'srt'], 
                        help='Output format: md (Markdown) or srt (SRT)')
    parser.add_argument('--output', '-o', default='./subtitles', 
                        help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Extract video ID
    video_id = extract_video_id(args.url)
    if not video_id:
        print("Error: Invalid YouTube URL")
        sys.exit(1)
    
    print(f"Video ID: {video_id}")
    
    # Get video info
    url = f"https://www.youtube.com/watch?v={video_id}"
    video_info = get_video_info(url)
    if not video_info:
        print("Error: Could not get video info")
        sys.exit(1)
    
    print(f"Title: {video_info['title']}")
    
    # Download subtitle
    print("Downloading subtitle...")
    result = download_subtitle(video_id, args.output)
    
    if not result:
        print("Error: Could not download subtitle")
        sys.exit(1)
    
    video_info['transcript'] = result['transcript']
    video_info['fetched'] = result['fetched']
    video_info['language'] = result['language']
    
    # Save file
    if args.format == 'md':
        filename = save_markdown(video_info, args.output)
    else:
        filename = save_srt(video_info, args.output)
    
    if filename:
        print(f"✓ Saved: {filename}")
        print(f"  Language: {result['language']}")
        print(f"  Characters: {len(result['transcript'])}")
    else:
        print("Error: Could not save file")
        sys.exit(1)


if __name__ == "__main__":
    main()
