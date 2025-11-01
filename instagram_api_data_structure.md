# Instagram API 데이터 구조 분석

## 전체 필드 목록 (Complete Field List)

| 인덱스 | 필드 구분 | 필드명 | 타입 | 설명 | 수집 필요 |
|--------|-----------|--------|------|------|----------|
| 1 | 게시물 기본 정보 | `pk` | string | 게시물 고유 식별자 (Primary Key) | 필수 |
| 2 | 게시물 기본 정보 | `id` | string | 게시물 전체 ID (pk_userid 형식) | 필수 |
| 3 | 게시물 기본 정보 | `code` | string | 게시물 단축 코드 (instagram.com/p/{code} URL 생성용) | 필수 |
| 4 | 게시물 기본 정보 | `taken_at` | string | 게시 시간 (ISO 8601 형식) | 필수 |
| 5 | 게시물 기본 정보 | `taken_at_ts` | integer | 게시 시간 (Unix Timestamp) | 필수 |
| 6 | 게시물 기본 정보 | `media_type` | integer | 미디어 타입 (1=이미지, 2=비디오, 8=캐러셀) | 필수 |
| 7 | 게시물 기본 정보 | `product_type` | string | 제품 타입 (feed, reels, igtv, clips 등) | 권장 |
| 8 | 게시물 기본 정보 | `title` | string | 게시물 제목 | 권장 |
| 9 | 미디어 정보 | `thumbnail_url` | string | 썸네일 이미지 URL | 필수 |
| 10 | 미디어 정보 | `image_versions` | array | 다양한 해상도의 이미지 배열 | 필수 |
| 11 | 미디어 정보 | `image_versions[].width` | integer | 이미지 너비 (픽셀) | 권장 |
| 12 | 미디어 정보 | `image_versions[].height` | integer | 이미지 높이 (픽셀) | 권장 |
| 13 | 미디어 정보 | `image_versions[].url` | string | 이미지 다운로드 URL | 필수 |
| 14 | 미디어 정보 | `image_versions[].scans_profile` | string | 스캔 프로필 (e35 등) | 불필요 |
| 15 | 미디어 정보 | `image_versions[].estimated_scans_sizes` | array | 예상 스캔 크기 배열 | 불필요 |
| 16 | 미디어 정보 | `image_versions[].is_spatial_image` | boolean | 공간 이미지 여부 | 불필요 |
| 17 | 미디어 정보 | `video_url` | string/null | 비디오 URL (비디오 타입인 경우) | 필수 |
| 18 | 미디어 정보 | `video_duration` | integer | 비디오 길이 (초, 0=이미지) | 권장 |
| 19 | 미디어 정보 | `video_versions` | array | 다양한 해상도의 비디오 배열 | 권장 |
| 20 | 미디어 정보 | `video_dash_manifest` | string | DASH 매니페스트 (스트리밍 정보) | 불필요 |
| 21 | 사용자 정보 | `user` | object | 사용자 정보 객체 | 필수 |
| 22 | 사용자 정보 | `user.pk` | string | 사용자 고유 ID | 필수 |
| 23 | 사용자 정보 | `user.id` | string | 사용자 ID (pk와 동일) | 불필요 |
| 24 | 사용자 정보 | `user.username` | string | 사용자명 (아이디) | 필수 |
| 25 | 사용자 정보 | `user.full_name` | string | 전체 이름 (비즈니스명) | 필수 |
| 26 | 사용자 정보 | `user.profile_pic_url` | string | 프로필 사진 URL (150x150) | 권장 |
| 27 | 사용자 정보 | `user.profile_pic_url_hd` | string/null | 고화질 프로필 사진 URL | 불필요 |
| 28 | 사용자 정보 | `user.is_private` | boolean | 비공개 계정 여부 | 권장 |
| 29 | 사용자 정보 | `user.is_verified` | boolean | 인증 배지 여부 (파란색 체크) | 필수 |
| 30 | 인게이지먼트 지표 | `like_count` | integer | 좋아요 수 | 필수 |
| 31 | 인게이지먼트 지표 | `comment_count` | integer | 댓글 수 | 필수 |
| 32 | 인게이지먼트 지표 | `play_count` | integer | 재생 수 (비디오) | 필수 |
| 33 | 인게이지먼트 지표 | `view_count` | integer | 조회 수 | 필수 |
| 34 | 인게이지먼트 지표 | `has_liked` | boolean | 현재 사용자의 좋아요 여부 | 불필요 |
| 35 | 인게이지먼트 지표 | `like_and_view_counts_disabled` | boolean | 좋아요/조회수 숨김 여부 | 권장 |
| 36 | 콘텐츠 정보 | `caption_text` | string | 게시물 본문/캡션 텍스트 | 필수 |
| 37 | 콘텐츠 정보 | `accessibility_caption` | string/null | 접근성 설명 (AI 자동 생성) | 권장 |
| 38 | 콘텐츠 정보 | `usertags` | array | 게시물에 태그된 사용자 목록 | 권장 |
| 39 | 콘텐츠 정보 | `sponsor_tags` | array | 스폰서 태그 목록 | 필수 |
| 40 | 콘텐츠 정보 | `location` | object/null | 위치 정보 (장소 이름, 좌표 등) | 필수 |
| 41 | 콘텐츠 정보 | `comments_disabled` | boolean | 댓글 비활성화 여부 | 권장 |
| 42 | 비즈니스/광고 | `is_paid_partnership` | boolean | 유료 파트너십(광고) 여부 | 필수 |
| 43 | 비즈니스/광고 | `coauthor_producers` | array | 공동 제작자 목록 | 권장 |
| 44 | 추가 메타데이터 | `resources` | array | 추가 리소스 (캐러셀 게시물의 개별 미디어) | 권장 |
| 45 | 추가 메타데이터 | `clips_metadata` | object | 릴스 메타데이터 (릴스 전용 정보) | 불필요 |

