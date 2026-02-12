---
name: claude-code-integration
description: |
  从 OpenClaw 调用 Claude Code 进行自动化开发。
  支持：项目开发、代码审查、Bug修复、规格驱动开发等。
  触发词："调用Claude Code"、"用Claude开发"、"Claude帮我写代码"
---

# Claude Code 集成 Skill

从 OpenClaw 调用 Claude Code 进行自动化开发的完整方案。

---

## 使用场景

1. **规格驱动开发** - 使用 OpenSpec/SpecKit 自动开发完整项目
2. **代码审查** - 自动分析代码质量、安全性、性能
3. **Bug修复** - 自动定位并修复代码中的问题
4. **功能开发** - 根据需求描述自动生成代码
5. **代码重构** - 优化现有代码结构和性能

---

## 前置要求

1. **Claude Code CLI 已安装**
   ```bash
   # macOS/Linux/WSL
   curl -fsSL https://claude.ai/install.sh | bash
   
   # Windows PowerShell
   irm https://claude.ai/install.ps1 | iex
   ```

2. **已登录 Claude Code**
   ```bash
   claude
   # 首次使用会提示登录
   ```

3. **项目目录已初始化 Git**（推荐）
   ```bash
   cd /your/project
   git init
   ```

---

## 使用方法

### 场景 1：规格驱动开发

**用户输入：**
> "调用 Claude Code，使用 OpenSpec 开发一个 X 风格的私人日记 Web 应用，要求具有输入框、时间线、情绪标签、图片上传功能"

**执行流程：**
```bash
cd /workspace/your-project && \
claude -p "使用 OpenSpec 开发一个 X 风格的私人日记 Web 应用。

需求：
1. 简单的发送输入框
2. 无限滚动时间线
3. 情绪标签功能
4. 图片上传功能
5. 日历快速跳转
6. 去年今日回顾

请使用规格驱动开发流程：
1. 先分析需求并创建规格文档
2. 根据规格实现代码
3. 生成测试数据
4. 验证功能完整性" \
  --allowedTools "Bash,Read,Edit,Write,Glob,Grep" \
  --output-format json \
  --append-system-prompt "你是一个全栈开发工程师，精通规格驱动开发。请使用最佳实践，确保代码质量。"
```

### 场景 2：代码审查

**用户输入：**
> "调用 Claude Code 审查当前项目的代码质量和安全问题"

**执行流程：**
```bash
cd /workspace/your-project && \
claude -p "审查当前项目的代码质量和安全性。

请分析：
1. 安全漏洞（注入、XSS、CSRF等）
2. 性能瓶颈
3. 代码可读性
4. 最佳实践遵循情况
5. 潜在的错误和异常处理

输出格式：
- 严重程度（高/中/低）
- 具体问题描述
- 修复建议
- 示例代码" \
  --allowedTools "Read,Glob,Grep,Bash" \
  --output-format json
```

### 场景 3：Bug 修复

**用户输入：**
> "调用 Claude Code 修复 auth.py 中的登录问题"

**执行流程：**
```bash
cd /workspace/your-project && \
claude -p "修复 auth.py 中的登录问题。

上下文：
- 用户报告无法正常登录
- 可能是 JWT 验证逻辑有问题

请：
1. 先分析 auth.py 的代码逻辑
2. 找出潜在问题
3. 修复问题
4. 运行测试验证修复" \
  --allowedTools "Read,Edit,Bash" \
  --output-format json
```

### 场景 4：功能开发

**用户输入：**
> "调用 Claude Code 给项目添加用户权限管理功能"

**执行流程：**
```bash
cd /workspace/your-project && \
claude -p "为项目添加用户权限管理功能。

需求：
1. 角色定义（admin, user, guest）
2. 权限检查中间件
3. 路由级别的权限控制
4. 前端权限展示

请：
1. 分析现有项目结构
2. 设计权限方案
3. 实现后端逻辑
4. 实现前端组件
5. 添加测试" \
  --allowedTools "Bash,Read,Edit,Write,Glob,Grep" \
  --output-format json
```

---

## 输出处理

### JSON 输出格式示例

