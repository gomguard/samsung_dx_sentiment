"""
Test RapidAPI Instagram endpoint
"""
import requests
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import RapidAPI key
try:
    import importlib.util
    parent_config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    secrets_path = os.path.join(parent_config_dir, 'secrets.py')

    spec = importlib.util.spec_from_file_location("parent_secrets", secrets_path)
    parent_secrets = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent_secrets)
    RAPIDAPI_KEY = parent_secrets.TIKTOK_RAPIDAPI_KEY
    print(f"API Key loaded: {RAPIDAPI_KEY[:20]}...")
except Exception as e:
    print(f"Error loading API key: {e}")
    sys.exit(1)

# Test different Instagram RapidAPI endpoints
endpoints = [
    {
        "name": "instagram-scraper-2023",
        "host": "instagram-scraper-2023.p.rapidapi.com",
        "url": "https://instagram-scraper-2023.p.rapidapi.com/tag/samsungtv"
    },
    {
        "name": "instagram-bulk-scraper",
        "host": "instagram-bulk-profile-scrapper.p.rapidapi.com",
        "url": "https://instagram-bulk-profile-scrapper.p.rapidapi.com/clients/api/ig/ig_profile"
    },
    {
        "name": "instagram47",
        "host": "instagram47.p.rapidapi.com",
        "url": "https://instagram47.p.rapidapi.com/hashtag_feed",
        "params": {"hashtag": "samsungtv"}
    }
]

print("="*80)
print("Testing Instagram RapidAPI Endpoints")
print("="*80)

for endpoint in endpoints:
    print(f"\n[{endpoint['name']}]")
    print(f"URL: {endpoint['url']}")

    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': endpoint['host']
    }

    try:
        params = endpoint.get('params', {})
        response = requests.get(endpoint['url'], headers=headers, params=params, timeout=10)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("SUCCESS!")
            try:
                data = response.json()
                print(f"Response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())[:10]}")
                print(f"Response preview: {str(data)[:500]}...")
            except:
                print(f"Response text: {response.text[:500]}...")
        else:
            print(f"Error: {response.text[:500]}")

    except Exception as e:
        print(f"Exception: {e}")

print("\n" + "="*80)
