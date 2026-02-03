#!/usr/bin/env python3
"""
Upload Post Skill - Post to social media platforms
"""

import json
import sys
import os
import argparse
import requests
from typing import Dict, List, Optional
from datetime import datetime
import subprocess


class UploadPost:
    """Upload content to social media platforms"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or os.environ.get("UPLOAD_POST_API_KEY")
        self.api_url = api_url or os.environ.get(
            "UPLOAD_POST_API_URL", "https://api.upload-post.com/v1"
        )
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def _request(self, endpoint: str, method: str = "GET",
                 data: dict = None, files: dict = None) -> dict:
        """Make API request"""
        url = f"{self.api_url}/{endpoint}"
        
        try:
            if method == "GET":
                resp = self.session.get(url, params=data)
            elif method == "POST":
                if files:
                    resp = self.session.post(url, data=data, files=files)
                else:
                    resp = self.session.post(url, json=data)
            elif method == "DELETE":
                resp = self.session.delete(url, json=data)
            
            return resp.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    # Upload methods
    def upload_video(self, file_path: str, platforms: List[str],
                     title: str = None, description: str = None,
                     schedule_time: str = None, **kwargs) -> Dict:
        """Upload video to platforms"""
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}
        
        # Build request
        data = {
            "platforms": ",".join(platforms),
            "type": "video"
        }
        
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if schedule_time:
            data["scheduled_time"] = schedule_time
        
        # Add platform-specific options
        data.update(self._build_platform_options(kwargs))
        
        # Add file
        with open(file_path, "rb") as f:
            files = {"media": (os.path.basename(file_path), f, "video/mp4")}
            result = self._request("upload", "POST", data=data, files=files)
        
        if "error" not in result:
            return {
                "success": True,
                "post_id": result.get("id"),
                "platforms": platforms,
                "urls": result.get("urls", {}),
                "scheduled_time": schedule_time
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def upload_photo(self, file_path: str, platforms: List[str],
                     caption: str = None, **kwargs) -> Dict:
        """Upload photo to platforms"""
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}
        
        data = {
            "platforms": ",".join(platforms),
            "type": "photo"
        }
        
        if caption:
            data["caption"] = caption
        
        data.update(self._build_platform_options(kwargs))
        
        with open(file_path, "rb") as f:
            files = {"media": (os.path.basename(file_path), f, "image/jpeg")}
            result = self._request("upload", "POST", data=data, files=files)
        
        if "error" not in result:
            return {
                "success": True,
                "post_id": result.get("id"),
                "platforms": platforms,
                "urls": result.get("urls", {})
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def post_text(self, content: str, platforms: List[str],
                  **kwargs) -> Dict:
        """Post text to platforms"""
        data = {
            "platforms": ",".join(platforms),
            "type": "text",
            "content": content
        }
        
        data.update(self._build_platform_options(kwargs))
        result = self._request("upload", "POST", data=data)
        
        if "error" not in result:
            return {
                "success": True,
                "post_id": result.get("id"),
                "platforms": platforms,
                "urls": result.get("urls", {})
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def schedule_post(self, file_path: str, platforms: List[str],
                      schedule_time: str, title: str = None,
                      **kwargs) -> Dict:
        """Schedule a post"""
        return self.upload_video(
            file_path=file_path,
            platforms=platforms,
            title=title,
            schedule_time=schedule_time,
            **kwargs
        )
    
    def upload_history(self, limit: int = 50) -> Dict:
        """Get upload history"""
        result = self._request(f"uploads?limit={limit}")
        
        if "error" not in result:
            return {
                "success": True,
                "count": len(result.get("uploads", [])),
                "uploads": result.get("uploads", [])
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def get_post(self, post_id: str) -> Dict:
        """Get post details"""
        result = self._request(f"uploads/{post_id}")
        
        if "error" not in result:
            return {"success": True, "post": result}
        else:
            return {"success": False, "error": result.get("error")}
    
    def delete_post(self, post_id: str) -> Dict:
        """Delete a post"""
        result = self._request(f"uploads/{post_id}", "DELETE")
        
        if "error" not in result:
            return {"success": True, "message": "Post deleted"}
        else:
            return {"success": False, "error": result.get("error")}
    
    # Analytics
    def analytics(self, platform: str = None, days: int = 30) -> Dict:
        """Get analytics"""
        endpoint = f"analytics?days={days}"
        if platform:
            endpoint += f"&platform={platform}"
        
        result = self._request(endpoint)
        
        if "error" not in result:
            return {
                "success": True,
                "platform": platform,
                "period_days": days,
                "stats": result
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    # FFmpeg processing
    def process_video(self, input_file: str, output_file: str = None,
                      resize: str = None, compress: bool = False,
                      trim_start: str = None, trim_end: str = None,
                      convert: str = None, extract_audio: bool = False,
                      thumbnail: bool = False) -> Dict:
        """Process video with FFmpeg"""
        ffmpeg_path = os.environ.get("FFMPEG_PATH", "ffmpeg")
        
        if not os.path.exists(input_file):
            return {"success": False, "error": f"Input file not found: {input_file}"}
        
        if not output_file:
            output_file = f"processed_{os.path.basename(input_file)}"
        
        cmd = [ffmpeg_path, "-y", "-i", input_file]
        
        # Resize
        if resize:
            cmd.extend(["-vf", f"scale={resize}"])
        
        # Compress
        if compress:
            cmd.extend(["-vcodec", "libx264", "-crf", "28"])
        
        # Trim
        if trim_start:
            cmd.extend(["-ss", trim_start])
            if trim_end:
                cmd.extend(["-to", trim_end])
        
        # Convert
        if convert:
            output_file = f"{os.path.splitext(output_file)[0]}.{convert}"
        
        # Extract audio
        if extract_audio:
            output_file = f"{os.path.splitext(output_file)[0]}.mp3"
            cmd = [ffmpeg_path, "-y", "-i", input_file, "-vn", "-acodec", "libmp3lame", output_file]
        
        # Thumbnail
        if thumbnail:
            thumb_file = f"{os.path.splitext(output_file)[0]}.jpg"
            cmd = [ffmpeg_path, "-y", "-i", input_file, "-vframes", "1", thumb_file]
            subprocess.run(cmd, check=True)
            return {
                "success": True,
                "input": input_file,
                "thumbnail": thumb_file
            }
        
        cmd.append(output_file)
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return {
                "success": True,
                "input": input_file,
                "output": output_file
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}
    
    # Helper methods
    def _build_platform_options(self, kwargs: dict) -> dict:
        """Build platform-specific options"""
        options = {}
        
        # TikTok
        if kwargs.get("disable_comment"):
            options["tiktok_disable_comments"] = True
        if kwargs.get("duet_off"):
            options["tiktok_duet_off"] = True
        if kwargs.get("stitch_off"):
            options["tiktok_stitch_off"] = True
        
        # Instagram
        if kwargs.get("story"):
            options["instagram_type"] = "story"
        if kwargs.get("reel"):
            options["instagram_type"] = "reel"
        if kwargs.get("carousel"):
            options["instagram_type"] = "carousel"
        if kwargs.get("location"):
            options["instagram_location"] = kwargs["location"]
        
        # YouTube
        if kwargs.get("privacy"):
            options["youtube_privacy"] = kwargs["privacy"]
        if kwargs.get("playlist"):
            options["youtube_playlist"] = kwargs["playlist"]
        if kwargs.get("tags"):
            options["youtube_tags"] = ",".join(kwargs["tags"]) if isinstance(kwargs["tags"], list) else kwargs["tags"]
        
        # X (Twitter)
        if kwargs.get("thread"):
            options["twitter_thread"] = True
        
        return options
    
    def list_platforms(self) -> Dict:
        """List supported platforms"""
        return {
            "success": True,
            "platforms": [
                {"id": "tiktok", "name": "TikTok", "types": ["video", "photo", "text"]},
                {"id": "instagram", "name": "Instagram", "types": ["video", "photo", "text"]},
                {"id": "youtube", "name": "YouTube", "types": ["video", "text", "document"]},
                {"id": "twitter", "name": "X (Twitter)", "types": ["video", "photo", "text"]},
                {"id": "linkedin", "name": "LinkedIn", "types": ["video", "photo", "text", "document"]},
                {"id": "facebook", "name": "Facebook", "types": ["video", "photo", "text", "document"]},
                {"id": "threads", "name": "Threads", "types": ["photo", "text"]},
                {"id": "pinterest", "name": "Pinterest", "types": ["photo", "text"]},
                {"id": "reddit", "name": "Reddit", "types": ["video", "photo", "text"]},
                {"id": "bluesky", "name": "Bluesky", "types": ["text"]}
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="Upload Post Skill")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Video upload
    video_parser = subparsers.add_parser("video", help="Upload video")
    video_parser.add_argument("--file", "-f", required=True, help="Video file path")
    video_parser.add_argument("--platforms", "-p", required=True, help="Platforms (comma-separated)")
    video_parser.add_argument("--title", "-t", help="Video title")
    video_parser.add_argument("--description", "-d", help="Video description")
    video_parser.add_argument("--schedule", help="Schedule time (YYYY-MM-DD HH:MM:SS)")
    
    # Photo upload
    photo_parser = subparsers.add_parser("photo", help="Upload photo")
    photo_parser.add_argument("--file", "-f", required=True, help="Image file path")
    photo_parser.add_argument("--platforms", "-p", required=True, help="Platforms (comma-separated)")
    photo_parser.add_argument("--caption", "-c", help="Photo caption")
    
    # Text post
    text_parser = subparsers.add_parser("text", help="Post text")
    text_parser.add_argument("--content", required=True, help="Text content")
    text_parser.add_argument("--platforms", "-p", required=True, help="Platforms (comma-separated)")
    
    # Schedule
    schedule_parser = subparsers.add_parser("schedule", help="Schedule post")
    schedule_parser.add_argument("--file", "-f", help="File to upload")
    schedule_parser.add_argument("--platforms", "-p", required=True, help="Platforms")
    schedule_parser.add_argument("--schedule", "-s", required=True, help="Schedule time")
    schedule_parser.add_argument("--title", "-t", help="Title")
    
    # History
    history_parser = subparsers.add_parser("history", help="Upload history")
    history_parser.add_argument("--limit", "-l", type=int, default=50, help="Max results")
    
    # Analytics
    analytics_parser = subparsers.add_parser("analytics", help="Analytics")
    analytics_parser.add_argument("--platform", help="Specific platform")
    analytics_parser.add_argument("--days", type=int, default=30, help="Time period")
    analytics_parser.add_argument("--export", help="Export to file")
    
    # Process video
    process_parser = subparsers.add_parser("process", help="Process video with FFmpeg")
    process_parser.add_argument("--input", "-i", required=True, help="Input file")
    process_parser.add_argument("--output", "-o", help="Output file")
    process_parser.add_argument("--resize", "-r", help="Resize (WxH)")
    process_parser.add_argument("--compress", action="store_true", help="Compress")
    process_parser.add_argument("--trim", help="Trim (start:end)")
    process_parser.add_argument("--convert", help="Convert format")
    process_parser.add_argument("--extract-audio", action="store_true", help="Extract audio")
    process_parser.add_argument("--thumbnail", action="store_true", help="Generate thumbnail")
    
    # List platforms
    subparsers.add_parser("platforms", help="List supported platforms")
    
    # Get/Delete post
    post_parser = subparsers.add_parser("post", help="Post management")
    post_subparsers = post_parser.add_subparsers(dest="post_command")
    get_parser = post_subparsers.add_parser("get", help="Get post")
    get_parser.add_argument("--id", required=True, help="Post ID")
    del_parser = post_subparsers.add_parser("delete", help="Delete post")
    del_parser.add_argument("--id", required=True, help="Post ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize
    uploader = UploadPost()
    
    # Execute
    if args.command == "video":
        platforms = [p.strip() for p in args.platforms.split(",")]
        result = uploader.upload_video(
            file_path=args.file,
            platforms=platforms,
            title=args.title,
            description=args.description,
            schedule_time=args.schedule
        )
    
    elif args.command == "photo":
        platforms = [p.strip() for p in args.platforms.split(",")]
        result = uploader.upload_photo(
            file_path=args.file,
            platforms=platforms,
            caption=args.caption
        )
    
    elif args.command == "text":
        platforms = [p.strip() for p in args.platforms.split(",")]
        result = uploader.post_text(
            content=args.content,
            platforms=platforms
        )
    
    elif args.command == "schedule":
        platforms = [p.strip() for p in args.platforms.split(",")]
        result = uploader.schedule_post(
            file_path=args.file,
            platforms=platforms,
            schedule_time=args.schedule,
            title=args.title
        )
    
    elif args.command == "history":
        result = uploader.upload_history(limit=args.limit)
    
    elif args.command == "analytics":
        result = uploader.analytics(platform=args.platform, days=args.days)
        if args.export and result["success"]:
            with open(args.export, "w") as f:
                json.dump(result, f, indent=2)
    
    elif args.command == "process":
        trim_start = None
        trim_end = None
        if args.trim and ":" in args.trim:
            parts = args.trim.split(":")
            trim_start = parts[0]
            trim_end = parts[1] if len(parts) > 1 else None
        
        result = uploader.process_video(
            input_file=args.input,
            output_file=args.output,
            resize=args.resize,
            compress=args.compress,
            trim_start=trim_start,
            trim_end=trim_end,
            convert=args.convert,
            extract_audio=args.extract_audio,
            thumbnail=args.thumbnail
        )
    
    elif args.command == "platforms":
        result = uploader.list_platforms()
    
    elif args.command == "post":
        if args.post_command == "get":
            result = uploader.get_post(args.id)
        elif args.post_command == "delete":
            result = uploader.delete_post(args.id)
        else:
            post_parser.print_help()
            sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
