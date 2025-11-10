"""
Get YouTube Category Mapping
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from collectors.youtube_api import YouTubeAnalyzer

# Get category mapping
analyzer = YouTubeAnalyzer()

try:
    # videoCategories.list API로 카테고리 목록 조회
    categories_response = analyzer.youtube.videoCategories().list(
        part='snippet',
        regionCode='US'
    ).execute()

    print('YouTube Video Category Mapping (US):')
    print('='*70)

    category_map = {}
    for category in categories_response.get('items', []):
        cat_id = category['id']
        cat_title = category['snippet']['title']
        category_map[cat_id] = cat_title
        print(f'  {cat_id:>3} = {cat_title}')

    print()
    print('Your collected videos use these categories:')
    print('  28 = Science & Technology')
    print('  26 = Howto & Style')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
