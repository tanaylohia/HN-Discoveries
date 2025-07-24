from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        discoveries = []
        
        # Check for Supabase credentials
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            try:
                import requests
                
                # Query Supabase for discoveries
                headers = {
                    'apikey': supabase_key,
                    'Authorization': f'Bearer {supabase_key}',
                    'Content-Type': 'application/json'
                }
                
                # Use the discovery_details view for easy querying
                response = requests.get(
                    f'{supabase_url}/rest/v1/discovery_details?order=created_time.desc&limit=100',
                    headers=headers
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    for row in results:
                        discovery = {
                            "id": row['id'],
                            "type": row['item_type'],
                            "name": row.get('analysis', {}).get('startup_name', row['title']),
                            "title": row['title'],
                            "url": row.get('url', ''),
                            "hn_url": f"https://news.ycombinator.com/item?id={row['id']}",
                            "innovation_score": float(row.get('innovation_score', 0)),
                            "summary": row.get('summary', ''),
                            "why_interesting": row.get('why_interesting', ''),
                            "category": row.get('category', ''),
                            "key_features": row.get('key_features', []),
                            "timestamp": datetime.fromtimestamp(row['created_time']).isoformat() + 'Z',
                            "score": row.get('score', 0),
                            "num_comments": row.get('num_comments', 0)
                        }
                        discoveries.append(discovery)
                else:
                    print(f"Supabase error: {response.status_code} - {response.text}")
                    discoveries = self.get_mock_discoveries()
                    
            except Exception as e:
                print(f"Error fetching from Supabase: {e}")
                discoveries = self.get_mock_discoveries()
        else:
            # No Supabase configured, use mock data
            discoveries = self.get_mock_discoveries()
        
        # Prepare response
        response_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat() + 'Z',
                "total_discoveries": len(discoveries),
                "total_startups": len([d for d in discoveries if d['type'] == 'startup']),
                "total_innovations": len([d for d in discoveries if d['type'] == 'innovation']),
                "data_source": "supabase" if (supabase_url and discoveries and discoveries != self.get_mock_discoveries()) else "mock"
            },
            "discoveries": discoveries
        }
        
        # Send response
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
    
    def get_mock_discoveries(self):
        """Return mock discoveries for demonstration"""
        return [
            {
                "id": 44657727,
                "type": "startup",
                "name": "AICodeAssist",
                "title": "Show HN: AICodeAssist - AI-powered code review for teams",
                "url": "https://aicodeassist.example.com",
                "hn_url": "https://news.ycombinator.com/item?id=44657727",
                "innovation_score": 8.5,
                "summary": "An AI-powered code review tool that automatically detects bugs, suggests improvements, and ensures code quality across your team.",
                "why_interesting": "Uses advanced LLMs to understand code context and provide meaningful reviews, reducing review time by 70%",
                "category": "Developer Tools, AI/ML",
                "key_features": ["Automatic bug detection", "Style consistency", "Security scanning", "Team collaboration"],
                "timestamp": "2024-07-15T10:30:00Z",
                "score": 245,
                "num_comments": 89
            },
            {
                "id": 44657728,
                "type": "innovation",
                "name": "QuantumSim",
                "title": "QuantumSim: Open-source quantum computing simulator in Rust",
                "url": "https://github.com/example/quantumsim",
                "hn_url": "https://news.ycombinator.com/item?id=44657728",
                "innovation_score": 9.2,
                "summary": "A blazing-fast quantum computing simulator written in Rust that can simulate up to 30 qubits on consumer hardware.",
                "why_interesting": "Achieves 10x performance improvement over existing simulators through novel optimization techniques",
                "category": "Quantum Computing, Open Source",
                "key_features": ["GPU acceleration", "Novel optimization algorithms", "Educational visualizations"],
                "timestamp": "2024-07-14T15:45:00Z",
                "score": 412,
                "num_comments": 156
            },
            {
                "id": 44657729,
                "type": "startup",
                "name": "DataLoom",
                "title": "Launch HN: DataLoom - Real-time data pipeline for ML teams",
                "url": "https://dataloom.io",
                "hn_url": "https://news.ycombinator.com/item?id=44657729",
                "innovation_score": 7.8,
                "summary": "DataLoom provides real-time data pipelines specifically designed for machine learning workflows, with automatic versioning and lineage tracking.",
                "why_interesting": "Solves the data versioning problem in ML with a Git-like interface for datasets",
                "category": "Data Infrastructure, Machine Learning",
                "key_features": ["Git-like versioning", "Real-time processing", "ML framework integration", "Data lineage"],
                "timestamp": "2024-07-13T09:20:00Z",
                "score": 178,
                "num_comments": 67
            }
        ]