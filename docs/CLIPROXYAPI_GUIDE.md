# CLI Proxy API 接入指南

## 概述
CLI Proxy API 是一个代理服务器，可以将反重力 (Antigravity) CLI 转换为 OpenAI/Gemini/Claude 兼容的 API。

通过此工具，可以在 OpenClaw 中接入：
- **Claude Opus 4.6** (通过反重力 Pro 订阅)
- **Gemini 2.5 Pro** (通过反重力)
- 额度：每 5 小时刷新一次，Opus 4.6 额度非常充裕

## 已安装组件

```
openclaw_warehouse/
├── bin/
│   └── cli-proxy-api          # CLI Proxy API 二进制文件 (v6.8.35)
├── config/
│   └── cliproxyapi.yaml       # 配置文件
└── scripts/
    └── cliproxyapi.sh         # 启动/管理脚本
```

## 快速开始

### 1. 登录反重力账号

```bash
cd /root/.openclaw/workspace/openclaw_warehouse
./scripts/cliproxyapi.sh login-antigravity
```

这会打开浏览器进行 OAuth 登录，获取反重力 Pro 的访问凭证。

### 2. 启动代理服务

```bash
./scripts/cliproxyapi.sh start
```

服务启动后，API Endpoint: `http://127.0.0.1:8080/v1`

### 3. 在 OpenClaw 中配置

在 `openclaw.json` 中添加 provider:

```json
"models": {
  "providers": {
    "antigravity": {
      "baseUrl": "http://127.0.0.1:8080/v1",
      "apiKey": "dummy",
      "api": "openai-chat",
      "models": [
        {
          "id": "claude-opus-4-6",
          "name": "Claude Opus 4.6 (Antigravity)",
          "reasoning": true
        }
      ]
    }
  }
}
```

### 4. 设置模型

```bash
openclaw models set antigravity/claude-opus-4-6
```

## 管理命令

| 命令 | 说明 |
|------|------|
| `./scripts/cliproxyapi.sh start` | 启动服务 |
| `./scripts/cliproxyapi.sh stop` | 停止服务 |
| `./scripts/cliproxyapi.sh restart` | 重启服务 |
| `./scripts/cliproxyapi.sh status` | 查看状态 |
| `./scripts/cliproxyapi.sh login-antigravity` | 登录反重力 |

## 实际体验

根据用户反馈：
- 生成 100 多页的完整产品说明书，额度消耗极少
- 在 OpenClaw 里可以直接生成图片，效果不错，速度快
- 可以接管博客管理、部署脚本、写文档、做网站
- 生产力提升巨大

## 注意事项

1. **OAuth 登录**：必须通过浏览器完成 OAuth 授权，无法自动化
2. **Token 有效期**：登录凭证会过期，需要定期重新登录
3. **本地服务**：CLI Proxy API 作为本地服务运行，重启后需要重新启动
4. **额度查询**：通过反重力 CLI 或管理面板查看剩余额度

## 故障排除

### 服务无法启动
```bash
# 检查日志
tail -f /tmp/cliproxyapi.log
```

### 认证失效
```bash
# 重新登录
./scripts/cliproxyapi.sh login-antigravity
```

### 模型无法调用
```bash
# 检查服务状态
./scripts/cliproxyapi.sh status

# 检查 OpenClaw 配置
openclaw models status
```