
import subprocess
import logging
import config
import os
import time
import threading

logger = logging.getLogger(__name__)

class StreamManager:
    def __init__(self):
        self.process = None
        self.is_running = False
        self.monitor_thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 50
        self.last_m3u8_url = None
        self.last_rtmp_url = None
        self.last_stream_key = None
        self.last_logo_path = None

    def monitor_process(self):
        """مراقبة العملية وإعادة الاتصال عند الفشل مع عدد محاولات أكبر"""
        consecutive_failures = 0
        
        while self.is_running:
            if self.process is None:
                break
            
            poll_result = self.process.poll()
            
            if poll_result is not None:
                consecutive_failures += 1
                self.reconnect_attempts += 1
                
                logger.warning(f"❌ البث توقف! (المحاولة {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                logger.warning(f"❌ فشل متتالي: {consecutive_failures}")
                
                # قراءة أخطاء FFmpeg
                if self.process.stderr:
                    try:
                        stderr_output = self.process.stderr.read()
                        if stderr_output:
                            logger.error(f"FFmpeg Error: {stderr_output[:500]}")
                    except:
                        pass
                
                if self.reconnect_attempts >= self.max_reconnect_attempts:
                    logger.error("❌ تم الوصول للحد الأقصى من محاولات إعادة الاتصال")
                    self.is_running = False
                    break
                
                # انتظار تصاعدي (exponential backoff)
                wait_time = min(2 ** min(consecutive_failures, 5), 30)
                logger.info(f"⏳ انتظار {wait_time} ثانية قبل إعادة الاتصال...")
                time.sleep(wait_time)
                
                if self.is_running:
                    self.restart_stream()
            else:
                # إذا نجح البث، إعادة تعيين العدادات
                if consecutive_failures > 0:
                    logger.info("✅ تم استعادة الاتصال بنجاح!")
                consecutive_failures = 0
                self.reconnect_attempts = 0
            
            time.sleep(5)

    def restart_stream(self):
        """إعادة تشغيل العملية مع تنظيف كامل"""
        logger.info("🔄 إعادة بناء الاتصال...")
        
        # إنهاء العملية القديمة بشكل آمن
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        
        # إعادة بناء الأمر مع إعدادات محسّنة
        if hasattr(self, 'last_command'):
            try:
                self.process = subprocess.Popen(
                    self.last_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                logger.info("✅ تم إعادة بناء عملية البث")
            except Exception as e:
                logger.error(f"❌ فشل إعادة البناء: {str(e)}")

    def start_stream(self, m3u8_url, rtmp_url, stream_key, logo_path=None):
        """بدء البث مع إعدادات استقرار محسّنة"""
        if self.is_running:
            return False, "البث يعمل بالفعل!"

        # حفظ البيانات للاستخدام في إعادة الاتصال
        self.last_m3u8_url = m3u8_url
        self.last_rtmp_url = rtmp_url
        self.last_stream_key = stream_key
        self.last_logo_path = logo_path
        self.reconnect_attempts = 0

        rtmp_url = rtmp_url.rstrip('/')
        full_rtmp_url = f"{rtmp_url}/{stream_key}"

        # أمر FFmpeg محسّن للاستقرار + Anti-Detection
        command = [
            config.FFMPEG_CMD,
            '-hide_banner',
            '-loglevel', 'error',
            
            # إعدادات إعادة الاتصال المحسّنة
            '-timeout', '30000000',
            '-reconnect', '1',
            '-reconnect_streamed', '1',
            '-reconnect_at_eof', '1',
            '-reconnect_delay_max', '15',
            '-multiple_requests', '1',
            '-rw_timeout', '10000000',
            
            # إعدادات الشبكة
            '-analyzeduration', '20000000',
            '-probesize', '20000000',
            
            # قراءة بسرعة حقيقية مع jitter طبيعي
            '-re',
            '-stream_loop', '-1',
            '-fflags', '+genpts+igndts',
            '-avoid_negative_ts', 'make_zero',
            
            # User Agent متنوع
            '-user_agent', config.USER_AGENT,
            '-headers', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            
            '-i', m3u8_url
        ]

        # إضافة اللوجو إذا كان موجوداً
        if logo_path and os.path.exists(logo_path):
            command.extend(['-i', logo_path])
            command.extend([
                '-filter_complex',
                '[0:v]fps=30,scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2[v];[1:v]scale=500:-1[logo];[v][logo]overlay=W-w-10:10:format=auto,format=yuv420p'
            ])
        else:
            command.extend([
                '-vf', 'fps=30,scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p'
            ])

        # إعدادات ترميز تبدو كبث أصلي (تخفي إعادة البث)
        command.extend([
            # فيديو - إعدادات تحاكي الكاميرات الحقيقية
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-tune', 'film',
            '-profile:v', 'main',
            '-level', '4.1',
            '-crf', '21',
            
            # GOP settings - تبدو طبيعية أكثر
            '-g', '120',
            '-keyint_min', '30',
            '-sc_threshold', '40',
            
            # Bitrate - ثابت ومستقر
            '-b:v', '2800k',
            '-minrate', '2400k',
            '-maxrate', '3200k',
            '-bufsize', '5600k',
            
            # Color settings
            '-pix_fmt', 'yuv420p',
            '-colorspace', 'bt709',
            '-color_primaries', 'bt709',
            '-color_trc', 'bt709',
            
            # صوت - معايير فيسبوك
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '48000',
            '-ac', '2',
            '-strict', 'experimental',
            
            # RTMP settings - محسّنة لفيسبوك
            '-f', 'flv',
            '-flvflags', 'no_duration_filesize+no_metadata',
            '-max_muxing_queue_size', '2048',
            
            # TCP settings للاستقرار
            '-rtmp_buffer', '5000',
            '-rtmp_live', 'live',
            
            full_rtmp_url
        ])

        try:
            logger.info(f"🚀 بدء البث: {m3u8_url[:50]}...")
            logger.info(f"🎯 الوجهة: {rtmp_url}")
            
            self.last_command = command
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            self.is_running = True
            
            # انتظار للتحقق من بدء البث
            time.sleep(8)
            
            if self.process.poll() is None:
                # بدء مراقبة العملية
                self.monitor_thread = threading.Thread(target=self.monitor_process, daemon=True)
                self.monitor_thread.start()
                
                logger.info("✅ البث نشط ونظام المراقبة يعمل!")
                return True, "✅ البث نشط الآن مع حماية ضد الانقطاع!\n\n🔄 سيتم إعادة الاتصال تلقائياً عند أي انقطاع."
            else:
                self.is_running = False
                stderr = self.process.stderr.read() if self.process.stderr else "لا توجد تفاصيل"
                logger.error(f"FFmpeg stderr: {stderr[:200]}")
                return False, f"❌ فشل البث.\n\nالخطأ: {stderr[:100]}"
                
        except Exception as e:
            self.is_running = False
            logger.error(f"❌ خطأ في بدء البث: {str(e)}")
            return False, f"❌ خطأ: {str(e)}"

    def stop_stream(self):
        """إيقاف البث بشكل آمن"""
        self.is_running = False
        
        if self.process and self.process.poll() is None:
            logger.info("🛑 إيقاف البث...")
            
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ العملية لم تتوقف، استخدام kill...")
                try:
                    self.process.kill()
                    self.process.wait(timeout=2)
                except:
                    pass
            except Exception as e:
                logger.error(f"خطأ في الإيقاف: {e}")
            
            self.process = None
            logger.info("✅ تم إيقاف البث")
            return True, "✅ تم إيقاف البث بنجاح."
        
        return False, "❌ لا يوجد بث نشط."

    def get_status(self):
        """التحقق من حالة البث مع معلومات إضافية"""
        # فحص حقيقي للعملية
        if self.process and self.process.poll() is None:
            self.is_running = True
            return {
                'active': True,
                'reconnect_attempts': self.reconnect_attempts,
                'max_attempts': self.max_reconnect_attempts
            }
        else:
            # إذا العملية ماتت، تحديث الحالة
            if self.is_running:
                logger.warning("⚠️ العملية توقفت لكن الحالة كانت مازالت نشطة - تم التصحيح")
                self.is_running = False
            return {'active': False}

    def get_detailed_status(self):
        """الحصول على حالة مفصلة"""
        status = self.get_status()
        if status['active']:
            return f"✅ البث نشط\n📊 محاولات إعادة الاتصال: {status['reconnect_attempts']}/{status['max_attempts']}"
        return "❌ البث متوقف"
