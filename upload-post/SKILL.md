---
name: upload-post
description: |
  Upload Videos, Photos & Text to TikTok, Instagram, YouTube, X, LinkedIn, Facebook, Threads, Pinterest, Reddit & Bluesky via Upload-Post API. Supports scheduling, analytics, FFmpeg processing, and upload history.
---

# Upload Post Skill

社交媒体发布工具 - 一键发布到多个平台

## Features

- 🎥 **视频发布** - TikTok, YouTube, Instagram, Facebook, LinkedIn
- 📸 **图片发布** - Instagram, Pinterest, Facebook, Threads
- 🖊️ **文本发布** - X (Twitter), Reddit, LinkedIn, Facebook, Threads, Bluesky
- 📁 **文档发布** - 支持多种文档格式
- ⏰ **定时发布** - 预约发布时间
- 📊 **数据分析** - 跨平台统计
- 🎬 **FFmpeg 处理** - 视频转换和编辑
- 📋 **历史记录** - 管理上传历史

## Supported Platforms

| Platform | Video | Photo | Text | Document |
|----------|-------|-------|------|----------|
| TikTok | ✅ | ✅ | ✅ | - |
| Instagram | ✅ | ✅ | ✅ | - |
| YouTube | ✅ | - | ✅ | ✅ |
| X (Twitter) | ✅ | ✅ | ✅ | - |
| LinkedIn | ✅ | ✅ | ✅ | ✅ |
| Facebook | ✅ | ✅ | ✅ | ✅ |
| Threads | - | ✅ | ✅ | - |
| Pinterest | - | ✅ | ✅ | - |
| Reddit | ✅ | ✅ | ✅ | - |
| Bluesky | - | - | ✅ | - |

## Usage

**发布视频：**
```
"发布视频到 TikTok 和 Instagram"
"上传 YouTube 视频"
```

**发布图片：**
```
"发图片到 Pinterest"
"Instagram 发图"
```

**定时发布：**
```
"预约明天早上 9 点发布"
"设置定时发布"
```

## Configuration

Required environment variables:
```bash
# Upload-Post API
UPLOAD_POST_API_KEY=your_api_key
UPLOAD_POST_API_URL=https://api.upload-post.com/v1
```

Optional settings:
```bash
# FFmpeg path (for video processing)
FFMPEG_PATH=/usr/bin/ffmpeg

# Default upload settings
DEFAULT_PRIVACY=public
AUTO_PROCESS=true
```

## Commands

### Upload Video

```bash
python3 scripts/upload.py video \
  --file video.mp4 \
  --platforms tiktok,youtube,instagram \
  --title "Video Title" \
  --description "Video description..."
```

### Upload Photo

```bash
python3 scripts/upload.py photo \
  --file image.jpg \
  --platforms instagram,pinterest,facebook \
  --caption "Photo caption"
```

### Post Text

```bash
python3 scripts/upload.py text \
  --content "Your post text here" \
  --platforms twitter,linkedin,reddit
```

### Schedule Post

```bash
python3 scripts/upload.py schedule \
  --file video.mp4 \
  --platforms youtube \
  --schedule "2026-02-04 09:00:00" \
  --title "Scheduled Video"
```

### List Upload History

```bash
python3 scripts/upload.py history --limit 50
```

### Get Analytics

```bash
python3 scripts/upload.py analytics --platform tiktok --days 30
```

### Process Video (FFmpeg)

```bash
python3 scripts/upload.py process \
  --input video.mp4 \
  --output optimized.mp4 \
  --resize 1080x1920 \
  --compress
```

## Platform-Specific Options

### TikTok
```bash
--disable-comment       # 关闭评论
--duet-off            # 禁止合拍
--stitch-off          # 禁止合拍
--visibility private  # 设为私密
```

### Instagram
```bash
--story              # 作为 Stories 发布
--reel              # 作为 Reels 发布
--carousel          # 多图轮播
--location "NYC"    # 添加位置
```

### YouTube
```bash
--privacy private    # 私密发布
--playlist "My List" # 添加到播放列表
--tags "python,tutorial" # 标签
```

### X (Twitter)
```bash
--thread            # 作为线程发布
--scheduled         # 定时推文
```

## Output Format

All commands return standardized JSON:

```json
{
  "success": true,
  "data": {
    "post_id": "abc123",
    "platforms": ["tiktok", "instagram"],
    "urls": {
      "tiktok": "https://tiktok.com/@user/video/...",
      "instagram": "https://instagram.com/p/..."
    },
    "scheduled_time": "2026-02-04T09:00:00Z"
  },
  "meta": {
    "command": "upload video",
    "timestamp": "2026-02-03T16:00:00Z"
  }
}
```

## Error Handling

- API rate limit → Retry with backoff
- Invalid file → Check file format
- Platform error → Check platform-specific options
- Network issues → Retry 3 times

## Automation Examples

### Multi-Platform Video Launch

```bash
#!/bin/bash
# Launch video across all platforms

python3 scripts/upload.py video \
  --file launch_video.mp4 \
  --platforms youtube,tiktok,instagram,facebook \
  --title "🚀 Product Launch 2026" \
  --description "Exciting news! Our new product is here..." \
  --schedule "2026-02-10 10:00:00"
```

### Daily Social Media Batch

```bash
#!/bin/bash
# Post daily content to all platforms

for platform in twitter linkedin instagram; do
  python3 scripts/upload.py photo \
    --file "daily_$platform.jpg" \
    --platforms $platform \
    --caption "$(date +%Y-%m-%d) Daily Update"
done
```

### Content Repurposing

```bash
#!/bin/bash
# Convert long video to short clips

python3 scripts/upload.py process \
  --input long_video.mp4 \
  --output clip_1.mp4 \
  --start 0 --duration 60 \
  --resize 1080x1920

# Upload as TikTok/Reels
python3 scripts/upload.py video \
  --file clip_1.mp4 \
  --platforms tiktok,instagram \
  --title "Best moments clip"
```

## Analytics Dashboard

```bash
# Get all-time stats
python3 scripts/upload.py analytics

# Platform-specific
python3 scripts/upload.py analytics --platform youtube --days 30

# Export to JSON
python3 scripts/upload.py analytics --export analytics.json
```

## FFmpeg Processing Options

| Option | Description |
|--------|-------------|
| --resize WxH | Resize video |
| --compress | Reduce file size |
| --convert mp4 | Convert format |
| --trim start:end | Trim video |
| --extract-audio | Get audio only |
| --thumbnail | Generate thumbnail |

## Limitations

- Some platforms require approval for API access
- Upload limits vary by platform and account type
- Scheduling may be delayed during high-traffic periods

## Links

- Upload-Post API: https://upload-post.com
- Platform Guidelines: https://developers.facebook.com, etc.

## Source

Skill from ClawHub by @victorcavero14
- ClawHub: https://www.clawhub.ai/victorcavero14/upload-post
