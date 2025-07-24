from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # For Vercel, we can't run long-running processes
        # So we'll return a message indicating manual refresh is needed
        response_data = {
            "success": True,
            "message": "Refresh noted. The data will be updated in the next scheduled run.",
            "timestamp": datetime.now().isoformat() + 'Z',
            "note": "For real-time updates, run the agent locally or use a scheduled job service."
        }
        
        # Send response
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return