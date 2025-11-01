# YouTube API 데이터 구조 분석

## 전체 필드 목록 (Complete Field List)

| 인덱스 | 필드 구분 | 필드명 | 타입 | 설명 | 수집 필요 |
|--------|-----------|--------|------|------|----------|
| 1 | 검색 관련 정보 | `video_id` | string | 비디오 고유 ID | 필수 |
| 2 | 검색 관련 정보 | `search_keyword` | string | 검색에 사용된 키워드 | 필수 |
| 3 | 검색 관련 정보 | `search_region` | string | 검색 지역 코드 (ISO 3166-1 alpha-2) | 필수 |
| 4 | 검색 관련 정보 | `search_order` | string | 정렬 순서 (relevance, date, rating, viewCount 등) | 권장 |
| 5 | 검색 관련 정보 | `collected_at` | string | 데이터 수집 시간 (ISO 8601) | 필수 |
| 6 | 비디오 기본 정보 | `title` | string | 비디오 제목 | 필수 |
| 7 | 비디오 기본 정보 | `description` | string | 비디오 설명 | 필수 |
| 8 | 비디오 기본 정보 | `published_at` | string | 게시 시간 (ISO 8601) | 필수 |
| 9 | 비디오 기본 정보 | `category_id` | string | 카테고리 ID (예: 22=People & Blogs, 28=Science & Technology) | 권장 |
| 10 | 비디오 기본 정보 | `tags` | string | 비디오 태그 (쉼표로 구분) | 필수 |
| 11 | 비디오 기본 정보 | `default_language` | string | 기본 언어 코드 | 권장 |
| 12 | 비디오 기본 정보 | `default_audio_language` | string | 기본 오디오 언어 코드 | 권장 |
| 13 | 비디오 기본 정보 | `live_broadcast_content` | string | 라이브 방송 상태 (none, upcoming, live) | 권장 |
| 14 | 채널 정보 | `channel_id` | string | 채널 고유 ID | 필수 |
| 15 | 채널 정보 | `channel_title` | string | 채널 이름 | 필수 |
| 16 | 채널 정보 | `channel_description` | string | 채널 설명 | 권장 |
| 17 | 채널 정보 | `channel_custom_url` | string | 채널 커스텀 URL | 권장 |
| 18 | 채널 정보 | `channel_published_at` | string | 채널 생성 날짜 | 권장 |
| 19 | 채널 정보 | `channel_country` | string | 채널 국가 | 필수 |
| 20 | 채널 통계 | `channel_subscriber_count` | integer | 채널 구독자 수 | 필수 |
| 21 | 채널 통계 | `channel_video_count` | integer | 채널 총 비디오 수 | 필수 |
| 22 | 채널 통계 | `channel_total_view_count` | integer | 채널 총 조회 수 | 필수 |
| 23 | 썸네일 정보 | `thumbnail_default` | string | 기본 썸네일 URL (120x90) | 권장 |
| 24 | 썸네일 정보 | `thumbnail_medium` | string | 중간 썸네일 URL (320x180) | 필수 |
| 25 | 썸네일 정보 | `thumbnail_high` | string | 고화질 썸네일 URL (480x360) | 필수 |
| 26 | 썸네일 정보 | `thumbnail_standard` | string | 표준 썸네일 URL (640x480) | 권장 |
| 27 | 썸네일 정보 | `thumbnail_maxres` | string | 최고화질 썸네일 URL (1280x720) | 권장 |
| 28 | 인게이지먼트 지표 | `view_count` | integer | 조회 수 | 필수 |
| 29 | 인게이지먼트 지표 | `like_count` | integer | 좋아요 수 | 필수 |
| 30 | 인게이지먼트 지표 | `dislike_count` | integer | 싫어요 수 (현재 API에서 제공 안 함) | 불필요 |
| 31 | 인게이지먼트 지표 | `favorite_count` | integer | 즐겨찾기 수 | 권장 |
| 32 | 인게이지먼트 지표 | `comment_count` | integer | 댓글 수 | 필수 |
| 33 | 콘텐츠 상세 정보 | `duration_seconds` | integer | 비디오 길이 (초) | 필수 |
| 34 | 콘텐츠 상세 정보 | `duration_iso` | string | 비디오 길이 (ISO 8601 Duration 형식, 예: PT4M13S) | 권장 |
| 35 | 콘텐츠 상세 정보 | `dimension` | string | 비디오 차원 (2d, 3d) | 권장 |
| 36 | 콘텐츠 상세 정보 | `definition` | string | 비디오 해상도 (sd, hd) | 필수 |
| 37 | 콘텐츠 상세 정보 | `caption` | string | 자막 제공 여부 (true, false) | 권장 |
| 38 | 콘텐츠 상세 정보 | `licensed_content` | boolean | 라이선스 콘텐츠 여부 | 권장 |
| 39 | 콘텐츠 상세 정보 | `content_rating` | string | 콘텐츠 등급 정보 | 권장 |
| 40 | 콘텐츠 상세 정보 | `projection` | string | 비디오 투영 방식 (rectangular, 360) | 권장 |
| 41 | 콘텐츠 상세 정보 | `has_custom_thumbnail` | boolean | 커스텀 썸네일 사용 여부 | 권장 |
| 42 | 비디오 상태 정보 | `upload_status` | string | 업로드 상태 (processed, uploaded, failed, rejected, deleted) | 권장 |
| 43 | 비디오 상태 정보 | `privacy_status` | string | 공개 상태 (public, private, unlisted) | 필수 |
| 44 | 비디오 상태 정보 | `license` | string | 라이선스 타입 (youtube, creativeCommon) | 권장 |
| 45 | 비디오 상태 정보 | `embeddable` | boolean | 임베드 가능 여부 | 권장 |
| 46 | 비디오 상태 정보 | `public_stats_viewable` | boolean | 공개 통계 조회 가능 여부 | 권장 |
| 47 | 비디오 상태 정보 | `made_for_kids` | boolean | 어린이용 콘텐츠 여부 | 필수 |
| 48 | 비디오 상태 정보 | `self_declared_made_for_kids` | boolean | 제작자가 선언한 어린이용 콘텐츠 여부 | 권장 |
| 49 | 주제 정보 | `topic_ids` | string | 주제 ID 목록 (쉼표로 구분) | 권장 |
| 50 | 주제 정보 | `relevant_topic_ids` | string | 관련 주제 ID 목록 | 권장 |
| 51 | 주제 정보 | `topic_categories` | string | 주제 카테고리 URL 목록 | 권장 |
| 52 | 녹화 정보 | `recording_date` | string | 녹화 날짜 | 권장 |
| 53 | 녹화 정보 | `location_latitude` | float | 녹화 위치 위도 | 권장 |
| 54 | 녹화 정보 | `location_longitude` | float | 녹화 위치 경도 | 권장 |
| 55 | 녹화 정보 | `location_altitude` | float | 녹화 위치 고도 | 불필요 |

