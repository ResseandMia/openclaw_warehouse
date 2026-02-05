#!/usr/bin/env python3
"""
AI 日程管家 - 任务管理
用法:
  python3 todo_manager.py add "任务名称" [--date 2026-02-04] [--priority 高|中|低]
  python3 todo_manager.py list [--date 2026-02-04]
  python3 todo_manager.py today
"""

import json
import sys
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/skills/notion-api-skill/scripts')
from notion import NotionAPI

CONFIG_FILE = "/root/.openclaw/workspace/config.json"
TODO_DB_ID = "2fd83d24-986d-810e-b00b-dfcfa9e53935"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def add_todo(title: str, date: str = None, priority: str = "中", note: str = ""):
    """添加待办事项到 Notion 数据库"""
    config = load_config()
    notion = NotionAPI(api_key=config["notion"]["api_key"])
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    data = {
        "parent": {"database_id": TODO_DB_ID},
        "properties": {
            "名称": {
                "title": [{"text": {"content": title}}]
            },
            "日期": {
                "date": {"start": date}
            },
            "状态": {
                "select": {"name": "待办"}
            },
            "优先级": {
                "select": {"name": priority}
            }
        }
    }
    
    if note:
        data["properties"]["备注"] = {"rich_text": [{"text": {"content": note}}]}
    
    result = notion._request("POST", "/pages", data)
    return result

def query_todos(date: str = None):
    """查询待办事项"""
    config = load_config()
    notion = NotionAPI(api_key=config["notion"]["api_key"])
    
    # 查询所有，然后用 Python 过滤
    result = notion._request("POST", f"/databases/{TODO_DB_ID}/query", {})
    
    if result.get("object") == "error":
        return {"success": False, "error": result.get("message")}
    
    items = result.get("results", [])
    
    # 按日期过滤
    if date:
        items = [i for i in items if i.get("properties", {}).get("日期", {}).get("date", {}).get("start", "").startswith(date)]
    
    return {"success": True, "results": items}

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 todo_manager.py add '任务名称' [--date 2026-02-04] [--priority 高|中|低]")
        print("  python3 todo_manager.py today")
        print("  python3 todo_manager.py all")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        if not title:
            print("请输入任务名称")
            return
        
        date = datetime.now().strftime("%Y-%m-%d")
        priority = "中"
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--date" and i+1 < len(sys.argv):
                date = sys.argv[i+1]
                i += 2
            elif sys.argv[i] == "--priority" and i+1 < len(sys.argv):
                priority = sys.argv[i+1]
                i += 2
            else:
                i += 1
        
        result = add_todo(title, date, priority)
        if result.get("object") == "page":
            print(f"✅ 已添加: {title} ({date}) [{priority}]")
        else:
            print(f"❌ 添加失败: {result}")
    
    elif command == "today":
        date = datetime.now().strftime("%Y-%m-%d")
        result = query_todos(date)
        
        if result.get("success"):
            items = result.get("results", [])
            print(f"\n📋 {date} 的待办事项 ({len(items)} 个):")
            
            # 按优先级分组
            high = [i for i in items if i.get("properties", {}).get("优先级", {}).get("select", {}).get("name") == "高"]
            medium = [i for i in items if i.get("properties", {}).get("优先级", {}).get("select", {}).get("name") == "中"]
            low = [i for i in items if i.get("properties", {}).get("优先级", {}).get("select", {}).get("name") == "低"]
            
            for title in [i.get("properties", {}).get("名称", {}).get("title", [{}])[0].get("plain_text", "") for i in high]:
                print(f"  🔴 {title}")
            for title in [i.get("properties", {}).get("名称", {}).get("title", [{}])[0].get("plain_text", "") for i in medium]:
                print(f"  🟡 {title}")
            for title in [i.get("properties", {}).get("名称", {}).get("title", [{}])[0].get("plain_text", "") for i in low]:
                print(f"  🔵 {title}")
        else:
            print(f"❌ 获取失败: {result.get('error')}")
    
    elif command == "all":
        result = query_todos()
        
        if result.get("success"):
            items = result.get("results", [])
            print(f"\n📋 所有待办事项 ({len(items)} 个):")
            for item in items[:10]:
                props = item.get("properties", {})
                title = props.get("名称", {}).get("title", [{}])[0].get("plain_text", "")
                date = props.get("日期", {}).get("date", {}).get("start", "")[:10]
                status = props.get("状态", {}).get("select", {}).get("name", "")
                emoji = {"已完成": "✅", "进行中": "🔄", "待办": "⏳"}.get(status, "⚪")
                print(f"  {emoji} {title} ({date})")
        else:
            print(f"❌ 获取失败: {result.get('error')}")
    
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()
