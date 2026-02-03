#!/usr/bin/env python3
"""
Notion API Skill - Interact with Notion workspaces
"""

import json
import sys
import argparse
import requests
from typing import Dict, List, Optional
from datetime import datetime

# API base
NOTION_API_BASE = "https://api.notion.com/v1"

# Default headers
DEFAULT_HEADERS = {
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}


class NotionAPI:
    """Notion API client with OAuth and token support"""
    
    def __init__(self, api_key: str = None, oauth_token: str = None):
        self.api_key = api_key
        self.oauth_token = oauth_token
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
    
    def _get_headers(self) -> Dict:
        """Get headers with auth"""
        headers = DEFAULT_HEADERS.copy()
        if self.oauth_token:
            headers["Authorization"] = f"Bearer {self.oauth_token}"
        elif self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _request(self, method: str, endpoint: str, 
                 data: dict = None) -> dict:
        """Make API request"""
        url = f"{NOTION_API_BASE}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method == "GET":
                resp = self.session.get(url, headers=headers)
            elif method == "POST":
                resp = self.session.post(url, headers=headers, json=data)
            elif method == "PATCH":
                resp = self.session.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                resp = self.session.delete(url, headers=headers)
            
            return resp.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    def list_databases(self) -> Dict:
        """List all accessible databases"""
        result = self._request("POST", "/search", {
            "filter": {"property": "object", "value": "database"},
            "page_size": 100
        })
        
        if "error" not in result:
            databases = []
            for item in result.get("results", []):
                databases.append({
                    "id": item.get("id"),
                    "title": self._extract_title(item.get("title", [])),
                    "created_time": item.get("created_time"),
                    "last_edited_time": item.get("last_edited_time")
                })
            
            return {
                "success": True,
                "count": len(databases),
                "databases": databases
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def query_database(self, database_id: str, 
                       filter_obj: dict = None,
                       sorts: list = None) -> Dict:
        """Query database contents"""
        endpoint = f"/databases/{database_id}/query"
        
        data = {}
        if filter_obj:
            data["filter"] = filter_obj
        if sorts:
            data["sorts"] = sorts
        
        result = self._request("POST", endpoint, data if data else None)
        
        if "error" not in result:
            results = []
            for item in result.get("results", []):
                results.append({
                    "id": item.get("id"),
                    "created_time": item.get("created_time"),
                    "last_edited_time": item.get("last_edited_time"),
                    "properties": self._extract_properties(item.get("properties", {}))
                })
            
            return {
                "success": True,
                "database_id": database_id,
                "count": len(results),
                "results": results
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def get_database(self, database_id: str) -> Dict:
        """Get database structure and data sources"""
        result = self._request("GET", f"/databases/{database_id}")
        
        if "error" not in result:
            return {
                "success": True,
                "id": result.get("id"),
                "title": self._extract_title(result.get("title", [])),
                "properties": self._extract_properties(result.get("properties", {})),
                "data_sources": result.get("data_sources", []),
                "created_time": result.get("created_time"),
                "last_edited_time": result.get("last_edited_time")
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def get_page(self, page_id: str) -> Dict:
        """Get page content"""
        result = self._request("GET", f"/pages/{page_id}")
        
        if "error" not in result:
            return {
                "success": True,
                "id": result.get("id"),
                "created_time": result.get("created_time"),
                "last_edited_time": result.get("last_edited_time"),
                "archived": result.get("archived"),
                "properties": self._extract_properties(result.get("properties", {})),
                "parent": result.get("parent")
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def get_page_content(self, page_id: str) -> Dict:
        """Get page blocks (content)"""
        result = self._request("GET", f"/blocks/{page_id}/children")
        
        if "error" not in result:
            blocks = []
            for block in result.get("results", []):
                blocks.append({
                    "id": block.get("id"),
                    "type": block.get("type"),
                    "content": self._extract_block_content(block)
                })
            
            return {
                "success": True,
                "page_id": page_id,
                "count": len(blocks),
                "blocks": blocks
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def create_page(self, parent_id: str, title: str, 
                    content: str = None, properties: dict = None) -> Dict:
        """Create a new page"""
        # Build content blocks
        blocks = []
        if content:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            })
        
        data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        }
        
        if blocks:
            data["children"] = blocks
        
        result = self._request("POST", "/pages", data)
        
        if "error" not in result:
            return {
                "success": True,
                "id": result.get("id"),
                "url": result.get("url"),
                "message": "Page created successfully"
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def update_page(self, page_id: str, properties: dict = None,
                    icon: str = None, cover: str = None) -> Dict:
        """Update page properties"""
        data = {}
        
        if properties:
            data["properties"] = properties
        if icon:
            data["icon"] = {"type": "emoji", "emoji": icon}
        if cover:
            data["cover"] = {"type": "external", "external": {"url": cover}}
        
        result = self._request("PATCH", f"/pages/{page_id}", data)
        
        if "error" not in result:
            return {
                "success": True,
                "id": result.get("id"),
                "message": "Page updated successfully"
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def add_block(self, page_id: str, block_type: str, 
                  content: str, after: str = None) -> Dict:
        """Add a block to a page"""
        block_content = self._build_block(block_type, content)
        
        if not block_content:
            return {"success": False, "error": f"Unknown block type: {block_type}"}
        
        data = {"children": [block_content]}
        
        # Add after specific block
        if after:
            endpoint = f"/blocks/{after}/children"
        else:
            endpoint = f"/blocks/{page_id}/children"
        
        result = self._request("POST", endpoint, data)
        
        if "error" not in result:
            return {
                "success": True,
                "block_id": result.get("id"),
                "message": "Block added successfully"
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    def delete_block(self, block_id: str) -> Dict:
        """Delete a block"""
        result = self._request("DELETE", f"/blocks/{block_id}")
        
        if "error" not in result:
            return {"success": True, "message": "Block deleted"}
        else:
            return {"success": False, "error": result.get("error")}
    
    def list_connections(self) -> Dict:
        """List workspace connections"""
        result = self._request("GET", "/connections")
        
        if "error" not in result:
            connections = []
            for conn in result.get("results", []):
                connections.append({
                    "id": conn.get("id"),
                    "name": conn.get("name"),
                    "type": conn.get("type"),
                    "created_time": conn.get("created_time")
                })
            
            return {
                "success": True,
                "count": len(connections),
                "connections": connections
            }
        else:
            return {"success": False, "error": result.get("error")}
    
    # Helper methods
    def _extract_title(self, title_array: List[dict]) -> str:
        """Extract title text from array"""
        if not title_array:
            return ""
        return "".join([t.get("plain_text", "") for t in title_array])
    
    def _extract_properties(self, props: dict) -> dict:
        """Extract simplified properties"""
        simplified = {}
        for key, prop in props.items():
            prop_type = prop.get("type")
            if prop_type == "title":
                simplified[key] = self._extract_title(prop.get("title", []))
            elif prop_type == "rich_text":
                simplified[key] = "".join([t.get("plain_text", "") 
                                           for t in prop.get("rich_text", [])])
            elif prop_type == "number":
                simplified[key] = prop.get("number")
            elif prop_type == "select":
                simplified[key] = prop.get("select", {}).get("name")
            elif prop_type == "multi_select":
                simplified[key] = [s.get("name") for s in prop.get("multi_select", [])]
            elif prop_type == "checkbox":
                simplified[key] = prop.get("checkbox")
            elif prop_type == "date":
                simplified[key] = prop.get("date", {}).get("start")
            elif prop_type == "url":
                simplified[key] = prop.get("url")
            else:
                simplified[key] = f"<{prop_type}>"
        return simplified
    
    def _extract_block_content(self, block: dict) -> str:
        """Extract block content as text"""
        block_type = block.get("type")
        content = block.get(block_type, {})
        
        if "rich_text" in content:
            return "".join([t.get("plain_text", "") for t in content.get("rich_text", [])])
        elif "text" in content:
            return content.get("text", {}).get("content", "")
        elif "url" in content:
            return content.get("url")
        else:
            return ""
    
    def _build_block(self, block_type: str, content: str) -> dict:
        """Build a block from type and content"""
        rich_text = [{"type": "text", "text": {"content": content}}]
        
        block_map = {
            "paragraph": {"paragraph": {"rich_text": rich_text}},
            "heading_1": {"heading_1": {"rich_text": rich_text}},
            "heading_2": {"heading_2": {"rich_text": rich_text}},
            "heading_3": {"heading_3": {"rich_text": rich_text}},
            "bullet_list_item": {"bullet_list_item": {"rich_text": rich_text}},
            "numbered_list_item": {"numbered_list_item": {"rich_text": rich_text}},
            "to_do": {"to_do": {"rich_text": rich_text, "checked": False}},
            "toggle": {"toggle": {"rich_text": rich_text}},
            "quote": {"quote": {"rich_text": rich_text}},
            "divider": {"divider": {}},
            "callout": {"callout": {"rich_text": rich_text, "icon": {"emoji": "💡"}}},
            "code": {"code": {"rich_text": rich_text, "language": "plain text"}},
        }
        
        if block_type in block_map:
            return {"object": "block", "type": block_type, **block_map[block_type]}
        return None


def main():
    parser = argparse.ArgumentParser(description="Notion API Skill")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List databases
    subparsers.add_parser("list-databases", help="List all databases")
    
    # Query database
    query_parser = subparsers.add_parser("query-database", help="Query database")
    query_parser.add_argument("--id", required=True, help="Database ID")
    
    # Get database
    db_parser = subparsers.add_parser("get-database", help="Get database structure")
    db_parser.add_argument("--id", required=True, help="Database ID")
    
    # Get page
    page_parser = subparsers.add_parser("get-page", help="Get page")
    page_parser.add_argument("--id", required=True, help="Page ID")
    
    # Get page content
    content_parser = subparsers.add_parser("get-content", help="Get page blocks")
    content_parser.add_argument("--id", required=True, help="Page ID")
    
    # Create page
    create_parser = subparsers.add_parser("create-page", help="Create page")
    create_parser.add_argument("--parent-id", required=True, help="Parent page ID")
    create_parser.add_argument("--title", "-t", required=True, help="Page title")
    create_parser.add_argument("--content", "-c", help="Page content")
    
    # Update page
    update_parser = subparsers.add_parser("update-page", help="Update page")
    update_parser.add_argument("--id", required=True, help="Page ID")
    update_parser.add_argument("--title", "-t", help="New title")
    update_parser.add_argument("--icon", help="Emoji icon")
    update_parser.add_argument("--cover", help="Cover image URL")
    
    # Add block
    block_parser = subparsers.add_parser("add-block", help="Add block")
    block_parser.add_argument("--page-id", required=True, help="Page ID")
    block_parser.add_argument("--type", required=True, 
                              help="Block type (paragraph, heading_1, etc.)")
    block_parser.add_argument("--content", "-c", required=True, help="Block content")
    block_parser.add_argument("--after", help="Insert after block ID")
    
    # Delete block
    del_parser = subparsers.add_parser("delete-block", help="Delete block")
    del_parser.add_argument("--id", required=True, help="Block ID")
    
    # List connections
    subparsers.add_parser("list-connections", help="List connections")
    
    # Auth
    auth_parser = subparsers.add_parser("auth", help="OAuth setup")
    auth_parser.add_argument("--client-id", help="Notion Client ID")
    auth_parser.add_argument("--client-secret", help="Notion Client Secret")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize
    notion = NotionAPI()
    
    # Execute
    if args.command == "list-databases":
        result = notion.list_databases()
    
    elif args.command == "query-database":
        result = notion.query_database(args.id)
    
    elif args.command == "get-database":
        result = notion.get_database(args.id)
    
    elif args.command == "get-page":
        result = notion.get_page(args.id)
    
    elif args.command == "get-content":
        result = notion.get_page_content(args.id)
    
    elif args.command == "create-page":
        result = notion.create_page(
            parent_id=args.parent_id,
            title=args.title,
            content=args.content
        )
    
    elif args.command == "update-page":
        result = notion.update_page(
            page_id=args.id,
            icon=args.icon,
            cover=args.cover
        )
    
    elif args.command == "add-block":
        result = notion.add_block(
            page_id=args.page_id,
            block_type=args.type,
            content=args.content,
            after=args.after
        )
    
    elif args.command == "delete-block":
        result = notion.delete_block(args.id)
    
    elif args.command == "list-connections":
        result = notion.list_connections()
    
    elif args.command == "auth":
        print("""
Notion OAuth Setup:
1. Go to https://www.notion.so/my-integrations
2. Create new integration
3. Copy Client ID and Client Secret
4. Use with: python3 scripts/notion.py auth --client-id XXX --client-secret XXX
        """)
        result = {"success": True}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
