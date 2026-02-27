# Learning Packet Template (V4)

Purpose: turn a source (video/article/thread) into a reusable packet that another agent can execute.

Note: you only propose actions. Execution/assignment is decided by Mimi.

## 0) Metadata
- Topic: OpenClaw 高级用法（模型容灾/多认证轮换/记忆检索/nodes 远程执行/多 Agent 协作）
- Source link(s): 视频字幕（OpenClaw/OpenCloud 高级用法；内部转写）
- Date learned: 2026-02-27
- Intended user (who will run this): 咪咪大总管（决策/派单）+ 代码喵/勤务喵（落地执行）

## 1) One-line takeaway
把 OpenClaw 当成“Gateway(脑)+Nodes(手脚)+Memory(可检索笔记)+隔离 Agents(团队)”来配置：先容灾+权限，再上节点与多 Agent 工作流，系统稳定性和可用性会明显提升。

## 2) 5 key points
1. 故障转移分两层：同 provider 内先轮换 auth profiles（冷却/禁用退避），全部失败才推进到 `agents.defaults.model.fallbacks`。
2. 模型容灾优先用 CLI 管（`openclaw models set` + `openclaw models fallbacks ...`），减少手改配置漂移。
3. 记忆的事实源是工作区 Markdown（`memory/YYYY-MM-DD.md` + 可选 `MEMORY.md`）；向量检索需要嵌入 provider（OpenAI/Gemini/local）。
4. 云端 Gateway 控本地机器的正解是 node host：本地节点主动出站连 Gateway；Gateway loopback 时用 SSH `-L` 端口转发。
5. 多 Agent 的价值不在“更多机器人”，而在“隔离工作区/认证/会话/权限”，把 coder/tester/docs/reviewer 流程化。

## 3) Action Pack (required)
At least 1 Quick Win that takes <= 10 minutes.

### Quick Win (<= 10m)
- Suggested owner: 勤务喵（执行 CLI）
- Need Mimi decision (yes/no + reason): no（只做状态检查与输出记录，不改动配置）
- Steps:
  1) 运行：`openclaw models status --plain`
  2) 记录当前 `default model`、`fallbacks`、以及认证概览（截图或粘贴到交付）
- Done (definition of done): 已拿到一份可读的“当前默认模型+fallback链+认证状态”快照
- Verification: 输出中能看到当前默认模型与 fallbacks（哪怕为空）
- Rollback: 无（只读操作）

## 4) Full playbook
### Preconditions
- Required accounts/keys:
  - 至少一个可用的模型 provider（OpenAI/Anthropic/Gemini/...）
  - 若启用记忆检索：一个可用的 embedding key（OpenAI 或 Gemini），或本地 GGUF 模型
- Required OS/tools:
  - Gateway 侧能运行 `openclaw` CLI
  - 需要 nodes 时：节点机器也能运行 `openclaw node run`
- Permissions needed:
  - 修改配置/认证需要能写 `~/.openclaw/openclaw.json` 与 agentDir

### Steps (copy/paste friendly)
1) 配置模型容灾（默认模型 + 回退链）

```bash
openclaw models status
openclaw models set <provider/model-or-alias>
openclaw models fallbacks list
openclaw models fallbacks add <provider/model>
openclaw models fallbacks add <provider/model>
openclaw models fallbacks list
```

预期：`fallbacks list` 能按顺序看到你添加的模型。

2) 配置多认证/多账号（同 provider 轮换）

```bash
openclaw models auth login --provider <providerId>
# 或
openclaw models auth paste-token

# 探测（会真实发请求，可能消耗额度）
openclaw models status --probe
```

预期：probe 不报错；如果某个 profile 失败，后续请求会被冷却/轮换。

3) 记忆检索（Memory Search）

最小目标：让 `memory_search` 可用，并能命中 `memory/*.md`。

配置方向（示例：Gemini 远程嵌入；具体 key 放你自己的密钥管理里）：

```js
// ~/.openclaw/openclaw.json (JSON5)
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "gemini",
        model: "gemini-embedding-001",
        remote: { apiKey: "<GEMINI_API_KEY>" }
      }
    }
  }
}
```

预期：重启后 `memory_search` 能返回命中文段。

4) nodes：云端 Gateway 控本地 node host

在节点机器上（前台运行）：

```bash
export OPENCLAW_GATEWAY_TOKEN="<gateway.auth.token>"
openclaw node run --host <gateway-host> --port 18789 --display-name "My Node"
```

如果 Gateway 绑定 loopback（远端不可直连），先在节点机建隧道：

```bash
ssh -N -L 18790:127.0.0.1:18789 user@gateway-host
export OPENCLAW_GATEWAY_TOKEN="<gateway.auth.token>"
openclaw node run --host 127.0.0.1 --port 18790 --display-name "My Node"
```

然后在 Gateway 侧批准/查看：

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes status
```

5) 多 Agent 协作（隔离团队）

建议 4 个角色：coder/tester/docs/reviewer，各自隔离 workspace + auth + sessions。由主 agent 调度流水线或 DAG 并行。

### Verification (what success looks like)
- 模型容灾：`openclaw models status` 显示 default + fallbacks；故障时能自动切换（日志出现 fallback 记录）。
- 认证轮换：同 provider 多 profile 下，遇到限流/欠费会轮换并进入 cooldown/disabled。
- 记忆检索：在 `memory/YYYY-MM-DD.md` 写入一条独特信息后，`memory_search` 用同义问法能命中。
- nodes：`openclaw nodes status` 显示 connected；在会话里设置 `host=node` 的 exec 能在节点执行。
- 多 Agent：同一任务能稳定产出（代码+测试+文档+审查），且互不污染上下文。

### Failure modes + fixes
- Symptom: `openclaw models status --probe` 失败
  - Likely cause: auth/token 过期或 provider 配置缺失
  - Fix: 重新 `models auth login` / `paste-token`，或更换 provider
- Symptom: `memory_search` 不可用 / 显示 unavailable
  - Likely cause: embedding provider 未配置/无 key
  - Fix: 配置 `agents.defaults.memorySearch.*` 并重启
- Symptom: node 连不上 Gateway
  - Likely cause: Gateway bind=loopback 或防火墙
  - Fix: SSH `-L` 隧道，或把 Gateway 暴露到 tailnet/反代后再连

## 5) Notes / caveats
- Cost / rate limits: `--probe` 会发真实请求；fallback 与轮换会因 provider 限流触发更多请求。
- Security / privacy: 多人/多群共享 Gateway 时强烈建议隔离 agent + sandbox + fs 限制；node exec 建议 default=allowlist。
- Portability: Windows/macOS/Linux 均可；SSH 隧道方案通用。

## 6) Output artifacts
- Files created/updated:
  - `KB/packets/2026-02-27-openclaw-advanced-usage.md`
- KB path:
  - `KB/openclaw-advanced-usage-playbook.md`（完整 playbook）
  - `KB/packets/2026-02-27-openclaw-advanced-usage.md`（本 packet）
