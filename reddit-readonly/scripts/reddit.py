#!/usr/bin/env python3
"""
Reddit (Read-Only) - Browse and search Reddit without authentication
"""

import json
import sys
import argparse
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
import requests

# Reddit API base
REDDIT_BASE = "https://www.reddit.com"

# Rate limiting
DEFAULT_DELAY = 1.0  # seconds between requests


class RedditReadOnly:
    """Reddit read-only client using public JSON endpoints"""
    
    def __init__(self, user_agent: str = None):
        # Use a realistic browser user agent
        if not user_agent:
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
    
    def _request(self, url: str, params: dict = None) -> Optional[dict]:
        """Make GET request with rate limiting"""
        try:
            time.sleep(DEFAULT_DELAY)
            
            resp = self.session.get(url, params=params, timeout=10)
            
            if resp.status_code == 429:
                # Rate limited
                retry_after = int(resp.headers.get("Retry-After", 60))
                print(f"Rate limited. Waiting {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after)
                return self._request(url, params)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"error": f"HTTP {resp.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_posts(self, data: dict) -> List[dict]:
        """Extract posts from Reddit API response"""
        posts = []
        
        try:
            children = data.get("data", {}).get("children", [])
            for child in children:
                post = child.get("data", {})
                posts.append({
                    "id": post.get("id"),
                    "title": post.get("title"),
                    "author": post.get("author"),
                    "subreddit": post.get("subreddit"),
                    "score": post.get("score"),
                    "ups": post.get("ups"),
                    "downs": post.get("downs"),
                    "num_comments": post.get("num_comments"),
                    "permalink": f"https://reddit.com{post.get('permalink')}",
                    "url": post.get("url"),
                    "selftext": post.get("selftext", "")[:500],
                    "created_utc": datetime.fromtimestamp(post.get("created_utc", 0)).isoformat(),
                    "domain": post.get("domain"),
                    "is_self": post.get("is_self"),
                    "flair": post.get("link_flair_text")
                })
        except Exception as e:
            print(f"Error extracting posts: {e}", file=sys.stderr)
        
        return posts
    
    def _extract_comments(self, data: List[dict]) -> List[dict]:
        """Extract comments from Reddit API response"""
        comments = []
        
        try:
            # Comments are in the second element of the list
            comment_data = data[1].get("data", {}).get("children", []) if len(data) > 1 else []
            
            for child in comment_data:
                if child.get("kind") == "t1":  # Comment
                    c = child.get("data", {})
                    comments.append({
                        "id": c.get("id"),
                        "author": c.get("author"),
                        "body": c.get("body", "")[:1000],
                        "score": c.get("score"),
                        "ups": c.get("ups"),
                        "downs": c.get("downs"),
                        "replies_count": c.get("replies", "").count('"kind":"t1"'),
                        "created_utc": datetime.fromtimestamp(c.get("created_utc", 0)).isoformat(),
                        "permalink": f"https://reddit.com{c.get('permalink')}",
                        "is_op": c.get("distinguished") == "op"
                    })
        except Exception as e:
            print(f"Error extracting comments: {e}", file=sys.stderr)
        
        return comments
    
    def listing(self, subreddit: str, sort: str = "hot", 
                limit: int = 25, time_filter: str = None) -> Dict:
        """Get posts from a subreddit"""
        subreddit = subreddit.lstrip('/r/').rstrip('/')
        
        # Build URL
        if sort in ["hot", "new", "rising", "controversial"]:
            url = f"{REDDIT_BASE}/r/{subreddit}/{sort}.json"
        elif sort == "top":
            url = f"{REDDIT_BASE}/r/{subreddit}/top.json"
            if time_filter:
                url += f"?t={time_filter}"
        else:
            url = f"{REDDIT_BASE}/r/{subreddit}/hot.json"
        
        params = {"limit": min(limit, 100)}
        
        data = self._request(url, params)
        
        if data and "error" not in data:
            posts = self._extract_posts(data)
            return {
                "success": True,
                "subreddit": subreddit,
                "sort": sort,
                "count": len(posts),
                "posts": posts
            }
        else:
            return {
                "success": False,
                "error": data.get("error") if data else "Unknown error",
                "subreddit": subreddit
            }
    
    def search(self, query: str, subreddit: str = None, 
               sort: str = "relevance", limit: int = 25) -> Dict:
        """Search for posts"""
        params = {
            "q": query,
            "limit": min(limit, 100),
            "sort": sort,
            "restrict_sr": "true" if subreddit else "false"
        }
        
        if subreddit:
            subreddit = subreddit.lstrip('/r/').rstrip('/')
            url = f"{REDDIT_BASE}/r/{subreddit}/search.json"
        else:
            url = f"{REDDIT_BASE}/search.json"
        
        data = self._request(url, params)
        
        if data and "error" not in data:
            posts = self._extract_posts(data)
            return {
                "success": True,
                "query": query,
                "subreddit": subreddit,
                "count": len(posts),
                "posts": posts
            }
        else:
            return {
                "success": False,
                "error": data.get("error") if data else "Unknown error"
            }
    
    def comments(self, post_id: str, sort: str = "best", 
                 limit: int = 100) -> Dict:
        """Get comments for a post"""
        post_id = post_id.lstrip('/')
        
        url = f"{REDDIT_BASE}/r/all/comments/{post_id}.json"
        params = {"sort": sort, "limit": min(limit, 100)}
        
        data = self._request(url, params)
        
        if data and "error" not in data:
            if isinstance(data, list):
                comments = self._extract_comments(data)
                return {
                    "success": True,
                    "post_id": post_id,
                    "count": len(comments),
                    "comments": comments
                }
            else:
                return {
                    "success": False,
                    "error": "Unexpected response format"
                }
        else:
            return {
                "success": False,
                "error": data.get("error") if data else "Unknown error"
            }
    
    def shortlist(self, subreddit: str, limit: int = 10, 
                  sort: str = "hot") -> Dict:
        """Build a shortlist of permalinks"""
        result = self.listing(subreddit, sort=sort, limit=limit)
        
        if result["success"]:
            shortlist = []
            for post in result["posts"][:limit]:
                shortlist.append({
                    "title": post["title"],
                    "permalink": post["permalink"],
                    "score": post["score"],
                    "comments": post["num_comments"]
                })
            
            return {
                "success": True,
                "subreddit": subreddit,
                "shortlist": shortlist
            }
        else:
            return result
    
    def multi_search(self, subreddits: List[str], query: str = None,
                     limit: int = 10) -> Dict:
        """Search across multiple subreddits"""
        all_posts = []
        
        for sub in subreddits:
            if query:
                result = self.search(query, subreddit=sub, limit=limit)
            else:
                result = self.listing(subreddit=sub, limit=limit)
            
            if result["success"]:
                all_posts.extend(result["posts"])
        
        # Sort by score
        all_posts.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return {
            "success": True,
            "subreddits": subreddits,
            "query": query,
            "count": len(all_posts),
            "posts": all_posts[:limit * len(subreddits)]
        }


def main():
    parser = argparse.ArgumentParser(description="Reddit Read-Only Client")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Listing command
    list_parser = subparsers.add_parser("listing", help="List subreddit posts")
    list_parser.add_argument("--subreddit", "-s", required=True, help="Subreddit name")
    list_parser.add_argument("--sort", choices=["hot", "new", "rising", "top", "controversial"],
                             default="hot", help="Sort method")
    list_parser.add_argument("--limit", "-l", type=int, default=25, help="Number of posts")
    list_parser.add_argument("--time", choices=["hour", "day", "week", "month", "year", "all"],
                             help="Time filter for top posts")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search posts")
    search_parser.add_argument("--query", "-q", required=True, help="Search query")
    search_parser.add_argument("--subreddit", "-s", help="Limit to subreddit")
    search_parser.add_argument("--sort", default="relevance", help="Sort method")
    search_parser.add_argument("--limit", "-l", type=int, default=25)
    
    # Comments command
    comments_parser = subparsers.add_parser("comments", help="Get post comments")
    comments_parser.add_argument("--post-id", "-p", required=True, help="Post ID")
    comments_parser.add_argument("--sort", default="best", help="Sort method")
    comments_parser.add_argument("--limit", "-l", type=int, default=100)
    
    # Shortlist command
    shortlist_parser = subparsers.add_parser("shortlist", help="Build permalink shortlist")
    shortlist_parser.add_argument("--subreddit", "-s", required=True, help="Subreddit name")
    shortlist_parser.add_argument("--sort", default="hot", help="Sort method")
    shortlist_parser.add_argument("--limit", "-l", type=int, default=10)
    
    # Multi search command
    multi_parser = subparsers.add_parser("multi", help="Search multiple subreddits")
    multi_parser.add_argument("--subreddits", required=True, help="Comma-separated subreddits")
    multi_parser.add_argument("--query", "-q", help="Search query")
    multi_parser.add_argument("--limit", "-l", type=int, default=10)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize client
    reddit = RedditReadOnly()
    
    # Execute command
    if args.command == "listing":
        result = reddit.listing(
            subreddit=args.subreddit,
            sort=args.sort,
            limit=args.limit,
            time_filter=args.time
        )
    
    elif args.command == "search":
        result = reddit.search(
            query=args.query,
            subreddit=args.subreddit,
            sort=args.sort,
            limit=args.limit
        )
    
    elif args.command == "comments":
        result = reddit.comments(
            post_id=args.post_id,
            sort=args.sort,
            limit=args.limit
        )
    
    elif args.command == "shortlist":
        result = reddit.shortlist(
            subreddit=args.subreddit,
            sort=args.sort,
            limit=args.limit
        )
    
    elif args.command == "multi":
        subs = [s.strip() for s in args.subreddits.split(",")]
        result = reddit.multi_search(
            subreddits=subs,
            query=args.query,
            limit=args.limit
        )
    
    # Print result
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
