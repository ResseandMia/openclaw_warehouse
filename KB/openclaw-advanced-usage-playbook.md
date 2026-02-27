# OpenClaw/OpenCloud 高级用法：可落地 Playbook

来源：视频字幕（模型容灾/多认证轮换/记忆检索/云端控本地 node/多 Agent 协作模式）。本文把它翻译成 OpenClaw 的“能直接照做”的步骤。

## 一句话结论
把 OpenClaw 当成“脑（Gateway）+ 手脚（nodes）+ 记忆（Markdown+向量检索）+ 团队（隔离 agents）”，先把模型容灾和权限边界搭好，再做多 Agent 工作流，稳定性会立刻上一个台阶。

## 1) 模型容灾（primary + fallbacks）

### 目标
主模型限流/额度/认证失败时自动切到备用模型，避免“主模型挂了整套系统不能用”。

### 核心配置键
- `agents.defaults.model.primary`
- `agents.defaults.model.fallbacks`（按顺序）

### 推荐操作（CLI 优先）
- 查看当前解析结果：`openclaw models status`
- 设置默认模型：`openclaw models set <provider/model-or-alias>`
- 管理回退链：
  - `openclaw models fallbacks list`
  - `openclaw models fallbacks add <provider/model>`
  - `openclaw models fallbacks remove <provider/model>`
  - `openclaw models fallbacks clear`

### 运行时规则（重要）
OpenClaw 故障转移分两层：
1. 同一提供商内：认证配置文件（profiles）轮换 + 冷却退避。
2. 提供商都失败：推进到 `agents.defaults.model.fallbacks` 的下一个模型。

## 2) 多认证/多账号轮换（Auth profiles）

### 目标
同一 provider 下配置多个 OAuth/API key 账户：A 限流/欠费/过期时自动切到 B。

### 关键文件/概念
- 每个 agent 独立：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- profiles 支持 OAuth + API key；OpenClaw 会做 cooldown/disabled 退避。

### 推荐操作
- 登录 OAuth：`openclaw models auth login --provider <id>`
- 添加/粘贴 token：`openclaw models auth setup-token` / `openclaw models auth paste-token`
- 验证（会发真实请求，可能消耗额度）：`openclaw models status --probe`

## 3) 记忆检索（Memory search：Markdown + sessions，可选混合搜索）

### 目标
让系统“越用越聪明”：能从 `MEMORY.md` + `memory/*.md`（以及可选 sessions）里语义检索历史。

### 默认记忆载体（事实源）
- `memory/YYYY-MM-DD.md`：日记式追加
- `MEMORY.md`：长期沉淀（注意隐私边界：不应在群聊上下文加载）

### 推荐配置（远程嵌入：Gemini 示例）
- `agents.defaults.memorySearch.provider = "gemini"`
- `agents.defaults.memorySearch.model = "gemini-embedding-001"`
- `agents.defaults.memorySearch.remote.apiKey = "<GEMINI_API_KEY>"`
- 可选：`agents.defaults.memorySearch.extraPaths = [...]`（把额外笔记目录纳入索引）
- 可选：启用实验性 session memory（以你当前版本 schema 为准）

### 验收
写入一条独特信息到 `memory/YYYY-MM-DD.md`，然后用语义问题（同义转述）做 `memory_search`，看是否能命中。

## 4) 云端 Gateway 控本地机器（node host + 必要时 SSH 隧道）

### 目标
让云端 Gateway 当“大脑”，本地机器当“执行端”（命令/浏览器/屏幕/相机），不需要内网穿透（本地主动出站）。

### 典型架构
- Gateway：接收消息、跑模型、做路由。
- Node host：执行 `system.run` / `system.which` 等（受 exec approvals/allowlist 限制）。

### 启动节点（前台）
在本地机器上：
- `openclaw node run --host <gateway-host> --port 18789 --display-name "My Node"`
- 认证：设置 `OPENCLAW_GATEWAY_TOKEN`（来自 `gateway.auth.token`）

### 如果 Gateway 只绑定 loopback（远程不可直连）
用 SSH 转发把远端 `127.0.0.1:18789` 暴露到本地端口：
- `ssh -N -L 18790:127.0.0.1:18789 user@gateway-host`
- 然后 node 连：`openclaw node run --host 127.0.0.1 --port 18790 ...`

### 安全落地（强烈建议）
- 把节点执行改成 allowlist：`openclaw config set tools.exec.security allowlist`
- 给节点加入允许列表命令：`openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/uname"`

### 验收
- `openclaw nodes status`
- 对指定 node 跑一次命令（需要时加 `host=node` / `node=<id>`）

## 5) 多 Agent 团队协作（流水线 / DAG 并行 / 辩论）

### 目标
把“写代码/测试/文档/审查”变成可复用工作流，提升交付稳定性。

### 最小可落地做法（不用先写 skill）
- 创建 4 个隔离 agent：coder/tester/docs/reviewer（各自独立 workspace + auth + sessions）。
- 由主 agent 调度：把任务拆成阶段并汇总交付。

### 三种模式的落地模板
- 线性流水线：coder -> tester -> docs -> reviewer -> 主 agent 汇总交付包
- DAG 并行：coder 与 docs 并行；接口定稿后 tester 并行跑；reviewer 最后关口
- 辩论：性能/安全/可维护性三方各给方案 -> 第二轮互相反驳 -> 主 agent 裁决并生成行动项

### 验收标准（建议固定一个 demo）
- 代码可运行 + 测试通过 + README 可复现 + reviewer 给出风险与改进清单。

## 快速检查清单（从 0 到 1）
1. `openclaw models status`（默认模型 + fallbacks 解析正确）
2. `openclaw models status --probe`（认证可用，注意会消耗额度）
3. 记忆：写 `memory/YYYY-MM-DD.md` -> `memory_search` 命中
4. nodes：`openclaw nodes pending/approve` -> `openclaw nodes status` connected
5. 多 agent：为 coder/tester/docs/reviewer 明确权限边界（exec/write/browser）
