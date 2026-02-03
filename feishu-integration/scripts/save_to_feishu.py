#!/usr/bin/env python3
"""
Save content to Feishu (飞书)
Usage: python save_to_feishu.py --title "标题" --content "Markdown内容" --images "img1.png,img2.png"
"""

import requests
import argparse
import sys
import os
import json
from datetime import datetime

# Credentials (should move to config in production)
APP_ID = "cli_a9f4a51627781cb5"
APP_SECRET = "AkbOrmLW4E3rDBVpvPdsybhiKzcA5hZQ"
FOLDER_ID = "WvAKfx94cl8AO0dyV70cuKBhnab"

def get_access_token():
    """Get tenant access token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get("tenant_access_token")
    else:
        print(f"Error getting token: {response.text}")
        return None

def create_document(token, title):
    """Create a new document in the folder"""
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"folder_token": FOLDER_ID, "title": title}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("data", {}).get("document_id")
    else:
        print(f"Error creating document: {response.text}")
        return None

def upload_image(token, image_path):
    """Upload image and return image_key"""
    # Step 1: Get upload URL
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": open(image_path, "rb")}
    data = {"image_type": "docx", "filename": os.path.basename(image_path)}
    
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        return response.json().get("data", {}).get("image_key")
    else:
        print(f"Error uploading image: {response.text}")
        return None

def add_text_block(token, document_id, text, block_type=2):
    """Add a text block to the document"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Split text into paragraphs
    paragraphs = text.strip().split('\n\n')
    
    for para in paragraphs:
        if not para.strip():
            continue
        data = {
            "children": [{
                "block_type": block_type,
                "text": {
                    "elements": [{"text_run": {"content": para.strip()}}]
                }
            }],
            "index": 0
        }
        response = requests.put(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Error adding text: {response.text}")

def add_image_block(token, document_id, image_key, image_size=None):
    """Add an image block to the document"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    data = {
        "children": [{
            "block_type": 10,
            "image": {
                "image_key": image_key,
                "width": {"type": "point", "value": 540},
                "height": {"type": "point", "value": 720}
            }
        }],
        "index": 0
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error adding image: {response.text}")

def save_to_feishu(title, content, image_paths=None):
    """Main function to save content to Feishu"""
    # Get access token
    token = get_access_token()
    if not token:
        return False
    
    # Create document
    document_id = create_document(token, title)
    if not document_id:
        return False
    
    print(f"Created document: {document_id}")
    
    # Add content
    add_text_block(token, document_id, content)
    
    # Add images
    if image_paths:
        for img_path in image_paths:
            if os.path.exists(img_path):
                image_key = upload_image(token, img_path)
                if image_key:
                    add_image_block(token, document_id, image_key)
    
    print(f"Document saved successfully!")
    print(f"URL: https://bytedance.larkoffice.com/docx/{document_id}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Save content to Feishu')
    parser.add_argument('--title', required=True, help='Document title')
    parser.add_argument('--content', required=True, help='Markdown content')
    parser.add_argument('--images', default='', help='Comma-separated image paths')
    parser.add_argument('--folder-id', default=FOLDER_ID, help='Feishu folder ID')
    
    args = parser.parse_args()
    
    image_paths = [p.strip() for p in args.images.split(',')] if args.images else []
    
    success = save_to_feishu(args.title, args.content, image_paths)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
