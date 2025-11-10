"""
Test new TikTok API endpoints
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
import json
from config.secrets import TIKTOK_API23_KEY

api_key = TIKTOK_API23_KEY
host = "tiktok-api23.p.rapidapi.com"

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host
}

print("="*80)
print("Testing TikTok API - New Endpoints")
print("="*80)

# Test 1: Search Video (instead of Search General)
print("\n[1] Testing Search Video endpoint...")
print("-" * 80)

url = f"https://{host}/api/search/video"
params = {"keyword": "samsung tv", "count": "5"}

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")

        # Try different possible keys
        videos = data.get('item_list') or data.get('data') or []
        print(f"Videos found: {len(videos) if isinstance(videos, list) else 0}")

        if videos and len(videos) > 0:
            print(f"\nFirst video sample:")
            first = videos[0]
            print(f"  Keys: {list(first.keys())[:10]}")
            print(f"  Full structure (first 500 chars): {str(first)[:500]}")

            if 'aweme_id' in first:
                print(f"  Video ID: {first.get('aweme_id')}")
            if 'desc' in first:
                print(f"  Description: {first.get('desc', '')[:80]}")
            if 'author' in first:
                author = first['author']
                print(f"  Author: {author.get('nickname', 'N/A')}")
            if 'statistics' in first:
                stats = first['statistics']
                print(f"  Views: {stats.get('play_count', 0)}")
                print(f"  Likes: {stats.get('digg_count', 0)}")
                print(f"  Comments: {stats.get('comment_count', 0)}")
        else:
            print(f"No videos in response. Full response (first 1000 chars):")
            print(str(data)[:1000])
    else:
        print(f"Error: {response.text[:200]}")

except Exception as e:
    print(f"Exception: {e}")

# Test 2: Get Trending Posts
print("\n\n[2] Testing Get Trending Posts endpoint...")
print("-" * 80)

url = f"https://{host}/api/post/trending"
params = {"count": "5", "region": "US"}

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")

        # Try different possible keys
        videos = data.get('itemList') or data.get('item_list') or data.get('data') or []
        print(f"Trending videos found: {len(videos) if isinstance(videos, list) else 0}")

        if videos and len(videos) > 0:
            print(f"\nFirst trending video:")
            first = videos[0]
            print(f"  Keys: {list(first.keys())[:10]}")
        else:
            print(f"No videos. Full response (first 1000 chars):")
            print(str(data)[:1000])
    else:
        print(f"Error: {response.text[:200]}")

except Exception as e:
    print(f"Exception: {e}")

# Test 3: Get Comments (if we have a video ID)
print("\n\n[3] Testing Get Comments of Post endpoint...")
print("-" * 80)
print("Note: Need a valid post ID to test this")

print("\n" + "="*80)
print("Test Complete")
print("="*80)
