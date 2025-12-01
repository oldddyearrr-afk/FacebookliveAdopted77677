import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8302564752:AAHBc-S_ezyiywnzuk2yOSIl8l4a9Q-bLc8")
FFMPEG_CMD = "ffmpeg"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
FACEBOOK_RTMP_URL = "rtmps://live-api-s.facebook.com:443/rtmp/"
LOG_FILE = "stream_bot.log"

# ═══════════════════════════════════════════════════════════
# 🎨 LOGO SETTINGS - اعدادات اللوجو
# ═══════════════════════════════════════════════════════════

LOGO_OFFSET_X = "8"
LOGO_OFFSET_Y = "-124"
LOGO_SIZE = "166:-1"
LOGO_OPACITY = "1.0"