```json
{
  "result": "任务完成摘要...",
  "session_id": "sess_abc123",
  "structured_output": {
    "functions": ["login", "logout", "register"],
    "issues_found": 3,
    "files_modified": ["auth.py", "models.py"]
  },
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 2500
  }
}
```

### 从 OpenClaw 解析输出

```bash
# 保存输出到文件
claude -p "Your prompt" --output-format json > /tmp/claude-output.json

# 提取关键信息
RESULT=$(cat /tmp/claude-output.json | jq -r '.result')
SESSION_ID=$(cat /tmp/claude-output.json | jq -r '.session_id')

# 发送结果给用户
echo "Claude Code 执行完成！"
echo "Session ID: $SESSION_ID"
echo "结果: $RESULT"
```

---

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p` | 提示词（非交互模式） | `-p "修复bug"` |
| `--allowedTools` | 自动授权的工具 | `"Bash,Read,Edit"` |
| `--output-format` | 输出格式 | `json` / `text` / `stream-json` |
| `--json-schema` | 结构化输出Schema | `'{"type":"object"...}'` |
| `--append-system-prompt` | 追加系统提示 | `"你是架构师"` |
| `--system-prompt` | 替换系统提示 | `"你是安全专家"` |
| `--continue` | 继续上次对话 | `--continue` |
| `--resume` | 恢复指定会话 | `--resume "sess_abc123"` |

### 工具授权语法

```bash
# 允许所有工具
--allowedTools "Bash,Read,Edit,Write,Glob,Grep"

# 只允许特定 Bash 命令（前缀匹配）
--allowedTools "Bash(git *),Bash(npm *),Bash(yarn *)"

# 只读模式
--allowedTools "Read,Glob,Grep"
```

---

## 错误处理

### 常见错误及解决

**错误 1：Claude Code 未安装**
```
claude: command not found
```
**解决：** 执行安装脚本

**错误 2：未登录**
```
Error: Not authenticated. Please run 'claude' to log in.
```
**解决：** 先运行 `claude` 完成登录

**错误 3：权限不足**
```
Error: Permission denied
```
**解决：** 检查 `--allowedTools` 是否包含所需工具

---

## 进阶用法

### 多步骤复杂任务

```bash
# 步骤1：创建规格
claude -p "为日记应用创建 OpenSpec 规格文档" \
  --allowedTools "Write" \
  --output-format json > /tmp/step1.json

# 步骤2：根据规格开发
claude -p "根据 specs/diary-app.md 开发前端代码" \
  --allowedTools "Read,Write,Edit" \
  --output-format json > /tmp/step2.json

# 步骤3：开发后端
claude -p "根据规格开发后端 API" \
  --allowedTools "Read,Write,Edit,Bash" \
  --output-format json > /tmp/step3.json
```

### 持续对话

```bash
# 启动任务
SESSION_JSON=$(claude -p "开始开发日记应用" --output-format json)
SESSION_ID=$(echo $SESSION_JSON | jq -r '.session_id')

# 继续对话
claude -p "添加用户认证功能" --resume "$SESSION_ID"

# 再次继续
claude -p "添加数据持久化" --resume "$SESSION_ID"
```

---

## 成本估算

| 任务类型 | 预计 Token | 成本 |
|----------|------------|------|
| 简单 Bug 修复 | 2K-5K | $0.01-0.03 |
| 代码审查 | 5K-15K | $0.03-0.10 |
| 功能开发 | 10K-50K | $0.05-0.30 |
| 完整项目开发 | 50K-200K | $0.30-1.50 |

---

## 最佳实践

1. **使用 JSON 输出** - 方便程序解析和处理
2. **明确授权工具** - 避免执行过程中的人工确认
3. **分步骤执行** - 复杂任务拆分为多个小任务
4. **保存 Session ID** - 方便继续对话和调试
5. **在 Git 仓库中执行** - 方便回滚和查看变更

---

## 相关资源

- Claude Code 文档：https://code.claude.com/docs
- Headless 模式：https://code.claude.com/docs/en/headless
- Subagent 文档：https://code.claude.com/docs/en/sub-agents
- CLI 参考：https://code.claude.com/docs/en/cli-reference

---

*Skill 创建时间: 2026-02-12*  
*版本: 1.0*
