"""
Debug YouTube API responses with different parameters
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from collectors.youtube_api import YouTubeAnalyzer
from datetime import datetime, timedelta

analyzer = YouTubeAnalyzer()

# Test 1: WITH regionCode='US'
print('='*80)
print('TEST 1: WITH regionCode=US + 90 days filter')
print('='*80)

ninety_days_ago = datetime.now() - timedelta(days=90)
search_params_with_region = {
    'part': 'snippet',
    'q': 'Samsung TV',
    'type': 'video',
    'regionCode': 'US',
    'maxResults': 50,
    'order': 'relevance',
    'publishedAfter': ninety_days_ago.isoformat() + 'Z'
}

response1 = analyzer.youtube.search().list(**search_params_with_region).execute()
print(f'Total Results: {response1.get("pageInfo", {}).get("totalResults", 0)}')
print(f'Results Per Page: {response1.get("pageInfo", {}).get("resultsPerPage", 0)}')
print(f'Items Returned: {len(response1.get("items", []))}')
print(f'Next Page Token: {"Yes" if response1.get("nextPageToken") else "No"}')

print()
print('='*80)
print('TEST 2: WITHOUT regionCode + 90 days filter')
print('='*80)

search_params_without_region = {
    'part': 'snippet',
    'q': 'Samsung TV',
    'type': 'video',
    'maxResults': 50,
    'order': 'relevance',
    'publishedAfter': ninety_days_ago.isoformat() + 'Z'
}

response2 = analyzer.youtube.search().list(**search_params_without_region).execute()
print(f'Total Results: {response2.get("pageInfo", {}).get("totalResults", 0)}')
print(f'Results Per Page: {response2.get("pageInfo", {}).get("resultsPerPage", 0)}')
print(f'Items Returned: {len(response2.get("items", []))}')
print(f'Next Page Token: {"Yes" if response2.get("nextPageToken") else "No"}')

print()
print('='*80)
print('TEST 3: WITHOUT regionCode + NO date filter')
print('='*80)

search_params_no_filter = {
    'part': 'snippet',
    'q': 'Samsung TV',
    'type': 'video',
    'maxResults': 50,
    'order': 'relevance'
}

response3 = analyzer.youtube.search().list(**search_params_no_filter).execute()
print(f'Total Results: {response3.get("pageInfo", {}).get("totalResults", 0)}')
print(f'Results Per Page: {response3.get("pageInfo", {}).get("resultsPerPage", 0)}')
print(f'Items Returned: {len(response3.get("items", []))}')
print(f'Next Page Token: {"Yes" if response3.get("nextPageToken") else "No"}')
