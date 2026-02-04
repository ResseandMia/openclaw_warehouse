---
name: morning-reminder
description: |
  AI Schedule Assistant - Morning task reminder with quotes.
  Reads Notion Todo and sends daily task summary with motivational quotes.
  AI 日程助手 - 早安任务提醒，带有名人警句。
---

# Morning Reminder Skill

AI 日程助手 - 早安任务提醒

## Features

- 🌅 **每日提醒** - 早上 8:00 自动发送
- 📋 **任务列表** - 读取 Notion Todo
- 💬 **名人警句** - 随机励志语录
- 🏷️ **优先级排序** - 高/中/低任务分类

## Usage

```bash
# 手动执行
python3 scripts/morning_reminder.py

# 输出示例
🌅 早上好！今天的你会比昨天更优秀。

今日安排：
🔴 高优先级：
  • 发布公众号文章
🟡 中优先级：
  • 回复邮件

共 3 个任务，开始执行吧！💪
```

## Cron Schedule

```bash
# 每天早上 8:00 (北京时间)
0 8 * * *
```

## Configuration

Requires Notion Todo database configured in `config.json`:

```json
{
  "notion": {
    "api_key": "your_notion_api_key",
    "todo_database_id": "your_database_id"
  }
}
```

## Motivational Quotes

20+ Chinese motivational quotes included:

- 今天的你会比昨天更优秀
- 每一个不曾起舞的日子，都是对生命的辜负
- 不要等待机会，而要创造机会
- 乘风破浪，勇往直前
- ...and more

## Files

- `scripts/morning_reminder.py` - Main script
- `SKILL.md` - This documentation
