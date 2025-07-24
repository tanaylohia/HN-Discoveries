#!/usr/bin/env python3

import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Dict

from database import init_database, is_post_processed, save_post, save_startup, get_last_processed_time, save_run_history, get_top_startups
from hn_client import HNClient
from startup_detector import StartupDetector
from ai_analyzer import AIAnalyzer
from reporter import Reporter
from scheduler import Scheduler
import config

# AIDEV-NOTE: Main entry point for the Hacker News Startup Discovery Agent
# Orchestrates the entire pipeline from data collection to report generation

class HNStartupAgent:
    def __init__(self, use_deepseek: bool = False):
        # Initialize all components
        self.hn_client = HNClient()
        self.detector = StartupDetector()
        self.analyzer = AIAnalyzer(use_deepseek=use_deepseek)
        self.reporter = Reporter()
        
        # Initialize database
        init_database()
        
        print("Hacker News Startup Agent initialized")
    
    def process_posts(self, posts: List[Dict]) -> tuple:
        """
        Process a list of posts through the pipeline
        
        Returns:
            Tuple of (processed_count, new_startups_count, startup_data_list)
        """
        processed_count = 0
        new_startups_count = 0
        startup_data_list = []
        
        # First, filter posts that look like startups
        potential_startups = self.detector.filter_startup_posts(posts)
        print(f"Found {len(potential_startups)} potential startups out of {len(posts)} posts")
        
        # Process each potential startup
        for post in potential_startups:
            # Skip if already processed
            if is_post_processed(post['id']):
                continue
            
            processed_count += 1
            
            # Analyze with AI
            print(f"Analyzing: {post['title'][:80]}...")
            analysis = self.analyzer.analyze_startup(post)
            
            if analysis and analysis['type'] in ['startup', 'innovation'] and analysis['innovation_score'] >= 5.0:
                # This is a quality startup or innovation
                new_startups_count += 1
                
                # Save to database
                post['is_startup'] = analysis['type'] == 'startup'
                post['is_innovation'] = analysis['type'] == 'innovation'
                post['item_type'] = analysis['type']
                save_post(post)
                
                startup_data = {
                    'post_id': post['id'],
                    'ai_score': analysis['ai_score'],
                    'category': analysis['category'],
                    'summary': analysis['summary'],
                    'founder_info': analysis.get('founder_info', ''),
                    'funding_stage': analysis.get('funding_stage', ''),
                    'analysis': str(analysis)  # Store full analysis as JSON string
                }
                save_startup(startup_data)
                
                startup_data_list.append({
                    'post': post,
                    'analysis': analysis
                })
            else:
                # Not a startup or low quality
                post['is_startup'] = False
                save_post(post)
        
        return processed_count, new_startups_count, startup_data_list
    
    def run_historical_scan(self, days: int = 60):
        """Run initial historical scan"""
        print(f"\n[Historical] Starting scan for last {days} days...")
        
        # Fetch historical posts
        posts = self.hn_client.fetch_historical_stories(days=days)
        print(f"Fetched {len(posts)} posts from the last {days} days")
        
        # Filter by minimum engagement
        engaged_posts = [p for p in posts if p.get('score', 0) >= config.MIN_SCORE]
        print(f"Filtered to {len(engaged_posts)} posts with minimum score of {config.MIN_SCORE}")
        
        # Process posts
        processed, new_startups, startup_data = self.process_posts(engaged_posts)
        
        # Generate report
        if startup_data:
            report_path = self.reporter.generate_report(startup_data)
            print(f"\n[Report] Generated: {report_path}")
        
        # Save run history
        save_run_history(processed, new_startups, len(posts))
        
        self.reporter.quick_summary(new_startups, processed)
    
    def run_daily_update(self):
        """Run daily update - only process new posts"""
        print(f"\n[Update] Running daily update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get last processed timestamp
        last_time = get_last_processed_time()
        
        if last_time:
            # Fetch posts since last run
            posts = self.hn_client.fetch_recent_stories(since_timestamp=last_time)
            print(f"Fetched {len(posts)} new posts since last run")
        else:
            # First run - do historical scan
            print("No previous run detected. Running historical scan...")
            return self.run_historical_scan()
        
        # Filter by minimum engagement
        engaged_posts = [p for p in posts if p.get('score', 0) >= config.MIN_SCORE]
        
        # Process posts
        processed, new_startups, startup_data = self.process_posts(engaged_posts)
        
        # Get recent top startups for report (last 7 days)
        all_recent_startups = get_top_startups(limit=50, days=7)
        
        # Generate report
        if all_recent_startups:
            report_path = self.reporter.generate_report(
                [{'post': s, 'analysis': {
                    'startup_name': s.get('title', 'Unknown'),
                    'category': s.get('category', 'Unknown'),
                    'stage': 'Unknown',
                    'summary': s.get('summary', ''),
                    'key_features': [],
                    'target_audience': '',
                    'business_model': '',
                    'founder_info': s.get('founder_info', ''),
                    'funding_stage': s.get('funding_stage', ''),
                    'why_interesting': s.get('analysis', ''),
                    'ai_score': s.get('ai_score', 0.0),
                    'is_startup': True,
                    'confidence': 1.0
                }} for s in all_recent_startups]
            )
            print(f"\n[Report] Generated: {report_path}")
        
        # Save run history
        save_run_history(processed, new_startups, len(posts))
        
        self.reporter.quick_summary(new_startups, processed)
    
    def run_custom_query(self, query: str):
        """Run a custom search query"""
        # AIDEV-TODO: Implement custom query functionality
        print("Custom query functionality not yet implemented")

def main():
    parser = argparse.ArgumentParser(
        description="Hacker News Startup Discovery Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run once and generate report
  python main.py --run-once
  
  # Run historical scan for last 30 days
  python main.py --historical --days 30
  
  # Run as scheduled daemon (8 AM IST daily)
  python main.py --daemon
  
  # Use DeepSeek instead of GPT for analysis
  python main.py --run-once --use-deepseek
        """
    )
    
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run once and exit (default: run as daemon)'
    )
    
    parser.add_argument(
        '--historical',
        action='store_true',
        help='Run historical scan'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=60,
        help='Days to look back for historical scan (default: 60)'
    )
    
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon with daily schedule'
    )
    
    parser.add_argument(
        '--use-deepseek',
        action='store_true',
        help='Use DeepSeek model instead of GPT'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Launch web dashboard'
    )
    
    args = parser.parse_args()
    
    # Check for API keys
    if not config.AZURE_OPENAI_API_KEY and not args.use_deepseek:
        print("Error: AZURE_OPENAI_API_KEY not set in .env file")
        sys.exit(1)
    
    if args.use_deepseek and not config.AZURE_DEEPSEEK_API_KEY:
        print("Error: AZURE_DEEPSEEK_API_KEY not set in .env file")
        sys.exit(1)
    
    # Check if launching dashboard
    if args.dashboard:
        from web_server import run_server
        run_server()
        return
    
    # Initialize agent
    agent = HNStartupAgent(use_deepseek=args.use_deepseek)
    
    if args.historical:
        # Run historical scan
        agent.run_historical_scan(days=args.days)
    elif args.daemon:
        # Run as daemon
        scheduler = Scheduler(agent.run_daily_update)
        scheduler.start()
    else:
        # Default: run once
        scheduler = Scheduler(agent.run_daily_update)
        scheduler.run_once()

if __name__ == "__main__":
    main()

# AIDEV-TODO: Add support for webhook notifications when high-score startups are found
# AIDEV-TODO: Add web dashboard for viewing reports