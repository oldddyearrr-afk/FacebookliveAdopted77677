import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8476070935:AAHADgmTDVTErkm25hVUt4dWjf6g37sZKEM")
FFMPEG_CMD = "ffmpeg"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
FACEBOOK_RTMP_URL = "rtmps://live-api-s.facebook.com:443/rtmp/"
LOG_FILE = "stream_bot.log"

# ═══════════════════════════════════════════════════════════
# 🎨 LOGO SETTINGS - اعدادات اللوجو
# ═══════════════════════════════════════════════════════════

LOGO_OFFSET_X = "19"
LOGO_OFFSET_Y = "-45"
LOGO_SIZE = "210:-1"
LOGO_OPACITY = "1.0"
