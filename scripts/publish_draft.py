#!/usr/bin/env python3
"""
发布微信公众号草稿
按顺序从最旧 → 最新发布

凭据从 /root/.openclaw/workspace/config.json 统一读取
"""

import json
import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/skills/wechat-oa-channel/scripts')

from channel import WeChatOAChannel

CONFIG_FILE = "/root/.openclaw/workspace/config.json"

def load_config():
    """从统一配置读取凭据"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_wechat_config():
    """获取微信配置"""
    config = load_config()
    return config.get("wechat", {})

# 草稿发布顺序 (从最旧到最新)
DRAFTS = [
    {"order": 1, "title": "第55期｜广告表现不稳定时，不要触碰在运行的东西原则是什么意思？", "media_id": "W0JiFokHGuwkJ3JGNNfK58Yg6C3RU5doN9yc8_s00gvqXuya2OpJTpZocIPM1JXJ"},
    {"order": 2, "title": "第56期｜在广告创意中，什么是钩子？", "media_id": "W0JiFokHGuwkJ3JGNNfK59FuOTIAfEy_RC3dV3B3llCmZTtHhKqNSmCy7GVKg6IF"},
    {"order": 3, "title": "第57期｜什么是贡献边际？", "media_id": "W0JiFokHGuwkJ3JGNNfK5-usrOyHnOkrtY_SETfGg92Nvw6c_NsI2jx8GI62uU2n"},
    {"order": 4, "title": "第58期｜什么是热门口袋？", "media_id": "W0JiFokHGuwkJ3JGNNfK5yCU4T2QTp0PVHAW5l8jGZdTPhJurN02qOeJ8whoLflt"},
    {"order": 5, "title": "第59期｜当你的广告CPM总是高但效果很差时，可能的原因有哪些？", "media_id": "W0JiFokHGuwkJ3JGNNfK5yDhmcbkzd8I_1hjuYg1aGsIJuND5eUunXt2GFLz_Epj"},
    {"order": 6, "title": "第60期｜什么是信号质量？", "media_id": "W0JiFokHGuwkJ3JGNNfK50bs7Lid1oXqniqWA1GV_uabkk0-lZXZzXXdkkJwNOyZ"},
    {"order": 7, "title": "第61期｜在Andromeda算法中，序列学习是什么概念？", "media_id": "W0JiFokHGuwkJ3JGNNfK55A9kAsepruxXV9P5ITBvrrtI_04pR1PF01aNPq0qP4g"},
    {"order": 8, "title": "第62期｜在Andromeda时代，建议将测试和Scaling分开展示？", "media_id": "W0JiFokHGuwkJ3JGNNfK55AeBvI_xQEtRJzXiCVHU4Ka5be77ulJd3l24TXPKoVp"},
    {"order": 9, "title": "第63期｜在Meta广告竞拍公式中，除了广告主出价，还有哪两个关键因素决定总价值？", "media_id": "W0JiFokHGuwkJ3JGNNfK56bnXydA2lotsIIoaaS5FBeNsZOTjmFcXxcJfDuM1fqJ"},
    {"order": 10, "title": "第64期｜为什么在广告中避免使用点击很重要？", "media_id": "W0JiFokHGuwkJ3JGNNfK53DWyGm2D1ScsD3KaUcLUdA4IeAL0xBMLWQX1khs9WB5"},
    {"order": 11, "title": "第65期｜在广告创意中，UGC代表什么？", "media_id": "W0JiFokHGuwkJ3JGNNfK5z_z7LKmv54pgXHgHKhyooKpCXxDLICnVhRe77BvSnhH"},
]

STATE_FILE = "/root/.openclaw/workspace/.draft_publish_state.json"

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"published_count": 0, "published_list": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def publish_draft(media_id: str):
    """发布草稿 - 从统一配置读取凭据"""
    config = get_wechat_config()
    channel = WeChatOAChannel(
        app_id=config.get("app_id"),
        app_secret=config.get("app_secret")
    )
    return channel.publish_draft(media_id)

def main():
    state = load_state()
    count = state["published_count"]
    
    if count >= len(DRAFTS):
        print("所有 {} 篇草稿已发布完成！".format(len(DRAFTS)))
        return
    
    draft = DRAFTS[count]
    next_title = draft["title"]
    media_id = draft["media_id"]
    
    print("准备发布第 {} 篇: {}".format(count + 1, next_title))
    
    result = publish_draft(media_id)
    
    if result.get("success"):
        print("发布成功! msg_id: {}".format(result.get("msg_id")))
        state["published_count"] += 1
        state["published_list"].append({
            "order": count + 1,
            "title": next_title,
            "media_id": media_id,
            "msg_id": result.get("msg_id")
        })
        save_state(state)
        print("状态已保存")
    else:
        print("发布失败: {}".format(result.get("error")))
        sys.exit(1)
    
    print("\n进度: {}/{}".format(state["published_count"], len(DRAFTS)))

if __name__ == "__main__":
    main()
