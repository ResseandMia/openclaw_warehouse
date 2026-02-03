---
name: imap-smtp-email
description: |
  Read and send email via IMAP/SMTP. Check for new/unread messages, fetch content, search mailboxes, mark as read/unread, and send emails with attachments. Works with any IMAP/SMTP server including Gmail, Outlook, 163.com, vip.163.com, 126.com, vip.126.com, 188.com, and vip.188.com.
---

# IMAP/SMTP Email Skill

邮件收发工具 - 支持 IMAP/SMTP 协议

## Features

- 📬 **邮件接收** - IMAP 协议读取邮件
- 📧 **邮件发送** - SMTP 协议发送邮件
- 🔍 **邮件搜索** - 搜索邮箱内容
- 📁 **附件下载** - 下载邮件附件
- ✅ **标记管理** - 标记已读/未读
- 📋 **文件夹管理** - 列出和选择文件夹

## Supported Providers

| Provider | IMAP | SMTP | Notes |
|----------|------|------|-------|
| Gmail | imap.gmail.com | smtp.gmail.com | 需启用 2FA + App Password |
| Outlook | outlook.office365.com | smtp.office365.com | |
| 163.com | imap.163.com | smtp.163.com | |
| vip.163.com | imap.vip.163.com | smtp.vip.163.com | |
| 126.com | imap.126.com | smtp.126.com | |
| vip.126.com | imap.vip.126.com | smtp.vip.126.com | |
| 188.com | imap.188.com | smtp.188.com | |
| vip.188.com | imap.vip.188.com | smtp.vip.188.com | |

## Usage

**检查新邮件：**
```
"检查 Gmail 新邮件"
"查看未读邮件"

**发送邮件：**
```
"发送邮件到 xxx@xxx.com"
"发送带附件的邮件"
```

**下载附件：**
```
"下载邮件附件"
"下载到指定目录"
```

## Configuration

Required environment variables:
```bash
# IMAP 配置
IMAP_HOST=imap.example.com
IMAP_PORT=993
IMAP_USER=your@email.com
IMAP_PASSWORD=your_password

# SMTP 配置  
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=your@email.com
SMTP_PASSWORD=your_password
```

### Gmail 特殊配置

1. 启用两步验证: https://myaccount.google.com/security
2. 创建 App Password: https://security.google.com/settings/security/apppasswords
3. 启用 IMAP: https://mail.google.com/settings/gmail/imap

## Commands

### List Folders

```bash
python3 scripts/email.py imap folders
```

### List Messages

```bash
python3 scripts/email.py imap list --folder INBOX --limit 10
```

### Search Messages

```bash
python3 scripts/email.py imap search --query "keyword" --folder INBOX
```

### Get Message

```bash
python3 scripts/email.py imap get --id MESSAGE_ID --include-body
```

### Mark as Read/Unread

```bash
python3 scripts/email.py imap mark --id MESSAGE_ID --read
python3 scripts/email.py imap mark --id MESSAGE_ID --unread
```

### Download Attachments

```bash
python3 scripts/email.py imap download --id MESSAGE_ID --output ./downloads
```

### Send Email

```bash
python3 scripts/email.py smtp send \
  --to "recipient@example.com" \
  --subject "邮件标题" \
  --body "邮件内容"
```

### Send with Attachment

```bash
python3 scripts/email.py smtp send \
  --to "recipient@example.com" \
  --subject "邮件标题" \
  --body "邮件内容" \
  --attachment /path/to/file.pdf
```

## Output Format

All commands return standardized JSON:

```json
{
  "success": true,
  "data": {...},
  "meta": {
    "command": "imap list",
    "timestamp": "2026-02-03T16:00:00Z"
  }
}
```

## Email Search Options

| Option | Description |
|--------|-------------|
| ALL | All messages |
| UNSEEN | Unread messages |
| SEEN | Read messages |
| FLAGGED | Flagged messages |
| UNFLAGGED | Unflagged messages |
| SUBJECT "keyword" | Subject contains keyword |
| FROM "keyword" | From contains keyword |
| BODY "keyword" | Body contains keyword |
| SINCE date | Since date |
| BEFORE date | Before date |

## Error Handling

- Authentication failed → Check credentials
- Connection timeout → Check server/port
- Invalid folder → List folders first
- Attachment not found → Verify message ID
- Rate limits → Respect server limits

## Automation Examples

### Daily Email Digest

```bash
#!/bin/bash
# Get unread email count

UNREAD=$(python3 scripts/email.py imap search --query UNSEEN | jq '.count')
echo "未读邮件: $UNREAD"

# List recent emails
python3 scripts/email.py imap list --folder INBOX --limit 5
```

### Download All Attachments from Sender

```bash
#!/bin/bash
# Download attachments from specific sender

MESSAGES=$(python3 scripts/email.py imap search --query "FROM sender@example.com")
for ID in $(echo $MESSAGES | jq -r '.[].id'); do
  python3 scripts/email.py imap download --id $ID --output ./attachments
done
```

### Send Report Email

```bash
#!/bin/bash
# Send daily report

TODAY=$(date +%Y-%m-%d)
python3 scripts/email.py smtp send \
  --to "team@example.com" \
  --subject "每日报告 - $TODAY" \
  --body "$(cat daily_report.txt)" \
  --attachment daily_report.pdf
```

## Security Notes

- Never commit credentials to version control
- Use App Passwords for Gmail/Outlook
- Consider using environment variables
- Enable 2FA on email accounts

## Source

Skill from ClawHub by @gzlicanyi
- ClawHub: https://www.clawhub.ai/gzlicanyi/imap-smtp-email
