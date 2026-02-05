#!/bin/bash
# OpenClaw 资料迁移脚本
# 用法:
#   ./migrate.sh backup    # 打包当前资料
#   ./migrate.sh restore  # 在新服务器恢复

set -e

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="/root/.openclaw/backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🦞 OpenClaw 迁移工具"
echo "===================="

# 创建备份目录
mkdir -p $BACKUP_DIR

backup() {
    echo "📦 打包资料中..."
    
    # 排除文件
    EXCLUDE="--exclude=node_modules \
             --exclude=.git \
             --exclude=*.log \
             --exclude=config.json \
             --exclude=*.state.json \
             --exclude=.env*"

    # 打包 scripts
    tar $EXCLUDE -czf $BACKUP_DIR/scripts_${DATE}.tar.gz -C $WORKSPACE scripts
    
    # 打包 skills
    tar $EXCLUDE -czf $BACKUP_DIR/skills_${DATE}.tar.gz -C $WORKSPACE skills
    
    # 打包 memory
    tar -czf $BACKUP_DIR/memory_${DATE}.tar.gz -C $WORKSPACE memory
    
    # 打包 cron 任务
    openclaw cron list --includeDisabled=true 2>/dev/null > $BACKUP_DIR/cron_${DATE}.json || echo "⚠️ Cron 导出失败，请手动记录"
    
    echo ""
    echo "✅ 备份完成！"
    echo ""
    echo "📁 备份文件："
    ls -lh $BACKUP_DIR/
    echo ""
    echo "🔧 下一步："
    echo "1. 下载这些文件到本地："
    echo "   - scripts_${DATE}.tar.gz"
    echo "   - skills_${DATE}.tar.gz"
    echo "   - memory_${DATE}.tar.gz"
    echo "   - cron_${DATE}.json (如果存在)"
    echo ""
    echo "2. 上传到新服务器"
    echo ""
    echo "3. 在新服务器执行："
    echo "   ./migrate.sh restore"
}

restore() {
    echo "📥 恢复资料中..."
    echo ""
    
    # 检查备份文件
    LATEST_SCRIPTS=$(ls -t $BACKUP_DIR/scripts_*.tar.gz 2>/dev/null | head -1)
    LATEST_SKILLS=$(ls -t $BACKUP_DIR/skills_*.tar.gz 2>/dev/null | head -1)
    LATEST_MEMORY=$(ls -t $BACKUP_DIR/memory_*.tar.gz 2>/dev/null | head -1)
    LATEST_CRON=$(ls -t $BACKUP_DIR/cron_*.json 2>/dev/null | head -1)
    
    if [ -z "$LATEST_SCRIPTS" ]; then
        echo "❌ 没有找到备份文件！"
        echo "请先在旧服务器执行：./migrate.sh backup"
        exit 1
    fi
    
    # 恢复 scripts
    if [ -n "$LATEST_SCRIPTS" ]; then
        echo "📂 恢复 scripts..."
        tar -xzf $LATEST_SCRIPTS -C $WORKSPACE/
    fi
    
    # 恢复 skills
    if [ -n "$LATEST_SKILLS" ]; then
        echo "📂 恢复 skills..."
        tar -xzf $LATEST_SKILLS -C $WORKSPACE/
    fi
    
    # 恢复 memory
    if [ -n "$LATEST_MEMORY" ]; then
        echo "📂 恢复 memory..."
        tar -xzf $LATEST_MEMORY -C $WORKSPACE/
    fi
    
    echo ""
    echo "✅ 文件恢复完成！"
    echo ""
    echo "🔧 手动步骤："
    echo ""
    echo "1. 配置 API 凭据："
    echo "   openclaw configure"
    echo "   - Notion API Token"
    echo "   - GitHub Token"
    echo "   - ImgBB API Key"
    echo "   - Telegram Bot Token"
    echo ""
    echo "2. 恢复 Cron 任务："
    if [ -n "$LATEST_CRON" ]; then
        echo "   参考文件: $BACKUP_DIR/$LATEST_CRON"
        echo "   手动执行：openclaw cron add ..."
    else
        echo "   ⚠️ Cron 备份不存在，需要手动重新创建"
    fi
    echo ""
    echo "3. 测试运行："
    echo "   python3 $WORKSPACE/scripts/morning_reminder.py"
    echo ""
    echo "4. 重启 Gateway："
    echo "   openclaw gateway restart"
    echo ""
    echo "🎉 迁移完成！"
}

case "$1" in
    backup)
        backup
        ;;
    restore)
        restore
        ;;
    *)
        echo "用法: $0 {backup|restore}"
        echo ""
        echo "  backup   - 打包当前资料（在一台服务器上执行）"
        echo "  restore  - 恢复资料（在另一台服务器上执行）"
        exit 1
        ;;
esac
