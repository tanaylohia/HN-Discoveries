import json
import os
import sqlite3
from datetime import datetime

def get_db_connection():
    """Create a database connection"""
    db_path = os.path.join('/tmp', 'hn_discoveries.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create minimal tables for reading
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT,
            author TEXT,
            score INTEGER DEFAULT 0,
            num_comments INTEGER DEFAULT 0,
            created_time INTEGER NOT NULL,
            item_type TEXT DEFAULT 'other'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS startups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            ai_score REAL DEFAULT 0.0,
            category TEXT,
            summary TEXT,
            analysis TEXT,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def handler(request, response):
    """Handle the API request"""
    # Set CORS headers
    response.status_code = 200
    response.headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return response
    
    try:
        # Initialize database
        init_database()
        
        # Mock data for now since database might be empty
        mock_discoveries = [
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
        
        # Try to get real data from database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get recent discoveries
            results = cursor.execute('''
                SELECT 
                    p.*, 
                    s.ai_score, 
                    s.category, 
                    s.summary,
                    s.analysis
                FROM posts p
                LEFT JOIN startups s ON p.id = s.post_id
                WHERE p.item_type IN ('startup', 'innovation')
                ORDER BY p.created_time DESC
                LIMIT 100
            ''').fetchall()
            
            if results:
                discoveries = []
                for row in results:
                    try:
                        analysis = json.loads(row['analysis'] or '{}')
                    except:
                        analysis = {}
                    
                    discovery = {
                        "id": row['id'],
                        "type": row['item_type'],
                        "name": analysis.get('startup_name', row['title']),
                        "title": row['title'],
                        "url": row['url'] or '',
                        "hn_url": f"https://news.ycombinator.com/item?id={row['id']}",
                        "innovation_score": analysis.get('innovation_score', row['ai_score'] or 0),
                        "summary": analysis.get('summary', row['summary'] or ''),
                        "why_interesting": analysis.get('why_interesting', ''),
                        "category": analysis.get('category', row['category'] or ''),
                        "key_features": analysis.get('key_features', []),
                        "timestamp": datetime.fromtimestamp(row['created_time']).isoformat() + 'Z',
                        "score": row['score'] or 0,
                        "num_comments": row['num_comments'] or 0
                    }
                    discoveries.append(discovery)
                
                mock_discoveries = discoveries
            
            conn.close()
        except Exception as e:
            # If database query fails, use mock data
            print(f"Database error: {e}")
        
        # Prepare response
        response_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat() + 'Z',
                "total_discoveries": len(mock_discoveries),
                "total_startups": len([d for d in mock_discoveries if d['type'] == 'startup']),
                "total_innovations": len([d for d in mock_discoveries if d['type'] == 'innovation'])
            },
            "discoveries": mock_discoveries
        }
        
        response.body = json.dumps(response_data)
        
    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({
            "error": str(e),
            "message": "Internal server error"
        })
    
    return response