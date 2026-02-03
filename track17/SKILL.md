---
name: track17
description: |
  Track parcels via the 17TRACK API with local SQLite database, polling, and optional webhook ingestion.
---

# 17TRACK Package Tracking

包裹追踪工具 - 通过 17TRACK API 追踪快递

## Features

- 📦 **包裹追踪** - 支持 17TRACK API
- 💾 **本地存储** - SQLite 数据库
- 🔄 **定时轮询** - 自动更新物流状态
- 🔗 **Webhook 支持** - 可选的 webhook 接收更新
- 📋 **CLI 管理** - 添加、列表、同步包裹

## Supported Carriers

17TRACK 支持 2000+ 物流商，包括：
- 顺丰 (SF Express)
- 中通 (ZTO)
- 圆通 (YTO)
- 申通 (STO)
- 韵达 (Yunda)
- 京东 (JD)
- 邮政 (China Post)
- DHL / FedEx / UPS / USPS
- 以及更多...

## Usage

**添加包裹：**
```
"追踪快递单号 XXX"
"添加包裹 123456789"
```

**查看状态：**
```
"查看所有包裹"
"快递 XXX 的状态"
```

**同步更新：**
```
"更新所有包裹"
"同步物流信息"
```

## Configuration

Required environment variables:
```bash
# 17TRACK API
TRACK17_API_KEY=your_api_key
TRACK17_API_URL=https://api.17track.net/v2
```

Optional settings:
```bash
# 数据目录
TRACK17_DATA_DIR=./data

# 轮询间隔（秒）
TRACK17_POLL_INTERVAL=3600

# Webhook 端口
TRACK17_WEBHOOK_PORT=8080
```

## Commands

### Add Package

```bash
python3 scripts/track.py add --number TRACKING_NUMBER --carrier CARRIER
```

**Example:**
```bash
python3 scripts/track.py add --number "1234567890" --carrier "sf_express"
python3 scripts/track.py add --number "UC123456789US" --carrier "usps"
```

### List Packages

```bash
python3 scripts/track.py list --status all
```

**Status options:** all, pending, in_transit, delivered, exception

### Get Package Status

```bash
python3 scripts/track.py get --number TRACKING_NUMBER
```

### Sync All Packages

```bash
python3 scripts/track.py sync
```

### Sync Single Package

```bash
python3 scripts/track.py sync --number TRACKING_NUMBER
```

### Delete Package

```bash
python3 scripts/track.py delete --number TRACKING_NUMBER
```

### Start Webhook Server

```bash
python3 scripts/track.py webhook --port 8080
```

### Import Packages from File

```bash
python3 scripts/track.py import --file packages.csv
```

### Export Packages

```bash
python3 scripts/track.py export --output packages.json
```

## Output Format

All commands return standardized JSON:

```json
{
  "success": true,
  "data": {
    "number": "1234567890",
    "carrier": "sf_express",
    "status": "in_transit",
    "events": [
      {
        "time": "2026-02-03T10:00:00Z",
        "location": "Shanghai",
        "description": "包裹已发出"
      }
    ],
    "last_update": "2026-02-03T16:00:00Z"
  }
}
```

## Status Types

| Status | Description |
|--------|-------------|
| pending | 等待处理 |
| in_transit | 运输中 |
| out_for_delivery | 派送中 |
| delivered | 已签收 |
| exception | 异常 |
| returned | 退回 |
| expired | 过期 |

## Automation Examples

### Daily Sync Cron

```bash
# Sync every 6 hours
0 */6 * * * python3 scripts/track.py sync
```

### Monitor Specific Packages

```bash
#!/bin/bash
# Check specific packages and alert

python3 scripts/track.py get --number "1234567890" | \
  jq -r '.data.status' | \
  xargs -I {} echo "Package status: {}"
```

### Batch Import and Track

```bash
#!/bin/bash
# Import packages and start tracking

# Import from CSV
python3 scripts/track.py import --file new_packages.csv

# Start sync
python3 scripts/track.py sync

# List all
python3 scripts/track.py list
```

### Webhook Handler

```bash
#!/bin/bash
# Start webhook receiver

python3 scripts/track.py webhook --port 8080

# In another terminal, test webhook
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"tracking_number": "1234567890", "status": "delivered"}'
```

## Database Schema

Packages stored in SQLite:

```sql
CREATE TABLE packages (
    id INTEGER PRIMARY KEY,
    tracking_number TEXT UNIQUE,
    carrier TEXT,
    status TEXT,
    last_update TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    package_id INTEGER,
    timestamp TIMESTAMP,
    location TEXT,
    description TEXT,
    FOREIGN KEY (package_id) REFERENCES packages(id)
);
```

## Error Handling

- Invalid tracking number → Validate format
- Unknown carrier → Suggest common carriers
- API rate limit → Retry with backoff
- Network issues → Retry 3 times

## Links

- 17TRACK API: https://www.17track.net/en/api
- Carrier List: https://www.17track.net/en/carriers

## Source

Skill from ClawHub by @tristanmanchester
- ClawHub: https://www.clawhub.ai/tristanmanchester/track17