### 수집 필요 표시 설명
- **필수**: Samsung 브랜드 분석에 반드시 필요한 데이터
- **권장**: 심화 분석 시 유용한 데이터
- **불필요**: 수집하지 않아도 되는 데이터

---

## YouTube 댓글 데이터 구조

| 인덱스 | 필드 구분 | 필드명 | 타입 | 설명 | 수집 필요 |
|--------|-----------|--------|------|------|----------|
| 1 | 댓글 기본 정보 | `video_id` | string | 비디오 ID | 필수 |
| 2 | 댓글 기본 정보 | `comment_id` | string | 댓글 고유 ID | 필수 |
| 3 | 댓글 기본 정보 | `comment_type` | string | 댓글 타입 (top_level, reply) | 필수 |
| 4 | 댓글 기본 정보 | `parent_comment_id` | string | 부모 댓글 ID (답글인 경우) | 필수 |
| 5 | 댓글 기본 정보 | `collected_at` | string | 수집 시간 | 필수 |
| 6 | 작성자 정보 | `author_display_name` | string | 작성자 표시 이름 | 필수 |
| 7 | 작성자 정보 | `author_profile_image_url` | string | 작성자 프로필 이미지 URL | 권장 |
| 8 | 작성자 정보 | `author_channel_url` | string | 작성자 채널 URL | 권장 |
| 9 | 작성자 정보 | `author_channel_id` | string | 작성자 채널 ID | 필수 |
| 10 | 댓글 내용 | `comment_text_display` | string | 댓글 텍스트 (HTML 포함) | 필수 |
| 11 | 댓글 내용 | `comment_text_original` | string | 댓글 원본 텍스트 (순수 텍스트) | 필수 |
| 12 | 댓글 내용 | `comment_text_length` | integer | 댓글 길이 | 권장 |
| 13 | 댓글 인게이지먼트 | `like_count` | integer | 댓글 좋아요 수 | 필수 |
| 14 | 댓글 인게이지먼트 | `reply_count` | integer | 답글 수 | 필수 |
| 15 | 댓글 상태 | `moderation_status` | string | 검토 상태 (published, heldForReview, likelySpam, rejected) | 권장 |
| 16 | 댓글 시간 정보 | `published_at` | string | 댓글 게시 시간 | 필수 |
| 17 | 댓글 시간 정보 | `updated_at` | string | 댓글 수정 시간 | 권장 |
| 18 | 댓글 추가 정보 | `viewer_rating` | string | 시청자 평가 (none, like) | 불필요 |
| 19 | 댓글 추가 정보 | `can_rate` | boolean | 평가 가능 여부 | 불필요 |

