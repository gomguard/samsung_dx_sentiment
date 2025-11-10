"""
Debug TikTok API response structure
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
print("TikTok API Response Structure Debug")
print("="*80)

# Test search endpoint
url = f"https://{host}/api/search/general"
params = {"keyword": "samsung", "count": "5"}

print(f"\nEndpoint: {url}")
print(f"Params: {params}")
print("-"*80)

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        print(f"\nResponse Keys: {list(data.keys())}")
        print(f"\nFull Response (formatted):")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])

        # Check what's in data
        if 'data' in data:
            print(f"\n\nData field type: {type(data['data'])}")
            print(f"Data field length: {len(data['data'])}")

            if isinstance(data['data'], list) and len(data['data']) > 0:
                print(f"\nFirst item in data:")
                first_item = data['data'][0]
                print(f"  Type: {type(first_item)}")
                if isinstance(first_item, dict):
                    print(f"  Keys: {list(first_item.keys())}")
                    print(f"  'type' field: {first_item.get('type')}")

                    # Check if it has video data
                    if 'aweme_list' in first_item:
                        print(f"  aweme_list length: {len(first_item.get('aweme_list', []))}")
                    if 'user_list' in first_item:
                        print(f"  user_list length: {len(first_item.get('user_list', []))}")
                    if 'video_list' in first_item:
                        print(f"  video_list length: {len(first_item.get('video_list', []))}")

    else:
        print(f"\nError: {response.text[:500]}")

except Exception as e:
    print(f"\nException: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
