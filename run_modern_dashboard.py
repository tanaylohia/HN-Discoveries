#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import time
import webbrowser

def check_npm():
    """Check if npm is installed"""
    # Try different ways to find npm on Windows
    npm_commands = ['npm', 'npm.cmd', 'C:\\Program Files\\nodejs\\npm.cmd']
    
    for npm_cmd in npm_commands:
        try:
            result = subprocess.run([npm_cmd, '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print(f"[OK] npm version {result.stdout.strip()} found")
                return True
        except:
            continue
    
    print("[ERROR] npm not found. Please install Node.js from https://nodejs.org/")
    return False

def setup_dashboard():
    """Install dependencies for the modern dashboard"""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'modern-dashboard')
    
    if not os.path.exists(dashboard_dir):
        print(f"[ERROR] Dashboard directory not found: {dashboard_dir}")
        return False
    
    os.chdir(dashboard_dir)
    
    # Check if node_modules exists
    if not os.path.exists('node_modules'):
        print("\n[INFO] Installing dependencies...")
        print("This may take a minute on first run...\n")
        
        result = subprocess.run(['npm', 'install'], capture_output=False, shell=True)
        if result.returncode != 0:
            print("[ERROR] Failed to install dependencies")
            return False
        
        print("\n[OK] Dependencies installed successfully")
    else:
        print("[OK] Dependencies already installed")
    
    return True

def copy_latest_data():
    """Copy latest.json to dashboard directory for development"""
    src = os.path.join(os.path.dirname(__file__), 'reports', 'latest.json')
    dst = os.path.join(os.path.dirname(__file__), 'modern-dashboard', 'reports')
    
    if os.path.exists(src):
        os.makedirs(dst, exist_ok=True)
        dst_file = os.path.join(dst, 'latest.json')
        shutil.copy2(src, dst_file)
        print(f"[OK] Copied latest data to dashboard")
        return True
    else:
        print("[WARNING] No data found. Run 'py main.py --run-once' to generate data first.")
        return False

def start_dev_server():
    """Start the Vite development server"""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'modern-dashboard')
    os.chdir(dashboard_dir)
    
    print("\n" + "="*50)
    print("Starting Modern HN Discoveries Dashboard")
    print("="*50)
    print("\nThe dashboard will open in your browser automatically.")
    print("If not, navigate to: http://localhost:3000")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the dev server
    try:
        subprocess.run(['npm', 'run', 'dev'], shell=True)
    except KeyboardInterrupt:
        print("\n\n[INFO] Dashboard stopped.")

def main():
    print("HN Discoveries - Modern Dashboard Setup")
    print("="*50)
    
    # Check prerequisites
    if not check_npm():
        return
    
    # Setup dashboard
    if not setup_dashboard():
        return
    
    # Copy data
    copy_latest_data()
    
    # Start server
    start_dev_server()

if __name__ == '__main__':
    main()