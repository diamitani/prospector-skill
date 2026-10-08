from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to sys.path so modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/status'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "skill": "signal-to-email-prospecting",
                "version": "0.3.0",
                "pal_protocol": "Parse → Ambiguity Scan → Latent Intent → Expand → Compile"
            }).encode('utf-8'))
            return
        elif self.path.startswith('/api/leads'):
            leads_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'run-output', 'leads.json')
            if not os.path.exists(leads_path):
                leads_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'leads.json')
            
            if os.path.exists(leads_path):
                with open(leads_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
                return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "name": "Prospector PAL API",
            "version": "0.3.0",
            "endpoints": ["/api/status", "/api/leads", "/api/run"]
        }).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception:
            body = {}
            
        brief = body.get('brief', 'Find 10 North American B2B SaaS companies hiring RevOps leaders')
        project = body.get('project', 'web-demo')
        
        try:
            import demo_adapter
            from prospect import Engine
            
            engine = Engine(demo_adapter)
            result = engine.run(brief, project, {'domains': set(), 'emails': set()})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
