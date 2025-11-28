#!/usr/bin/env python3
"""
exchange_token.py - Exchange a short-lived Instagram token for a long-lived one

Usage:
    python3 exchange_token.py

This script will:
1. Take your short-lived token (from Graph API Explorer)
2. Exchange it for a 60-day token
3. Show you the new token to put in your .env file

Requirements:
    - Your Facebook App ID
    - Your Facebook App Secret
    - A short-lived token from Graph API Explorer
"""

import requests
import sys

def exchange_token(short_lived_token, app_id, app_secret):
    """Exchange short-lived token for long-lived token"""

    url = "https://graph.facebook.com/v19.0/oauth/access_token"

    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_lived_token
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        result = response.json()

        if 'access_token' in result:
            print("\n✅ Successfully exchanged token!")
            print(f"\n📋 Long-lived token (valid for ~60 days):")
            print(f"{result['access_token']}\n")

            if 'expires_in' in result:
                days = result['expires_in'] / 86400
                print(f"⏰ Expires in: {days:.0f} days\n")

            print("💡 Add this to your .env file as INSTAGRAM_ACCESS_TOKEN")
            return result['access_token']
        else:
            print(f"❌ Error: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None

def main():
    print("\n🔄 Instagram Token Exchange Tool\n")
    print("This will exchange a short-lived token (1 hour) for a long-lived token (60 days)\n")

    # Get user inputs
    print("You'll need:")
    print("1. Your Facebook App ID (from https://developers.facebook.com/apps/)")
    print("2. Your Facebook App Secret (from the same page)")
    print("3. A short-lived token (from Graph API Explorer)\n")

    app_id = input("Enter your Facebook App ID: ").strip()
    app_secret = input("Enter your Facebook App Secret: ").strip()
    short_lived_token = input("Enter your short-lived token: ").strip()

    if not app_id or not app_secret or not short_lived_token:
        print("\n❌ All fields are required!")
        sys.exit(1)

    print("\n🔄 Exchanging token...")
    long_lived_token = exchange_token(short_lived_token, app_id, app_secret)

    if not long_lived_token:
        print("\n❌ Token exchange failed. Please check your credentials.")
        sys.exit(1)

if __name__ == "__main__":
    main()