---

## Samsung 브랜드 모니터링 핵심 수집 데이터

### 우선순위 1 (필수)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 비디오 ID | `video_id` | 고유 식별 |
| 제목/설명 | `title`, `description` | 키워드 분석, 제품 언급 파악 |
| 게시 시간 | `published_at` | 시계열 분석 |
| 채널 정보 | `channel_id`, `channel_title`, `channel_subscriber_count` | 인플루언서 영향력 파악 |
| 인게이지먼트 | `view_count`, `like_count`, `comment_count` | 인기도/반응 측정 |
| 태그 | `tags` | 키워드/해시태그 분석 |
| 썸네일 | `thumbnail_high`, `thumbnail_medium` | 시각적 콘텐츠 수집 |

### 우선순위 2 (권장)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 비디오 길이 | `duration_seconds` | 콘텐츠 타입 분류 |
| 화질 | `definition` | 프리미엄 콘텐츠 여부 |
| 지역 정보 | `search_region`, `channel_country` | 지역별 트렌드 |
| 공개 상태 | `privacy_status` | 콘텐츠 접근성 |
| 어린이용 여부 | `made_for_kids` | 타겟 오디언스 분류 |
| 댓글 데이터 | 댓글 전체 필드 | 소비자 피드백 분석 |

### 우선순위 3 (참고)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 카테고리 | `category_id` | 콘텐츠 분류 |
| 라이선스 | `license`, `licensed_content` | 저작권 정보 |
| 주제 정보 | `topic_categories` | 콘텐츠 주제 분류 |
| 녹화 정보 | `recording_date`, `location_*` | 제작 배경 정보 |

---

## 데이터 수집 전략

### 검색 키워드 기반 수집
```python
# 추천 Samsung 검색 키워드
samsung_keywords = [
    "samsung",
    "samsung tv",
    "samsung galaxy",
    "samsung phone review",
    "samsung unboxing",
    "samsung comparison",
    "갤럭시",
    "삼성전자"
]
```

### 페이지네이션 구현
```python
def collect_youtube_videos(keyword, region_code="US", max_results=100):
    analyzer = YouTubeAnalyzer()

    # 최대 100개까지 수집 (API 제한)
    video_data, video_ids = analyzer.get_comprehensive_video_data(
        keyword=keyword,
        region_code=region_code,
        max_results=max_results,
        order="relevance"  # relevance, date, rating, viewCount
    )

    # 댓글 수집 (선택사항)
    if video_ids:
        comments_data = analyzer.get_comprehensive_comments(
            video_ids=video_ids,
            max_comments_per_video=50
        )

    return video_data, comments_data
```

### API 파라미터 설명

**search.list API**
- `q`: 검색 키워드 (필수)
- `maxResults`: 결과 수 (최대 50, 기본값 5)
- `regionCode`: 지역 코드 (예: US, KR, JP)
- `pageToken`: 페이지네이션 토큰 (nextPageToken, prevPageToken)
- `order`: 정렬 순서
  - `relevance`: 관련도 순 (기본값)
  - `date`: 최신순
  - `rating`: 평점순
  - `viewCount`: 조회수순
- `publishedAfter`: 게시 날짜 필터 (ISO 8601, 예: 2025-01-01T00:00:00Z)

**videos.list API**
- `part`: 가져올 정보 부분
  - `snippet`: 기본 정보 (제목, 설명, 썸네일 등)
  - `statistics`: 통계 (조회수, 좋아요, 댓글 수)
  - `contentDetails`: 콘텐츠 상세 (길이, 화질 등)
  - `status`: 상태 (공개 여부, 업로드 상태)
  - `topicDetails`: 주제 정보
  - `recordingDetails`: 녹화 정보
