#!/bin/bash

# ═══════════════════════════════════════════════════════════
# ملف الإعدادات - Facebook Live Stream Configuration
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 1. إعدادات المصدر والوجهة
# ═══════════════════════════════════════════════════════════

# رابط مصدر الفيديو M3U8
SOURCE="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"

# رابط RTMP لفيسبوك (يتم جلب Stream Key من متغيرات البيئة للأمان)
RTMP_SERVER="rtmp://rtmp-api.facebook.com:80/rtmp/"

# ═══════════════════════════════════════════════════════════
# 2. إعدادات الجودة المختلفة (Quality Presets)
# ═══════════════════════════════════════════════════════════

# اختر أحد الأوضاع: low, medium, high, ultra, custom
QUALITY_MODE="ultra"

# ─────────────────────────────────────────────────────────
# وضع LOW - 720p @ 30fps (للإنترنت الضعيف)
# ─────────────────────────────────────────────────────────
LOW_RESOLUTION="1280x720"
LOW_FPS="30"
LOW_BITRATE="2000k"
LOW_MAXRATE="2500k"
LOW_BUFSIZE="4000k"
LOW_AUDIO_BITRATE="96k"

# ─────────────────────────────────────────────────────────
# وضع MEDIUM - 720p @ 30fps (جودة متوسطة)
# ─────────────────────────────────────────────────────────
MEDIUM_RESOLUTION="1280x720"
MEDIUM_FPS="30"
MEDIUM_BITRATE="3000k"
MEDIUM_MAXRATE="3500k"
MEDIUM_BUFSIZE="6000k"
MEDIUM_AUDIO_BITRATE="128k"

# ─────────────────────────────────────────────────────────
# وضع HIGH - 1080p @ 30fps (جودة عالية)
# ─────────────────────────────────────────────────────────
HIGH_RESOLUTION="1920x1080"
HIGH_FPS="30"
HIGH_BITRATE="4500k"
HIGH_MAXRATE="5000k"
HIGH_BUFSIZE="9000k"
HIGH_AUDIO_BITRATE="160k"

# ─────────────────────────────────────────────────────────
# وضع ULTRA - 1080p @ 30fps (أفضل جودة) ⭐ الإعدادات الجديدة
# ─────────────────────────────────────────────────────────
ULTRA_RESOLUTION="1920x1080"
ULTRA_FPS="30"
ULTRA_BITRATE="5000k"
ULTRA_MAXRATE="6000k"
ULTRA_BUFSIZE="10000k"
ULTRA_AUDIO_BITRATE="192k"
ULTRA_KEYINT="2"  # Key interval 2 seconds

# ─────────────────────────────────────────────────────────
# وضع CUSTOM - إعدادات مخصصة
# ─────────────────────────────────────────────────────────
CUSTOM_RESOLUTION="1920x1080"
CUSTOM_FPS="30"
CUSTOM_BITRATE="5000k"
CUSTOM_MAXRATE="6000k"
CUSTOM_BUFSIZE="10000k"
CUSTOM_AUDIO_BITRATE="192k"
CUSTOM_KEYINT="2"

# ═══════════════════════════════════════════════════════════
# 3. إعدادات متقدمة
# ═══════════════════════════════════════════════════════════

# إعادة الاتصال التلقائي
RECONNECT_ENABLED="true"
RECONNECT_DELAY_MAX="10"
RECONNECT_ATTEMPTS="-1"  # -1 = محاولات غير محدودة

# إعدادات الترميز
PRESET="veryfast"  # ultrafast, superfast, veryfast, faster, fast, medium, slow
TUNE="zerolatency"  # للبث المباشر
PIXEL_FORMAT="yuv420p"

# إعدادات الصوت
AUDIO_CODEC="aac"
AUDIO_RATE="44100"

# ═══════════════════════════════════════════════════════════
# 4. إعدادات الأداء
# ═══════════════════════════════════════════════════════════

# استخدام GPU للترميز (إن وجد)
USE_GPU="auto"  # auto, nvidia, intel, amd, off

