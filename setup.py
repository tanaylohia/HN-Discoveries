#!/usr/bin/env python3

import os
import sys
import subprocess

print("HN Discoveries - Setup Script")
print("="*50)

# Install dependencies
print("\n1. Installing dependencies...")
result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                       capture_output=True, text=True)

if result.returncode != 0:
    print(f"Error installing dependencies: {result.stderr}")
    sys.exit(1)
else:
    print("[OK] Dependencies installed")

# Check for .env file
print("\n2. Checking configuration...")
if not os.path.exists('.env'):
    print("Creating .env file from template...")
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as src:
            with open('.env', 'w') as dst:
                dst.write(src.read())
        print("[OK] Created .env file")
        print("\n[WARNING]  IMPORTANT: Edit .env and add your Azure OpenAI API key!")
        print("   Open .env in a text editor and replace 'your-api-key-here' with your actual key")
    else:
        print("[ERROR] .env.example not found!")
else:
    print("[OK] .env file exists")

# Create directories
print("\n3. Creating directories...")
os.makedirs('reports', exist_ok=True)
os.makedirs('dashboard', exist_ok=True)
print("[OK] Directories created")

print("\n" + "="*50)
print("Setup complete!")
print("\nNext steps:")
print("1. Edit .env file and add your Azure OpenAI API key")
print("2. Run: py deploy_local.py")
print("   Or double-click: start_dashboard.bat")
print("\nFor help, see README.md")