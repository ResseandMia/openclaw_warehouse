#!/usr/bin/env python3
"""
YouTube Transcript Skill - Fetch and summarize YouTube video transcripts
"""

import json
import sys
import os
import argparse
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("Warning: youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")


class YouTubeTranscript:
    """YouTube transcript fetcher with proxy support"""
    
    def __init__(self, proxy_url: str = None, cache_dir: str = "./cache"):
        self.proxy_url = proxy_url or os.environ.get("PROXY_URL")
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_video_id(self, url: str) -> str:
        """Extract video ID from URL"""
        # Standard YouTube URL
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
            r'(?:youtube\.com\/shorts\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _get_cache_path(self, video_id: str, lang: str = "en") -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{video_id}_{lang}.json")
    
    def _load_cache(self, video_id: str, lang: str = "en") -> Optional[Dict]:
        """Load from cache"""
        cache_path = self._get_cache_path(video_id, lang)
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return json.load(f)
        return None
    
    def _save_cache(self, video_id: str, lang: str, data: Dict):
        """Save to cache"""
        cache_path = self._get_cache_path(video_id, lang)
        with open(cache_path, "w") as f:
            json.dump(data, f)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to timestamp"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def get_transcript(self, url: str, lang: str = "en") -> Dict:
        """Get transcript for a video"""
        if not YOUTUBE_API_AVAILABLE:
            return {"success": False, "error": "youtube-transcript-api not installed"}
        
        video_id = self._get_video_id(url)
        if not video_id:
            return {"success": False, "error": "Invalid YouTube URL"}
        
        # Check cache
        cached = self._load_cache(video_id, lang)
        if cached:
            return {"success": True, "cached": True, **cached}
        
        try:
            # Fetch transcript
            transcript_api = YouTubeTranscriptApi()
            transcript = transcript_api.fetch(video_id)
            
            # Get available languages
            available_langs = transcript.get_language_codes()
            
            # Find requested language or fallback
            if lang not in available_langs:
                # Try English or first available
                if "en" in available_langs:
                    lang = "en"
                elif available_langs:
                    lang = available_langs[0]
                else:
                    return {"success": False, "error": "No transcripts available"}
            
            # Get transcript data
            captions = transcript.get_transcript(language_code=lang)
            
            # Build result
            result = {
                "video_id": video_id,
                "language": lang,
                "available_languages": available_langs,
                "transcript": [],
                "full_text": ""
            }
            
            for entry in captions:
                result["transcript"].append({
                    "start": entry["start"],
                    "duration": entry["duration"],
                    "text": entry["text"]
                })
                result["full_text"] += entry["text"] + " "
            
            result["full_text"] = result["full_text"].strip()
            
            # Save to cache
            self._save_cache(video_id, lang, result)
            
            return {"success": True, "cached": False, **result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_transcripts(self, url: str) -> Dict:
        """Get all available transcripts for a video"""
        if not YOUTUBE_API_AVAILABLE:
            return {"success": False, "error": "youtube-transcript-api not installed"}
        
        video_id = self._get_video_id(url)
        if not video_id:
            return {"success": False, "error": "Invalid YouTube URL"}
        
        try:
            transcript_api = YouTubeTranscriptApi()
            transcript = transcript_api.fetch(video_id)
            
            languages = {}
            for lang_code in transcript.get_language_codes():
                try:
                    captions = transcript.get_transcript(language_code=lang_code)
                    full_text = " ".join([c["text"] for c in captions])
                    languages[lang_code] = {
                        "language": lang_code,
                        "text": full_text,
                        "entries": len(captions)
                    }
                except Exception:
                    continue
            
            return {
                "success": True,
                "video_id": video_id,
                "available_languages": list(languages.keys()),
                "transcripts": languages
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def download_transcript(self, url: str, format: str = "srt",
                           output: str = None, lang: str = "en") -> Dict:
        """Download transcript in specified format"""
        result = self.get_transcript(url, lang)
        
        if not result["success"]:
            return result
        
        transcript = result["transcript"]
        
        if format == "srt":
            content = ""
            for i, entry in enumerate(transcript, 1):
                start = self._format_srt_timestamp(entry["start"])
                end = self._format_srt_timestamp(entry["start"] + entry["duration"])
                content += f"{i}\n{start} --> {end}\n{entry['text']}\n\n"
        
        elif format == "txt":
            content = ""
            for entry in transcript:
                timestamp = self._format_timestamp(entry["start"])
                content += f"[{timestamp}] {entry['text']}\n"
        
        elif format == "vtt":
            content = "WEBVTT\n\n"
            for entry in transcript:
                start = self._format_srt_timestamp(entry["start"]).replace(",", ".")
                end = self._format_srt_timestamp(entry["start"] + entry["duration"]).replace(",", ".")
                content += f"{start} --> {end}\n{entry['text']}\n\n"
        
        elif format == "json":
            content = json.dumps(transcript, indent=2)
        
        else:
            return {"success": False, "error": f"Unknown format: {format}"}
        
        if output:
            with open(output, "w") as f:
                f.write(content)
            return {"success": True, "output": output}
        else:
            return {"success": True, "content": content}
    
    def generate_summary(self, url: str, max_length: int = 500) -> Dict:
        """Generate a summary of the video content"""
        result = self.get_transcript(url)
        
        if not result["success"]:
            return result
        
        full_text = result["full_text"]
        
        # Simple extractive summary (first sentences)
        sentences = full_text.split(". ")
        summary = ". ".join(sentences[:min(5, len(sentences))])
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return {
            "success": True,
            "video_id": result["video_id"],
            "language": result["language"],
            "summary": summary,
            "original_length": len(full_text),
            "summary_length": len(summary)
        }
    
    def list_cache(self) -> Dict:
        """List cached transcripts"""
        cached = []
        for f in os.listdir(self.cache_dir):
            if f.endswith(".json"):
                parts = f.replace(".json", "").split("_")
                cached.append({
                    "video_id": parts[0],
                    "language": parts[1] if len(parts) > 1 else "unknown"
                })
        
        return {
            "success": True,
            "count": len(cached),
            "cached_videos": cached
        }
    
    def clear_cache(self, video_id: str = None) -> Dict:
        """Clear cache"""
        cleared = 0
        
        if video_id:
            # Clear specific video
            for lang in ["en", "zh-Hans", "ja"]:
                path = self._get_cache_path(video_id, lang)
                if os.path.exists(path):
                    os.remove(path)
                    cleared += 1
        else:
            # Clear all
            for f in os.listdir(self.cache_dir):
                if f.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, f))
                    cleared += 1
        
        return {
            "success": True,
            "cleared": cleared,
            "message": f"Cleared {cleared} cached files"
        }
    
    def get_video_info(self, url: str) -> Dict:
        """Get basic video info"""
        video_id = self._get_video_id(url)
        if not video_id:
            return {"success": False, "error": "Invalid YouTube URL"}
        
        return {
            "success": True,
            "video_id": video_id,
            "url": url,
            "embed_url": f"https://www.youtube.com/embed/{video_id}",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }


