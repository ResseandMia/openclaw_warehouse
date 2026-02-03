#!/usr/bin/env python3
"""
Facebook Ads Monitor - Fetch daily data and save to Notion
Usage: python3 monitor_ads.py [--save] [--days N] [--date YYYY-MM-DD]
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
FB_TOKEN = "YOUR_FB_TOKEN"
ACCOUNT_ID = "act_YOUR_ACCOUNT_ID"  # PetzyMart

NOTION_TOKEN = "YOUR_NOTION_TOKEN"
NOTION_DATABASE_ID = "YOUR_DATABASE_ID"

# ============ Facebook Functions ============

def get_campaign_list():
    """Get campaign list with status"""
    url = f"https://graph.facebook.com/v18.0/{ACCOUNT_ID}/campaigns"
    params = {"fields": "id,name,status", "limit": 20}
    headers = {"Authorization": f"Bearer {FB_TOKEN}"}
    
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    if resp.status_code == 200:
        return resp.json().get("data", [])
    return []

def parse_actions(actions, action_values):
    """Parse actions and action_values arrays"""
    result = {
        "link_clicks": 0,
        "add_to_cart": 0,
        "checkouts": 0,
        "purchases": 0,
        "purchase_value": 0
    }
    
    if actions:
        for action in actions:
            action_type = action.get("action_type", "")
            value = int(action.get("value", 0))
            
            if action_type == "link_click":
                result["link_clicks"] = value
            elif action_type == "add_to_cart":
                result["add_to_cart"] = value
            elif action_type == "initiate_checkout":
                result["checkouts"] = value
            elif action_type == "purchase":
                result["purchases"] = value
    
    if action_values:
        for action in action_values:
            action_type = action.get("action_type", "")
            value = float(action.get("value", 0))
            
            if action_type == "purchase":
                result["purchase_value"] = value
    
    return result

def get_insights(campaign_id, date_preset="last_14d"):
    """Get insights for a campaign"""
    url = f"https://graph.facebook.com/v18.0/{campaign_id}/insights"
    params = {
        "date_preset": date_preset,
        "fields": "spend,impressions,clicks,ctr,cpc,cpm,actions,action_values"
    }
    headers = {"Authorization": f"Bearer {FB_TOKEN}"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data:
                return data[0]
    except Exception as e:
        print(f"Error: {e}")
    return None

# ============ Notion Functions ============

def save_to_notion(data, date_str):
    """Save campaign data to Notion database"""
    
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    saved_count = 0
    for item in data:
        spend = float(item.get("spend", 0))
        if spend <= 0:
            continue
            
        campaign_name = item.get("name", "Unknown")
        status = item.get("status", "PAUSED")
        imps = int(item.get("impressions", 0))
        link_clicks = int(item.get("link_clicks", 0))
        all_clicks = int(item.get("all_clicks", 0))
        ctr_all = float(item.get("ctr_all", 0))
        add_to_cart = int(item.get("add_to_cart", 0))
        checkouts = int(item.get("checkouts", 0))
        purchases = int(item.get("purchases", 0))
        purchase_value = float(item.get("purchase_value", 0))
        
        # Calculate CTR(link) and CPC(link)
        ctr_link = (link_clicks / imps * 100) if imps > 0 else 0
        cpc_link = (spend / link_clicks) if link_clicks > 0 else 0
        
        # Results = purchases (or could be custom conversion)
        results = purchases
        
        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
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
                "花费": {"number": round(spend, 2)},
                "展示": {"number": imps},
                "点击": {"number": all_clicks},
                "CTR(ALL)": {"number": round(ctr_all, 2)},
                " CTR(link)": {"number": round(ctr_link, 2)},
                "Add to Cart": {"number": add_to_cart},
                "Checkouts": {"number": checkouts},
                "Results": {"number": results},
                "CPC (cost per link click)": {"number": round(cpc_link, 2)},
                "CPM": {"number": round(float(item.get("cpm", 0)), 2)},
                "Purchases Value": {"number": round(purchase_value, 2)}
            }
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            print(f"✅ Saved: {campaign_name}")
            saved_count += 1
        else:
            print(f"❌ Error: {resp.text[:200]}")
    
    print(f"\n✅ Saved {saved_count} campaigns to Notion")
    return saved_count

def check_existing(date_str):
    """Check if data already exists for date"""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
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
        return len(resp.json().get("results", []))
    return 0

# ============ Main ============

def main():
    save_mode = "--save" in sys.argv
    
    # Parse arguments
    date_str = None
    days = 14
    
    for i, arg in enumerate(sys.argv):
        if arg == "--date" and i + 1 < len(sys.argv):
            date_str = sys.argv[i + 1]
        if arg == "--days" and i + 1 < len(sys.argv):
            days = int(sys.argv[i + 1])
    
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    date_preset = f"last_{days}d"
    
    print(f"📊 Fetching {days} days data for PetzyMart...")
    print(f"   Date range: last {days} days")
    
    # Check existing entries
    if save_mode:
        existing = check_existing(date_str)
        if existing > 0:
            print(f"⚠️  Found {existing} existing entries for {date_str}")
    
    # Get campaigns
    campaigns = get_campaign_list()
    if not campaigns:
        print("❌ No campaigns found or API error")
        return
    
    # Get insights for each campaign
    result = []
    for camp in campaigns:
        insights = get_insights(camp["id"], date_preset)
        
        if insights:
            spend = float(insights.get("spend", 0))
            if spend > 0:
                actions_data = parse_actions(
                    insights.get("actions", []),
                    insights.get("action_values", [])
                )
                
                link_clicks = actions_data["link_clicks"]
                all_clicks = int(insights.get("clicks", 0))
                imps = int(insights.get("impressions", 0))
                ctr_all = float(insights.get("ctr", 0))
                cpm = float(insights.get("cpm", 0))
                
                # Calculate CTR(link) and CPC(link)
                ctr_link = (link_clicks / imps * 100) if imps > 0 else 0
                cpc_link = (spend / link_clicks) if link_clicks > 0 else 0
                
                result.append({
                    "name": camp["name"],
                    "status": camp["status"],
                    "spend": spend,
                    "impressions": imps,
                    "all_clicks": all_clicks,
                    "link_clicks": link_clicks,
                    "ctr_all": ctr_all,
                    "ctr_link": ctr_link,
                    "add_to_cart": actions_data["add_to_cart"],
                    "checkouts": actions_data["checkouts"],
                    "purchases": actions_data["purchases"],
                    "purchase_value": actions_data["purchase_value"],
                    "results": actions_data["purchases"],
                    "cpc_link": cpc_link,
                    "cpm": cpm
                })
    
    if not result:
        print(f"❌ No data found for last {days} days")
        return
    
    # Print report
    print(f"\n📊 PetzyMart - Last {days} Days")
    print("=" * 140)
    
    total_spend = 0
    total_impressions = 0
    total_link_clicks = 0
    total_all_clicks = 0
    total_add_to_cart = 0
    total_checkouts = 0
    total_purchases = 0
    total_purchase_value = 0
    
    for item in result:
        status_emoji = "🟢" if item["status"] == "ACTIVE" else "🔴" if item["status"] == "PAUSED" else "🟡"
        print(f"{status_emoji} {item['name']}")
        print(f"   💰 ${item['spend']:>8.2f} | 👁️ {item['impressions']:>8,} | 👆 {item['all_clicks']:>5,}/{item['link_clicks']:>4} | 📊 CTR(ALL): {item['ctr_all']:.2f}% | 🔗 {item['ctr_link']:.2f}%")
        print(f"   🛒 ATC: {item['add_to_cart']:>3} | 💳 Chk: {item['checkouts']:>2} | 🛍️ Purch: {item['purchases']} | 💵 ${item['purchase_value']:.2f}")
        print(f"   💵 CPC(link): ${item['cpc_link']:.2f} | CPM: ${item['cpm']:.2f}")
        
        total_spend += item['spend']
        total_impressions += item['impressions']
        total_link_clicks += item['link_clicks']
        total_all_clicks += item['all_clicks']
        total_add_to_cart += item['add_to_cart']
        total_checkouts += item['checkouts']
        total_purchases += item['purchases']
        total_purchase_value += item['purchase_value']
    
    print("=" * 140)
    print(f"\n📈 TOTAL (Last {days} Days)")
    print(f"   💰 Spend: ${total_spend:,.2f}")
    print(f"   👁️ Impressions: {total_impressions:,}")
    print(f"   👆 Clicks(all/link): {total_all_clicks:,}/{total_link_clicks:,}")
    print(f"   🛒 Add to Cart: {total_add_to_cart}")
    print(f"   💳 Checkouts: {total_checkouts}")
    print(f"   🛍️ Purchases: {total_purchases} | Value: ${total_purchase_value:,.2f}")
    
    if total_impressions > 0:
        ctr_all = total_all_clicks / total_impressions * 100
        ctr_link = total_link_clicks / total_impressions * 100
        cpc_link = total_spend / total_link_clicks if total_link_clicks > 0 else 0
        roas = total_purchase_value / total_spend if total_spend > 0 else 0
        
        print(f"   📊 CTR(ALL): {ctr_all:.2f}%")
        print(f"   📊 CTR(link): {ctr_link:.2f}%")
        print(f"   💵 CPC(link): ${cpc_link:.2f}")
        print(f"   📈 ROAS: {roas:.2f}x")
    
    # Save to Notion
    if save_mode:
        print(f"\n💾 Saving to Notion...")
        save_to_notion(result, date_str)
    
    return result

if __name__ == "__main__":
    main()
