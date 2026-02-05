#!/usr/bin/env python3
"""
广告素材自动分类工具
分析 Primary Copy、Headline、CTA，自动分类产品类别和创意风格
"""

import json
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/notion-api-skill/scripts')
from notion import NotionAPI

# 产品类别关键词映射
PRODUCT_CATEGORIES = {
    "宠物用品": ["pet", "dog", "cat", "puppy", "kitten", "doggy", "kitty", "pet's", "paw", "fur", "pet supplies", "dog food", "cat litter", "pet toy", "宠物", "猫", "狗", "宠物用品"],
    "家居用品": ["home", "house", "kitchen", "living room", "bedroom", "furniture", "decor", "cleaning", "storage", "home decor", "家居", "厨房", "家具", "收纳", "清洁"],
    "3C电子": ["phone", "iphone", "android", "tablet", "laptop", "computer", "tech", "gadget", "electronic", "camera", "headphone", "wireless", "手机", "电脑", "电子", "科技", "平板"],
    "服饰配件": ["clothing", "wear", "shirt", "dress", "pants", "shoes", "bag", "watch", "jewelry", "accessory", "fashion", "衣服", "服装", "鞋子", "包包", "配饰"],
    "美妆个护": ["skin", "face", "beauty", "makeup", "cosmetic", "cream", "lotion", "serum", "skincare", "hair", "cosmetic", "护肤", "化妆", "美容", "美妆", "头发"],
    "户外运动": ["outdoor", "sport", "fitness", "gym", "running", "hiking", "camping", "exercise", "workout", "户外", "运动", "健身", "跑步", "露营"],
    "母婴玩具": ["baby", "kid", "child", "toy", "infant", "toddler", "maternal", "pregnancy", "baby gear", "婴儿", "儿童", "玩具", "母婴"],
}

# 创意风格关键词映射
CREATIVE_STYLES = {
    "UGC": ["真实", "普通", "日常", "like me", "i tried", "真实使用", "素人", "真实测评", "honest", "my honest", "my review"],
    "品牌官方": ["official", "brand", "premium", "quality", "官方", "品牌", "高端", "官方旗舰店", "professional studio"],
    "促销": ["sale", "discount", "deal", "off", "free", "promo", "限时", "折扣", "特价", "优惠", "促销", "百分之", "% off", "cheap"],
    "故事型": ["story", "journey", "transformation", "before after", "我的故事", "变化", "旅程", "从前", "结果", "before & after", "transformation"],
    "对比型": ["vs", "compare", "other vs", "other brand", "对比", "比较", "other brands", "versus", "different from"],
    "教程型": ["how to", "tutorial", "guide", "step", "learn", "教程", "教学", "指南", "怎么", "步骤", "easy way", "tips"],
    "测评型": ["review", "test", "try", "评测", "测评", "体验", "tested", "testing", "unboxing", "开箱"],
}


def classify_product(text):
    """分析文本，自动分类产品类别"""
    text_lower = text.lower()
    
    scores = {}
    for category, keywords in PRODUCT_CATEGORIES.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        scores[category] = score
    
    # 返回得分最高的类别
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "其他"


def classify_creative_style(primary_copy, headline, cta):
    """分析广告文案，自动分类创意风格"""
    text = f"{primary_copy} {headline} {cta}".lower()
    
    scores = {}
    for style, keywords in CREATIVE_STYLES.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        scores[style] = score
    
    # 返回得分最高的风格
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "其他"


def analyze_and_classify(primary_copy, headline, cta, creative_desc=""):
    """综合分析，返回分类结果"""
    full_text = f"{primary_copy} {headline} {cta} {creative_desc}"
    
    product = classify_product(full_text)
    style = classify_creative_style(primary_copy, headline, cta)
    
    return {
        "产品类别": product,
        "创意风格": style
    }


def main():
    if len(sys.argv) < 4:
        print("用法: python3 ad_classifier.py '<primary_copy>' '<headline>' '<cta>'")
        print("示例: python3 ad_classifier.py '让肌肤焕发光彩' '这款面霜太神奇了' '立即购买'")
        sys.exit(1)
    
    primary_copy = sys.argv[1]
    headline = sys.argv[2] if len(sys.argv) > 2 else ""
    cta = sys.argv[3] if len(sys.argv) > 3 else ""
    
    result = analyze_and_classify(primary_copy, headline, cta)
    
    print(f"\n📊 分析结果：")
    print(f"  产品类别：{result['产品类别']}")
    print(f"  创意风格：{result['创意风格']}")
    
    return result


if __name__ == "__main__":
    main()
