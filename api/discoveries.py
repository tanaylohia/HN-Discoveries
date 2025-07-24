"""
Vercel Serverless Function for HN Discoveries API
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Import here to avoid module loading issues
            from database import init_database, get_top_startups
            from reporter import Reporter
            
            # Initialize database
            init_database()
            
            # Get recent discoveries
            discoveries = get_top_startups(limit=100, days=30)
            
            # Format response
            response = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_discoveries": len(discoveries)
                },
                "discoveries": []
            }
            
            for item in discoveries:
                try:
                    analysis = json.loads(item.get('analysis', '{}'))
                except:
                    analysis = {}
                
                discovery = {
                    "id": item['id'],
                    "type": item.get('item_type', 'startup'),
                    "name": analysis.get('startup_name', item['title']),
                    "title": item['title'],
                    "url": item.get('url', ''),
                    "hn_url": f"https://news.ycombinator.com/item?id={item['id']}",
                    "innovation_score": analysis.get('innovation_score', item.get('ai_score', 0)),
                    "summary": analysis.get('summary', item.get('summary', '')),
                    "why_interesting": analysis.get('why_interesting', ''),
                    "category": analysis.get('category', item.get('category', '')),
                    "key_features": analysis.get('key_features', []),
                    "timestamp": datetime.fromtimestamp(item['created_time']).isoformat(),
                    "score": item.get('score', 0),
                    "num_comments": item.get('num_comments', 0)
                }
                response["discoveries"].append(discovery)
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "message": "Failed to fetch discoveries"
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()