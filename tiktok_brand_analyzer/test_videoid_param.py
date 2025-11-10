"""
Test comments API with correct videoId parameter
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from config.secrets import TIKTOK_API23_KEY

api_key = TIKTOK_API23_KEY
host = 'tiktok-api23.p.rapidapi.com'

headers = {
    'X-RapidAPI-Key': api_key,
    'X-RapidAPI-Host': host
}

# Use videoId parameter!
video_id = '7557264196560276758'
url = f'https://{host}/api/post/comments'
params = {
    'videoId': video_id,  # CORRECT parameter name!
    'count': '10',
    'cursor': '0'
}

print('='*80)
print('Testing TikTok Comments API with videoId parameter')
print('='*80)
print(f'URL: {url}')
print(f'Params: {params}')
print()

response = requests.get(url, headers=headers, params=params, timeout=10)
print(f'Status: {response.status_code}')
print()

if response.status_code == 200:
    data = response.json()
    print(f'[SUCCESS!!!] Response keys: {list(data.keys())}')
    print()

    # Find comments
    for key in ['comments', 'comment_list', 'data', 'commentList', 'items']:
        if key in data:
            comments = data[key]
            if isinstance(comments, list):
                print(f'Found {len(comments)} comments in key: "{key}"')
                if len(comments) > 0:
                    first = comments[0]
                    print(f'First comment keys: {list(first.keys())[:15]}')
                    print(f'First comment text: {first.get("text", first.get("comment_text", "N/A"))[:100]}')
                    print()
                    print('>>> COMMENTS API WORKS!!!')
                break
else:
    print(f'[ERROR] {response.status_code}')
    print(f'Response: {response.text[:300]}')

print()
print('='*80)
