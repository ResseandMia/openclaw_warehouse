---
name: notion-api-skill
description: |
  Notion API integration with managed OAuth. Query databases, create and update pages, manage blocks. Use when users want to interact with Notion workspaces, databases, or pages.
  Notion API 集成，支持 OAuth 管理。查询数据库、创建/更新页面、管理 blocks。
---

# Notion API Skill

Notion API 集成工具 - 支持 OAuth 管理

## Features

- 🔐 **OAuth 管理** - 自动处理 Notion OAuth 认证
- 📊 **数据库查询** - 查询数据库内容、结构和数据源
- 📝 **页面管理** - 创建和更新页面
- 🧱 **Blocks 管理** - 添加、编辑、删除 blocks
- 🔗 **连接管理** - 查看和管理工作区连接

## Usage

**查询数据库：**
```
"查询 Notion 数据库"
"获取数据库结构"
```

**页面操作：**
```
"创建 Notion 页面"
"更新页面内容"
```

**Blocks 操作：**
```
"添加段落到页面"
"插入表格"
```

## Prerequisites

1. Notion Integration (notion.so/my-integrations)
2. OAuth credentials OR Internal Integration Token
3. Share databases/pages with the integration

## Configuration

### Option 1: OAuth (Recommended)
```bash
# OAuth flow managed automatically
# Just configure credentials
NOTION_CLIENT_ID=your_client_id
NOTION_CLIENT_SECRET=your_client_secret
```

### Option 2: Internal Integration Token
```bash
NOTION_API_KEY=secret_your_integration_token
```

## Commands

### Query Database

```bash
python3 scripts/notion.py query-database --id DATABASE_ID
```

### List Databases

```bash
python3 scripts/notion.py list-databases
```

### Get Page

```bash
python3 scripts/notion.py get-page --id PAGE_ID
```

### Create Page

```bash
python3 scripts/notion.py create-page \
  --parent-id PARENT_PAGE_ID \
  --title "Page Title" \
  --content "Page content here..."
```

### Update Page

```bash
python3 scripts/notion.py update-page \
  --id PAGE_ID \
  --title "New Title"
```

### Add Block

```bash
python3 scripts/notion.py add-block \
  --page-id PAGE_ID \
  --type paragraph \
  --content "New paragraph"
```

### List Connections

```bash
python3 scripts/notion.py list-connections
```

## Block Types

| Type | Description |
|------|-------------|
| paragraph | Text paragraph |
| heading_1 | Heading 1 |
| heading_2 | Heading 2 |
| heading_3 | Heading 3 |
| bullet_list_item | Bullet list |
| numbered_list_item | Numbered list |
| to_do | Todo item |
| toggle | Toggle list |
| code | Code block |
| quote | Quote block |
| divider | Divider |
| callout | Callout block |
| image | Image |

## Output Format

All commands return standardized JSON:

```json
{
  "success": true,
  "data": {...},
  "meta": {
    "endpoint": "/v1/databases/...",
    "timestamp": "2026-02-03T16:00:00Z"
  }
}
```

## Error Handling

- Invalid credentials → Prompt for OAuth setup
- Permission denied → Check integration sharing
- Rate limited → Retry with backoff
- Invalid page ID → Return error with suggestions

## OAuth Flow

1. User initiates connection
2. OpenClaw generates OAuth URL
3. User authorizes in Notion
4. Callback received with token
5. Token stored securely for future use

## Automation Examples

### Sync Database to Local

```bash
#!/bin/bash
# Sync Notion database to local JSON

DATABASE_ID="your_db_id"
OUTPUT_FILE="notion_backup.json"

python3 scripts/notion.py query-database --id $DATABASE_ID > $OUTPUT_FILE
echo "Synced to $OUTPUT_FILE"
```

### Create Page from Template

```bash
python3 scripts/notion.py create-page \
  --parent-id PARENT_ID \
  --title "Daily Note $(date +%Y-%m-%d)" \
  --content "## Today\n\n- \n\n## Notes\n"
```

### Batch Update

```bash
# Update multiple pages
for PAGE_ID in $(cat pages.txt); do
  python3 scripts/notion.py update-page --id $PAGE_ID --title "Updated"
done
```

## Links

- Notion API: https://developers.notion.com
- Create Integration: https://www.notion.so/my-integrations
- Rate Limits: https://developers.notion.com/reference/rate-limits

## Source

Skill from ClawHub by @byungkyu
- ClawHub: https://www.clawhub.ai/byungkyu/notion-api-skill
