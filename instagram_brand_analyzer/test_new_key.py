"""
Test new RapidAPI key for Instagram
"""
import requests
import json

NEW_KEY = "827897ee92msh433e0607a3391fap1807ccjsna7656712e78a"

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
        "url": "https://instagram-bulk-profile-scrapper.p.rapidapi.com/clients/api/ig/ig_profile",
        "params": {"ig": "samsungusa"}
    },
    {
        "name": "instagram47",
        "host": "instagram47.p.rapidapi.com",
        "url": "https://instagram47.p.rapidapi.com/hashtag_feed",
        "params": {"hashtag": "samsungtv"}
    },
    {
        "name": "instagram-data1",
        "host": "instagram-data1.p.rapidapi.com",
        "url": "https://instagram-data1.p.rapidapi.com/hashtag/samsungtv"
    }
]

print("="*80)
print("Testing Instagram RapidAPI with New Key")
print(f"Key: {NEW_KEY[:20]}...")
print("="*80)

for endpoint in endpoints:
    print(f"\n[{endpoint['name']}]")
    print(f"URL: {endpoint['url']}")

    headers = {
        'x-rapidapi-key': NEW_KEY,
        'x-rapidapi-host': endpoint['host']
    }

    try:
        params = endpoint.get('params', {})
        response = requests.get(endpoint['url'], headers=headers, params=params, timeout=10)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS!")
            try:
                data = response.json()
                print(f"Response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())[:10]}")
                print(f"Response preview:\n{json.dumps(data, indent=2)[:1000]}...")
            except:
                print(f"Response text: {response.text[:500]}...")
        else:
            print(f"❌ Error: {response.text[:500]}")

    except Exception as e:
        print(f"Exception: {e}")

print("\n" + "="*80)
