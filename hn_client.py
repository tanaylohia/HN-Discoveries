import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import config

# AIDEV-NOTE: Hacker News API client with support for historical data fetching
# Uses Firebase API for efficient data retrieval

class HNClient:
    def __init__(self):
        self.base_url = config.HN_API_BASE
        self.session = requests.Session()
        
    def _get(self, endpoint: str) -> Optional[Dict]:
        """Make a GET request to HN API"""
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}.json")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
            return None
    
    def get_item(self, item_id: int) -> Optional[Dict]:
        """Get a single item (story, comment, etc.) by ID"""
        return self._get(f"item/{item_id}")
    
    def get_top_stories(self, limit: int = 500) -> List[int]:
        """Get top story IDs"""
        story_ids = self._get("topstories") or []
        return story_ids[:limit]
    
    def get_new_stories(self, limit: int = 500) -> List[int]:
        """Get new story IDs"""
        story_ids = self._get("newstories") or []
        return story_ids[:limit]
    
    def get_best_stories(self, limit: int = 500) -> List[int]:
        """Get best story IDs"""
        story_ids = self._get("beststories") or []
        return story_ids[:limit]
    
    def get_show_stories(self, limit: int = 200) -> List[int]:
        """Get Show HN story IDs"""
        story_ids = self._get("showstories") or []
        return story_ids[:limit]
    
    def get_ask_stories(self, limit: int = 200) -> List[int]:
        """Get Ask HN story IDs"""
        story_ids = self._get("askstories") or []
        return story_ids[:limit]
    
    def fetch_stories_by_time(self, start_time: int, end_time: Optional[int] = None) -> List[Dict]:
        """
        Fetch stories within a time range
        
        Args:
            start_time: Unix timestamp for start
            end_time: Unix timestamp for end (default: now)
        """
        if end_time is None:
            end_time = int(datetime.now().timestamp())
        
        # AIDEV-NOTE: HN API doesn't support time-based queries directly
        # We need to fetch stories and filter by timestamp
        stories = []
        
        # For initial testing, just fetch from Show HN and top stories
        print("Fetching Show HN stories...")
        show_ids = self.get_show_stories(limit=200)
        
        print("Fetching top stories...")
        top_ids = self.get_top_stories(limit=200)
        
        all_story_ids = list(set(show_ids + top_ids))
        print(f"Checking {len(all_story_ids)} stories for time range...")
        
        # Process in batches to avoid overwhelming the API
        batch_size = 10
        processed = 0
        found = 0
        
        for story_id in all_story_ids:
            story = self.get_item(story_id)
            
            if story and story.get('type') == 'story':
                story_time = story.get('time', 0)
                
                if start_time <= story_time <= end_time:
                    stories.append(story)
                    found += 1
                    
                    # Stop early if we have enough stories for testing
                    if found >= 50:
                        print(f"Found {found} stories, stopping early for testing...")
                        break
            
            processed += 1
            if processed % batch_size == 0:
                print(f"Processed {processed}/{len(all_story_ids)} stories, found {found} in time range...")
                time.sleep(0.5)  # Lighter rate limiting
        
        return sorted(stories, key=lambda x: x.get('time', 0), reverse=True)
    
    def fetch_historical_stories(self, days: int = 60) -> List[Dict]:
        """
        Fetch historical stories going back specified days
        
        Args:
            days: Number of days to look back
        """
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        print(f"Fetching stories from last {days} days...")
        return self.fetch_stories_by_time(start_time, end_time)
    
    def fetch_recent_stories(self, since_timestamp: int) -> List[Dict]:
        """
        Fetch stories created after a specific timestamp
        
        Args:
            since_timestamp: Unix timestamp
        """
        return self.fetch_stories_by_time(since_timestamp)
    
    def get_story_with_comments(self, story_id: int, max_depth: int = 2) -> Optional[Dict]:
        """
        Get a story with its comment tree
        
        Args:
            story_id: HN story ID
            max_depth: Maximum depth of comment tree to fetch
        """
        story = self.get_item(story_id)
        if not story:
            return None
        
        # AIDEV-TODO: Implement recursive comment fetching if needed for deeper analysis
        # For now, we'll just return the story with basic info
        
        return story

# AIDEV-NOTE: Consider implementing caching to reduce API calls for frequently accessed stories