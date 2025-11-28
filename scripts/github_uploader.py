#!/usr/bin/env python3
"""
github_uploader.py - Upload files to GitHub repository and return raw URLs

Usage:
    python github_uploader.py <local_file_path>

Configuration:
    - GITHUB_TOKEN: Your GitHub personal access token (read from environment)
    - GITHUB_REPO: Your username/repository format
    - GITHUB_BRANCH: Branch to upload to (default: main)
"""

import sys
import os

# Auto-activate virtual environment if it exists
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
venv_python = os.path.join(project_root, "venv", "bin", "python3")

if os.path.exists(venv_python) and sys.executable != venv_python:
    os.execv(venv_python, [venv_python] + sys.argv)

# Now import the rest after venv is activated
import subprocess
import requests
from pathlib import Path
import base64
import json

# Load environment variables from .env file
env_file = os.path.join(project_root, ".env")
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# --- CONFIGURATION ---
# Your GitHub personal access token (needs repo scope)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "master")  # Default to master

if not GITHUB_TOKEN or not GITHUB_REPO:
    print("❌ Error: GITHUB_TOKEN and GITHUB_REPO must be set in .env file", file=sys.stderr)
    sys.exit(1)

def upload_to_github(local_file_path):
    """Upload a file to GitHub and return raw URL"""
    
    # Validate input file
    if not os.path.exists(local_file_path):
        print(f"Error: File not found at '{local_file_path}'", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isfile(local_file_path):
        print(f"Error: '{local_file_path}' is not a file", file=sys.stderr)
        sys.exit(1)
    
    # Check file size (GitHub limit is 100MB per file)
    file_size = os.path.getsize(local_file_path)
    if file_size > 100 * 1024 * 1024:  # 100MB
        print(f"Error: File size ({file_size/1024/1024:.1f}MB) exceeds GitHub's 100MB limit", file=sys.stderr)
        sys.exit(1)
    
    # Get file info
    file_name = os.path.basename(local_file_path)
    file_path_in_repo = f"media/{file_name}"  # Organize in media folder
    
    print(f"-> Uploading '{file_name}' ({file_size/1024/1024:.1f}MB) to GitHub...", file=sys.stderr)
    
    try:
        # Read file content
        with open(local_file_path, 'rb') as f:
            file_content = f.read()
        
        # Encode file content for GitHub API
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        # GitHub API URL
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path_in_repo}"
        
        # Headers
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        # Request body
        data = {
            "message": f"Upload {file_name} via Album 3 Instagram automation",
            "content": encoded_content,
            "branch": GITHUB_BRANCH
        }
        
        # Check if file already exists
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            # File exists, update it
            existing_file = response.json()
            data["sha"] = existing_file["sha"]
            data["message"] = f"Update {file_name} via Album 3 Instagram automation"
        
        # Upload/create file
        response = requests.put(api_url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            raw_url = result["content"]["download_url"]
            print(f"-> File uploaded successfully.", file=sys.stderr)
            return raw_url
        else:
            print(f"Error uploading to GitHub: {response.status_code} - {response.text}", file=sys.stderr)
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"Error: GitHub API request failed. Check your token and repo details.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python github_uploader.py <local_file_path>", file=sys.stderr)
        sys.exit(1)
    
    local_file_path = sys.argv[1]
    
    # Upload and get the raw URL
    raw_url = upload_to_github(local_file_path)
    
    # Print only the URL to stdout (for piping)
    print(raw_url)

if __name__ == "__main__":
    main()