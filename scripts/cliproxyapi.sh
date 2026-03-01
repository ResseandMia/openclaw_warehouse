#!/bin/bash
# CLI Proxy API 启动脚本
# 反重力 (Antigravity) Claude Opus 4.6 代理服务

CONFIG_FILE="/root/.openclaw/workspace/openclaw_warehouse/config/cliproxyapi.yaml"
BINARY="/root/.openclaw/workspace/openclaw_warehouse/bin/cli-proxy-api"
PIDFILE="/tmp/cliproxyapi.pid"
LOGFILE="/tmp/cliproxyapi.log"

case "$1" in
  start)
    echo "Starting CLI Proxy API..."
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
      echo "Already running (PID: $(cat $PIDFILE))"
      exit 0
    fi
    nohup "$BINARY" -config "$CONFIG_FILE" > "$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"
    sleep 2
    if kill -0 $(cat "$PIDFILE") 2>/dev/null; then
      echo "Started (PID: $(cat $PIDFILE))"
      echo "API Endpoint: http://127.0.0.1:8080/v1"
    else
      echo "Failed to start"
      exit 1
    fi
    ;;
  stop)
    if [ -f "$PIDFILE" ]; then
      kill $(cat "$PIDFILE") 2>/dev/null && echo "Stopped" || echo "Not running"
      rm -f "$PIDFILE"
    else
      echo "Not running"
    fi
    ;;
  restart)
    $0 stop
    sleep 1
    $0 start
    ;;
  status)
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
      echo "Running (PID: $(cat $PIDFILE))"
      echo "API Endpoint: http://127.0.0.1:8080/v1"
    else
      echo "Not running"
    fi
    ;;
  login-antigravity)
    echo "Logging in to Antigravity..."
    "$BINARY" -antigravity-login -config "$CONFIG_FILE"
    ;;
  login-claude)
    echo "Logging in to Claude..."
    "$BINARY" -claude-login -config "$CONFIG_FILE"
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|login-antigravity|login-claude}"
    exit 1
    ;;
esac