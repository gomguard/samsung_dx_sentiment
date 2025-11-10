"""
Test HikerAPI/Instagram Premium API endpoints
"""
import requests
import json

API_KEY = "827897ee92msh433e0607a3391fap1807ccjsna7656712e78a"
BASE_URL = "https://instagram-premium-api-2023.p.rapidapi.com"
HOST = "instagram-premium-api-2023.p.rapidapi.com"

# Based on HikerAPI documentation
endpoints = [
    # V1 endpoints
    {
        "name": "hashtag_medias_recent_v1",
        "url": f"{BASE_URL}/v1/hashtag/medias/recent",
        "params": {"name": "samsungtv", "amount": 10}
    },
    {
        "name": "hashtag_medias_top_v1",
        "url": f"{BASE_URL}/v1/hashtag/medias/top",
        "params": {"name": "samsungtv", "amount": 10}
    },
    {
        "name": "hashtag_by_name_v1",
        "url": f"{BASE_URL}/v1/hashtag/by/name",
        "params": {"name": "samsungtv"}
    },
    {
        "name": "search_hashtags_v1",
        "url": f"{BASE_URL}/v1/search/hashtags",
        "params": {"query": "samsungtv"}
    },
    # V2 endpoints
    {
        "name": "hashtag_medias_recent_v2",
        "url": f"{BASE_URL}/v2/hashtag/medias/recent",
        "params": {"name": "samsungtv"}
    },
    {
        "name": "hashtag_medias_top_v2",
        "url": f"{BASE_URL}/v2/hashtag/medias/top",
        "params": {"name": "samsungtv"}
    },
    # Alternative URL patterns
    {
        "name": "hashtag_recent_alt",
        "url": f"{BASE_URL}/hashtag/samsungtv/recent",
    },
    {
        "name": "hashtag_top_alt",
        "url": f"{BASE_URL}/hashtag/samsungtv/top",
    }
]

headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': HOST
}

print("="*80)
print("Testing Instagram Premium API 2023 (HikerAPI-based) Endpoints")
print(f"Base URL: {BASE_URL}")
print("="*80)

working_endpoints = []

for endpoint in endpoints:
    print(f"\n[Testing: {endpoint['name']}]")
    print(f"URL: {endpoint['url']}")

    try:
        params = endpoint.get('params', {})
        response = requests.get(endpoint['url'], headers=headers, params=params, timeout=15)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("SUCCESS!")
            working_endpoints.append(endpoint)

            try:
                data = response.json()
                print(f"Response type: {type(data)}")

                # Analyze structure
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())[:10]}")

                    if 'items' in data and isinstance(data['items'], list):
                        print(f"Items count: {len(data['items'])}")
                        if len(data['items']) > 0:
                            print(f"First item keys: {list(data['items'][0].keys())[:15]}")

                    if 'data' in data:
                        print(f"Data type: {type(data['data'])}")
                        if isinstance(data['data'], list) and len(data['data']) > 0:
                            print(f"First data item keys: {list(data['data'][0].keys())[:15]}")

                print(f"\nResponse preview:\n{json.dumps(data, indent=2)[:1000]}...")

            except Exception as e:
                print(f"JSON parse error: {e}")
                print(f"Response text: {response.text[:500]}")

        elif response.status_code == 403:
            print("403 - Not subscribed or invalid API key")
        elif response.status_code == 404:
            print("404 - Endpoint not found")
        elif response.status_code == 429:
            print("429 - Rate limit exceeded")
        else:
            print(f"Error {response.status_code}: {response.text[:200]}")

    except Exception as e:
        print(f"Exception: {str(e)[:200]}")

print("\n" + "="*80)
if working_endpoints:
    print(f"FOUND {len(working_endpoints)} WORKING ENDPOINT(S)!")
    for ep in working_endpoints:
        print(f"  - {ep['name']}: {ep['url']}")
else:
    print("NO WORKING ENDPOINTS FOUND")
    print("\nPlease check:")
    print("1. Instagram Premium API 2023 subscription is active")
    print("2. API key is correct")
    print("3. Visit: https://rapidapi.com/NikitusLLP/api/instagram-premium-api-2023/")
print("="*80)
