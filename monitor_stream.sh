#!/bin/bash

# ═══════════════════════════════════════════════════════════
# Stream Monitor & Auto-Restart
# ═══════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_stream() {
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

restart_stream() {
    log "${YELLOW}⚠️  البث متوقف - إعادة تشغيل تلقائية...${NC}"
    
    if [ -n "$FB_STREAM_KEY" ]; then
        FB_STREAM_KEY="$FB_STREAM_KEY" bash "$SCRIPT_DIR/main.sh" >> "$LOG_DIR/monitor.log" 2>&1
        log "${GREEN}✅ تم إعادة تشغيل البث${NC}"
    else
        log "${RED}❌ لم يتم العثور على FB_STREAM_KEY${NC}"
        exit 1
    fi
}

log "${GREEN}🔍 بدء مراقبة البث...${NC}"
log "سيتم فحص البث كل 10 ثوانٍ وإعادة التشغيل التلقائي عند التوقف"
echo ""

while true; do
    if ! check_stream; then
        restart_stream
        sleep 5
    fi
    sleep 10
done
