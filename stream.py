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

    def monitor_process(self):
        """مراقبة العملية وإعادة الاتصال عند الفشل"""
        while self.is_running:
            if self.process is None:
                break
            
            if self.process.poll() is not None:
                logger.warning("❌ البث توقف! محاولة إعادة الاتصال...")
                time.sleep(2)
                if self.is_running:
                    self.restart_stream()
            
            time.sleep(3)

    def restart_stream(self):
        """إعادة تشغيل العملية"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            time.sleep(1)
        
        if hasattr(self, 'last_command'):
            self.process = subprocess.Popen(
                self.last_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

    def start_stream(self, m3u8_url, rtmp_url, stream_key, logo_path=None):
        """بدء البث مع إعادة الاتصال التلقائي"""
        if self.is_running:
            return False, "البث يعمل بالفعل!"

        rtmp_url = rtmp_url.rstrip('/')
        full_rtmp_url = f"{rtmp_url}/{stream_key}"

        # الأمر - نسخ مباشر من المصدر مع اللوجو
        command = [
            config.FFMPEG_CMD,
            '-hide_banner',
            '-loglevel', 'error',
            '-timeout', '15000000',
            '-reconnect', '1',
            '-reconnect_streamed', '1',
            '-reconnect_delay_max', '10',
            '-re',
            '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-i', m3u8_url
        ]

        # إضافة اللوجو إذا كان موجوداً
        if logo_path and os.path.exists(logo_path):
            command.extend(['-i', logo_path])
            command.extend([
                '-filter_complex',
                '[0:v]fps=30[v];[1:v]scale=600:-1[logo];[v][logo]overlay=W-w-10:10'
            ])
        else:
            command.extend(['-vf', 'fps=30'])

        command.extend([
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-crf', '28',
            '-g', '2',
            '-b:v', '3500k',
            '-maxrate', '4000k',
            '-bufsize', '8000k',
            '-c:a', 'copy',
            '-f', 'flv',
            full_rtmp_url
        ])

        try:
            logger.info(f"🚀 بدء البث: {m3u8_url[:50]}...")
            
            self.last_command = command
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.is_running = True
            time.sleep(5)
            
            if self.process.poll() is None:
                # بدء مراقبة العملية
                self.monitor_thread = threading.Thread(target=self.monitor_process, daemon=True)
                self.monitor_thread.start()
                
                logger.info("✅ البث نشط!")
                return True, "✅ البث نشط الآن! تحقق من فيسبوك."
            else:
                self.is_running = False
                return False, "❌ فشل البث. تحقق من الروابط."
                
        except Exception as e:
            self.is_running = False
            logger.error(f"❌ خطأ: {str(e)}")
            return False, f"❌ خطأ: {str(e)}"

    def stop_stream(self):
        """إيقاف البث"""
        self.is_running = False
        
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            
            self.process = None
            logger.info("✅ تم إيقاف البث")
            return True, "✅ تم إيقاف البث."
        
        return False, "❌ لا يوجد بث نشط."

    def get_status(self):
        """التحقق من حالة البث"""
        return self.is_running and self.process and self.process.poll() is None
