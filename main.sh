#!/bin/bash

# ═══════════════════════════════════════════════════════════
# Facebook Live Stream - نسخة محسّنة
# ═══════════════════════════════════════════════════════════

set -e

# تحميل ملف الإعدادات
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# ═══════════════════════════════════════════════════════════
# الألوان للرسائل
# ═══════════════════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════
# دالة الطباعة الملونة
# ═══════════════════════════════════════════════════════════

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ═══════════════════════════════════════════════════════════
# 1. فحص المتطلبات الأساسية
# ═══════════════════════════════════════════════════════════

check_requirements() {
    log_info "فحص المتطلبات الأساسية..."
    
    local missing_deps=()
    
    if ! command -v ffmpeg &> /dev/null; then
        missing_deps+=("ffmpeg")
    fi
    
    if ! command -v tmux &> /dev/null; then
        missing_deps+=("tmux")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "المكتبات التالية مفقودة: ${missing_deps[*]}"
        log_info "الرجاء تثبيتها أولاً"
        exit 1
    fi
    
    log_success "جميع المتطلبات متوفرة"
}

# ═══════════════════════════════════════════════════════════
# 2. فحص الاتصال بالإنترنت
# ═══════════════════════════════════════════════════════════

check_internet() {
    log_info "فحص الاتصال بالإنترنت..."
    
    if ! ping -c 1 -W 3 8.8.8.8 &> /dev/null; then
        log_error "لا يوجد اتصال بالإنترنت!"
        log_info "الرجاء التحقق من اتصال الشبكة"
        exit 1
    fi
    
    log_success "الاتصال بالإنترنت متوفر"
}

# ═══════════════════════════════════════════════════════════
# 3. فحص مفتاح البث (Stream Key)
# ═══════════════════════════════════════════════════════════

check_stream_key() {
    log_info "فحص مفتاح البث..."
    
    if [ -z "$FB_STREAM_KEY" ]; then
        log_error "مفتاح البث غير موجود!"
        log_warning "الرجاء تعيين متغير البيئة: FB_STREAM_KEY"
        log_info "مثال: export FB_STREAM_KEY='your-stream-key-here'"
        exit 1
    fi
    
    if [ "$FB_STREAM_KEY" = "YOUR_STREAM_KEY_HERE" ]; then
        log_error "الرجاء تغيير مفتاح البث من القيمة الافتراضية"
        exit 1
    fi
    
    log_success "مفتاح البث موجود"
}

# ═══════════════════════════════════════════════════════════
# 4. فحص صلاحية رابط المصدر
# ═══════════════════════════════════════════════════════════

check_source() {
    log_info "فحص رابط المصدر..."
    
    if ! curl -Is --max-time 10 "$SOURCE" | head -n 1 | grep -q "200\|302\|301"; then
        log_warning "تحذير: رابط المصدر قد لا يكون صالح"
        log_info "سيتم المحاولة في جميع الأحوال..."
    else
        log_success "رابط المصدر صالح"
    fi
}

# ═══════════════════════════════════════════════════════════
# 5. إنشاء مجلد السجلات
# ═══════════════════════════════════════════════════════════

setup_logs() {
    if [ "$LOG_ENABLED" = "true" ]; then
        mkdir -p "$LOG_DIR"
        log_success "مجلد السجلات جاهز: $LOG_DIR"
    fi
}

# ═══════════════════════════════════════════════════════════
# 6. الحصول على إعدادات الجودة
# ═══════════════════════════════════════════════════════════

get_quality_settings

# ═══════════════════════════════════════════════════════════
# 7. كشف GPU Encoder
# ═══════════════════════════════════════════════════════════

VIDEO_ENCODER=$(detect_gpu_encoder)

if [ "$VIDEO_ENCODER" != "libx264" ]; then
    log_success "تم اكتشاف GPU encoder: $VIDEO_ENCODER"
else
    log_info "استخدام CPU encoder: libx264"
fi

# ═══════════════════════════════════════════════════════════
# 8. بناء معاملات ffmpeg
# ═══════════════════════════════════════════════════════════

build_ffmpeg_params() {
    local params=""
    
    # معاملات إعادة الاتصال
    if [ "$RECONNECT_ENABLED" = "true" ]; then
        params="$params -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max $RECONNECT_DELAY_MAX"
    fi
    
    # معاملات الفيديو
    params="$params -c:v $VIDEO_ENCODER"
    
    # إعدادات خاصة بـ libx264
    if [ "$VIDEO_ENCODER" = "libx264" ]; then
        params="$params -preset $PRESET -tune $TUNE"
    fi
    
    # الدقة والـ FPS
    params="$params -s $RESOLUTION -r $FPS"
    
    # Bitrate و Buffer
    params="$params -b:v $BITRATE -maxrate $MAXRATE -bufsize $BUFSIZE"
    
    # Key Interval (2 seconds)
    local keyint_frames=$((FPS * KEYINT))
    params="$params -g $keyint_frames -keyint_min $keyint_frames"
    
    # Pixel Format
    params="$params -pix_fmt $PIXEL_FORMAT"
    
    # معاملات الصوت
    params="$params -c:a $AUDIO_CODEC -b:a $AUDIO_BITRATE -ar $AUDIO_RATE"
    
    # الخيوط
    if [ "$THREADS" != "0" ]; then
        params="$params -threads $THREADS"
    fi
    
    # مستوى السجل
    if [ "$LOG_ENABLED" = "true" ]; then
        params="$params -loglevel $LOG_LEVEL"
    else
        params="$params -loglevel error"
    fi
    
    echo "$params"
}

