# Samsung DX 브랜드 감성 분석 - 스케줄러 실행 가이드

## 📋 개요

YouTube, Instagram, TikTok 3개 플랫폼의 데이터를 수집하고 감성 분석을 수행하는 통합 파이프라인입니다.

---

## 🚀 통합 실행

### 기본 실행 방법

```bash
cd D:\Gomguard\program\samsung_crawl
python sentiment_main.py
```

### 각 플랫폼별 작업 내용

#### 1. YouTube (`youtube_brand_analyzer/`)
- YouTube API로 영상 정보 수집
- 댓글 수집 (최대 100개/비디오)
- 자막 추출 및 요약 (OpenAI GPT-4o-mini)
- 댓글 요약 (OpenAI GPT-4o-mini)
- PostgreSQL 저장

**수집 키워드:**
- Samsung TV, Samsung QLED, LG TV, Sony TV 등

**예상 소요 시간:** 10-30분
- API 호출: 영상당 2-3초
- OpenAI 요약: 영상당 5-10초
- 총 10-20개 영상 처리

---

#### 2. Instagram (`instagram_brand_analyzer/`)
- Instagram API로 게시물 정보 수집
- 댓글 수집
- 감정 분석 수행 (TextBlob)
- 댓글 요약 (OpenAI GPT-4o-mini)
- PostgreSQL 저장

**수집 해시태그:**
- #samsungtv, #lgтv, #sonytv 등

**예상 소요 시간:** 5-20분
- API 호출: 게시물당 1-2초
- 감정 분석: 댓글당 0.1초
- OpenAI 요약: 게시물당 3-5초

---

#### 3. TikTok (`tiktok_brand_analyzer/`)
- TikTok API로 비디오 정보 수집 (RapidAPI)
- 댓글 수집
- 감정 분석 수행
- 비디오 요약 (OpenAI GPT-4o-mini)
- 댓글 요약 (OpenAI GPT-4o-mini)
- 국가 정보 추론 (채널명, 제목, 설명 분석)
- PostgreSQL 저장

**수집 키워드:**
- Samsung TV, Samsung QLED, LG TV, Sony TV 등

**예상 소요 시간:** 10-25분
- RapidAPI 호출: 비디오당 2-3초
- OpenAI 요약: 비디오당 5-10초

---

## ⏱️ 전체 예상 실행 시간

### 정상 상황
- **최소:** 25분 (각 플랫폼 빠르게 완료)
- **평균:** 45분 (일반적인 경우)
- **최대:** 75분 (많은 데이터 + API 지연)

### 영향 요인
1. **API Rate Limit**
   - YouTube API: 10,000 units/day
   - Instagram API: 제한 있음
   - TikTok RapidAPI: 요청 제한 있음

2. **OpenAI API 속도**
   - GPT-4o-mini: 일반적으로 빠름
   - Rate limit: 분당 호출 제한

3. **수집 데이터 양**
   - 각 플랫폼에서 수집하는 데이터 수에 비례

---

## 🔧 Windows 작업 스케줄러 설정

### 1. 작업 스케줄러 열기
```
Windows 검색 → "작업 스케줄러" (Task Scheduler)
```

### 2. 기본 작업 만들기
1. 우측 패널 → **"기본 작업 만들기"** 클릭
2. 이름: `Samsung_Sentiment_Analysis`
3. 설명: `YouTube, Instagram, TikTok 브랜드 감성 분석`

### 3. 트리거 설정
**옵션 1: 매일 실행**
- 트리거: 매일
- 시작 시간: `02:00 AM` (새벽 2시)

**옵션 2: 주간 실행**
- 트리거: 매주
- 요일: 월요일, 수요일, 금요일
- 시작 시간: `02:00 AM`

### 4. 작업 설정
- 작업: **"프로그램 시작"**
- 프로그램/스크립트:
  ```
  C:\Users\[사용자명]\AppData\Local\Programs\Python\Python39\python.exe
  ```
  (또는 Python 설치 경로)

- 인수 추가:
  ```
  sentiment_main.py
  ```

- 시작 위치:
  ```
  D:\Gomguard\program\samsung_crawl
  ```

