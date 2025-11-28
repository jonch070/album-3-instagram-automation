#!/usr/bin/env python3
"""
upload_and_post_story.py - Upload media to GitHub and post to Instagram Story

Usage:
    python upload_and_post_story.py <local_file_path> <MEDIA_TYPE>

Arguments:
    <local_file_path>: Path to the local video or image file
    <MEDIA_TYPE>: Specify 'VIDEO' for video files or 'IMAGE' for image files

Configuration:
    - GITHUB_TOKEN: Your GitHub personal access token (with repo scope)
    - GITHUB_REPO: Your repository in username/repo format
    - INSTAGRAM_ACCESS_TOKEN: Your Instagram Access Token from Meta Graph API
    - INSTAGRAM_ACCOUNT_ID: Your Instagram Business Account ID

Examples:
    python upload_and_post_story.py "./my_video.mp4" "VIDEO"
    python upload_and_post_story.py "./my_photo.png" "IMAGE"
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
import requests
import time

# Load environment variables from .env file
env_file = os.path.join(project_root, ".env")
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Import the github uploader
sys.path.append(script_dir)
from github_uploader import upload_to_github

# --- CONFIGURATION ---
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
    print("❌ Error: INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID must be set in environment variables")
    sys.exit(1)

# --- API Endpoints ---
BASE_URL = f"https://graph.facebook.com/v19.0"
MEDIA_UPLOAD_URL = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media"
MEDIA_PUBLISH_URL = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
STATUS_URL = f"{BASE_URL}/{{container_id}}"

def upload_media(media_url, media_type):
    """
    Step 2: Uploads media to Instagram and returns a container ID.
    """
    print("Step 2: Uploading media to Instagram...")

    # Prepare the request payload
    data = {}

    # Add is_share_to_story parameter
    if media_type == 'IMAGE':
        data['media_type'] = 'STORIES'
        data['image_url'] = media_url
    elif media_type == 'VIDEO':
        data['media_type'] = 'STORIES'
        data['video_url'] = media_url

    try:
        response = requests.post(MEDIA_UPLOAD_URL, params={'access_token': ACCESS_TOKEN}, data=data)

        result = response.json()

        if response.status_code != 200:
            print(f"❌ Instagram API Error ({response.status_code}):")
            print(f"   Response: {result}")
            return None

        if 'id' in result:
            print(f"✅ Media uploaded successfully. Container ID: {result['id']}")
            return result['id']
        else:
            print(f"❌ Error uploading media: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error uploading media: {e}")
        return None

def publish_story(container_id):
    """
    Step 3: Publishes the uploaded media as a Story.
    """
    print("Step 3: Publishing to Story...")

    data = {
        'creation_id': container_id,
    }

    try:
        response = requests.post(MEDIA_PUBLISH_URL, params={'access_token': ACCESS_TOKEN}, data=data)
        response.raise_for_status()

        result = response.json()
        if 'id' in result:
            print(f"✅ Story published successfully! Media ID: {result['id']}")
            return result['id']
        else:
            print(f"❌ Error publishing story: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error publishing story: {e}")
        return None

def check_media_status(container_id, media_type):
    """
    Step 2.5: Check the status of uploaded media before publishing.
    """
    print(f"Step 2.5: Checking media status...")

    try:
        response = requests.get(
            STATUS_URL.format(container_id=container_id),
            params={
                'access_token': ACCESS_TOKEN,
                'fields': 'id,status_code'
            }
        )
        response.raise_for_status()

        result = response.json()
        status_code = result.get('status_code')

        # For Stories with images, status_code might not be returned (immediate processing)
        if status_code is None and media_type == 'IMAGE':
            print("✅ Media is ready for publishing (Stories don't require status check).")
            return True

        if status_code == 'FINISHED':
            print("✅ Media is ready for publishing.")
            return True
        elif status_code == 'IN_PROGRESS':
            print("⏳ Media is still processing. Waiting...")
            time.sleep(5)
            return check_media_status(container_id, media_type)
        elif status_code == 'FAILED':
            print(f"❌ Media processing failed: {result}")
            return False
        else:
            print(f"⚠️ Unknown status: {result}")
            # For Stories, proceed anyway if we have an ID
            if 'id' in result:
                print("✅ Proceeding with publication...")
                return True
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking media status: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python upload_and_post_story.py <local_file_path> <MEDIA_TYPE>")
        print("       MEDIA_TYPE should be 'VIDEO' or 'IMAGE'")
        sys.exit(1)

    local_file_path = sys.argv[1]
    media_type = sys.argv[2].upper()

    if media_type not in ['VIDEO', 'IMAGE']:
        print("❌ Invalid media type. Use 'VIDEO' or 'IMAGE'")
        sys.exit(1)

    if not os.path.exists(local_file_path):
        print(f"❌ File not found: {local_file_path}")
        sys.exit(1)

    print(f"📱 Uploading and posting {media_type} to Instagram Story...")
    print(f"📁 Local file: {local_file_path}")

    # Step 1: Upload to GitHub
    try:
        print("Step 1: Uploading to GitHub...")
        media_url = upload_to_github(local_file_path)
        print(f"✅ File uploaded to GitHub")
        print(f"🔗 Public URL: {media_url}")
    except Exception as e:
        print(f"❌ Failed to upload to GitHub: {e}")
        sys.exit(1)

    # Step 2: Upload media to Instagram
    container_id = upload_media(media_url, media_type)

    if not container_id:
        print("❌ Failed to upload media to Instagram. Aborting.")
        sys.exit(1)

    # Step 2.5: Check media status (important for videos)
    if not check_media_status(container_id, media_type):
        print("❌ Media is not ready for publishing. Aborting.")
        sys.exit(1)

    # Step 3: Publish as Story
    story_id = publish_story(container_id)

    if story_id:
        print(f"🎉 Success! Your Instagram Story has been published.")
        print(f"📱 Story ID: {story_id}")
        print(f"🔗 Media hosted at: {media_url}")
        print("💡 Note: Stories expire after 24 hours.")
        print("💡 You can manually add this Story to Highlights in the Instagram app.")
    else:
        print("❌ Failed to publish Story.")
        sys.exit(1)

if __name__ == "__main__":
    main()
