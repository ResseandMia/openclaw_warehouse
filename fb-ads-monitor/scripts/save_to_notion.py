#!/usr/bin/env python3
"""
Save Facebook Ads data to Notion
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
NOTION_TOKEN = "YOUR_NOTION_TOKEN"
DATABASE_ID = "YOUR_NOTION_DATABASE_ID"

def save_to_notion(data, date_str=None):
    """Save campaign data to Notion database"""
    
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    url = "https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    for item in data:
        # Skip if no spend
        spend = float(item.get("spend", {}).get("value", 0))
        if spend <= 0:
            continue
            
        campaign_name = item.get("name", "Unknown")
        status = item.get("status", "PAUSED")
        impressions = int(item.get("insights", {}).get("impressions", 0))
        clicks = int(item.get("insights", {}).get("clicks", 0))
        ctr = float(item.get("insights", {}).get("ctr", 0))
        cpc = float(item.get("insights", {}).get("cpc", 0))
        cpm = float(item.get("insights", {}).get("cpm", 0))
        
        payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "日期 (Date)": {
                    "title": [{"text": {"content": date_str}}]
                },
                "Campaign (Title)": {
                    "rich_text": [{"text": {"content": campaign_name[:2000]}}]
                },
                "Select": {
                    "select": {"name": status}
                },
                "花费": {
                    "number": round(spend, 2)
                },
                "展示": {
                    "number": impressions
                },
                "点击": {
                    "number": clicks
                },
                "CTR": {
                    "number": round(ctr, 2)
                },
                "CPC": {
                    "number": round(cpc, 2)
                },
                "CPM": {
                    "number": round(cpm, 2)
                }
            }
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            print(f"✅ Saved: {campaign_name}")
        else:
            print(f"❌ Error saving {campaign_name}: {resp.text}")
    
    print("\n✅ Done saving to Notion!")

def query_notion(date_str=None):
    """Query existing entries for a date"""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "filter": {
            "property": "日期 (Date)",
            "title": {"equals": date_str}
        }
    }
    
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json().get("results", [])
    return []

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Check existing entries
        date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime("%Y-%m-%d")
        entries = query_notion(date_str)
        print(f"Found {len(entries)} entries for {date_str}")
        return
    
    # Simulated data for testing
    test_data = [
        {
            "name": "Calming kit_CBO_TESTING_US",
            "status": "PAUSED",
            "spend": {"value": 253.93},
            "insights": {
                "impressions": 10955,
                "clicks": 663,
                "ctr": 6.05,
                "cpc": 0.38,
                "cpm": 23.18
            }
        }
    ]
    
    save_to_notion(test_data)

if __name__ == "__main__":
    main()
