import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import config
from stream import StreamManager

# تفعيل السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات الحوار
M3U8, KEY = range(2)

stream_manager = StreamManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بداية الحوار"""
    await update.message.reply_text(
        "👋 مرحباً بك في بوت البث المحسّن!\n\n"
        "🎯 الميزات:\n"
        "• إعادة اتصال تلقائية (50 محاولة)\n"
        "• حماية من الانقطاع\n"
        "• استقرار محسّن\n\n"
        "📋 الأوامر:\n"
        "/stream - بدء البث\n"
        "/stop - إيقاف البث\n"
        "/status - حالة البث"
    )
    return ConversationHandler.END

async def start_stream_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """أمر بدء البث"""
    if stream_manager.get_status():
        await update.message.reply_text("⚠️ البث يعمل بالفعل! استخدم /stop لإيقافه أولاً.")
        return ConversationHandler.END

    await update.message.reply_text(
        "🚀 إعداد البث\n\n"
        "أرسل رابط M3U8 (مثال: https://...stream.m3u8)"
    )
    return M3U8

async def get_m3u8(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """استقبال رابط M3U8"""
    context.user_data['m3u8'] = update.message.text
    await update.message.reply_text(
        "✅ تم استقبال الرابط.\n\n"
        "الآن أرسل مفتاح البث (Stream Key) من فيسبوك\n"
        "(مثال: FB-1234567...)"
    )
    return KEY

async def get_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """استقبال مفتاح البث"""
    m3u8 = context.user_data['m3u8']
    key = update.message.text
    
    await update.message.reply_text(
        "⏳ جاري بدء البث... يرجى الانتظار...\n\n"
        "⚠️ تنبيه: استخدم Stream Key جديد لكل بث لتجنب الحظر!"
    )
    
    # الرابط الافتراضي لفيسبوك
    rtmp = config.FACEBOOK_RTMP_URL
    
    # بدء البث
    success, msg = stream_manager.start_stream(m3u8, rtmp, key, logo_path="logo.png")
    
    if success:
        await update.message.reply_text(
            f"{msg}\n\n"
            "📺 يمكنك الآن الذهاب لصفحة البث المباشر في فيسبوك.\n"
            "استخدم /stop لإيقاف البث."
        )
    else:
        await update.message.reply_text(msg)
    
    return ConversationHandler.END

async def stop_stream_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """أمر إيقاف البث"""
    success, msg = stream_manager.stop_stream()
    await update.message.reply_text(msg)
    return ConversationHandler.END

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """التحقق من حالة البث"""
    status_msg = stream_manager.get_detailed_status()
    await update.message.reply_text(f"📊 حالة البث:\n\n{status_msg}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """إلغاء الحوار"""
    await update.message.reply_text("❌ تم إلغاء العملية.")
    return ConversationHandler.END

def main() -> None:
    """تشغيل البوت"""
    application = Application.builder().token(config.BOT_TOKEN).build()

    # معالج الحوار
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("stream", start_stream_command)],
        states={
            M3U8: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_m3u8)],
            KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_key)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_stream_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
