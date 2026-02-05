#!/usr/bin/env python3
"""
图片上传到 ImgBB
"""

import json
import requests
import sys
import base64

CONFIG_FILE = "/root/.openclaw/workspace/config.json"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def upload_to_imgbb(image_path):
    """上传图片到 ImgBB，返回公开 URL"""
    config = load_config()
    api_key = config.get("imgbb", {}).get("api_key")
    
    if not api_key:
        return {"success": False, "error": "ImgBB API key not found"}
    
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # 转换为 base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": api_key,
                "image": base64_image,
            },
            timeout=30
        )
        
        result = response.json()
        
        if result.get("success"):
            return {
                "success": True,
                "url": result["data"]["url"],
                "delete_url": result["data"]["delete_url"],
                "width": result["data"]["width"],
                "height": result["data"]["height"]
            }
        else:
            return {"success": False, "error": result.get("error", {}).get("message", "Upload failed")}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("用法: python3 imgbb_upload.py <图片路径>")
        print("示例: python3 imgbb_upload.py /root/.openclaw/media/inbound/image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print(f"📤 上传图片: {image_path}")
    result = upload_to_imgbb(image_path)
    
    if result["success"]:
        print(f"✅ 上传成功!")
        print(f"🔗 {result['url']}")
        return result["url"]
    else:
        print(f"❌ 上传失败: {result['error']}")
        return None

if __name__ == "__main__":
    main()
