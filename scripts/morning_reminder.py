#!/usr/bin/env python3
"""
AI 日程管家 - 每日任务提醒
每天早上 8:00 执行
"""

import json
import random
from datetime import datetime

CONFIG_FILE = "/root/.openclaw/workspace/config.json"
TODO_DB_ID = "2fd83d24-986d-810e-b00b-dfcfa9e53935"

# 名人警句 / 心灵鸡汤库
QUOTES = [
    "🌟 今天的你会比昨天更优秀。",
    "💪 每一个不曾起舞的日子，都是对生命的辜负。",
    "🚀 不要等待机会，而要创造机会。",
    "🌈 你的潜力无限，不要给自己设限。",
    "🔥 成功不是将来才有的，而是从决定去做的那一刻起。",
    "💡 每天都是一个新的开始，把握当下。",
    "⭐ 努力不一定成功，但放弃一定失败。",
    "🌻 向阳而生，逐光而行。",
    "🎯 专注一件事，做到极致。",
    "💫 人生没有白走的路，每一步都算数。",
    "🌊 乘风破浪，勇往直前。",
    "🔆 你的时间有限，不要浪费在重复别人的生活上。",
    "🏆 今天的汗水，是明天的骄傲。",
    "✨ 相信相信的力量。",
    "🌱 播种一种行动，收获一种习惯。",
    "💪 最累的时候，恰恰是进步最大的时候。",
    "🎨 你是自己人生的作者，何必写那么难的情节。",
    "🌟 星星之火，可以燎原。",
    "🔮 未来属于那些相信自己梦想的人。",
    "💖 温柔且坚定，自信且谦逊。",
]

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
    
    # 先查询所有，再用 Python 过滤
    result = notion._request("POST", f"/databases/{TODO_DB_ID}/query", {})
    
    if result.get("object") == "error":
        return {"success": False, "error": result.get("message")}
    
    items = result.get("results", [])
    
    # 过滤：今天的、未完成的任务
    items = [i for i in items if i.get("properties", {}).get("日期", {}).get("date", {}).get("start", "").startswith(today)]
    items = [i for i in items if i.get("properties", {}).get("状态", {}).get("select", {}).get("name") != "已完成"]
    
    return {"success": True, "results": items}

def format_morning_message():
    """生成早安消息"""
    todos = get_today_todos()
    
    if not todos.get("success"):
        return "早上好！无法获取今天的任务。"
    
    items = todos.get("results", [])
    
    # 随机选择一句警句
    quote = random.choice(QUOTES)
    
    # 按优先级分组
    high = [i for i in items if i.get("properties", {}).get("优先级", {}).get("select", {}).get("name") == "高"]
    medium = [i for i in items if i.get("properties", {}).get("优先级", {}).get("select", {}).get("name") == "中"]
    low = [i for i in items if i.get("properties", {}).get("优先级", {}).get("select", {}).get("name") == "低"]
    
    msg = f"🌅 早上好！{quote}\n\n"
    
    if len(items) > 0:
        msg += "今日安排：\n"
        
        if high:
            msg += "🔴 高优先级：\n"
            for t in high:
                title = t.get("properties", {}).get("名称", {}).get("title", [{}])[0].get("plain_text", "")
                msg += f"  • {title}\n"
            msg += "\n"
        
        if medium:
            msg += "🟡 中优先级：\n"
            for t in medium:
                title = t.get("properties", {}).get("名称", {}).get("title", [{}])[0].get("plain_text", "")
                msg += f"  • {title}\n"
            msg += "\n"
        
        if low:
            msg += "🔵 低优先级：\n"
            for t in low:
                title = t.get("properties", {}).get("名称", {}).get("title", [{}])[0].get("plain_text", "")
                msg += f"  • {title}\n"
        
        msg += f"\n共 {len(items)} 个任务，开始执行吧！💪"
    else:
        msg += "今天没有待办事项，好好休息一下~ ☕"
    
    return msg

def main():
    print("\n🌅 AI 日程管家 - 早安")
    print("=" * 40)
    
    msg = format_morning_message()
    print(msg)
    
    print("\n" + "=" * 40)
    print("准备好发送给用户了！")

if __name__ == "__main__":
    main()
