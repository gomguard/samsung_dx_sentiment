"""
Test Instagram Premium API 2023
"""
import requests
import json

API_KEY = "827897ee92msh433e0607a3391fap1807ccjsna7656712e78a"
BASE_URL = "https://instagram-premium-api-2023.p.rapidapi.com"
HOST = "instagram-premium-api-2023.p.rapidapi.com"

# Test different endpoints
endpoints = [
    {
        "name": "Hashtag Feed",
        "url": f"{BASE_URL}/tag/samsungtv",
        "method": "GET"
    },
    {
        "name": "Hashtag Info",
        "url": f"{BASE_URL}/hashtag",
        "params": {"tag": "samsungtv"}
    },
    {
        "name": "Search Hashtag",
        "url": f"{BASE_URL}/search",
        "params": {"query": "samsungtv", "type": "hashtag"}
    },
    {
        "name": "Tag Posts",
        "url": f"{BASE_URL}/tag/posts/samsungtv",
        "method": "GET"
    }
]

headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': HOST
}

print("="*80)
print("Testing Instagram Premium API 2023")
print(f"Base URL: {BASE_URL}")
print(f"API Key: {API_KEY[:30]}...")
print("="*80)

working_endpoint = None

for endpoint in endpoints:
    print(f"\n[Testing: {endpoint['name']}]")
    print(f"URL: {endpoint['url']}")

    try:
        params = endpoint.get('params', {})
        response = requests.get(endpoint['url'], headers=headers, params=params, timeout=15)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("SUCCESS!")
            working_endpoint = endpoint

            try:
                data = response.json()
                print(f"Response type: {type(data)}")

                if isinstance(data, dict):
                    print(f"Top-level keys: {list(data.keys())}")

                    # Check for common data structures
                    if 'data' in data:
                        print(f"data type: {type(data['data'])}")
                        if isinstance(data['data'], dict):
                            print(f"data keys: {list(data['data'].keys())[:10]}")
                        elif isinstance(data['data'], list) and len(data['data']) > 0:
                            print(f"data[0] keys: {list(data['data'][0].keys())[:10]}")

                    if 'items' in data:
                        print(f"items count: {len(data['items']) if isinstance(data['items'], list) else 'not a list'}")
                        if isinstance(data['items'], list) and len(data['items']) > 0:
                            print(f"items[0] keys: {list(data['items'][0].keys())[:15]}")

                    if 'sections' in data:
                        print(f"sections count: {len(data['sections']) if isinstance(data['sections'], list) else 'not a list'}")

                print(f"\nResponse preview:\n{json.dumps(data, indent=2)[:1500]}...")

            except Exception as e:
                print(f"JSON parse error: {e}")
                print(f"Response text: {response.text[:500]}")

        elif response.status_code == 403:
            print("Not subscribed or invalid API key")
        elif response.status_code == 404:
            print("Endpoint not found")
        elif response.status_code == 429:
            print("Rate limit exceeded")
        else:
            print(f"Error: {response.text[:300]}")

    except Exception as e:
        print(f"Exception: {str(e)[:200]}")

if working_endpoint:
    print("\n" + "="*80)
    print("FOUND WORKING ENDPOINT!")
    print(f"Name: {working_endpoint['name']}")
    print(f"URL Pattern: {working_endpoint['url']}")
    print("="*80)
else:
    print("\n" + "="*80)
    print("No working endpoint found")
    print("Please check:")
    print("1. API subscription is active")
    print("2. API key is correct")
    print("3. Check API documentation for correct endpoints")
    print("="*80)
