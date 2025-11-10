"""
Test TikTok User Info API to get real follower/video counts
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

print('Testing User Info API...')
print('=' * 80)

# Get a test user from video search
search_url = f'https://{host}/api/search/video'
search_params = {'keyword': 'samsung tv', 'count': '1'}

response = requests.get(search_url, headers=headers, params=search_params, timeout=10)
if response.status_code == 200:
    data = response.json()
    videos = data.get('item_list', [])
    if videos:
        author = videos[0].get('author', {})
        unique_id = author.get('uniqueId', '')
        user_id = author.get('id', '')

        print(f'Test user:')
        print(f'  uniqueId: {unique_id}')
        print(f'  id: {user_id}')
        print()

        # Test User Info API endpoints
        user_endpoints = [
            '/api/user/info',
            '/api/user/detail',
            '/api/user/profile',
        ]

        for endpoint in user_endpoints:
            print(f'Testing endpoint: {endpoint}')
            url = f'https://{host}{endpoint}'

            # Try with uniqueId
            params = {'uniqueId': unique_id}
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=10)
                print(f'  Status with uniqueId: {resp.status_code}')

                if resp.status_code == 200:
                    user_data = resp.json()
                    print(f'  Response keys: {list(user_data.keys())[:10]}')

                    # Find user info object
                    user_info = user_data.get('userInfo') or user_data.get('user') or user_data.get('data')
                    if user_info and isinstance(user_info, dict):
                        print(f'  User info keys: {list(user_info.keys())[:20]}')
                        print()

                        # Check stats object
                        stats = user_info.get('stats', {})
                        if stats:
                            print('  Stats object keys:')
                            for key, value in stats.items():
                                print(f'    {key}: {value}')
                            print()

                        # Check user object
                        user = user_info.get('user', {})
                        if user:
                            print('  User object keys (first 20):')
                            for i, (key, value) in enumerate(list(user.items())[:20]):
                                if isinstance(value, (str, int, float, bool)):
                                    print(f'    {key}: {value}')
                                else:
                                    print(f'    {key}: <{type(value).__name__}>')
                            print()

                        # Find follower count fields
                        print('  Follower/Subscriber fields:')
                        for key in user_info.keys():
                            if 'follow' in key.lower() or 'fan' in key.lower() or 'subscriber' in key.lower():
                                print(f'    {key}: {user_info[key]}')

                        # Find video count fields
                        print()
                        print('  Video/Post count fields:')
                        for key in user_info.keys():
                            if 'video' in key.lower() or 'aweme' in key.lower() or 'post' in key.lower():
                                print(f'    {key}: {user_info[key]}')

                        print()
                        print(f'  >>> SUCCESS! WORKING ENDPOINT: {endpoint}')
                        break
                elif resp.status_code == 404:
                    print('  [404] Not found')
                else:
                    print(f'  [{resp.status_code}] {resp.text[:100]}')

            except Exception as e:
                print(f'  Error: {e}')

            print()

print('=' * 80)
