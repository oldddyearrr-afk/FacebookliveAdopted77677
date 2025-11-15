
#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__)

def get_stream_status():
    """Check if stream is running"""
    try:
        result = subprocess.run(
            ['tmux', 'has-session', '-t', 'fbstream'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def get_stream_info():
    """Get stream information"""
    status = get_stream_status()
    
    info = {
        'status': 'running' if status else 'stopped',
        'uptime': None,
        'log_file': None
    }
    
    if status:
        # Get uptime
        try:
            result = subprocess.run(
                ['tmux', 'display-message', '-t', 'fbstream', '-p', '#{session_created}'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                info['uptime'] = result.stdout.strip()
        except:
            pass
    
    # Get latest log file
    if os.path.exists('logs'):
        logs = [f for f in os.listdir('logs') if f.endswith('.log')]
        if logs:
            info['log_file'] = max(logs)
    
    return info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    return jsonify(get_stream_info())

@app.route('/api/start', methods=['POST'])
def api_start():
    try:
        # Check if already running
        if get_stream_status():
            # Stop first
            subprocess.run(['bash', 'control.sh', 'stop'], check=False)
            import time
            time.sleep(2)
        
        # Start stream directly using main.sh in background
        # This avoids the issue with control.sh waiting
        subprocess.Popen(
            ['bash', '-c', 'source config.sh && bash main.sh &'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Give it a moment to start
        import time
        time.sleep(3)
        
        # Verify it started
        if get_stream_status():
            return jsonify({'success': True, 'message': 'Stream started'})
        else:
            return jsonify({'success': False, 'error': 'Stream failed to start - check secrets and config'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    try:
        subprocess.run(['bash', 'control.sh', 'stop'], check=True)
        return jsonify({'success': True, 'message': 'Stream stopped'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs')
def api_logs():
    try:
        info = get_stream_info()
        if info['log_file']:
            log_path = os.path.join('logs', info['log_file'])
            with open(log_path, 'r') as f:
                lines = f.readlines()
                return jsonify({'logs': lines[-50:]})  # Last 50 lines
        return jsonify({'logs': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
