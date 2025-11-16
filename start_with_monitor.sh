#!/bin/bash

# ═══════════════════════════════════════════════════════════
# Start Stream with Auto-Monitor
# ═══════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${BLUE}   بدء البث مع المراقبة التلقائية   ${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""

# Start initial stream
echo -e "${GREEN}🚀 بدء البث الأولي...${NC}"
bash "$SCRIPT_DIR/control.sh" start

sleep 3

# Start monitor in background
echo -e "${GREEN}🔍 بدء المراقبة التلقائية...${NC}"
echo ""
echo -e "${BLUE}ℹ️  المراقبة تعمل الآن:${NC}"
echo "   - سيتم فحص البث كل 10 ثوانٍ"
echo "   - إعادة تشغيل تلقائية عند التوقف"
echo "   - السجلات في: logs/monitor.log"
echo ""
echo -e "${GREEN}✅ النظام يعمل الآن!${NC}"
echo ""

# Run monitor
bash "$SCRIPT_DIR/monitor_stream.sh"
