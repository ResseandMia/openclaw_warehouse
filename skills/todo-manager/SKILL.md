---
name: todo-manager
description: |
  Notion Todo database management for AI Schedule Assistant.
  Add, list, and manage tasks in Notion with priority and status.
  与 Notion Todo 数据库集成，管理任务（添加、列出、状态更新）。
---

# Todo Manager Skill

Notion Todo 任务管理 - 与 Notion 数据库集成

## Features

- ✅ **添加任务** - 添加待办事项到 Notion
- 📋 **列出任务** - 按日期查看任务
- 🏷️ **优先级支持** - 高/中/低优先级
- 📊 **状态跟踪** - 待办/进行中/已完成/已取消

## Usage

**添加任务:**
```
"添加任务 [任务名]"
"添加任务 [任务名] --date 2026-02-05 --priority 高"
```

**查看任务:**
```
"今天的任务"
"明天的任务"
"所有任务"
```

## Commands

```bash
# 添加任务
python3 scripts/todo_manager.py add "任务名称" [--date YYYY-MM-DD] [--priority 高|中|低]

# 查看今天任务
python3 scripts/todo_manager.py today

# 查看所有任务
python3 scripts/todo_manager.py all
```

## Notion Database Schema

| Field | Type | Options |
|-------|------|---------|
| 名称 | title | - |
| 日期 | date | - |
| 状态 | select | 待办/进行中/已完成/已取消 |
| 优先级 | select | 高/中/低 |
| 备注 | rich_text | - |

## Automation Examples

### Add Task from Chat

```bash
#!/bin/bash
# 从对话中添加任务
python3 scripts/todo_manager.py add "$1" --priority "$2"
```

### Morning Reminder Integration

```bash
#!/bin/bash
# 早安任务提醒
python3 scripts/morning_reminder.py
```

## Links

- Notion API: https://developers.notion.com
