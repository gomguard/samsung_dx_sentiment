# API Keys and Database Config - Import from secrets.py (not tracked by git)
try:
    from .secrets import (
        YOUTUBE_API_KEY,
        YOUTUBE_API_KEYS,
        OPENAI_API_KEY,
        TIKTOK_CLIENT_KEY,
        TIKTOK_CLIENT_SECRET,
        TIKTOK_API23_KEY,
        TIKTOK_RAPIDAPI_KEY,
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_USER,
        POSTGRES_PASSWORD,
        POSTGRES_DB
    )
except ImportError:
    raise ImportError(
        "secrets.py not found! Please create youtube_brand_analyzer/config/secrets.py file.\n"
        "See secrets.py.example for template."
    )

# YouTube API 설정
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# TikTok API URL 설정
TIKTOK_API_BASE_URL = "https://open.tiktokapis.com/v2"
TIKTOK_API23_BASE_URL = "https://tiktok-api23.p.rapidapi.com"
TIKTOK_RAPIDAPI_BASE_URL = "https://tiktok-scraper2.p.rapidapi.com"

# 데이터 수집 설정
MAX_RESULTS_PER_SEARCH = 50  # 검색당 최대 결과 수
MAX_COMMENTS_PER_VIDEO = 100  # 비디오당 최대 댓글 수

# 검색 지역 설정 (쉽게 변경 가능)
SEARCH_REGIONS = ["US"]  # 미국만 검색
# SEARCH_REGIONS = ["US", "KR"]  # 미국, 한국
# SEARCH_REGIONS = ["US", "KR", "GB", "CA", "AU"]  # 다중 지역

# 지역별 설정
REGION_SETTINGS = {
    "US": {
        "name": "미국",
        "language": "en",
        "timezone": "America/New_York",
        "keywords_suffix": ["usa", "america", "us"]
    },
    "KR": {
        "name": "한국", 
        "language": "ko",
        "timezone": "Asia/Seoul",
        "keywords_suffix": ["korea", "korean", "kr"]
    },
    "GB": {
        "name": "영국",
        "language": "en", 
        "timezone": "Europe/London",
        "keywords_suffix": ["uk", "britain", "gb"]
    },
    "CA": {
        "name": "캐나다",
        "language": "en",
        "timezone": "America/Toronto", 
        "keywords_suffix": ["canada", "canadian", "ca"]
    },
    "AU": {
        "name": "호주",
        "language": "en",
        "timezone": "Australia/Sydney",
        "keywords_suffix": ["australia", "aussie", "au"]
    }
}

# 브랜드 검색 키워드 설정 (쉽게 추가/수정 가능)
BRAND_KEYWORDS = [
    # 기본 브랜드 키워드
    "samsung tv",
    
    # Samsung 제품 관련
    "samsung television",
    "samsung smart tv", 
    "samsung qled",
    "samsung neo qled",
    "samsung frame tv",
    "samsung the frame",
    
    # 경쟁 브랜드 키워드 (비교 분석용)
    "lg tv",
    "sony tv", 
    "tcl tv",
    
    # 일반 TV 키워드
    "smart tv",
    "4k tv",
    "oled tv",
    "qled tv"
]

# TikTok 특화 키워드 (해시태그 형태)
TIKTOK_HASHTAG_KEYWORDS = [
    "samsung",
    "samsungtv", 
    "smarttv",
    "television",
    "tv",
    "qled",
    "oled",
    "4ktv"
]

# 분석 설정
SENTIMENT_THRESHOLD_POSITIVE = 0.1
SENTIMENT_THRESHOLD_NEGATIVE = -0.1

# 출력 설정
OUTPUT_DIR = "data"
CSV_ENCODING = "utf-8-sig"

# 파일명 템플릿
FILE_TEMPLATES = {
    "01_video_metadata": "01_video_metadata_{keyword}_{region}_{date}.csv",
    "02_video_statistics": "02_video_statistics_{keyword}_{region}_{date}.csv", 
    "03_channel_info": "03_channel_info_{keyword}_{region}_{date}.csv",
    "04_comments_raw": "04_comments_raw_{keyword}_{region}_{date}.csv",
    "05_comments_sentiment": "05_comments_sentiment_{keyword}_{region}_{date}.csv",
    "06_trend_analysis": "06_trend_analysis_{keyword}_{region}_{date}.csv",
    "07_keyword_mentions": "07_keyword_mentions_{keyword}_{region}_{date}.csv",
    "08_competitor_comparison": "08_competitor_comparison_{keyword}_{region}_{date}.csv"
}