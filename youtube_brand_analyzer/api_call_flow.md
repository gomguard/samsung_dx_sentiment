# YouTube API 호출 흐름 정리

## 현재 구조 (pipeline_youtube_analysis.py)

### Step 1: 영상 데이터 수집
**함수**: `get_comprehensive_video_data()`

#### 1.1 비디오 ID 수집 (배치 단위)
```
search.list() 호출
- 비용: 100 units
- 호출 횟수: 배치당 1-3회 (50개씩 수집, nextPageToken으로 반복)
- 목적: video_id 리스트 수집
```

#### 1.2 비디오 상세 정보 수집
```
videos.list() 호출
- 비용: 1 unit
- 호출 횟수: (비디오 수 / 50) 올림
  예: 50개 비디오 → 1회
- 목적: title, view_count, like_count, category_id, channel_id 등
```

#### 1.3 채널 정보 수집 (최적화됨 ✅)
```
channels.list() 호출
- 비용: 1 unit
- 호출 횟수: (고유 채널 수 / 50) 올림
  예: 5개 고유 채널 → 1회
- 목적: channel_country, subscriber_count 등
- 최적화: set()으로 중복 제거됨
```

#### 1.4 필터링 (API 호출 없음)
```
로컬 필터링:
- channel_country == 'US'
- category_id == '28'
- channel_subscriber_count >= 10,000
- engagement_rate >= 2.0%

필터링 통과한 비디오만 다음 단계로
```

### Step 1.5: DB 저장 (API 호출 없음)
```
PostgreSQL 저장:
- youtube_videos_raw: 모든 수집 데이터
- youtube_videos: 필터링된 데이터
```

### Step 2: 댓글 데이터 수집 (필터링된 비디오만! ✅)
```
commentThreads.list() 호출
- 비용: 1 unit
- 호출 횟수: 필터링된 비디오 수
  예: 5개 필터링됨 → 5회
- 목적: 각 비디오의 댓글 수집
```

### Step 3: 댓글 요약 (OpenAI API, YouTube 아님)
```
OpenAI API 호출:
- 비용: OpenAI 비용 (YouTube API 아님)
- 호출 횟수: 필터링된 비디오 수
```

### Step 4: DB 저장 (API 호출 없음)
```
PostgreSQL 업데이트:
- youtube_videos: comment_text_summary 업데이트
- youtube_comments: 댓글 데이터 삽입
```

---

## API 호출 타이밍 예시

### 시나리오: 548개 수집 → 5개 필터링 통과

```
[시작]
  ↓
[배치 1: 50개 비디오 수집]
  ├─ search.list() × 1회 = 100 units
  ├─ videos.list() × 1회 = 1 unit
  ├─ channels.list() × 1회 = 1 unit (10개 고유 채널 가정)
  └─ 로컬 필터링 → 1개 통과

[배치 2: 50개 비디오 수집]
  ├─ search.list() × 1회 = 100 units
  ├─ videos.list() × 1회 = 1 unit
  ├─ channels.list() × 1회 = 1 unit
  └─ 로컬 필터링 → 0개 통과

... (반복)

[배치 11: 48개 비디오 수집]
  ├─ search.list() × 1회 = 100 units
  ├─ videos.list() × 1회 = 1 unit
  ├─ channels.list() × 1회 = 1 unit
  └─ 로컬 필터링 → 1개 통과

[Step 1.5] DB 저장

[Step 2] 댓글 수집 (5개 비디오만!)
  ├─ commentThreads.list() × 5회 = 5 units

[Step 3] OpenAI 댓글 요약
  ├─ OpenAI API × 5회

[Step 4] DB 저장

[완료]
```

### 총 API 비용 (548개 수집 → 5개 필터링)

```
YouTube API:
- search.list(): 100 units × 11회 = 1,100 units (67%)
- videos.list(): 1 unit × 11회 = 11 units (0.7%)
- channels.list(): 1 unit × 11회 = 11 units (0.7%)
- commentThreads.list(): 1 unit × 5회 = 5 units (0.3%)

총: 1,127 units (하루 할당량 10,000 중 11.3%)

OpenAI API:
- 댓글 요약: 5회
```

---

## 최적화 완료 사항 ✅

1. **channel_ids 중복 제거**: set() 사용으로 중복 채널 정보 요청 방지
2. **commentThreads.list() 최적화**: 필터링된 비디오에만 호출 (5/548 = 0.9%)
3. **배치 내 중복 제거**: video_id set()으로 중복 방지
4. **조기 종료**: 3번 연속 빈 배치 시 중단

---

## 병목 지점

**search.list()가 가장 비싸다** (67% 차지)
- 548개 수집했지만 5개만 사용 (0.9% 효율)
- 해결책: 더 정확한 검색 필터 사용 (하지만 YouTube API 제약)

**engagement_rate >= 2% 필터가 가장 많이 걸러냄**
- 17개 → 5개 (12개 탈락, 70% 탈락률)
- 현재: 유지하기로 결정
