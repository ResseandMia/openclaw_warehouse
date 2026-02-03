#!/usr/bin/env python3
"""
WeChat OA Channel - Official Account Draft Box Management Tool
"""

import json
import sys
import argparse
import requests
from typing import Dict, List, Optional
from datetime import datetime

# Configuration
DEFAULT_API_BASE = "https://api.weixin.qq.com"


class WeChatOAChannel:
    """WeChat Official Account Channel Management"""
    
    def __init__(self, app_id: str = None, app_secret: str = None, 
                 access_token: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.api_base = DEFAULT_API_BASE
    
    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token:
            return self.access_token
        
        if not self.app_id or not self.app_secret:
            raise ValueError("Missing WECHAT_APP_ID or WECHAT_APP_SECRET")
        
        url = f"{self.api_base}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if data.get("errcode") == 0:
            self.access_token = data["access_token"]
            return self.access_token
        else:
            raise Exception(f"Failed to get access_token: {data}")
    
    def _call_api(self, endpoint: str, method: str = "POST", 
                  data: dict = None) -> dict:
        """Make API call to WeChat"""
        token = self._get_access_token()
        url = f"{self.api_base}/cgi-bin/{endpoint}"
        params = {"access_token": token}
        
        if method == "GET":
            resp = requests.get(url, params=params)
        else:
            resp = requests.post(url, params=params, json=data)
        
        return resp.json()
    
    def create_draft(self, title: str, content: str, 
                     author: str = None, thumb_media_id: str = None,
                     digest: str = None, need_open_comment: int = 0,
                     only_fans_can_comment: int = 0) -> Dict:
        """Create a graphic draft article"""
        
        # Auto-extract digest from first paragraph if not provided
        if not digest and content:
            first_para = content.strip().split('\n')[0][:120]
            digest = first_para
        
        data = {
            "articles": [{
                "title": title,
                "thumb_media_id": thumb_media_id,
                "author": author or "",
                "digest": digest or "",
                "show_cover_pic": 1,
                "content": content,
                "need_open_comment": need_open_comment,
                "only_fans_can_comment": only_fans_can_comment
            }]
        }
        
        result = self._call_api("draft/add", data=data)
        
        if result.get("errcode") == 0:
            return {
                "success": True,
                "media_id": result.get("media_id"),
                "message": "草稿创建成功"
            }
        else:
            return {
                "success": False,
                "error": result.get("errmsg"),
                "errcode": result.get("errcode")
            }
    
    def list_drafts(self, offset: int = 0, count: int = 20) -> Dict:
        """List all draft articles"""
        data = {
            "offset": offset,
            "count": count,
            "no_content": 0  # Include content
        }
        
        result = self._call_api("draft/list", data=data)
        
        if result.get("errcode") == 0:
            items = result.get("item", [])
            drafts = []
            for item in items:
                drafts.append({
                    "id": item.get("media_id"),
                    "title": item.get("content", {}).get("news_item", [{}])[0].get("title"),
                    "author": item.get("content", {}).get("news_item", [{}])[0].get("author"),
                    "digest": item.get("content", {}).get("news_item", [{}])[0].get("digest"),
                    "update_time": datetime.fromtimestamp(item.get("update_time")).isoformat()
                })
            
            return {
                "success": True,
                "total_count": result.get("total_count"),
                "drafts": drafts
            }
        else:
            return {
                "success": False,
                "error": result.get("errmsg")
            }
    
    def publish_draft(self, media_id: str) -> Dict:
        """Publish a draft article"""
        data = {"media_id": media_id}
        
        result = self._call_api("draft/publish", data=data)
        
        if result.get("errcode") == 0:
            return {
                "success": True,
                "msg_id": result.get("msg_id"),
                "message": "草稿发布成功"
            }
        else:
            return {
                "success": False,
                "error": result.get("errmsg")
            }
    
    def delete_draft(self, media_id: str) -> Dict:
        """Delete a draft"""
        data = {"media_id": media_id}
        
        result = self._call_api("draft/delete", data=data)
        
        if result.get("errcode") == 0:
            return {
                "success": True,
                "message": "草稿删除成功"
            }
        else:
            return {
                "success": False,
                "error": result.get("errmsg")
            }
    
    def upload_image(self, file_path: str) -> Dict:
        """Upload image to WeChat"""
        url = f"{self.api_base}/cgi-bin/media/uploadimg"
        token = self._get_access_token()
        
        with open(file_path, 'rb') as f:
            files = {'media': (file_path, f, 'image/jpeg')}
            params = {'access_token': token, 'type': 'image'}
            resp = requests.post(url, params=params, files=files)
        
        result = resp.json()
        
        if result.get("errcode") == 0:
            return {
                "success": True,
                "url": result.get("url"),
                "media_id": result.get("media_id")
            }
        else:
            return {
                "success": False,
                "error": result.get("errmsg")
            }


def main():
    parser = argparse.ArgumentParser(description="WeChat OA Channel Management")
    parser.add_argument("command", choices=["create", "list", "publish", "delete", "upload"],
                        help="Command to execute")
    parser.add_argument("--title", "-t", help="Article title")
    parser.add_argument("--content", "-c", help="Article content")
    parser.add_argument("--file", "-f", help="File containing article content")
    parser.add_argument("--author", "-a", help="Article author")
    parser.add_argument("--cover", help="Cover image URL or media_id")
    parser.add_argument("--id", help="Draft media_id")
    parser.add_argument("--offset", type=int, default=0, help="Offset for list")
    parser.add_argument("--count", type=int, default=20, help="Count for list")
    parser.add_argument("--app-id", help="WeChat App ID")
    parser.add_argument("--app-secret", help="WeChat App Secret")
    parser.add_argument("--token", help="Access token (optional)")
    
    args = parser.parse_args()
    
    # Initialize channel
    channel = WeChatOAChannel(
        app_id=args.app_id,
        app_secret=args.app_secret,
        access_token=args.token
    )
    
    # Execute command
    if args.command == "create":
        content = args.content
        if args.file:
            with open(args.file, 'r') as f:
                content = f.read()
        
        if not content:
            print("Error: Content required (--content or --file)")
            sys.exit(1)
        
        result = channel.create_draft(
            title=args.title or "Untitled",
            content=content,
            author=args.author
        )
        
    elif args.command == "list":
        result = channel.list_drafts(offset=args.offset, count=args.count)
        
    elif args.command == "publish":
        if not args.id:
            print("Error: Draft ID required (--id)")
            sys.exit(1)
        result = channel.publish_draft(args.id)
        
    elif args.command == "delete":
        if not args.id:
            print("Error: Draft ID required (--id)")
            sys.exit(1)
        result = channel.delete_draft(args.id)
        
    elif args.command == "upload":
        if not args.file:
            print("Error: File path required (--file)")
            sys.exit(1)
        result = channel.upload_image(args.file)
    
    # Print result
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
