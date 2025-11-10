"""
Find which Instagram API is subscribed
"""
import requests
import json

API_KEY = "827897ee92msh433e0607a3391fap1807ccjsna7656712e78a"

# Comprehensive list of Instagram APIs on RapidAPI
apis_to_test = [
    # Scraper APIs
    {
        "name": "Instagram Scraper 2023",
        "url": "https://instagram-scraper-2023.p.rapidapi.com/tag/samsungtv",
        "host": "instagram-scraper-2023.p.rapidapi.com"
    },
    {
        "name": "Instagram Bulk Profile Scraper",
        "url": "https://instagram-bulk-profile-scrapper.p.rapidapi.com/clients/api/ig/ig_profile",
        "host": "instagram-bulk-profile-scrapper.p.rapidapi.com",
        "params": {"ig": "samsungusa"}
    },
    {
        "name": "Instagram Data",
        "url": "https://instagram-data1.p.rapidapi.com/hashtag/samsungtv",
        "host": "instagram-data1.p.rapidapi.com"
    },
    # API v1.2
    {
        "name": "Instagram API v1.2 (instagram28)",
        "url": "https://instagram28.p.rapidapi.com/hashtag_feed",
        "host": "instagram28.p.rapidapi.com",
        "params": {"hashtag": "samsungtv"}
    },
    # Instagram47
    {
        "name": "Instagram47",
        "url": "https://instagram47.p.rapidapi.com/hashtag_feed",
        "host": "instagram47.p.rapidapi.com",
        "params": {"hashtag": "samsungtv"}
    },
    # Instagram Looter
    {
        "name": "Instagram Looter",
        "url": "https://instagram-looter.p.rapidapi.com/hashtag/samsungtv",
        "host": "instagram-looter.p.rapidapi.com"
    },
    # Instagram API
    {
        "name": "Instagram API (APIMATIC)",
        "url": "https://instagram-api-2021.p.rapidapi.com/api/search/hashtag",
        "host": "instagram-api-2021.p.rapidapi.com",
        "params": {"hashtag": "samsungtv"}
    },
    # Instagram Profile Picture
    {
        "name": "Instagram Profile Picture Downloader",
        "url": "https://instagram-profile-picture-downloader.p.rapidapi.com/api/instagram/user/profile/samsungusa",
        "host": "instagram-profile-picture-downloader.p.rapidapi.com"
    },
    # Instagram Hashtags
    {
        "name": "Instagram Hashtags",
        "url": "https://instagram-hashtags.p.rapidapi.com/generate",
        "host": "instagram-hashtags.p.rapidapi.com",
        "params": {"keyword": "samsung"}
    },
    # Fresh Instagram Data
    {
        "name": "Fresh Instagram Data",
        "url": "https://fresh-instagram-data.p.rapidapi.com/hashtag/samsungtv",
        "host": "fresh-instagram-data.p.rapidapi.com"
    }
]

print("="*100)
print("SEARCHING FOR SUBSCRIBED INSTAGRAM API")
print(f"API Key: {API_KEY[:30]}...")
print("="*100)

found_working = False

for idx, api in enumerate(apis_to_test, 1):
    print(f"\n[{idx}/{len(apis_to_test)}] Testing: {api['name']}")
    print(f"    URL: {api['url']}")

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': api['host']
    }

    try:
        response = requests.get(
            api['url'],
            headers=headers,
            params=api.get('params', {}),
            timeout=15
        )

        print(f"    Status: {response.status_code}", end=" - ")

        if response.status_code == 200:
            print("✅ SUCCESS! THIS API IS WORKING!")
            found_working = True
            print(f"    Host: {api['host']}")
            print(f"    Response preview: {response.text[:300]}...")

            # Try to parse JSON
            try:
                data = response.json()
                print(f"    Response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"    Keys: {list(data.keys())}")
            except:
                pass

            print("\n" + "="*100)
            print(f"FOUND WORKING API: {api['name']}")
            print(f"Host to use: {api['host']}")
            print(f"Base URL: https://{api['host']}")
            print("="*100)

        elif response.status_code == 403:
            print("Not subscribed")
        elif response.status_code == 404:
            print("Endpoint not found")
        elif response.status_code == 429:
            print("Rate limit exceeded")
        else:
            print(f"Error: {response.text[:100]}")

    except Exception as e:
        print(f"Exception: {str(e)[:100]}")

if not found_working:
    print("\n" + "="*100)
    print("❌ NO WORKING INSTAGRAM API FOUND")
    print("\nPlease:")
    print("1. Go to https://rapidapi.com/")
    print("2. Search 'Instagram'")
    print("3. Subscribe to one of these recommended APIs:")
    print("   - Instagram Scraper 2023 (recommended)")
    print("   - Instagram47")
    print("   - Fresh Instagram Data")
    print("4. Make sure subscription is active in your RapidAPI dashboard")
    print("="*100)
