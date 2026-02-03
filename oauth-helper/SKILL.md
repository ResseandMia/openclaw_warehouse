---
name: oauth-helper
description: |
  Automate OAuth login flows with user confirmation via Telegram.
  Supports 7 providers: Google, Apple, Microsoft, GitHub, Discord, WeChat, QQ.
  Trigger: "login with" / "oauth" / "授权登录"
---

# OAuth Helper

Automate OAuth login with Telegram confirmation. Supports 7 major providers.

## Supported Providers

| Provider | Status | Detection Domain |
|----------|--------|------------------|
| Google | ✅ | accounts.google.com |
| Apple | ✅ | appleid.apple.com |
| Microsoft | ✅ | login.microsoftonline.com, login.live.com |
| GitHub | ✅ | github.com/login/oauth |
| Discord | ✅ | discord.com/oauth2 |
| WeChat | ✅ | open.weixin.qq.com |
| QQ | ✅ | graph.qq.com |

## Usage

**Login to a site with OAuth:**
```
"Login to [site name]"
"Authorize with Google"
"Use OAuth login"
```

**Example:**
```
User: Login to Kaggle for me

Agent:
1. Navigate to kaggle.com/account/login
2. Detect Google/Facebook/Yahoo options
3. Ask user to choose via Telegram
4. User selects Google
5. Click Google login
6. Confirm via Telegram
7. Login successful
```

## Workflow

### Flow A: Multiple Login Options
1. Open login page
2. Scan for OAuth buttons
3. Ask user to choose via Telegram
4. Click selected option
5. Continue to Flow B

### Flow B: OAuth Confirmation
1. Detect OAuth provider page
2. Extract target site info
3. Confirm with user via Telegram
4. Execute provider-specific clicks
5. Wait for redirect
6. Notify success

## Prerequisites

1. Clawd browser logged into OAuth providers (one-time setup)
2. Telegram channel configured

## One-Time Setup

Login to each provider in clawd browser:

```bash
# Google
browser action=navigate url=https://accounts.google.com

# Apple
browser action=navigate url=https://appleid.apple.com

# Microsoft
browser action=navigate url=https://login.live.com

# GitHub
browser action=navigate url=https://github.com/login

# Discord
browser action=navigate url=https://discord.com/login

# WeChat/QQ - Use QR scan, no pre-login needed
```

## Error Handling

- No user reply → Cancel and notify
- 2FA required → Prompt user manually
- QR timeout → Re-screenshot
- Login failed → Screenshot for debugging