# ═══════════════════════════════════════════════════════════
# 9. عرض معلومات البث
# ═══════════════════════════════════════════════════════════

display_stream_info() {
    echo ""
    log_info "═══════════════════════════════════════════"
    log_info "معلومات البث"
    log_info "═══════════════════════════════════════════"
    echo -e "${BLUE}📊 الجودة:${NC} $QUALITY_MODE"
    echo -e "${BLUE}📐 الدقة:${NC} $RESOLUTION"
    echo -e "${BLUE}🎬 FPS:${NC} $FPS"
    echo -e "${BLUE}📡 Bitrate:${NC} $BITRATE (max: $MAXRATE)"
    echo -e "${BLUE}🔑 Key Interval:${NC} ${KEYINT}s (كل $((FPS * KEYINT)) إطار)"
    echo -e "${BLUE}🔊 الصوت:${NC} $AUDIO_BITRATE @ ${AUDIO_RATE}Hz"
    echo -e "${BLUE}⚙️  الترميز:${NC} $VIDEO_ENCODER"
    echo -e "${BLUE}📺 المصدر:${NC} $SOURCE"
    log_info "═══════════════════════════════════════════"
    echo ""
}

# ═══════════════════════════════════════════════════════════
# 10. بدء البث
# ═══════════════════════════════════════════════════════════

start_stream() {
    log_info "إيقاف أي جلسة سابقة..."
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
    
    log_info "بناء معاملات ffmpeg..."
    FFMPEG_PARAMS=$(build_ffmpeg_params)
    
    display_stream_info
    
    # بناء الأمر الكامل
    RTMP_URL="${RTMP_SERVER}${FB_STREAM_KEY}"
    
    local LOG_FILE=""
    if [ "$LOG_ENABLED" = "true" ]; then
        LOG_FILE="$LOG_DIR/stream_$(date +%Y%m%d_%H%M%S).log"
        touch "$LOG_FILE"
    fi
    
    log_info "بدء البث..."
    
    # إنشاء سكريبت مؤقت لتشغيله داخل tmux
    local TEMP_SCRIPT="/tmp/fbstream_$$.sh"
    cat > "$TEMP_SCRIPT" << EOFSCRIPT
#!/bin/bash
echo "═══════════════════════════════════════════"
echo "البث بدأ في: \$(date)"
echo "═══════════════════════════════════════════"
EOFSCRIPT

    if [ -n "$LOG_FILE" ]; then
        cat >> "$TEMP_SCRIPT" << EOFSCRIPT
echo "ملف السجل: $LOG_FILE"
echo "═══════════════════════════════════════════"
ffmpeg -i "$SOURCE" $FFMPEG_PARAMS -f flv "$RTMP_URL" 2>&1 | tee -a "$LOG_FILE"
EOFSCRIPT
    else
        cat >> "$TEMP_SCRIPT" << EOFSCRIPT
echo "═══════════════════════════════════════════"
ffmpeg -i "$SOURCE" $FFMPEG_PARAMS -f flv "$RTMP_URL"
EOFSCRIPT
    fi
    
    chmod +x "$TEMP_SCRIPT"
    
    # إنشاء جلسة tmux وتشغيل السكريبت
    tmux new-session -d -s "$SESSION_NAME" "$TEMP_SCRIPT"
    
    # الانتظار والتحقق من بدء الجلسة
    sleep 1
    
    local attempt=0
    local max_attempts=5
    local session_started=false
    
    while [ $attempt -lt $max_attempts ]; do
        if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
            session_started=true
            break
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ "$session_started" = true ]; then
        log_success "البث بدأ بنجاح! 🚀"
        echo ""
        log_info "للاطلاع على حالة البث:"
        echo -e "  ${GREEN}tmux attach -t $SESSION_NAME${NC}"
        echo ""
        log_info "أو استخدم:"
        echo -e "  ${GREEN}./control.sh status${NC}"
        echo ""
        if [ -n "$LOG_FILE" ]; then
            log_info "ملف السجل: $LOG_FILE"
        fi
        echo ""
        log_warning "ملاحظة: إذا توقف البث فجأة، تحقق من:"
        echo -e "  - صحة مفتاح البث (FB_STREAM_KEY)"
        echo -e "  - صحة رابط المصدر"
        echo -e "  - الاتصال بالإنترنت"
        echo -e "  - السجلات: ${GREEN}./control.sh logs${NC}"
    else
        log_error "فشل بدء البث!"
        echo ""
        if [ -n "$LOG_FILE" ] && [ -f "$LOG_FILE" ]; then
            log_info "آخر السجلات:"
            tail -n 20 "$LOG_FILE"
        fi
        rm -f "$TEMP_SCRIPT"
        exit 1
    fi
}

# ═══════════════════════════════════════════════════════════
# البرنامج الرئيسي
# ═══════════════════════════════════════════════════════════

main() {
    echo ""
    log_info "═══════════════════════════════════════════"
    log_info "🔴 Facebook Live Stream - البث المباشر"
    log_info "═══════════════════════════════════════════"
    echo ""
    
    check_requirements
    check_internet
    check_stream_key
    check_source
    setup_logs
    start_stream
    
    echo ""
    log_success "تم بنجاح! ✨"
    echo ""
}

main "$@"
