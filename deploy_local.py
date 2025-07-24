#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import webbrowser
import threading

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")
    try:
        import requests
        import openai
        import azure.ai.inference
        import dotenv
        import bs4
        import schedule
        import rich
        import pytz
        print("[OK] All dependencies installed")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("\nPlease run: py -m pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists with API keys"""
    if not os.path.exists('.env'):
        print("[ERROR] .env file not found")
        print("\nPlease create .env file with your Azure OpenAI API key:")
        print("cp .env.example .env")
        print("Then edit .env and add your API key")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('AZURE_OPENAI_API_KEY'):
        print("[ERROR] AZURE_OPENAI_API_KEY not set in .env")
        return False
    
    print("[OK] Environment configured")
    return True

def initialize_data():
    """Run initial data fetch if no data exists"""
    if not os.path.exists('reports/latest.json'):
        print("\nNo data found. Running initial scan...")
        print("This will take a few minutes...")
        
        result = subprocess.run([sys.executable, 'main.py', '--historical', '--days', '1'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Initial data loaded successfully")
            return True
        else:
            print(f"[ERROR] Error loading data: {result.stderr}")
            return False
    else:
        print("[OK] Data already exists")
        return True

def start_dashboard():
    """Start the web dashboard"""
    print("\nStarting dashboard server...")
    
    # Start server in a separate thread
    def run_server():
        subprocess.run([sys.executable, 'main.py', '--dashboard'])
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(2)
    
    # Open browser
    url = 'http://localhost:8080'
    print(f"\n[OK] Dashboard running at {url}")
    print("Opening in browser...")
    webbrowser.open(url)
    
    print("\n" + "="*50)
    print("HN Discoveries Dashboard is running!")
    print("="*50)
    print("\nOptions:")
    print("- View dashboard: http://localhost:8080")
    print("- Refresh data: Click 'Refresh Now' button in dashboard")
    print("- Stop server: Press Ctrl+C")
    print("\nDaily updates: The agent will run automatically at 8 AM IST")
    print("\nTo run daemon mode (for daily updates):")
    print("  py main.py --daemon")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down dashboard...")
        print("Goodbye!")

def main():
    print("HN Discoveries - Local Deployment")
    print("="*50)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check everything is ready
    if not check_dependencies():
        return
    
    if not check_env_file():
        return
    
    if not initialize_data():
        return
    
    # Start dashboard
    start_dashboard()

if __name__ == '__main__':
    main()