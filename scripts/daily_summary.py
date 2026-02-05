#!/usr/bin/env python3
"""
每日复盘同步到 Notion
每天晚上 12:00 (北京时间) 执行

功能：
- 读取当天的 memory/*.md 文件
- 提取执行内容、错误、经验
- 同步到 Notion
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/skills/notion-api-skill/scripts')
from notion import NotionAPI

CONFIG_FILE = "/root/.openclaw/workspace/config.json"
MEMORY_DIR = "/root/.openclaw/workspace/memory"
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_FILE = f"{MEMORY_DIR}/{TODAY}.md"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_today_memory():
    """读取今天 memory 文件"""
    if os.path.exists(TODAY_FILE):
        with open(TODAY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def parse_memory(content):
    """解析 memory 内容，提取关键信息"""
    if not content:
        return None
    
    sections = {
        "完成的任务": [],
        "犯的错误": [],
        "经验教训": [],
        "待办": []
    }
    
    current_section = None
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        # 检测章节
        if line.startswith("## ") or line.startswith("### "):
            current_section = None
            if "完成" in line:
                current_section = "完成的任务"
            elif "错误" in line or "问题" in line:
                current_section = "犯的错误"
            elif "经验" in line or "教训" in line:
                current_section = "经验教训"
            elif "待办" in line:
                current_section = "待办"
        
        # 提取列表项
        if current_section and (line.startswith("- ") or line.startswith("* ")):
            sections[current_section].append(line[2:])
    
    return sections

def sync_to_notion(sections):
    """同步到 Notion"""
    config = load_config()
    notion = NotionAPI(api_key=config["notion"]["api_key"])
    
    # 构建内容
    lines = [f"## {TODAY} 每日复盘\n"]
    
    if sections.get("完成的任务"):
        lines.append("\n### ✅ 完成的任务")
        for item in sections["完成的任务"]:
            lines.append(f"- {item}")
    
    if sections.get("犯的错误"):
        lines.append("\n### ❌ 犯的错误")
        for item in sections["犯的错误"]:
            lines.append(f"- {item}")
    
    if sections.get("经验教训"):
        lines.append("\n### 💡 经验教训")
        for item in sections["经验教训"]:
            lines.append(f"- {item}")
    
    if sections.get("待办"):
        lines.append("\n### 📋 待办")
        for item in sections["待办"]:
            lines.append(f"- {item}")
    
    content = "\n".join(lines)
    
    # 搜索是否已存在今天的页面
    search_result = notion._request("POST", "/search", {
        "filter": {"property": "object", "value": "page"},
        "query": TODAY
    })
    
    page_id = None
    for page in search_result.get("results", []):
        title = page.get("properties", {}).get("title", {}).get("title", [])
        if title and TODAY in title[0].get("plain_text", ""):
            page_id = page["id"]
            break
    
    if page_id:
        # 更新现有页面
        print(f"找到现有页面: {page_id}")
    else:
        # 创建新页面
        # 先获取父页面 ID
        search_result = notion._request("POST", "/search", {
            "filter": {"property": "object", "value": "page"},
            "query": "OpenClaw 执行日志"
        })
        parent_id = search_result["results"][0]["id"] if search_result.get("results") else None
        
        if parent_id:
            result = notion.create_page(
                parent_id=parent_id,
                title=f"📓 {TODAY} 复盘",
                content=content
            )
            page_id = result.get("id")
            print(f"创建新页面: https://www.notion.so/{page_id}")
    
    return page_id

def main():
    print(f"\n📅 {TODAY} 每日复盘\n")
    
    # 读取今天 memory
    content = get_today_memory()
    if not content:
        print("今天还没有记录")
        return
    
    # 解析内容
    sections = parse_memory(content)
    if not sections or not any(sections.values()):
        print("今天没有可同步的内容")
        return
    
    # 打印摘要
    for section, items in sections.items():
        if items:
            print(f"{section}: {len(items)} 项")
    
    # 同步到 Notion
    page_id = sync_to_notion(sections)
    
    if page_id:
        print(f"\n✅ 已同步到 Notion")
    else:
        print("\n❌ 同步失败")

if __name__ == "__main__":
    main()
