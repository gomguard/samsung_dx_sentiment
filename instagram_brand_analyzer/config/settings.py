# Import RapidAPI key from parent config
import os
import sys

# Load RapidAPI key using importlib to avoid circular import
INSTAGRAM_RAPIDAPI_KEY = ""
try:
    import importlib.util
    parent_config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
    secrets_path = os.path.join(parent_config_dir, 'secrets.py')

    if os.path.exists(secrets_path):
        spec = importlib.util.spec_from_file_location("parent_secrets", secrets_path)
        parent_secrets = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parent_secrets)
        # Use Instagram-specific key if available
        if hasattr(parent_secrets, 'INSTAGRAM_RAPIDAPI_KEY'):
            INSTAGRAM_RAPIDAPI_KEY = parent_secrets.INSTAGRAM_RAPIDAPI_KEY
        else:
            INSTAGRAM_RAPIDAPI_KEY = parent_secrets.TIKTOK_RAPIDAPI_KEY
except Exception as e:
    print(f"Warning: Could not load RapidAPI key: {e}")
    INSTAGRAM_RAPIDAPI_KEY = ""

# Instagram RapidAPI 설정 (Instagram Premium API 2023)
INSTAGRAM_RAPIDAPI_BASE_URL = "https://instagram-premium-api-2023.p.rapidapi.com"
INSTAGRAM_RAPIDAPI_HOST = "instagram-premium-api-2023.p.rapidapi.com"

# Instagram API 설정 (Legacy - Not used)
INSTAGRAM_ACCESS_TOKEN = ""  # Instagram Basic Display API 토큰
INSTAGRAM_APP_ID = ""        # Instagram 앱 ID
INSTAGRAM_APP_SECRET = ""    # Instagram 앱 시크릿

# Instagram Graph API 설정 (비즈니스 계정용 - Legacy - Not used)
INSTAGRAM_GRAPH_ACCESS_TOKEN = ""

# 데이터 수집 설정
MAX_RESULTS_PER_SEARCH = 30  # 검색당 최대 결과 수
MAX_COMMENTS_PER_POST = 50   # 게시물당 최대 댓글 수

# 검색 지역 설정
SEARCH_REGIONS = ["US"]  # 미국만 검색

# 지역별 설정
REGION_SETTINGS = {
    "US": {
        "name": "미국",
        "language": "en",
        "timezone": "America/New_York",
        "location_tags": ["usa", "america", "us"]
    },
    "KR": {
        "name": "한국", 
        "language": "ko",
        "timezone": "Asia/Seoul",
        "location_tags": ["korea", "korean", "kr"]
    }
}

# Instagram 검색 키워드 설정
INSTAGRAM_KEYWORDS = [
    # Samsung 관련
    "Samsung TV",
    "Samsung QLED",
    "Samsung OLED",
    "Samsung Frame TV",
    "Samsung 4K TV",
    "Samsung 8K",
    "Samsung Smart TV",

    # 경쟁사
    "LG TV",
    "LG OLED",
    "LG QNED",
    "LG 4K TV",
    "LG 8K",
    "Sony TV",
    "Sony Bravia",
    "TCL TV",
    "Apple TV",

    # 일반 TV 키워드
    "Smart TV",
    "4K TV",
    "OLED TV",
    "QLED TV",
    "Television Review",
    "New TV"
]

# 분석 설정
SENTIMENT_THRESHOLD_POSITIVE = 0.1
SENTIMENT_THRESHOLD_NEGATIVE = -0.1

# 출력 설정
OUTPUT_DIR = "data"
CSV_ENCODING = "utf-8-sig"

# 파일명 템플릿
FILE_TEMPLATES = {
    "instagram_posts": "instagram_posts_{hashtag}_{region}_{date}.csv",
    "instagram_comments": "instagram_comments_{hashtag}_{region}_{date}.csv",
    "instagram_analysis": "instagram_analysis_{hashtag}_{region}_{date}.csv"
}

# Instagram API 제약사항
API_RATE_LIMITS = {
    "rapidapi": {
        "requests_per_month": 100,  # Free tier limit
        "delay_between_requests": 2  # seconds
    },
    "basic_display": {
        "requests_per_hour": 200,
        "requests_per_day": 1000
    },
    "graph_api": {
        "requests_per_hour": 200,
        "requests_per_day": 4800
    }
}