import re
from typing import Dict, List, Tuple
import config

# AIDEV-NOTE: Startup detection module using keyword matching and heuristics
# This provides initial filtering before AI analysis

class StartupDetector:
    def __init__(self):
        self.keywords = config.STARTUP_KEYWORDS
        self.domain_patterns = [
            r'producthunt\.com',
            r'techcrunch\.com',
            r'ycombinator\.com',
            r'github\.com/.*launch',
            r'.*\.ai/?$',  # Many AI startups use .ai domains
            r'.*app\.com',
            r'.*\.io/?$'
        ]
        
        # Negative patterns - likely NOT startups
        self.negative_patterns = [
            r'wikipedia\.org',
            r'arxiv\.org',
            r'medium\.com',
            r'reddit\.com',
            r'twitter\.com',
            r'youtube\.com'
        ]
    
    def calculate_startup_score(self, post: Dict) -> Tuple[float, List[str]]:
        """
        Calculate a startup likelihood score (0-1) and return matching indicators
        
        Returns:
            Tuple of (score, list of matching indicators)
        """
        score = 0.0
        indicators = []
        
        title = post.get('title', '').lower()
        url = post.get('url', '').lower()
        
        # Check title for startup keywords
        for keyword in self.keywords:
            if keyword.lower() in title:
                score += 0.2
                indicators.append(f"Title contains '{keyword}'")
        
        # Special boost for "Show HN" posts
        if title.startswith('show hn:'):
            score += 0.3
            indicators.append("Show HN post")
        
        # Check URL patterns
        if url:
            for pattern in self.domain_patterns:
                if re.search(pattern, url):
                    score += 0.1
                    indicators.append(f"URL matches startup pattern: {pattern}")
                    break
            
            # Negative patterns reduce score
            for pattern in self.negative_patterns:
                if re.search(pattern, url):
                    score -= 0.3
                    indicators.append(f"URL matches non-startup pattern: {pattern}")
                    break
        
        # Engagement metrics
        if post.get('score', 0) >= 50:
            score += 0.1
            indicators.append("High engagement score")
        
        if post.get('descendants', 0) >= 20:
            score += 0.1
            indicators.append("Active discussion")
        
        # Cap score between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score, indicators
    
    def is_likely_startup(self, post: Dict, threshold: float = 0.3) -> bool:
        """
        Determine if a post is likely about a startup
        
        Args:
            post: HN post data
            threshold: Minimum score to consider as startup (default 0.3)
        """
        score, _ = self.calculate_startup_score(post)
        return score >= threshold
    
    def filter_startup_posts(self, posts: List[Dict], threshold: float = 0.3) -> List[Dict]:
        """
        Filter a list of posts to find likely startup-related ones or technical innovations
        
        Args:
            posts: List of HN posts
            threshold: Minimum score threshold
        """
        startup_posts = []
        
        for post in posts:
            title = post.get('title', '').lower()
            
            # Be more inclusive - let AI decide if it's interesting
            # Primary filter is Show HN posts or high engagement
            if 'show hn:' in title or post.get('score', 0) >= 50:
                score, indicators = self.calculate_startup_score(post)
                post['startup_score'] = score
                post['startup_indicators'] = indicators
                startup_posts.append(post)
            elif post.get('score', 0) >= 30 and post.get('descendants', 0) >= 10:
                # Also include high engagement posts that might be innovations
                score, indicators = self.calculate_startup_score(post)
                post['startup_score'] = score
                post['startup_indicators'] = indicators
                startup_posts.append(post)
        
        return startup_posts
    
    def extract_startup_signals(self, post: Dict) -> Dict:
        """
        Extract specific startup-related signals from a post
        
        Returns dict with extracted information
        """
        signals = {
            'is_show_hn': post.get('title', '').lower().startswith('show hn:'),
            'is_launch_hn': post.get('title', '').lower().startswith('launch hn:'),
            'mentions_funding': False,
            'mentions_yc': False,
            'has_product_url': False,
            'founder_post': False
        }
        
        title_lower = post.get('title', '').lower()
        
        # Check for funding mentions
        funding_keywords = ['raised', 'funding', 'seed', 'series a', 'series b', '$m', '$k']
        signals['mentions_funding'] = any(kw in title_lower for kw in funding_keywords)
        
        # Check for YC mentions
        yc_keywords = ['yc', 'y combinator', 'ycombinator']
        signals['mentions_yc'] = any(kw in title_lower for kw in yc_keywords)
        
        # Check if posted by founder (heuristic based on "we" usage)
        founder_keywords = ['we built', 'we launched', 'our startup', 'i built', 'i launched']
        signals['founder_post'] = any(kw in title_lower for kw in founder_keywords)
        
        # Check if has product URL (not just discussion)
        url = post.get('url', '')
        if url and not any(domain in url for domain in ['ycombinator.com', 'reddit.com', 'medium.com']):
            signals['has_product_url'] = True
        
        return signals

# AIDEV-TODO: Add ML-based classification if rule-based approach isn't sufficient