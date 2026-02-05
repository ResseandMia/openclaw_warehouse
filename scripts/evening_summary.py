#!/usr/bin/env python3
"""
AI 日程管家 - 晚间记录
每天晚上 10:00 执行
"""

import json
from datetime import datetime

CONFIG_FILE = "/root/.openclaw/workspace/config.json"
TODO_DB_ID = "2fd83d24-986d-810e-b00b-dfcfa9e53935"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_today_todos():
    """获取今天的待办事项"""
    import sys
    sys.path.insert(0, '/root/.openclaw/workspace/skills/notion-api-skill/scripts')
    from notion import NotionAPI
    
    config = load_config()
    notion = NotionAPI(api_key=config["notion"]["api_key"])
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 查询所有
    result = notion._request("POST", f"/databases/{TODO_DB_ID}/query", {})
    
    if result.get("object") == "error":
        return {"success": False, "error": result.get("message")}
    
    items = result.get("results", [])
    
    # 过滤：今天的任务
    items = [i for i in items if i.get("properties", {}).get("日期", {}).get("date", {}).get("start", "").startswith(today)]
    
    return {"success": True, "results": items}

def format_evening_message():
    """生成晚间消息"""
    todos = get_today_todos()
    
    if not todos.get("success"):
        return "晚上好！无法获取今天的任务数据。"
    
    items = todos.get("results", [])
    
    completed = [i for i in items if i.get("properties", {}).get("状态", {}).get("select", {}).get("name") == "已完成"]
    pending = [i for i in items if i.get("properties", {}).get("状态", {}).get("select", {}).get("name") != "已完成"]
    
    msg = "🌙 晚上好！今日总结：\n\n"
    
    msg += f"✅ 已完成: {len(completed)} 个\n"
    msg += f"⏳ 待完成: {len(pending)} 个\n\n"
    
    if completed:
        msg += "完成的事项：\n"
        for t in completed:
            title = t.get("properties", {}).get("名称", {}).get("title", [{}])[0].get("plain_text", "")
            msg += f"  • {title}\n"
        msg += "\n"
    
    if pending:
        msg += "还需要努力：\n"
        for t in pending:
            title = t.get("properties", {}).get("名称", {}).get("title", [{}])[0].get("plain_text", "")
            priority = t.get("properties", {}).get("优先级", {}).get("select", {}).get("name", "")
            emoji = {"高": "🔴", "中": "🟡", "低": "🔵"}.get(priority, "⚪")
            msg += f"  {emoji} {title}\n"
    
    completion_rate = len(completed) / len(items) * 100 if items else 0
    msg += f"\n📊 今日完成率: {completion_rate:.0f}%"
    
    if completion_rate == 100:
        msg += " 🎉 太棒了！"
    
    return msg

def main():
    print("\n🌙 AI 日程管家 - 晚间")
    print("=" * 40)
    
    msg = format_evening_message()
    print(msg)
    
    print("\n" + "=" * 40)
    print("准备好发送给用户了！")

if __name__ == "__main__":
    main()
