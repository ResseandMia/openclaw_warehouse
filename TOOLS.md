# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without sharing your infrastructure.

---

## API 凭证

### 微信公众号
- **公众号**: Resse的独立站
- **用途**: wechat-publisher 发布文章到公众号

```bash
export WECHAT_APP_ID=wx4689509a2ae864d9
export WECHAT_APP_SECRET=46267614dc6edf23436cf32abcf450a3
```

### TranscriptAPI
- **用途**: YouTube 字幕提取
- **官网**: https://transcriptapi.com

```bash
export TRANSCRIPT_API_KEY="sk_Pbx0hxMHKMtQfQNSJB8At2ZvLVhRBNj8lZpBZhwoN8I"
```

### 速创 Nano Banana API (第三方)
- **用途**: AI图片生成（小红书配图）
- **官网**: https://api.wuyinkeji.com
- **控制台**: 密钥管理查看 Authorization

**接口地址**:
- 生成图片: `POST https://api.wuyinkeji.com/api/img/nanoBanana-pro`
- 查询状态: `GET https://api.wuyinkeji.com/api/img/drawDetail`

**请求Header**:
```
Content-Type: application/json;charset:utf-8;
Authorization: 你的密钥
```

**请求参数**:
- `prompt` (必填): 图片生成指令
- `img_url` (可选): 参考图片URL（数组）
- `aspectRatio` (可选): 比例 (auto/1:1/16:9/9:16/4:3/3:4/3:2/2:3/5:4/4:5/21:9)
- `imageSize` (可选): 大小 (1K/2K/4K) 默认1K

**返回格式**:
```json
{
  "msg": "成功",
  "data": { "id": 23 },
  "code": 200
}
```

**状态码**:
- 0: 排队中
- 1: 生成中
- 2: 成功
- 3: 失败

```bash
export NANOBANANA_KEY="RS3onk9L9pkY237VGMRsJIWsXG"
export NANOBANANA_API_URL="https://api.wuyinkeji.com/api/img/nanoBanana-pro"
```

**注意**: API Key 已配置，可直接使用。

---

Add whatever helps you do your job. This is your cheat sheet.