### 5. 고급 설정
- ✅ **"작업이 실패할 경우 다시 시작"** (3회)
- ✅ **"작업 실행 시간이 다음보다 오래 걸리면 중지"** → 3시간
- ✅ **"로그 기록"**

---

## 📊 실행 결과 확인

### 1. 콘솔 출력
스크립트 실행 시 실시간 진행 상황이 출력됩니다:

```
================================================================================
  Samsung DX 브랜드 감성 분석 - 통합 파이프라인
================================================================================
시작 시간: 2025-01-04 02:00:00

실행할 플랫폼: YouTube, Instagram, TikTok

================================================================================
  YouTube 데이터 수집 및 분석 시작
================================================================================
...
[OK] YouTube 파이프라인 완료
     소요 시간: 15분 32초

================================================================================
  전체 실행 결과 요약
================================================================================
시작 시간: 2025-01-04 02:00:00
종료 시간: 2025-01-04 02:45:23
총 소요 시간: 45분 23초

플랫폼별 결과:
[OK] YouTube        - 15분 32초
[OK] Instagram      - 12분 18초
[OK] TikTok         - 17분 33초

성공: 3/3개 플랫폼
```

### 2. 데이터베이스 확인
PostgreSQL 데이터베이스 (`samsung_dx_sentiment`)에서 확인:

```sql
-- YouTube 데이터
SELECT COUNT(*) FROM youtube_videos;
SELECT COUNT(*) FROM youtube_comments;

-- Instagram 데이터
SELECT COUNT(*) FROM instagram_posts;
SELECT COUNT(*) FROM instagram_comments;

-- TikTok 데이터
SELECT COUNT(*) FROM tiktok_videos;
SELECT COUNT(*) FROM tiktok_comments;
```

### 3. CSV 파일 확인
각 플랫폼 폴더의 `data/` 디렉토리:
- `youtube_brand_analyzer/data/videos_final.csv`
- `instagram_brand_analyzer/data/instagram_posts_final.csv`
- `tiktok_brand_analyzer/tiktok_video_summaries_final.csv`

---

## 🔍 문제 해결

### 특정 플랫폼만 실행하기

`sentiment_main.py` 파일에서 `enabled` 설정 변경:

```python
PLATFORMS = {
    'youtube': {
        'name': 'YouTube',
        'enabled': True  # False로 변경하면 비활성화
    },
    'instagram': {
        'name': 'Instagram',
        'enabled': True
    },
    'tiktok': {
        'name': 'TikTok',
        'enabled': True
    }
}
```

### API 키 확인
```
config/secrets.py
```
파일에서 모든 API 키가 설정되어 있는지 확인:
- `YOUTUBE_API_KEY`
- `INSTAGRAM_ACCESS_TOKEN`
- `TIKTOK_API23_KEY`
- `OPENAI_API_KEY`

### 데이터베이스 연결 확인
```python
from config.db_manager import YouTubeDBManager

db = YouTubeDBManager()
if db.connect():
    print("연결 성공!")
else:
    print("연결 실패")
```

---

## 📝 로그 파일 저장 (선택사항)

실행 로그를 파일로 저장하려면:

```bash
python sentiment_main.py > logs/sentiment_$(date +%Y%m%d_%H%M%S).log 2>&1
```

Windows 작업 스케줄러에서는:
```batch
cmd /c "python sentiment_main.py > D:\Gomguard\program\samsung_crawl\logs\sentiment.log 2>&1"
```

---

## ⚠️ 주의사항

1. **API 할당량 관리**
   - YouTube API: 일일 할당량 확인
   - RapidAPI: 월간 요청 제한 확인
   - OpenAI API: 사용량 모니터링

2. **네트워크 안정성**
   - 안정적인 인터넷 연결 필요
   - VPN 사용 시 속도 저하 가능

3. **디스크 공간**
   - PostgreSQL 데이터베이스 용량
   - CSV 파일 용량

4. **실행 시간대**
   - API 트래픽이 적은 시간대 권장 (새벽 2-4시)
   - 업무 시간 외 실행 권장

---

## 📞 지원

문제 발생 시:
1. 로그 파일 확인
2. API 키 유효성 확인
3. 데이터베이스 연결 확인
4. 네트워크 상태 확인
