import sqlite3
from datetime import datetime
from contextlib import contextmanager
import config

# AIDEV-NOTE: Database module for tracking processed posts and discovered startups
# Uses SQLite for simplicity and portability

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Posts table - tracks all processed HN posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT,
                author TEXT,
                score INTEGER DEFAULT 0,
                num_comments INTEGER DEFAULT 0,
                created_time INTEGER NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_startup BOOLEAN DEFAULT 0,
                is_innovation BOOLEAN DEFAULT 0,
                item_type TEXT DEFAULT 'other'
            )
        ''')
        
        # Startups table - detailed info about identified startups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS startups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                ai_score REAL DEFAULT 0.0,
                category TEXT,
                summary TEXT,
                founder_info TEXT,
                funding_stage TEXT,
                analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        ''')
        
        # Run history - track agent runs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posts_processed INTEGER DEFAULT 0,
                new_startups_found INTEGER DEFAULT 0,
                total_posts_fetched INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed',
                error_message TEXT
            )
        ''')
        
        # Create indices for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_created_time ON posts(created_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_is_startup ON posts(is_startup)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_startups_ai_score ON startups(ai_score)')
        
        conn.commit()

def is_post_processed(post_id):
    """Check if a post has already been processed"""
    with get_db() as conn:
        cursor = conn.cursor()
        result = cursor.execute('SELECT 1 FROM posts WHERE id = ?', (post_id,)).fetchone()
        return result is not None

def save_post(post_data):
    """Save a processed post to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO posts 
            (id, title, url, author, score, num_comments, created_time, is_startup, is_innovation, item_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post_data['id'],
            post_data['title'],
            post_data.get('url'),
            post_data.get('by'),
            post_data.get('score', 0),
            post_data.get('descendants', 0),
            post_data['time'],
            post_data.get('is_startup', False),
            post_data.get('is_innovation', False),
            post_data.get('item_type', 'other')
        ))
        conn.commit()

def save_startup(startup_data):
    """Save identified startup information"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO startups 
            (post_id, ai_score, category, summary, founder_info, funding_stage, analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            startup_data['post_id'],
            startup_data.get('ai_score', 0.0),
            startup_data.get('category'),
            startup_data.get('summary'),
            startup_data.get('founder_info'),
            startup_data.get('funding_stage'),
            startup_data.get('analysis')
        ))
        conn.commit()

def get_last_processed_time():
    """Get the timestamp of the most recently processed post"""
    with get_db() as conn:
        cursor = conn.cursor()
        result = cursor.execute(
            'SELECT MAX(created_time) as last_time FROM posts'
        ).fetchone()
        return result['last_time'] if result['last_time'] else None

def get_top_startups(limit=50, days=7):
    """Get top startups by AI score from recent days"""
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff_time = int((datetime.now().timestamp() - (days * 24 * 60 * 60)))
        
        results = cursor.execute('''
            SELECT 
                p.*, 
                s.ai_score, 
                s.category, 
                s.summary,
                s.funding_stage,
                s.analysis
            FROM posts p
            JOIN startups s ON p.id = s.post_id
            WHERE p.created_time > ?
            ORDER BY s.ai_score DESC
            LIMIT ?
        ''', (cutoff_time, limit)).fetchall()
        
        return [dict(row) for row in results]

def save_run_history(posts_processed, new_startups, total_fetched, status='completed', error=None):
    """Save run history for monitoring"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO run_history 
            (posts_processed, new_startups_found, total_posts_fetched, status, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (posts_processed, new_startups, total_fetched, status, error))
        conn.commit()

# AIDEV-TODO: Add functions for data cleanup and maintenance (e.g., remove old posts)