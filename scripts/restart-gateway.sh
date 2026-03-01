#!/bin/bash
# Gateway restart wrapper with auto-start

LOGFILE=/tmp/openclaw/gateway-manual.log
PIDFILE=/tmp/openclaw/gateway.pid

# Kill existing
cat $PIDFILE 2>/dev/null | xargs kill 2>/dev/null
sleep 2

# Start new
cd /root/.openclaw/workspace
nohup openclaw gateway > $LOGFILE 2>&1 &
echo $! > $PIDFILE

sleep 3
if pgrep -f "openclaw gateway" > /dev/null; then
    echo "Gateway started (PID: $(cat $PIDFILE))"
else
    echo "Failed to start gateway"
    exit 1
fi