from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from api.utils import PPTGenerator

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len)
        try:
            data = json.loads(post_body)
            slides = data.get('slides')
            
            if not slides:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Slides data is required"}).encode('utf-8'))
                return

            ppt_gen = PPTGenerator()
            ppt_io = ppt_gen.generate_ppt({"slides": slides})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
            self.send_header('Content-Disposition', 'attachment; filename="presentation.pptx"')
            self.end_headers()
            self.wfile.write(ppt_io.getvalue())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
