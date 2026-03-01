# LESSONS_LEARNED.md

## 2026-03-01 Gateway 重启失效事故

### 错误描述
执行 Gateway 重启时，仅终止了旧进程，未成功启动新进程，导致服务中断。

### 根本原因
在没有 systemd 的环境中，仅使用 `kill` 命令终止进程，但未使用 `nohup` 或可靠脚本确保后台进程重新拉起。

### 影响
服务中断，需等待人工介入恢复。

### 修复方案
创建 `scripts/restart-gateway.sh` 脚本，包含：
1. 终止旧进程
2. 等待资源释放
3. 使用 `nohup` 后台启动新进程
4. 记录 PID 到文件
5. 验证进程存活

### 预防措施 (SOP)
- [ ] 任何 Gateway 重启操作必须通过 `restart-gateway.sh` 脚本执行
- [ ] 禁止裸用 `kill` 命令后无后续启动动作
- [ ] 重启后必须执行 `openclaw status` 验证 Gateway reachable
