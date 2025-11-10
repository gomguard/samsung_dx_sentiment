"""
Check RapidAPI subscription status
"""
import requests

API_KEY = "827897ee92msh433e0607a3391fap1807ccjsna7656712e78a"

# Test simple request to check which APIs are accessible
test_apis = [
    {
        "name": "Instagram Scraper 2023",
        "url": "https://instagram-scraper-2023.p.rapidapi.com/tag/test",
        "host": "instagram-scraper-2023.p.rapidapi.com"
    },
    {
        "name": "Instagram Bulk Scraper",
        "url": "https://instagram-bulk-profile-scrapper.p.rapidapi.com/clients/api/ig/ig_profile",
        "host": "instagram-bulk-profile-scrapper.p.rapidapi.com",
        "params": {"ig": "test"}
    },
    {
        "name": "Instagram Data",
        "url": "https://instagram-data1.p.rapidapi.com/hashtag/test",
        "host": "instagram-data1.p.rapidapi.com"
    },
    {
        "name": "Instagram API v1.2",
        "url": "https://instagram28.p.rapidapi.com/user_info",
        "host": "instagram28.p.rapidapi.com",
        "params": {"user_id": "25025320"}
    }
]

print("="*80)
print("Checking RapidAPI Subscription Status")
print(f"API Key: {API_KEY[:20]}...")
print("="*80)

for api in test_apis:
    print(f"\n[Testing: {api['name']}]")
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': api['host']
    }

    try:
        response = requests.get(
            api['url'],
            headers=headers,
            params=api.get('params', {}),
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("SUCCESS! This API is subscribed and working!")
            print(f"Response: {response.text[:200]}")
        elif response.status_code == 403:
            error_msg = response.json() if response.text else {}
            print(f"NOT SUBSCRIBED - {error_msg.get('message', 'Unknown error')}")
        elif response.status_code == 404:
            print("ENDPOINT NOT FOUND")
        else:
            print(f"Error: {response.text[:200]}")

    except Exception as e:
        print(f"Exception: {str(e)[:200]}")

print("\n" + "="*80)
print("\nTo subscribe to an Instagram API:")
print("1. Go to https://rapidapi.com/")
print("2. Search for 'Instagram'")
print("3. Choose an API (e.g., 'Instagram Scraper 2023')")
print("4. Click 'Subscribe to Test'")
print("5. Select a plan (Free or Paid)")
print("="*80)