def main():
    parser = argparse.ArgumentParser(description="YouTube Transcript Skill")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Get transcript
    get_parser = subparsers.add_parser("get", help="Get transcript")
    get_parser.add_argument("--url", "-u", required=True, help="YouTube URL")
    get_parser.add_argument("--lang", "-l", default="en", help="Language code")
    
    # Get all transcripts
    all_parser = subparsers.add_parser("get-all", help="Get all transcripts")
    all_parser.add_argument("--url", "-u", required=True, help="YouTube URL")
    
    # Download transcript
    dl_parser = subparsers.add_parser("download", help="Download transcript")
    dl_parser.add_argument("--url", "-u", required=True, help="YouTube URL")
    dl_parser.add_argument("--format", "-f", default="srt", 
                           choices=["srt", "txt", "vtt", "json"],
                           help="Output format")
    dl_parser.add_argument("--output", "-o", help="Output file")
    dl_parser.add_argument("--lang", "-l", default="en", help="Language")
    
    # Summarize
    sum_parser = subparsers.add_parser("summarize", help="Generate summary")
    sum_parser.add_argument("--url", "-u", required=True, help="YouTube URL")
    sum_parser.add_argument("--max-length", "-m", type=int, default=500,
                            help="Max summary length")
    
    # List cache
    subparsers.add_parser("list-cache", help="List cached transcripts")
    
    # Clear cache
    clear_parser = subparsers.add_parser("clear-cache", help="Clear cache")
    clear_parser.add_argument("--video", "-v", help="Specific video ID")
    
    # Video info
    info_parser = subparsers.add_parser("info", help="Get video info")
    info_parser.add_argument("--url", "-u", required=True, help="YouTube URL")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize
    transcript = YouTubeTranscript()
    
    # Execute
    if args.command == "get":
        result = transcript.get_transcript(url=args.url, lang=args.lang)
        if result.get("success") and "transcript" in result:
            print(f"Language: {result.get('language')}")
            print(f"Available: {result.get('available_languages')}")
            print("\nTranscript:")
            print(result.get("full_text", "")[:2000])
    
    elif args.command == "get-all":
        result = transcript.get_all_transcripts(url=args.url)
    
    elif args.command == "download":
        result = transcript.download_transcript(
            url=args.url,
            format=args.format,
            output=args.output,
            lang=args.lang
        )
    
    elif args.command == "summarize":
        result = transcript.generate_summary(url=args.url, max_length=args.max_length)
    
    elif args.command == "list-cache":
        result = transcript.list_cache()
    
    elif args.command == "clear-cache":
        result = transcript.clear_cache(video_id=args.video)
    
    elif args.command == "info":
        result = transcript.get_video_info(url=args.url)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
