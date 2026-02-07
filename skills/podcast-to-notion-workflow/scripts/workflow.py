#!/usr/bin/env python3
"""一键播客工作流 - 简化版"""
import os
import sys

# 从环境变量读取API Keys
TRANSCRIPT_KEY = os.getenv("TRANSCRIPT_API_KEY")
NANOBANANA_KEY = os.getenv("NANOBANANA_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

def main():
    print("🎙️ 播客工作流")
    print("使用: python3 workflow.py --url <youtube_url> --channel <name>")
    print("")
    print("环境变量:")
    print(f"  TRANSCRIPT_API_KEY: {'✅' if TRANSCRIPT_KEY else '❌'}")
    print(f"  NANOBANANA_KEY: {'✅' if NANOBANANA_KEY else '❌'}")
    print(f"  NOTION_TOKEN: {'✅' if NOTION_TOKEN else '❌'}")

if __name__ == "__main__":
    main()
