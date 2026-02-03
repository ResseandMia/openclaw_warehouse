#!/usr/bin/env python3
"""
OAuth Helper - Detect and automate OAuth login flows
"""

import re
from typing import Dict, List, Optional, Tuple

# OAuth Provider configurations
OAUTH_PROVIDERS = {
    "google": {
        "domains": [
            "accounts.google.com/o/oauth2",
            "accounts.google.com/signin/oauth",
            "accounts.google.com/v3/signin"
        ],
        "selectors": {
            "account": '[data-identifier], .JDAKTe',
            "allow": 'button:has-text("Allow"), button:has-text("Continue")'
        }
    },
    "apple": {
        "domains": [
            "appleid.apple.com/auth/authorize",
            "appleid.apple.com/auth/oauth2"
        ],
        "selectors": {
            "email": 'input[type="email"], #account_name_text_field',
            "password": 'input[type="password"], #password_text_field',
            "continue": 'button#sign-in, button:has-text("Continue")',
            "trust": 'button:has-text("Trust")'
        }
    },
    "microsoft": {
        "domains": [
            "login.microsoftonline.com/common/oauth2",
            "login.microsoftonline.com/consumers",
            "login.live.com/oauth20"
        ],
        "selectors": {
            "account": '.table-row[data-test-id]',
            "email": 'input[name="loginfmt"]',
            "password": 'input[name="passwd"]',
            "next": 'button#idSIButton9',
            "accept": 'button#idBtn_Accept'
        }
    },
    "github": {
        "domains": [
            "github.com/login/oauth/authorize",
            "github.com/login",
            "github.com/sessions/two-factor"
        ],
        "selectors": {
            "email": 'input#login_field',
            "password": 'input#password',
            "signin": 'input[type="submit"]',
            "authorize": 'button[name="authorize"]',
            "2fa": 'input#app_totp'
        }
    },
    "discord": {
        "domains": [
            "discord.com/oauth2/authorize",
            "discord.com/login",
            "discord.com/api/oauth2"
        ],
        "selectors": {
            "email": 'input[name="email"]',
            "password": 'input[name="password"]',
            "login": 'button[type="submit"]',
            "authorize": 'button:has-text("Authorize")'
        }
    },
    "wechat": {
        "domains": [
            "open.weixin.qq.com/connect/qrconnect",
            "open.weixin.qq.com/connect/oauth2"
        ],
        "selectors": {
            "qr": 'img[src*="qrcode"]'
        },
        "method": "qr_scan"
    },
    "qq": {
        "domains": [
            "graph.qq.com/oauth2.0/authorize",
            "ssl.xui.ptlogin2.qq.com",
            "ui.ptlogin2.qq.com"
        ],
        "selectors": {
            "switch": 'a:has-text("密码登录")',
            "username": 'input#u',
            "password": 'input#p',
            "login": 'input#login_button'
        },
        "method": "qr_or_password"
    }
}

# OAuth button detection patterns
OAUTH_BUTTONS = {
    "google": {
        "selectors": ['[data-provider="google"]', '.google-btn'],
        "text_patterns": ["Continue with Google", "Sign in with Google", "Login with Google"]
    },
    "apple": {
        "selectors": ['[data-provider="apple"]', '.apple-btn'],
        "text_patterns": ["Sign in with Apple", "Continue with Apple"]
    },
    "microsoft": {
        "selectors": ['[data-provider="microsoft"]'],
        "text_patterns": ["Sign in with Microsoft", "Login with Microsoft"]
    },
    "github": {
        "selectors": ['[data-provider="github"]'],
        "text_patterns": ["Continue with GitHub", "Sign in with GitHub", "Login with GitHub"]
    },
    "discord": {
        "selectors": ['[data-provider="discord"]'],
        "text_patterns": ["Login with Discord", "Continue with Discord"]
    },
    "wechat": {
        "selectors": ['.wechat-btn', 'img[src*="wechat"]'],
        "text_patterns": ["WeChat Login", "微信登录"]
    },
    "qq": {
        "selectors": ['.qq-btn', 'img[src*="qq"]'],
        "text_patterns": ["QQ Login", "QQ登录"]
    }
}

# Emoji mapping for Telegram messages
PROVIDER_EMOJI = {
    "google": "🔵",
    "apple": "⚫",
    "microsoft": "🔴",
    "github": "⚫",
    "discord": "🟣",
    "wechat": "🟢",
    "qq": "🔵"
}


def detect_oauth_provider(url: str) -> Optional[str]:
    """Detect which OAuth provider a URL belongs to."""
    for provider, config in OAUTH_PROVIDERS.items():
        for domain in config["domains"]:
            if domain in url:
                return provider
    return None


def format_provider_list(providers: List[str]) -> str:
    """Format provider list for Telegram selection."""
    lines = []
    emojis = {"1️⃣": "google", "2️⃣": "apple", "3️⃣": "microsoft", 
              "4️⃣": "github", "5️⃣": "discord", "6️⃣": "wechat", "7️⃣": "qq"}
    
    for i, provider in enumerate(providers, 1):
        emoji = PROVIDER_EMOJI.get(provider, "🔐")
        name = provider.capitalize()
        lines.append(f"{i}️⃣ {emoji} {name}")
    
    return "\n".join(lines)


def create_confirmation_message(site: str, provider: str) -> str:
    """Create OAuth confirmation message."""
    emoji = PROVIDER_EMOJI.get(provider, "🔐")
    return f"""🔐 {site} requests {provider.upper()} login.

{emoji} Provider: {provider.capitalize()}
📋 Action: Authorize access to your account

Reply "yes" to confirm, or anything else to cancel."""


def get_click_sequence(provider: str, step: str) -> str:
    """Get click selector for a specific step."""
    if provider in OAUTH_PROVIDERS:
        selectors = OAUTH_PROVIDERS[provider].get("selectors", {})
        return selectors.get(step, "")
    return ""


def detect_oauth_buttons(page_content: str) -> List[str]:
    """Detect available OAuth buttons on a login page."""
    found = []
    
    for provider, config in OAUTH_BUTTONS.items():
        # Check for selectors
        for selector in config["selectors"]:
            if selector in page_content:
                found.append(provider)
                break
        else:
            # Check for text patterns
            for text in config["text_patterns"]:
                if text.lower() in page_content.lower():
                    found.append(provider)
                    break
    
    return list(set(found))


def main():
    """Main function for OAuth helper."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 oauth_helper.py <detect|confirm> [url]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "detect" and len(sys.argv) > 2:
        url = sys.argv[2]
        provider = detect_oauth_provider(url)
        if provider:
            print(f"Detected OAuth provider: {provider}")
        else:
            print("No OAuth provider detected")
    
    elif command == "providers" and len(sys.argv) > 2:
        page_content = sys.argv[2]
        providers = detect_oauth_buttons(page_content)
        print(f"Available providers: {', '.join(providers)}")
    
    else:
        print("Usage: python3 oauth_helper.py <detect|confirm> [url]")


if __name__ == "__main__":
    main()
