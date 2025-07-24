"""
Supabase database module for HN Discoveries
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AIDEV-NOTE: Supabase database module for cloud persistence
# Replaces local SQLite with Supabase PostgreSQL

class SupabaseDB:
    def __init__(self):
        """Initialize Supabase client"""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment")
        
        self.client: Client = create_client(url, key)
    
    def is_post_processed(self, post_id: int) -> bool:
        """Check if a post has already been processed"""
        try:
            response = self.client.table('posts').select('id').eq('id', post_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error checking post {post_id}: {e}")
            return False
    
    def save_post(self, post_data: Dict) -> bool:
        """Save a processed post to database"""
        try:
            # Prepare post data
            post_record = {
                'id': post_data['id'],
                'title': post_data['title'],
                'url': post_data.get('url'),
                'author': post_data.get('by'),
                'score': post_data.get('score', 0),
                'num_comments': post_data.get('descendants', 0),
                'created_time': post_data['time'],
                'is_startup': post_data.get('is_startup', False),
                'is_innovation': post_data.get('is_innovation', False),
                'item_type': post_data.get('item_type', 'other')
            }
            
            # Upsert post
            self.client.table('posts').upsert(post_record).execute()
            return True
        except Exception as e:
            print(f"Error saving post {post_data.get('id')}: {e}")
            return False
    
    def save_discovery(self, discovery_data: Dict) -> bool:
        """Save discovery (startup/innovation) information"""
        try:
            # Parse analysis if it's a string
            analysis = discovery_data.get('analysis', {})
            if isinstance(analysis, str):
                try:
                    analysis = json.loads(analysis)
                except:
                    analysis = {}
            
            # Prepare discovery record
            discovery_record = {
                'post_id': discovery_data['post_id'],
                'innovation_score': float(discovery_data.get('ai_score', 0.0)),
                'category': discovery_data.get('category', ''),
                'summary': discovery_data.get('summary', ''),
                'why_interesting': analysis.get('why_interesting', ''),
                'key_features': analysis.get('key_features', []),
                'analysis': analysis
            }
            
            # Insert discovery
            self.client.table('discoveries').insert(discovery_record).execute()
            return True
        except Exception as e:
            print(f"Error saving discovery for post {discovery_data.get('post_id')}: {e}")
            return False
    
    def get_last_processed_time(self) -> Optional[int]:
        """Get the timestamp of the most recently processed post"""
        try:
            response = self.client.table('posts')\
                .select('created_time')\
                .order('created_time', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]['created_time']
            return None
        except Exception as e:
            print(f"Error getting last processed time: {e}")
            return None
    
    def get_top_discoveries(self, limit: int = 50, days: int = 7) -> List[Dict]:
        """Get top discoveries by innovation score from recent days"""
        try:
            # Calculate cutoff timestamp
            cutoff_time = int((datetime.now().timestamp() - (days * 24 * 60 * 60)))
            
            # Query using the view
            response = self.client.table('discovery_details')\
                .select('*')\
                .gte('created_time', cutoff_time)\
                .order('innovation_score', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
        except Exception as e:
            print(f"Error getting top discoveries: {e}")
            return []
    
    def save_run_history(self, posts_processed: int, new_discoveries: int, 
                        total_fetched: int, status: str = 'completed', error: Optional[str] = None):
        """Save run history for monitoring"""
        try:
            # Create run_history table if it doesn't exist
            # Note: In production, this should be in your Supabase schema
            run_record = {
                'posts_processed': posts_processed,
                'new_discoveries_found': new_discoveries,
                'total_posts_fetched': total_fetched,
                'status': status,
                'error_message': error
            }
            
            # For now, we'll just log this
            print(f"Run completed: {run_record}")
            return True
        except Exception as e:
            print(f"Error saving run history: {e}")
            return False

# Create a singleton instance
_db_instance = None

def get_db() -> SupabaseDB:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SupabaseDB()
    return _db_instance

# Export functions that match the original database.py interface
def init_database():
    """Initialize database (no-op for Supabase as schema is pre-created)"""
    get_db()  # Just ensure connection works
    print("Connected to Supabase database")

def is_post_processed(post_id: int) -> bool:
    return get_db().is_post_processed(post_id)

def save_post(post_data: Dict):
    return get_db().save_post(post_data)

def save_startup(startup_data: Dict):
    return get_db().save_discovery(startup_data)

def get_last_processed_time() -> Optional[int]:
    return get_db().get_last_processed_time()

def get_top_startups(limit: int = 50, days: int = 7) -> List[Dict]:
    return get_db().get_top_discoveries(limit, days)

def save_run_history(posts_processed: int, new_startups: int, total_fetched: int, 
                    status: str = 'completed', error: Optional[str] = None):
    return get_db().save_run_history(posts_processed, new_startups, total_fetched, status, error)