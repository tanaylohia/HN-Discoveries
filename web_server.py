#!/usr/bin/env python3

import os
import json
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import sys

# AIDEV-NOTE: Simple web server to serve the dashboard and handle API requests

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory=".", **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Serve dashboard files
        if parsed_path.path == '/':
            self.path = '/dashboard/index.html'
        elif parsed_path.path == '/reports/latest.json':
            # Serve the latest report
            self.serve_latest_report()
            return
        
        # Default file serving
        super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/refresh':
            self.handle_refresh()
        else:
            self.send_error(404)
    
    def serve_latest_report(self):
        """Serve the latest JSON report"""
        try:
            report_path = os.path.join('reports', 'latest.json')
            if os.path.exists(report_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                with open(report_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            else:
                # No report exists yet, return empty structure
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                empty_report = {
                    'metadata': {
                        'total_discoveries': 0,
                        'total_startups': 0,
                        'total_innovations': 0,
                        'generated_at_ist': 'No data yet'
                    },
                    'discoveries': []
                }
                self.wfile.write(json.dumps(empty_report).encode())
                
        except Exception as e:
            self.send_error(500, f"Error serving report: {str(e)}")
    
    def handle_refresh(self):
        """Handle refresh request by running the agent"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Start refresh in background thread
        def run_agent():
            try:
                # Run the agent
                subprocess.run([sys.executable, "main.py", "--run-once"], 
                             capture_output=True, text=True)
            except Exception as e:
                print(f"Error running agent: {e}")
        
        thread = threading.Thread(target=run_agent)
        thread.daemon = True
        thread.start()
        
        response = {'status': 'refresh_started'}
        self.wfile.write(json.dumps(response).encode())
    
    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def run_server(port=8080):
    """Run the web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print(f"Dashboard server running at http://localhost:{port}")
    print(f"Open http://localhost:{port} in your browser to view the dashboard")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='HN Discoveries Dashboard Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run server on')
    args = parser.parse_args()
    
    run_server(args.port)