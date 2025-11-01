# Instagram API 설정
INSTAGRAM_ACCESS_TOKEN = ""  # Instagram Basic Display API 토큰
INSTAGRAM_APP_ID = ""        # Instagram 앱 ID
INSTAGRAM_APP_SECRET = ""    # Instagram 앱 시크릿

# Instagram Graph API 설정 (비즈니스 계정용)
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

# 브랜드 검색 해시태그 설정
BRAND_HASHTAGS = [
    # Samsung 관련
    "samsungtv",
    "samsung",
    "samsungqled",
    "samsungframe",
    "theframe",
    "samsungsmartTV",
    
    # 경쟁사
    "lgtv",
    "lg",
    "sonytv", 
    "sony",
    "tcltv",
    "appletv",
    
    # 일반 TV 해시태그
    "smarttv",
    "4ktv",
    "oledtv",
    "qledtv",
    "television",
    "tvreview",
    "newTV"
]

# Instagram 특화 키워드
INSTAGRAM_KEYWORDS = [
    "samsung tv",
    "samsung qled", 
    "samsung frame tv",
    "lg tv",
    "sony tv",
    "tcl tv",
    "apple tv",
    "smart tv",
    "4k tv",
    "oled tv",
    "qled tv"
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
    "basic_display": {
        "requests_per_hour": 200,
        "requests_per_day": 1000
    },
    "graph_api": {
        "requests_per_hour": 200,
        "requests_per_day": 4800
    }
}