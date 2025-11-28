from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add root directory to path to allow importing api.utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from api.utils import ContentGenerator

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len)
        try:
            data = json.loads(post_body)
            api_key = data.get('api_key')
            topic = data.get('topic')
            materials = data.get('materials', '')
            slide_count = data.get('slide_count', 10)
            language = data.get('language', 'Korean')

            if not api_key:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "API Key is required"}).encode('utf-8'))
                return

            generator = ContentGenerator(api_key)
            result = generator.analyze_and_generate_structure(topic, materials, language, slide_count)
            
            if result:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Failed to generate structure"}).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
