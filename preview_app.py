#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
import config
from pathlib import Path

PORT = 5000

class PreviewHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('templates/preview.html', 'r', encoding='utf-8') as f:
                html = f.read()
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = {
                'offset_x': config.LOGO_OFFSET_X,
                'offset_y': config.LOGO_OFFSET_Y,
                'size': config.LOGO_SIZE,
                'opacity': config.LOGO_OPACITY
            }
            self.wfile.write(json.dumps(data).encode('utf-8'))
        elif self.path == '/static/logo.png':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open('static/logo.png', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Handler = PreviewHandler
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"معاينة اللوجو تعمل على http://localhost:{PORT}")
        httpd.serve_forever()
