#!/usr/bin/env python3
"""
保存广告素材到 Notion
自动上传图片到 ImgBB
"""

import json
import sys
import requests
import base64
sys.path.insert(0, '/root/.openclaw/workspace/skills/notion-api-skill/scripts')
from notion import NotionAPI

CONFIG_FILE = "/root/.openclaw/workspace/config.json"
AD_DB_ID = "2fd83d24-986d-81fd-b54a-e5d83c646d21"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def upload_to_imgbb(image_path):
    """上传图片到 ImgBB"""
    config = load_config()
    api_key = config.get("imgbb", {}).get("api_key")
    
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": base64_image},
            timeout=30
        )
        result = response.json()
        
        if result.get("success"):
            return {"success": True, "url": result["data"]["url"]}
        return {"success": False, "error": result.get("error", {}).get("message")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def classify_ad(primary_copy, headline, cta):
    """自动分类广告"""
    product_keywords = {
        "宠物用品": ["dog", "cat", "pet", "宠物", "猫", "狗"],
        "家居用品": ["home", "kitchen", "furniture", "家居", "厨房"],
        "3C电子": ["phone", "tech", "电子", "科技", "手机"],
        "服饰配件": ["clothing", "shoes", "bag", "衣服", "鞋子"],
        "美妆个护": ["skin", "beauty", "detox", "护肤", "美容", "排毒", "保健品"],
        "户外运动": ["outdoor", "sport", "fitness", "运动", "健身"],
        "母婴玩具": ["baby", "kid", "toy", "婴儿", "儿童"],
    }
    style_keywords = {
        "UGC": ["honest", "真实", "素人", "my honest", "i tried"],
        "品牌官方": ["official", "brand", "官方", "品牌"],
        "促销": ["sale", "discount", "限时", "折扣", "shop", "stock"],
        "故事型": ["story", "journey", "before after", "变化", "transformation"],
        "对比型": ["vs", "compare", "对比", "比较"],
        "教程型": ["how to", "tutorial", "教程", "教学"],
        "测评型": ["review", "test", "评测", "测评"],
    }
    
    text = f"{primary_copy} {headline} {cta}".lower()
    
    product_scores = {k: sum(1 for kw in v if kw.lower() in text) for k, v in product_keywords.items()}
    product = max(product_scores, key=product_scores.get) if max(product_scores.values()) > 0 else "其他"
    
    style_scores = {k: sum(1 for kw in v if kw.lower() in text) for k, v in style_keywords.items()}
    style = max(style_scores, key=style_scores.get) if max(style_scores.values()) > 0 else "其他"
    
    return product, style

def save_ad(primary_copy, headline, cta, landing_page="", platform="", image_path="", product_category="", creative_style="", status="待分析"):
    """保存广告素材到 Notion"""
    config = load_config()
    notion = NotionAPI(api_key=config["notion"]["api_key"])
    
    # 自动分类
    if not product_category or not creative_style:
        auto_product, auto_style = classify_ad(primary_copy, headline, cta)
        product_category = product_category or auto_product
        creative_style = creative_style or auto_style
    
    # 上传图片
    image_url = None
    if image_path:
        print(f"📤 上传图片: {image_path}")
        img_result = upload_to_imgbb(image_path)
        if img_result["success"]:
            image_url = img_result["url"]
            print(f"✅ 图片已上传: {image_url}")
        else:
            print(f"⚠️ 图片上传失败: {img_result['error']}")
    
    # 构建属性
    properties = {
        "Primary Copy": {"rich_text": [{"text": {"content": primary_copy[:1900]}}]},
        "Headline": {"rich_text": [{"text": {"content": headline}}]},
        "CTA": {"rich_text": [{"text": {"content": cta}}]},
        "状态": {"select": {"name": status}},
        "产品类别": {"select": {"name": product_category}},
        "创意风格": {"select": {"name": creative_style}},
    }
    
    if platform:
        properties["平台"] = {"select": {"name": platform}}
    if landing_page:
        properties["Landing Page"] = {"url": landing_page}
    
    # 创建页面
    result = notion._request("POST", "/pages", {
        "parent": {"database_id": AD_DB_ID},
        "properties": properties,
        "children": [
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {"url": image_url} if image_url else {"url": ""},
                    "caption": [{"text": {"content": "广告素材"}}]
                }
            }
        ] if image_url else []
    })
    
    return result

def main():
    print("\n📝 广告素材保存工具")
    print("=" * 50)
    print("\n用法: python3 save_ad.py <参数>")
    print("\n示例:")
    print('  python3 save_ad.py "主文案" "标题" "CTA" --platform Meta --image /path/to/image.jpg')
    print('  python3 save_ad.py "文案" "标题" "CTA" --product 美妆个护 --style 促销')
    print("\n自动分类:")
    print("  - 产品类别: 根据关键词自动识别")
    print("  - 创意风格: 根据文案自动判断")
    print("=" * 50)

if __name__ == "__main__":
    main()
