"""
Test TikTok API23 comment endpoints
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from config.secrets import TIKTOK_API23_KEY

api_key = TIKTOK_API23_KEY
host = "tiktok-api23.p.rapidapi.com"
base_url = f"https://{host}"

print("="*80)
print("TikTok API23 - Testing Comment Endpoints")
print("="*80)

# First, get a real video ID from search
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host
}

print("\n[1] Getting a sample video ID from search...")
search_response = requests.get(
    f"{base_url}/api/search/general",
    headers=headers,
    params={"keyword": "samsung tv", "count": "5"},
    timeout=10
)

video_id = None
if search_response.status_code == 200:
    data = search_response.json()
    print(f"Search response keys: {data.keys()}")

    # Extract first video ID
    if 'data' in data:
        for item in data['data']:
            if item.get('type') == 1 and 'aweme_list' in item:
                aweme_list = item['aweme_list']
                if aweme_list and len(aweme_list) > 0:
                    video = aweme_list[0]
                    video_id = video.get('id') or video.get('aweme_id')
                    video_desc = video.get('desc', '')[:50]
                    print(f"Found video ID: {video_id}")
                    print(f"Description: {video_desc}")
                    break

if not video_id:
    print("Could not find video ID from search")
    video_id = "7300000000000000000"  # Use a placeholder
    print(f"Using placeholder: {video_id}")

# Test possible comment endpoints
print(f"\n[2] Testing comment endpoints with video ID: {video_id}")
print("-" * 80)

comment_endpoints = [
    # Format: (endpoint, params)
    (f"{base_url}/api/comment/list", {"aweme_id": video_id, "count": "10"}),
    (f"{base_url}/api/video/comments", {"video_id": video_id, "count": "10"}),
    (f"{base_url}/api/video/comments", {"aweme_id": video_id, "count": "10"}),
    (f"{base_url}/api/comments", {"id": video_id, "count": "10"}),
    (f"{base_url}/comment/list", {"aweme_id": video_id, "count": "10"}),
]

for endpoint, params in comment_endpoints:
    print(f"\nTesting: {endpoint}")
    print(f"Params: {params}")

    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            print(f"  [OK] Status: 200")
            try:
                data = response.json()
                print(f"  Response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())}")
                    if 'comments' in data:
                        print(f"  Comments count: {len(data.get('comments', []))}")
                    elif 'data' in data:
                        print(f"  Data type: {type(data['data'])}")
                print(f"  First 300 chars: {str(data)[:300]}")
            except:
                print(f"  Response (text): {response.text[:200]}")
        else:
            print(f"  [{response.status_code}] {response.text[:150]}")

    except Exception as e:
        print(f"  [FAIL] {str(e)[:100]}")

print("\n" + "="*80)
print("Test Complete")
print("="*80)
