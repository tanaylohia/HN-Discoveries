import schedule
import time
from datetime import datetime
import pytz
import config

# AIDEV-NOTE: Scheduler module for running the agent at 8 AM IST daily

class Scheduler:
    def __init__(self, job_func):
        """
        Initialize scheduler with the job function to run
        
        Args:
            job_func: Function to execute on schedule
        """
        self.job_func = job_func
        self.timezone = config.TIMEZONE
        
    def run_if_time(self):
        """Check if it's time to run and execute job"""
        current_time = datetime.now(self.timezone)
        scheduled_hour, scheduled_minute = map(int, config.REFRESH_TIME.split(':'))
        
        if (current_time.hour == scheduled_hour and 
            current_time.minute == scheduled_minute):
            print(f"Running scheduled job at {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            self.job_func()
            # Sleep for 60 seconds to avoid running multiple times in the same minute
            time.sleep(60)
    
    def start(self):
        """Start the scheduler loop"""
        print(f"Scheduler started. Will run daily at {config.REFRESH_TIME} IST")
        print(f"Current time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Schedule the job
        schedule.every().day.at(config.REFRESH_TIME).do(self.job_func)
        
        # Also run immediately on first start
        print("Running initial scan...")
        self.job_func()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    def run_once(self):
        """Run the job once and exit"""
        print(f"Running one-time execution at {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        self.job_func()

# AIDEV-TODO: Add support for multiple schedules (e.g., different times for different types of scans)
# AIDEV-TODO: Add scheduling persistence to resume after restarts