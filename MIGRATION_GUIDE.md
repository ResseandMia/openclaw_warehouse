# OpenClaw 迁移文档

## 📋 概述

将 OpenClaw 从当前服务器迁移到新服务器。

**当前环境：**
- 工作目录：`/root/.openclaw/workspace`
- Git 仓库：https://github.com/ResseandMia/openclaw_warehouse
- 定时任务：早安提醒、晚间总结、发传单提醒

---

## 🚀 快速开始

### 步骤 1：克隆代码

```bash
cd /root/.openclaw/workspace
git clone https://github.com/ResseandMia/openclaw_workspace.git .
```

### 步骤 2：配置 API 凭据

```bash
openclaw configure
```

需要配置的凭据：

| 服务 | 如何获取 |
|------|----------|
| **Telegram Bot** | @BotFather 创建 |
| **Notion API** | https://www.notion.so/my-integrations |
| **GitHub Token** | https://github.com/settings/tokens |
| **ImgBB API** | https://api.imgbb.com |

### 步骤 3：重建定时任务

```bash
# 早安提醒（每天 8:00 北京时间）
openclaw cron add --name "早安提醒" --schedule "0 8 * * *" --tz "Asia/Shanghai" --payload '{"kind":"systemEvent","text":"🌅 早上好！..."}' --session-target "main"

# 发传单提醒（每天 15:00 北京时间）
openclaw cron add --name "发传单提醒" --schedule "0 15 * * *" --tz "Asia/Shanghai" --payload '{"kind":"systemEvent","text":"⏰ 下午3:00了！该发传单了"}' --session-target "main"

# 晚间总结（每天 22:00 北京时间）
openclaw cron add --name "晚间总结" --schedule "0 22 * * *" --tz "Asia/Shanghai" --payload '{"kind":"systemEvent","text":"🌙 晚上好！今日总结..."}' --session-target "main"

# 每日复盘（每天 00:00 北京时间）
openclaw cron add --name "每日复盘" --schedule "0 0 * * *" --tz "Asia/Shanghai" --payload '{"kind":"systemEvent","text":"📅 每日复盘任务"}' --session-target "main"
```

### 步骤 4：重启 Gateway

```bash
openclaw gateway restart
```

---

## 📁 重要文件

| 文件 | 说明 | 迁移方式 |
|------|------|----------|
| `scripts/` | 定时任务脚本 | Git 自动同步 |
| `skills/` | Skills 目录 | Git 自动同步 |
| `memory/` | 记忆文件 | Git 自动同步 |
| `config.json` | API 凭据 | **手动配置** |
| `cron` | 定时任务 | **手动重建** |

---

## 🔧 手动配置

### 1. config.json

在 `/root/.openclaw/workspace/config.json` 中配置：

```json
{
  "notion": {
    "api_key": "YOUR_NOTION_API_KEY"
  },
  "github": {
    "repo_url": "https://github.com/ResseandMia/openclaw_warehouse",
    "token": "YOUR_GITHUB_TOKEN"
  },
  "imgbb": {
    "api_key": "YOUR_IMGBB_API_KEY"
  }
}
```

### 2. Telegram Bot

```bash
openclaw channels login --channel telegram
# 或
openclaw config set --channel telegram --token "YOUR_BOT_TOKEN"
```

### 3. Notion 数据库

**Todo 数据库：**
- ID: `2fd83d24-986d-810e-b00b-dfcfa9e53935`
- 链接: https://www.notion.so/2fd83d24986d810eb00bdfcfa9e53935

**竞争对手广告素材库：**
- ID: `2fd83d24-986d-81fd-b54a-e5d83c646d21`
- 链接: https://www.notion.so/2fd83d24986d81fdb54ae5d83c646d21

---

## 📝 常用命令

```bash
# 重启 Gateway
openclaw gateway restart

# 查看状态
openclaw status

# 查看定时任务
openclaw cron list

# 测试早安脚本
python3 /root/.openclaw/workspace/scripts/morning_reminder.py

# 测试晚间脚本
python3 /root/.openclaw/workspace/scripts/evening_summary.py

# 发送测试消息
openclaw message send --target "YOUR_CHAT_ID" --message "测试消息"
```

---

## ⚠️ 注意事项

1. **Token 安全**
   - 不要将 config.json 上传到 Git
   - 已添加 .gitignore 保护

2. **定时任务时区**
   - 所有任务使用 `Asia/Shanghai` 时区
   - 注意：北京时间和 UTC 相差 8 小时

3. **Chrome Relay**
   - 如果使用浏览器功能，需要重新连接
   - 在 Chrome 浏览器中点击 OpenClaw 扩展图标

---

## 🔗 有用链接

- OpenClaw 文档: https://docs.openclaw.ai
- GitHub 仓库: https://github.com/ResseandMia/openclaw_workspace
- ClawHub Skills: https://clawhub.ai

---

## ❓ 常见问题

**Q: 定时任务不执行？**
A: 检查 Gateway 状态：`openclaw status`

**Q: 收不到消息？**
A: 检查 Telegram 连接：`openclaw channels list`

**Q: Notion 同步失败？**
A: 验证 API Token 权限

---

*文档生成时间: 2026-02-05*
