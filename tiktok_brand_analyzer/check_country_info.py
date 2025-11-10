"""
TikTok User Info API에서 국가 정보 확인
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

# 다양한 국가의 사용자 테스트
test_users = [
    'supersaf',          # UK
    'gizmodojapan',      # Japan
    'lg_uk',             # UK
    'samsung_kenya',     # Kenya
    'abenson.ph',        # Philippines
]

print('=' * 80)
print('TikTok User Info에서 국가 정보 확인')
print('=' * 80)
print()

for username in test_users:
    url = f'https://{host}/api/user/info'
    params = {'uniqueId': username}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            user_info = data.get('userInfo', {})
            user = user_info.get('user', {})

            print(f'@{username}:')

            # 모든 필드에서 국가/지역 관련 찾기
            country_related = []
            for key, value in user.items():
                key_lower = str(key).lower()
                if any(word in key_lower for word in ['country', 'region', 'location', 'nation', 'area']):
                    country_related.append((key, value))

            if country_related:
                print('  국가/지역 관련 필드 발견:')
                for field, value in country_related:
                    print(f'    {field}: {value}')
            else:
                print('  [INFO] 국가 필드 없음')

            # Signature(bio)에서 국가 힌트
            sig = user.get('signature', '')
            if sig and len(sig) > 0:
                # 국가명 키워드 찾기
                keywords = ['UK', 'Japan', 'Kenya', 'Philippines', 'USA', 'Korea', 'India']
                found_keywords = [k for k in keywords if k.lower() in sig.lower()]
                if found_keywords:
                    print(f'  Bio에서 발견: {found_keywords}')
                    print(f'  Bio: {sig[:80]}')

            print()
        else:
            print(f'@{username}: API Error {response.status_code}')
            print()

    except Exception as e:
        print(f'@{username}: Error - {e}')
        print()

print('=' * 80)
print('결론:')
print('TikTok User Info API에서 국가 정보를 직접 제공하지 않는 것 같습니다.')
print('대안: Bio/채널명에서 추론하거나, 별도 데이터 소스 필요')
print('=' * 80)
