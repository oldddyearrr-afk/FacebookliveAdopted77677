import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8476070935:AAHADgmTDVTErkm25hVUt4dWjf6g37sZKEM")

# FFmpeg Settings
FFMPEG_CMD = "ffmpeg"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Default RTMP URL
FACEBOOK_RTMP_URL = "rtmps://live-api-s.facebook.com:443/rtmp/"

# Logging Settings
LOG_FILE = "stream_bot.log"

# ═══════════════════════════════════════════════════════════
# 🎨 LOGO SETTINGS - اعدادات اللوجو
# ═══════════════════════════════════════════════════════════

# الموضع الأفقي (من اليمين)
# أرقام سالبة = من اليمين ، أرقام موجبة = من اليسار
LOGO_OFFSET_X = "-27"

# الموضع العمودي (من الأعلى)  
# أرقام سالبة = فوق الشاشة ، أرقام موجبة = تحت
LOGO_OFFSET_Y = "-36"

# حجم اللوجو (العرض والارتفاع)
LOGO_SIZE = "480:-1"

# شفافية اللوجو (0.0 = شفاف, 1.0 = معتم)
LOGO_OPACITY = "1.0"
