"""
post_story.py - A script to publish Instagram Stories via Meta Graph API.

Usage:
    python post_story.py <public_media_url> <MEDIA_TYPE>

Arguments:
    <public_media_url>: The direct, publicly accessible URL of your video or image file.
                        - For Dropbox links, ensure you change '?dl=0' to '?dl=1' for a direct link.
                        - Example: 'https://www.dropbox.com/s/your-file-id/my_video.mp4?dl=1'
    <MEDIA_TYPE>:       Specify 'VIDEO' for video files or 'IMAGE' for image files.

Configuration:
    - INSTAGRAM_ACCESS_TOKEN: Your Instagram Access Token from Meta Graph API
    - INSTAGRAM_ACCOUNT_ID: Your Instagram Business Account ID

Examples:
    # To post a video story:
    python post_story.py "https://www.example.com/my_awesome_video.mp4" "VIDEO"

    # To post an image story (using a Dropbox direct link):
    python post_story.py "https://www.dropbox.com/s/your-image-id/my_photo.png?dl=1" "IMAGE"

Important Notes:
    - The media file MUST be hosted on a publicly accessible server.
    - For Instagram Stories, direct upload from your local machine is NOT supported by the API.
    - Ensure your Instagram account is a Business or Creator account linked to a Facebook Page.
    - The script requires the 'requests' library: pip install requests
"""

import requests
import time
import sys
import os

# --- CONFIGURATION ---
# Read from environment variables
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
    print("❌ Error: INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID must be set in environment variables")
    print("   Create a .env file in the project root with these values")
    sys.exit(1)

# The public URL of the video or image you want to post will be provided as a command-line argument.
# The media type (VIDEO or IMAGE) will also be provided as a command-line argument.

# --- API Endpoints ---
BASE_URL = f"https://graph.facebook.com/v19.0"
MEDIA_UPLOAD_URL = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media"
MEDIA_PUBLISH_URL = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
STATUS_URL = f"{BASE_URL}/{{container_id}}"

def upload_media(media_url, media_type):
    """
    Step 1: Uploads media to Instagram and returns a container ID.
    """
    print("Step 1: Uploading media...")
    
    # Prepare the request payload
    data = {
        'media_type': media_type,
        'media_url': media_url,
    }
    
    # Add is_share_to_story parameter
    if media_type == 'IMAGE':
        data['is_share_to_story'] = True
    elif media_type == 'VIDEO':
        data['video_url'] = media_url
        data['media_type'] = 'REELS'
        data['is_share_to_story'] = True
    
    try:
        response = requests.post(MEDIA_UPLOAD_URL, params={'access_token': ACCESS_TOKEN}, data=data)
        response.raise_for_status()
        
        result = response.json()
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
    Step 2: Publishes the uploaded media as a Story.
    """
    print("Step 2: Publishing to Story...")
    
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

def check_media_status(container_id):
    """
    Optional: Check the status of uploaded media before publishing.
    """
    print(f"Step 1.5: Checking media status...")
    
    try:
        response = requests.get(STATUS_URL.format(container_id=container_id), params={'access_token': ACCESS_TOKEN})
        response.raise_for_status()
        
        result = response.json()
        status_code = result.get('status_code')
        
        if status_code == 'FINISHED':
            print("✅ Media is ready for publishing.")
            return True
        elif status_code == 'IN_PROGRESS':
            print("⏳ Media is still processing. Waiting...")
            time.sleep(5)
            return check_media_status(container_id)
        elif status_code == 'FAILED':
            print(f"❌ Media processing failed: {result}")
            return False
        else:
            print(f"⚠️ Unknown status: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking media status: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python post_story.py <public_media_url> <MEDIA_TYPE>")
        print("       MEDIA_TYPE should be 'VIDEO' or 'IMAGE'")
        sys.exit(1)
    
    media_url = sys.argv[1]
    media_type = sys.argv[2].upper()
    
    if media_type not in ['VIDEO', 'IMAGE']:
        print("❌ Invalid media type. Use 'VIDEO' or 'IMAGE'")
        sys.exit(1)
    
    print(f"📱 Posting {media_type} to Instagram Story...")
    print(f"🔗 Media URL: {media_url}")
    
    # Step 1: Upload media
    container_id = upload_media(media_url, media_type)
    
    if not container_id:
        print("❌ Failed to upload media. Aborting.")
        sys.exit(1)
    
    # Step 1.5: Check media status (important for videos)
    if not check_media_status(container_id):
        print("❌ Media is not ready for publishing. Aborting.")
        sys.exit(1)
    
    # Step 2: Publish as Story
    story_id = publish_story(container_id)
    
    if story_id:
        print(f"🎉 Success! Your Instagram Story has been published.")
        print(f"📱 Story ID: {story_id}")
        print("💡 Note: Stories expire after 24 hours.")
        print("💡 You can manually add this Story to Highlights in the Instagram app.")
    else:
        print("❌ Failed to publish Story.")
        sys.exit(1)

if __name__ == "__main__":
    main()