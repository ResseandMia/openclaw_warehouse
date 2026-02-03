---
name: fb-ads-monitor
description: Monitor Meta Ads performance and save to Notion. Tracks spend, impressions, clicks, CTR, CPC, CPM daily with campaign breakdown. Use when user wants to check ad performance or automate daily reporting.
---

# Facebook Ads Monitor

Monitor PetzyMart ad account and save daily metrics to Notion.

## Configuration

**Facebook API:**
- Token: `YOUR_FB_TOKEN`
- Account ID: `act_YOUR_ACCOUNT_ID`

**Notion:**
- Database: `YOUR_NOTION_DATABASE_URL`
- Integration Token: `YOUR_NOTION_TOKEN`

## Metrics Tracked

| Column | Description |
|--------|-------------|
| 日期 (Date) | Report date |
| Campaign (Title) | Campaign name |
| Select | Status (ACTIVE/PAUSED) |
| 花费 | Total spend ($) |
| 展示 | Impressions |
| 点击 | Clicks |
| CTR | Click-through rate (%) |
| CPC | Cost per click ($) |
| CPM | Cost per 1000 impressions ($) |

## Usage

**Get today's report:**
```
"检查广告数据"
"FB广告表现"
```

**Get specific date:**
```
"2026-02-01 的广告数据"
"上周广告数据"
```

**Trigger words:**
- 检查广告
- FB广告
- Meta广告
- 广告数据
- 广告表现

## Commands

```bash
# Get today's data
python3 monitor_ads.py

# Get specific date
python3 monitor_ads.py --date 2026-02-01

# Save to Notion
python3 monitor_ads.py --save

# Check existing entries
python3 monitor_ads.py --check --date 2026-02-03
```

## Example Output

```
📊 PetzyMart (Last 7 Days)
====================================================================================================
🔴 Calming kit_CBO_TESTING_US
   💰 $  253.93 | 👁️   10,955 | 👆   663 | 📊 6.05%
====================================================================================================
📈 TOTAL: $253.93 | 👁️ 10,955 | 👆 663
   📊 CTR: 6.05%
```

## Automation

**Cron Job:**
- Schedule: `0 9 * * *` (每天 9:00 北京时间)
- Command: `python3 monitor_ads.py --save`
- Log: `/tmp/ads_monitor.log`

**Workflow:**
1. Fetch campaign data from Meta API
2. Format metrics
3. Display report
4. Save to Notion database

## Error Handling

| Error | Solution |
|-------|----------|
| Token expired | Refresh token from Meta Developer Portal |
| No data for date | Check if campaign is active |
| Notion permission error | Re-share database with integration |
| API rate limit | Wait and retry |

## Files

```
/root/.openclaw/workspace/skills/fb-ads-monitor/
├── SKILL.md
├── cron.json           # Cron configuration
└── scripts/
    ├── monitor_ads.py  # Main script
    └── save_to_notion.py  # Notion integration
```
