---
name: feishu-integration
description: Save content to Feishu (飞书). Use when user wants to save notes, summaries, or documents to Feishu. Supports saving markdown content as Feishu documents with images.
---

# Feishu Integration

Save content to Feishu documents in a specified folder.

## Credentials

Store these securely:
- **App ID**: `cli_a9f4a51627781cb5`
- **App Secret**: `AkbOrmLW4E3rDBVpvPdsybhiKzcA5hZQ`
- **Folder ID**: `WvAKfx94cl8AO0dyV70cuKBhnab`

## Workflow

### 1. Get Access Token

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "cli_a9f4a51627781cb5", "app_secret": "AkbOrmLW4E3rDBVpvPdsybhiKzcA5hZQ"}'
```

Response contains `tenant_access_token` (expires 2 hours).

### 2. Create Document

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_token": "WvAKfx94cl8AO0dyV70cuKBhnab",
    "title": "Document Title"
  }'
```

Returns `document_id` and `document_revision_id`.

### 3. Update Document Content

Use block API to add content:

```bash
curl -s -X PUT "https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "block_type": 2,
        "text": {
          "elements": [{"text_run": {"content": "Your markdown content here"}}]
        }
      }
    ],
    "index": 0
  }'
```

## Block Types

| Type | Description |
|------|-------------|
| 2 | Text paragraph |
| 3 | Heading 1 |
| 4 | Heading 2 |
| 5 | Heading 3 |
| 10 | Image |
| 17 | Code block |

## Image Upload

1. Get upload URL:
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/images" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_type": "docx", "filename": "image.png"}'
```

2. Upload image bytes to returned `upload_url`

3. Use `image_key` in block content

## Automation Script

Use `scripts/save_to_feishu.py` for automated workflow:

```bash
python3 scripts/save_to_feishu.py \
  --title "播客摘要" \
  --content "Markdown content here" \
  --images "page_1.png,page_2.png"
```

## Error Handling

- `40001`: Invalid credentials - Check App ID/Secret
- `99991603`: Token expired - Refresh token
- `99991688`: Permission denied - Check folder access

## Rate Limits

- 100 requests/minute for most APIs
- Image upload: 10MB max per file
