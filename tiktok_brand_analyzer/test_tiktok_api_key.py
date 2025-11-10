"""
Test TikTok API endpoints with the new RapidAPI key
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from config.secrets import TIKTOK_API23_KEY, TIKTOK_RAPIDAPI_KEY

# Test different potential TikTok API hosts
API_HOSTS = [
    "tiktok-api23.p.rapidapi.com",
    "tiktok-premium-api.p.rapidapi.com",
    "tiktok-scraper7.p.rapidapi.com",
    "tiktok-video-no-watermark2.p.rapidapi.com",
    "tokapi-mobile-version.p.rapidapi.com"
]

# Use the new API key
api_key = TIKTOK_API23_KEY or TIKTOK_RAPIDAPI_KEY

print("="*80)
print("TikTok RapidAPI Key Test")
print("="*80)
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print()

# Test each host with a simple endpoint
for host in API_HOSTS:
    print(f"\nTesting: {host}")
    print("-" * 80)

    # Try different common endpoints
    test_endpoints = []

    if "api23" in host:
        test_endpoints = [
            ("GET", f"https://{host}/api/search/general", {"keyword": "samsung", "count": "5"}),
        ]
    elif "premium" in host:
        test_endpoints = [
            ("GET", f"https://{host}/v1/search/video", {"keyword": "samsung", "count": "5"}),
            ("GET", f"https://{host}/search/video", {"keyword": "samsung", "count": "5"}),
        ]
    elif "scraper" in host:
        test_endpoints = [
            ("GET", f"https://{host}/search/video", {"keyword": "samsung", "count": "5"}),
        ]
    elif "tokapi" in host:
        test_endpoints = [
            ("GET", f"https://{host}/v1/search/video", {"keyword": "samsung", "count": "5"}),
        ]
    else:
        # Generic test
        test_endpoints = [
            ("GET", f"https://{host}/search", {"q": "samsung"}),
        ]

    for method, url, params in test_endpoints:
        try:
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": host
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                print(f"  [OK] SUCCESS: {url}")
                print(f"     Status: {response.status_code}")
                try:
                    data = response.json()
                    print(f"     Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"     Keys: {list(data.keys())[:5]}")
                    print(f"     First 200 chars: {str(data)[:200]}")
                except:
                    print(f"     Response (text): {response.text[:200]}")

                # This API works!
                print(f"\n>>> FOUND WORKING API: {host}")
                print(f"   Endpoint: {url}")
                break

            elif response.status_code == 403:
                print(f"  [403] Not subscribed: {url}")
                print(f"     Status: {response.status_code}")
                print(f"     Message: {response.text[:200]}")

            elif response.status_code == 404:
                print(f"  [404] Endpoint not found: {url}")

            else:
                print(f"  [ERROR] Error {response.status_code}: {url}")
                print(f"     Message: {response.text[:200]}")

        except Exception as e:
            print(f"  [FAIL] Request failed: {url}")
            print(f"     Error: {str(e)[:100]}")

print("\n" + "="*80)
print("Test Complete")
print("="*80)
