# Learning Packet Template (V4)

Purpose: turn a source (video/article/thread) into a reusable packet that another agent can execute.

Note: you only propose actions. Execution/assignment is decided by Mimi.

## 0) Metadata
- Topic: 用 Cloud Code Hooks + OpenClaw Webhooks 实现“零轮询”回调，显著降低 token 消耗
- Source link(s): 视频字幕（Cloud Code hooks/Agent Teams + OpenClaw 回调；内部转写）
- Date learned: 2026-02-27
- Intended user (who will run this): 咪咪大总管（决定是否启用 hooks/暴露方式）+ 代码喵（写 hook 脚本/集成）

## 1) One-line takeaway
把“OpenClaw 盯着 Cloud Code 轮询”改成“Cloud Code 结束后回调 OpenClaw”，token 成本从 O(运行时) 变成 O(1)：只消耗派发一次 + 收尾一次。

## 2) 5 key points
1. 轮询耗 token 的根因：每几秒一次状态检查会持续触发模型/工具回合，耗时越久烧得越多。
2. 回调式工作流：OpenClaw 只负责启动 Cloud Code（后台）+ 最后读取结果并发通知；中间完全不参与。
3. 回调双保险：用 Cloud Code 的 `stop` hook 做主回调；再加 `session end` 做兜底（防止 stop 未触发）。
4. OpenClaw 侧用 webhook 入口：`POST /hooks/wake`（轻量事件）或 `POST /hooks/agent`（可直接投递到指定群/频道）。
5. 必须做幂等：stop 与 session end 可能都触发；用 marker 文件或 runId 做“只发一次”。

## 3) Action Pack (required)
At least 1 Quick Win that takes <= 10 minutes.

### Quick Win (<= 10m)
- Suggested owner: 代码喵（本机测试）
- Need Mimi decision (yes/no + reason): yes（启用 `hooks.enabled` 会打开 HTTP 入口；需确认暴露范围/令牌管理/是否仅 loopback）
- Steps:
  1) 在 Gateway 配置启用 hooks（见下方配置块），并重启 gateway
  2) 运行一次 wake 测试：

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer <HOOKS_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"text":"[wake test] cloudcode hook","mode":"now"}'
```

- Done (definition of done): curl 返回 HTTP 200，且 Gateway 侧产生对应 system event（mode=now 时能触发即时心跳）
- Verification: curl 无 401/400；并能在会话/日志看到 wake 事件
- Rollback: 关闭 `hooks.enabled` 并重启 gateway（或把 bind 保持 loopback，避免对外暴露）

## 4) Full playbook
### Preconditions
- Required accounts/keys:
  - OpenClaw webhook token（与 gateway auth token 分开，建议专用）
- Required OS/tools:
  - Cloud Code/Claude Code 能运行 hooks 脚本（bash/node 任一）
  - `curl` 可用
- Permissions needed:
  - 可修改 `~/.openclaw/openclaw.json` 并重启 gateway

### Steps (copy/paste friendly)
1) OpenClaw：启用 webhook 入口

在 `~/.openclaw/openclaw.json`（JSON5）加入：

```js
{
  hooks: {
    enabled: true,
    token: "<HOOKS_TOKEN>",
    path: "/hooks",
  },
}
```

说明：
- 请求必须带 `Authorization: Bearer <HOOKS_TOKEN>`。

2) 选择回调端点

- 轻量事件：`POST /hooks/wake`

```json
{ "text": "Cloud Code finished: <runId>", "mode": "now" }
```

- 可直接投递到指定 Discord 频道：`POST /hooks/agent`

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer <HOOKS_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "CloudCode",
    "message": "Cloud Code finished. Path=<repoPath> Tests=<n> Duration=<t>",
    "wakeMode": "now",
    "deliver": true,
    "channel": "discord",
    "to": "channel:<DISCORD_CHANNEL_ID>"
  }'
```

预期：HTTP 202（异步），随后频道收到完成通知。

3) Cloud Code：写 hook 脚本（幂等）

核心原则：
- 从 result 文件读取必要信息（限制长度，例如 1k-8k 字符）
- 用 marker 文件保证只发送一次

示例（bash）：

```bash
#!/usr/bin/env bash
set -euo pipefail

GATEWAY_URL="${OPENCLAW_GATEWAY_URL:-http://127.0.0.1:18789}"
HOOKS_TOKEN="${OPENCLAW_HOOKS_TOKEN:?missing OPENCLAW_HOOKS_TOKEN}"
DISCORD_CHANNEL_ID="${DISCORD_CHANNEL_ID:?missing DISCORD_CHANNEL_ID}"

RUN_ID="${1:-unknown-run}"
RESULT_PATH="${2:-result.txt}"
MARKER_FILE=".openclaw_hook_sent_${RUN_ID}"

# Idempotency
if [ -f "$MARKER_FILE" ]; then
  exit 0
fi

touch "$MARKER_FILE"

RESULT_CONTENT="(missing result file)"
if [ -f "$RESULT_PATH" ]; then
  RESULT_CONTENT="$(head -c 4000 "$RESULT_PATH")"
fi

cat > payload.json <<EOF
{
  "name": "CloudCode",
  "message": "Cloud Code finished. runId=$RUN_ID\n\nResult (truncated):\n\n$RESULT_CONTENT",
  "wakeMode": "now",
  "deliver": true,
  "channel": "discord",
  "to": "channel:$DISCORD_CHANNEL_ID"
}
EOF

curl -sS -X POST "$GATEWAY_URL/hooks/agent" \
  -H "Authorization: Bearer $HOOKS_TOKEN" \
  -H 'Content-Type: application/json' \
  -d @payload.json
```

4) Cloud Code：注册两个 hooks
- 主：`stop` hook -> 调用脚本
- 兜底：`session end` hook -> 调用脚本（同 runId/marker，确保不重复）

### Verification (what success looks like)
- Cloud Code 跑一个 1-2 分钟任务：期间 OpenClaw 主会话不被阻塞、没有轮询输出。
- 任务结束后：目标频道只收到 1 条完成通知（stop 或 session end）。

### Failure modes + fixes
- Symptom: webhook 返回 401
  - Likely cause: token 不对 / header 缺失
  - Fix: 确认 `Authorization: Bearer <HOOKS_TOKEN>`；不要复用 gateway auth token
- Symptom: webhook 无法访问 gateway
  - Likely cause: gateway 仅 loopback 且 Cloud Code 不在同机
  - Fix: 通过 tailnet/反代/SSH 隧道让 Cloud Code 能访问 gateway
- Symptom: 重复通知
  - Likely cause: stop 与 session end 都触发
  - Fix: marker 文件幂等（按 runId）

## 5) Notes / caveats
- Cost / rate limits: 回调 payload 尽量小；大日志改成“产物路径/下载链接”。
- Security / privacy: hooks 是外部入口；强烈建议 loopback/tailnet + 专用 token；不要在日志里打印原始 payload。
- Portability: 所有系统可用；关键是 Cloud Code hook 注册方式与可达性。

## 6) Output artifacts
- Files created/updated:
  - `KB/packets/2026-02-27-cloudcode-hooks-zero-polling.md`
- KB path:
  - `KB/openclaw-cloudcode-hooks-zero-polling.md`（完整 playbook）
  - `KB/packets/2026-02-27-cloudcode-hooks-zero-polling.md`（本 packet）
