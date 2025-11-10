"""
Test TikTok Comments API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from config.secrets import TIKTOK_API23_KEY

api_key = TIKTOK_API23_KEY
host = "tiktok-api23.p.rapidapi.com"

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host
}

print("="*80)
print("Testing TikTok Comments API")
print("="*80)

# Use the video ID we found from search
video_id = "7557264196560276758"

print(f"\nTesting Get Comments of Post...")
print(f"Video ID: {video_id}")
print("-" * 80)

# Try different possible endpoints
endpoints = [
    "/api/post/comment/list",
    "/api/comment",
    "/post/comment/list",
    "/comment/list",
]

for endpoint in endpoints:
    print(f"\nTrying endpoint: {endpoint}")
    url = f"https://{host}{endpoint}"
    params = {"aweme_id": video_id, "count": "10", "cursor": "0"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Response keys: {list(data.keys())}")

            # Try to find comments
            comments = data.get('comments') or data.get('comment_list') or []
            print(f"  Comments found: {len(comments) if isinstance(comments, list) else 0}")

            if comments and len(comments) > 0:
                print(f"\n  First comment sample:")
                first = comments[0]
                print(f"    Keys: {list(first.keys())[:15]}")
                print(f"    Comment ID: {first.get('cid', 'N/A')}")
                print(f"    Text: {first.get('text', 'N/A')[:100]}")
                print(f"    User: {first.get('user', {}).get('nickname', 'N/A')}")
                print(f"    Likes: {first.get('digg_count', 0)}")

                print(f"\n  >>> SUCCESS! Working endpoint: {endpoint}")
                break
            else:
                print(f"    No comments in response (first 500 chars): {str(data)[:500]}")

        elif response.status_code == 404:
            print(f"  [404] Endpoint does not exist")
        else:
            print(f"  [ERROR] {response.status_code}: {response.text[:200]}")

    except Exception as e:
        print(f"  [EXCEPTION] {e}")

print("\n" + "="*80)
