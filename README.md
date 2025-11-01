# Samsung DX Sentiment Analysis

삼성 DX 제품에 대한 소셜 미디어 반응 및 감성 분석 프로젝트입니다. YouTube, TikTok, Instagram에서 데이터를 수집하고 분석합니다.

## 목차
- [설치 방법](#설치-방법)
- [프로젝트 구조](#프로젝트-구조)
- [API 설정 가이드](#api-설정-가이드)
- [실행 방법](#실행-방법)
- [데이터 구조](#데이터-구조)

## 설치 방법

### 1. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
각 플랫폼별 설정 파일에 API 키를 추가하세요:
- `youtube_brand_analyzer/config/settings.py`
- `tiktok_brand_analyzer/config/settings.py`
- `instagram_brand_analyzer/config/settings.py`

## 프로젝트 구조

```
samsung_crawl/
├── youtube_brand_analyzer/          # YouTube 데이터 수집 및 분석
│   ├── collectors/
│   │   └── youtube_api.py          # YouTube API 수집기
│   ├── analyzers/
│   │   └── sentiment.py            # 감성 분석 모듈
│   ├── config/
│   │   └── settings.py             # YouTube API 설정
│   ├── data/                       # 수집된 데이터 (CSV)
│   └── main.py                     # 실행 파일
│
├── tiktok_brand_analyzer/           # TikTok 데이터 수집 및 분석
│   ├── collectors/
│   │   └── tiktok_api.py           # TikTok API 수집기
│   ├── analyzers/
│   │   └── sentiment.py            # 감성 분석 모듈
│   ├── config/
│   │   └── settings.py             # TikTok API 설정
│   ├── data/                       # 수집된 데이터 (CSV)
│   └── main.py                     # 실행 파일
│
├── instagram_brand_analyzer/        # Instagram 데이터 수집 및 분석
│   ├── collectors/
│   │   └── instagram_api.py        # Instagram API 수집기
│   ├── analyzers/
│   │   └── sentiment.py            # 감성 분석 모듈
│   ├── config/
│   │   └── settings.py             # Instagram API 설정
│   ├── data/                       # 수집된 데이터 (CSV)
│   └── main.py                     # 실행 파일
│
└── sample_data/                     # API 응답 샘플 데이터
```

## API 설정 가이드

### 1. YouTube Data API v3

#### API 키 발급 방법

1. **Google Cloud Console 접속**
   - https://console.cloud.google.com/ 방문
   - Google 계정으로 로그인

2. **새 프로젝트 생성**
   - 상단 프로젝트 선택 드롭다운 클릭
   - "새 프로젝트" 클릭
   - 프로젝트 이름 입력 (예: "Samsung-Sentiment-Analysis")
   - "만들기" 클릭

3. **YouTube Data API v3 활성화**
   - 왼쪽 메뉴에서 "API 및 서비스" > "라이브러리" 선택
   - 검색창에 "YouTube Data API v3" 검색
   - "YouTube Data API v3" 클릭
   - "사용" 버튼 클릭

4. **API 키 생성**
   - 왼쪽 메뉴에서 "API 및 서비스" > "사용자 인증 정보" 선택
   - 상단 "+ 사용자 인증 정보 만들기" 클릭
   - "API 키" 선택
   - API 키가 생성됨 (복사하여 안전하게 보관)

5. **API 키 제한 설정 (권장)**
   - 생성된 API 키 옆의 편집 아이콘 클릭
   - "API 제한사항" 섹션에서 "키 제한" 선택
   - "YouTube Data API v3"만 선택
   - "저장" 클릭

#### 사용량 및 할당량
- **무료 할당량**: 일일 10,000 units
- **동영상 검색**: 100 units/요청
- **동영상 세부정보**: 1 unit/요청
- **댓글 수집**: 1 unit/요청
- **할당량 확인**: Google Cloud Console > "API 및 서비스" > "할당량"

#### 설정 파일에 추가
```python
# youtube_brand_analyzer/config/settings.py
YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"
```

---

### 2. TikTok Research API

#### API 접근 신청 방법

1. **TikTok for Developers 등록**
   - https://developers.tiktok.com/ 방문
   - "Get Started" 또는 "Sign Up" 클릭
   - TikTok 계정으로 로그인 (없으면 생성)

2. **앱 생성**
   - Dashboard에서 "Manage Apps" 선택
   - "+ Create New App" 클릭
   - 앱 이름 입력
   - App Type: "Research" 선택
   - 약관 동의 후 "Submit" 클릭

3. **Research API 신청**
   - https://developers.tiktok.com/products/research-api/ 방문
   - "Apply for Access" 클릭
   - 신청 양식 작성:
     - Organization type (연구기관/대학/기업)
     - Research purpose (연구 목적 상세 설명)
     - Data usage plan (데이터 사용 계획)
   - 신청서 제출 (승인까지 수 주 소요 가능)

4. **API 키 발급** (승인 후)
   - Dashboard > "My Apps" > 해당 앱 선택
   - "Keys & Tokens" 탭
   - Client Key와 Client Secret 확인

5. **인증 토큰 생성**
   - OAuth 2.0 flow를 통해 Access Token 발급
   - 또는 API 문서의 인증 가이드 참고

#### 사용량 및 제한사항
- **승인 필요**: Research API는 승인 신청 필수
- **데이터 제한**: 특정 데이터 필드만 접근 가능
- **Rate Limit**: 승인된 앱에 따라 다름 (일반적으로 분당 100-1000 요청)
- **데이터 보존**: 수집된 데이터의 보존 기간 및 사용 목적 제한 있음

#### 대안: RapidAPI TikTok API
연구용이 아닌 경우 RapidAPI를 통한 비공식 API 사용 가능:
1. https://rapidapi.com/hub 방문
2. "TikTok" 검색
3. 적합한 API 선택 (예: "TikTok API by dfox")
4. Subscribe 후 API Key 발급

#### 설정 파일에 추가
```python
# tiktok_brand_analyzer/config/settings.py
TIKTOK_CLIENT_KEY = "YOUR_CLIENT_KEY_HERE"
TIKTOK_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
TIKTOK_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

# 또는 RapidAPI 사용 시
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY_HERE"
RAPIDAPI_HOST = "tiktok-api.p.rapidapi.com"
```

---

### 3. Instagram Graph API / Basic Display API

#### API 접근 신청 방법

1. **Facebook 개발자 계정 생성**
   - https://developers.facebook.com/ 방문
   - Facebook 계정으로 로그인
   - "시작하기" 클릭
   - 개발자 등록 양식 작성

2. **앱 생성**
   - 우측 상단 "내 앱" > "앱 만들기" 클릭
   - 사용 사례 선택:
     - "비즈니스" (기업용) 또는
     - "소비자" (개인용)
   - 앱 이름 및 연락처 이메일 입력
   - "앱 만들기" 클릭

3. **Instagram Graph API 추가** (비즈니스 계정용)
   - 대시보드에서 "제품 추가" 섹션 찾기
   - "Instagram" 찾아서 "설정" 클릭
   - Instagram Graph API 선택

   **또는 Instagram Basic Display API** (개인 계정용)
   - "Instagram Basic Display" 찾아서 "설정" 클릭

4. **앱 설정**
   - 좌측 메뉴에서 "설정" > "기본 설정" 선택
   - 앱 ID와 앱 시크릿 키 확인 (복사 후 보관)

5. **Instagram 계정 연결** (Graph API)
   - Instagram 비즈니스 계정 필요
   - Facebook 페이지와 연결된 Instagram 계정 사용
   - "도구" > "Graph API 탐색기"에서 테스트

6. **Access Token 발급**
   - Graph API 탐색기에서 "사용자 또는 페이지" 선택
   - 필요한 권한 선택:
     - `instagram_basic`
     - `pages_read_engagement`
     - `instagram_manage_insights` (insights 필요 시)
   - "액세스 토큰 생성" 클릭

7. **장기 토큰으로 변환** (권장)
   ```bash
   curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
   ```

#### 사용량 및 제한사항
- **Rate Limit**:
  - Graph API: 시간당 200 calls (기본)
  - Basic Display API: 시간당 200 calls
- **데이터 접근**:
  - Graph API: 비즈니스/크리에이터 계정만
  - Basic Display API: 개인 계정 기본 데이터만
- **토큰 유효기간**:
  - 단기 토큰: 1시간
  - 장기 토큰: 60일 (자동 갱신 가능)

#### 개인 계정 데이터 수집 (Basic Display API)
1. 앱 설정 > Basic Display > "Instagram 테스터 추가"
2. Instagram 계정에서 테스터 초대 수락
3. 인증 URL 생성하여 접근 토큰 발급

#### 설정 파일에 추가
```python
# instagram_brand_analyzer/config/settings.py
INSTAGRAM_APP_ID = "YOUR_APP_ID_HERE"
INSTAGRAM_APP_SECRET = "YOUR_APP_SECRET_HERE"
INSTAGRAM_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

# Business Account ID (Graph API 사용 시)
INSTAGRAM_BUSINESS_ACCOUNT_ID = "YOUR_BUSINESS_ACCOUNT_ID"
```

---

## 실행 방법

### YouTube 데이터 수집
```bash
cd youtube_brand_analyzer
python main.py
```

### TikTok 데이터 수집
```bash
cd tiktok_brand_analyzer
python main.py
```

### Instagram 데이터 수집
```bash
cd instagram_brand_analyzer
python main.py
```

## 데이터 구조

### YouTube 데이터
수집된 CSV 파일 구조:
```csv
video_id,title,description,published_at,view_count,like_count,comment_count,channel_title
```

### TikTok 데이터
수집된 CSV 파일 구조:
```csv
video_id,description,create_time,view_count,like_count,comment_count,share_count,author
```

### Instagram 데이터
수집된 CSV 파일 구조:
```csv
media_id,caption,timestamp,like_count,comment_count,media_type,permalink,username
```

자세한 API 응답 구조는 다음 문서를 참고하세요:
- `youtube_api_data_structure.md`
- `tiktok_api_data_structure.md`
- `instagram_api_data_structure.md`

## 주의사항

1. **API 키 보안**: API 키는 절대 공개 저장소에 커밋하지 마세요
2. **Rate Limit**: 각 API의 사용량 제한을 확인하고 준수하세요
3. **데이터 사용 약관**: 각 플랫폼의 데이터 사용 정책을 준수하세요
4. **개인정보 보호**: 수집된 데이터에서 개인정보를 적절히 처리하세요

## 문제 해결

### YouTube API
- **할당량 초과**: Google Cloud Console에서 할당량 증가 요청
- **403 Forbidden**: API 키 제한 설정 확인

### TikTok API
- **접근 거부**: Research API 승인 상태 확인
- **Rate Limit**: 요청 속도 조절 필요

### Instagram API
- **Token 만료**: 장기 토큰으로 변환 또는 자동 갱신 구현
- **권한 오류**: 필요한 권한(scope)이 토큰에 포함되어 있는지 확인

## 참고 자료

- [YouTube Data API 문서](https://developers.google.com/youtube/v3)
- [TikTok Research API 문서](https://developers.tiktok.com/doc/research-api-overview)
- [Instagram Graph API 문서](https://developers.facebook.com/docs/instagram-api)
- [Instagram Basic Display API 문서](https://developers.facebook.com/docs/instagram-basic-display-api)

## 라이선스

이 프로젝트는 연구 및 분석 목적으로 제작되었습니다.
