"""
Check author field structure in API response
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

# Search for videos
url = f'https://{host}/api/search/video'
params = {'keyword': 'samsung tv', 'count': '1'}

print("="*80)
print("Checking Author Field Structure")
print("="*80)

response = requests.get(url, headers=headers, params=params, timeout=10)
if response.status_code == 200:
    data = response.json()
    videos = data.get('item_list', [])

    if videos:
        video = videos[0]
        author = video.get('author', {})

        print('\n=== Author Field Keys ===')
        for i, key in enumerate(list(author.keys())[:30], 1):
            value = author[key]
            # Only print first 100 chars of value
            if isinstance(value, (str, int, float, bool)):
                print(f'{i}. {key}: {str(value)[:100]}')
            else:
                print(f'{i}. {key}: <{type(value).__name__}>')

        print()
        print('=== Follower/Subscriber Count ===')
        for key in author.keys():
            if 'follow' in key.lower() or 'fan' in key.lower() or 'subscriber' in key.lower():
                print(f'  {key}: {author[key]}')

        print()
        print('=== Video/Aweme Count ===')
        for key in author.keys():
            if 'aweme' in key.lower() or 'video' in key.lower() or 'post' in key.lower():
                print(f'  {key}: {author[key]}')

print()
print("="*80)