# عدد الخيوط للمعالج
THREADS="0"  # 0 = تلقائي

# ═══════════════════════════════════════════════════════════
# 5. إعدادات tmux
# ═══════════════════════════════════════════════════════════

SESSION_NAME="fbstream"

# ═══════════════════════════════════════════════════════════
# 6. إعدادات السجلات
# ═══════════════════════════════════════════════════════════

LOG_DIR="logs"
LOG_ENABLED="true"
LOG_LEVEL="info"  # quiet, panic, fatal, error, warning, info, verbose, debug

# ═══════════════════════════════════════════════════════════
# دالة لاختيار الجودة المناسبة
# ═══════════════════════════════════════════════════════════

get_quality_settings() {
    case $QUALITY_MODE in
        low)
            RESOLUTION=$LOW_RESOLUTION
            FPS=$LOW_FPS
            BITRATE=$LOW_BITRATE
            MAXRATE=$LOW_MAXRATE
            BUFSIZE=$LOW_BUFSIZE
            AUDIO_BITRATE=$LOW_AUDIO_BITRATE
            KEYINT="2"
            ;;
        medium)
            RESOLUTION=$MEDIUM_RESOLUTION
            FPS=$MEDIUM_FPS
            BITRATE=$MEDIUM_BITRATE
            MAXRATE=$MEDIUM_MAXRATE
            BUFSIZE=$MEDIUM_BUFSIZE
            AUDIO_BITRATE=$MEDIUM_AUDIO_BITRATE
            KEYINT="2"
            ;;
        high)
            RESOLUTION=$HIGH_RESOLUTION
            FPS=$HIGH_FPS
            BITRATE=$HIGH_BITRATE
            MAXRATE=$HIGH_MAXRATE
            BUFSIZE=$HIGH_BUFSIZE
            AUDIO_BITRATE=$HIGH_AUDIO_BITRATE
            KEYINT="2"
            ;;
        ultra)
            RESOLUTION=$ULTRA_RESOLUTION
            FPS=$ULTRA_FPS
            BITRATE=$ULTRA_BITRATE
            MAXRATE=$ULTRA_MAXRATE
            BUFSIZE=$ULTRA_BUFSIZE
            AUDIO_BITRATE=$ULTRA_AUDIO_BITRATE
            KEYINT=$ULTRA_KEYINT
            ;;
        custom)
            RESOLUTION=$CUSTOM_RESOLUTION
            FPS=$CUSTOM_FPS
            BITRATE=$CUSTOM_BITRATE
            MAXRATE=$CUSTOM_MAXRATE
            BUFSIZE=$CUSTOM_BUFSIZE
            AUDIO_BITRATE=$CUSTOM_AUDIO_BITRATE
            KEYINT=$CUSTOM_KEYINT
            ;;
        *)
            echo "⚠️  جودة غير معروفة: $QUALITY_MODE - استخدام ULTRA افتراضياً"
            QUALITY_MODE="ultra"
            get_quality_settings
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════
# دالة لكشف وتفعيل GPU encoding
# ═══════════════════════════════════════════════════════════

detect_gpu_encoder() {
    if [ "$USE_GPU" = "off" ]; then
        echo "libx264"
        return
    fi
    
    if [ "$USE_GPU" = "nvidia" ] || { [ "$USE_GPU" = "auto" ] && command -v nvidia-smi &> /dev/null; }; then
        if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q "h264_nvenc"; then
            echo "h264_nvenc"
            return
        fi
    fi
    
    if [ "$USE_GPU" = "intel" ] || [ "$USE_GPU" = "auto" ]; then
        if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q "h264_vaapi"; then
            echo "h264_vaapi"
            return
        fi
        if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q "h264_qsv"; then
            echo "h264_qsv"
            return
        fi
    fi
    
    if [ "$USE_GPU" = "amd" ] || [ "$USE_GPU" = "auto" ]; then
        if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q "h264_amf"; then
            echo "h264_amf"
            return
        fi
    fi
    
    echo "libx264"
}