- `id`: 비디오 ID (최대 50개, 쉼표로 구분)

**channels.list API**
- `part`: 가져올 정보 부분
  - `snippet`: 채널 기본 정보
  - `statistics`: 채널 통계
  - `brandingSettings`: 브랜딩 설정
- `id`: 채널 ID (최대 50개, 쉼표로 구분)

**commentThreads.list API**
- `part`: `snippet`, `replies`
- `videoId`: 비디오 ID
- `maxResults`: 최대 100
- `order`: `time` (시간순), `relevance` (관련도순)

### 저장 형식 예시
```json
{
  "video_id": "dQw4w9WgXcQ",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "collected_at": "2025-10-12T11:09:47Z",
  "search_keyword": "samsung galaxy review",
  "title": "Samsung Galaxy S25 Ultra Review",
  "description": "Comprehensive review of Samsung Galaxy S25 Ultra...",
  "published_at": "2025-01-25T10:00:00Z",
  "channel": {
    "channel_id": "UC1234567890",
    "channel_title": "Tech Reviewer",
    "subscriber_count": 1500000,
    "country": "US"
  },
  "metrics": {
    "view_count": 250000,
    "like_count": 15000,
    "comment_count": 1200,
    "duration_seconds": 720,
    "definition": "hd"
  },
  "content": {
    "tags": ["samsung", "galaxy", "s25", "review", "tech"],
    "category_id": "28",
    "thumbnail_high": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
  }
}
```

---

## API 응답 구조 요약

```
YouTube Video Object
├── Search Info (video_id, keyword, region, collected_at)
├── Basic Info (snippet)
│   ├── Title & Description
│   ├── Published Date
│   ├── Category & Tags
│   ├── Language
│   └── Thumbnails (default, medium, high, standard, maxres)
├── Channel Info (snippet + statistics)
│   ├── Channel ID & Title
│   ├── Description & Custom URL
│   ├── Subscriber Count
│   ├── Video Count
│   └── Total View Count
├── Statistics
│   ├── View Count
│   ├── Like Count
│   ├── Comment Count
│   └── Favorite Count
├── Content Details
│   ├── Duration (seconds, ISO)
│   ├── Definition (sd, hd)
│   ├── Dimension (2d, 3d)
│   ├── Caption
│   └── Licensed Content
├── Status
│   ├── Upload Status
│   ├── Privacy Status
│   ├── Embeddable
│   └── Made For Kids
├── Topic Details
│   ├── Topic IDs
│   └── Topic Categories
└── Recording Details
    ├── Recording Date
    └── Location (latitude, longitude)

YouTube Comment Object
├── Comment ID & Type
├── Video ID & Parent ID
├── Author Info
│   ├── Display Name
│   ├── Channel ID
│   └── Profile Image URL
├── Comment Text
│   ├── Text Display (HTML)
│   └── Text Original (plain)
├── Engagement
│   ├── Like Count
│   └── Reply Count
└── Time Info
    ├── Published At
    └── Updated At
```

---

## API 할당량 관리

YouTube Data API v3는 일일 할당량이 10,000 units입니다.

### 비용 계산
- `search.list`: 100 units
- `videos.list`: 1 unit
- `channels.list`: 1 unit
- `commentThreads.list`: 1 unit

### 수집 시나리오 예시
1. 키워드 1개로 50개 비디오 검색: 100 units
2. 50개 비디오 상세 정보: 1 unit (배치 처리)
3. 50개 채널 정보: 1 unit (배치 처리)
4. 50개 비디오 댓글: 50 units
5. **총합**: 152 units

**하루 수집 가능량**: 약 65회 검색 (3,250개 비디오)

---

## 참고사항

1. **API 할당량**: 일일 10,000 units 제한 주의
2. **페이지네이션**: 검색 결과는 최대 50개씩, 총 100개까지 수집 가능
3. **배치 처리**: videos.list와 channels.list는 최대 50개 ID를 한번에 처리
4. **Rate Limiting**: API 호출 간 0.1초 지연 권장
5. **댓글 비활성화**: 일부 비디오는 댓글이 비활성화되어 있음
6. **썸네일 만료**: 썸네일 URL은 만료되지 않으므로 직접 저장 불필요
7. **날짜 필터**: publishedAfter 파라미터로 최근 데이터만 수집 권장 (기본 90일)
