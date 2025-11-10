"""
Test all possible comment endpoint paths
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

# Use the video ID we found from search
video_id = "7557264196560276758"

print("="*80)
print("Testing ALL possible comment endpoint paths")
print(f"Video ID: {video_id}")
print("="*80)

# Try ALL possible endpoint paths and parameter combinations
test_cases = [
    # /api/post/comments with different param combinations
    ("/api/post/comments", {"aweme_id": video_id, "count": "10", "cursor": "0"}),
    ("/api/post/comments", {"awemeId": video_id, "count": "10"}),
    ("/api/post/comments", {"id": video_id, "count": "10", "cursor": "0"}),
    ("/api/post/comments", {"video_id": video_id, "count": "10"}),
    ("/api/post/comments", {"postId": video_id, "count": "10"}),
    ("/api/post/comments", {"post_id": video_id, "count": "10", "cursor": "0"}),

    # Without count parameter
    ("/api/post/comments", {"aweme_id": video_id}),
    ("/api/post/comments", {"id": video_id}),
    ("/api/post/comments", {"aweme_id": video_id, "cursor": "0"}),
]

for endpoint, params in test_cases:
    print(f"\n[TEST] {endpoint}")
    print(f"  Params: {params}")

    url = f"https://{host}{endpoint}"

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"  [SUCCESS!!!] Status: 200")
            print(f"  Response keys: {list(data.keys())}")

            # Try to find comments
            for key in ['comments', 'comment_list', 'data', 'items']:
                if key in data:
                    items = data[key]
                    if isinstance(items, list) and len(items) > 0:
                        print(f"  Found {len(items)} comments in '{key}'!")
                        print(f"  First comment keys: {list(items[0].keys())[:10]}")
                        print(f"\n  >>> WORKING ENDPOINT: {endpoint}")
                        print(f"  >>> WORKING PARAMS: {params}")
                        break

        elif response.status_code == 404:
            print(f"  [404] Not found")
        elif response.status_code == 400:
            print(f"  [400] Bad request: {response.text[:100]}")
        else:
            print(f"  [{response.status_code}] {response.text[:100]}")

    except Exception as e:
        print(f"  [ERROR] {str(e)[:80]}")

print("\n" + "="*80)
print("Test Complete")
print("="*80)