### 수집 필요 표시 설명
- **필수**: Samsung 브랜드 분석에 반드시 필요한 데이터
- **권장**: 심화 분석 시 유용한 데이터
- **불필요**: 수집하지 않아도 되는 데이터

---

## Samsung 브랜드 모니터링 핵심 수집 데이터

### 우선순위 1 (필수)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 게시물 ID | `id`, `code` | 고유 식별, URL 생성 |
| 게시 시간 | `taken_at`, `taken_at_ts` | 시계열 분석 |
| 사용자 정보 | `user.username`, `user.full_name` | 판매자/인플루언서 추적 |
| 캡션 | `caption_text` | 해시태그, 키워드 분석 |
| 인게이지먼트 | `like_count`, `comment_count` | 인기도 측정 |
| 미디어 URL | `thumbnail_url`, `image_versions[0].url` | 이미지 수집 |

### 우선순위 2 (권장)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 미디어 타입 | `media_type`, `product_type` | 콘텐츠 분류 |
| 위치 정보 | `location` | 지역별 트렌드 |
| 광고 여부 | `is_paid_partnership` | 광고/유기적 게시물 구분 |
| 태그 정보 | `usertags`, `sponsor_tags` | 협업 네트워크 |

### 우선순위 3 (참고)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 프로필 사진 | `user.profile_pic_url` | 사용자 프로필 저장 |
| 인증 여부 | `user.is_verified` | 인플루언서 필터링 |
| 재생 수 | `play_count`, `view_count` | 비디오 성과 분석 |

---

## 데이터 수집 전략

### 해시태그 기반 수집
```python
# 추천 Samsung 해시태그
samsung_hashtags = [
    "#samsung",
    "#samsungtv",
    "#samsunggalaxy",
    "#samsungphone",
    "#samsungelectronics",
    "#galaxys25",
    "#갤럭시",
    "#삼성전자"
]
```

### 수집 주기
- **실시간 모니터링:** 1시간마다
- **일일 수집:** 하루 1회 (자정)
- **주간 분석:** 매주 월요일

### 저장 형식
```json
{
  "post_id": "3740857427222934039",
  "post_url": "https://instagram.com/p/DPqMgKZATIX",
  "collected_at": "2025-10-12T00:00:00Z",
  "user": {
    "username": "homeessentials.ghana",
    "full_name": "Home Essentials Ghana"
  },
  "metrics": {
    "likes": 4,
    "comments": 0,
    "engagement_rate": 0.0
  },
  "content": {
    "caption": "#samsung #samsungtv",
    "media_type": "image",
    "media_url": "https://..."
  }
}
```

---

## API 응답 구조 요약

```
Instagram Post Object
├── Basic Info (id, code, taken_at)
├── Media
│   ├── Images (image_versions[])
│   └── Videos (video_url, video_versions[])
├── User
│   ├── Profile (username, full_name)
│   └── Status (is_verified, is_private)
├── Engagement
│   ├── Counts (like_count, comment_count)
│   └── Flags (has_liked)
├── Content
│   ├── Text (caption_text)
│   ├── Tags (usertags, sponsor_tags)
│   └── Location (location)
└── Business
    ├── Partnership (is_paid_partnership)
    └── Coauthors (coauthor_producers[])
```

---

## 참고사항

1. **URL 만료:** CDN URL은 일정 시간 후 만료될 수 있으므로 즉시 다운로드 권장
2. **Rate Limiting:** API 호출 제한 준수 필요
3. **개인정보:** 사용자 정보 수집 시 개인정보보호법 준수
4. **저작권:** 이미지/비디오 사용 시 저작권 주의
