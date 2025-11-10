# Instagram Brand Analyzer

Instagram 데이터 수집 및 분석 파이프라인입니다.
YouTube와 동일한 구조로 키워드 기반 데이터 수집을 지원합니다.

## 프로젝트 구조

```
instagram_brand_analyzer/
├── collectors/           # 데이터 수집 모듈
│   ├── __init__.py
│   └── instagram_api.py  # Instagram API 클라이언트
├── analyzers/            # 데이터 분석 모듈
│   ├── __init__.py
│   └── sentiment.py      # 감정 분석
├── config/               # 설정 파일
│   ├── settings.py       # Instagram API 설정
│   └── db_manager.py     # PostgreSQL DB 관리자
├── data/                 # 수집된 데이터 저장
├── storage/              # 데이터 구조 문서
│   └── data_structure.txt
├── pipeline_instagram_analysis.py  # 통합 파이프라인
├── batch_collect.py      # 배치 수집 스크립트
├── manage_keywords.py    # 해시태그 관리 스크립트
├── create_database.py    # DB 테이블 생성
├── test_db.py            # DB 연결 테스트
├── requirements.txt      # Python 의존성
└── README.md
```

## 주요 기능

1. **Instagram 데이터 수집**
   - 해시태그 기반 게시물 검색
   - 게시물 댓글 수집
   - 작성자 정보 수집

2. **감정 분석**
   - TextBlob을 사용한 댓글 감정 분석
   - Positive/Negative/Neutral 분류

3. **데이터베이스 저장**
   - PostgreSQL 데이터베이스에 저장
   - 증분 업데이트 지원

4. **배치 처리**
   - 여러 해시태그 자동 처리
   - 수집 통계 관리

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. PostgreSQL 설정:
- `config/secrets.py`에서 데이터베이스 연결 정보 설정
- 데이터베이스 테이블 생성:
```bash
python create_database.py
```

3. Instagram API 설정:
- `config/settings.py`에서 API 토큰 설정
- API 토큰이 없으면 데모 모드로 실행됩니다

## 사용법

### 1. 단일 키워드 수집

```bash
python pipeline_instagram_analysis.py --keyword "Samsung TV" --max-posts 30
```

옵션:
- `--keyword`: 검색할 키워드 (필수, 예: "Samsung TV")
- `--max-posts`: 최대 게시물 수 (기본값: 30)
- `--max-comments`: 게시물당 최대 댓글 수 (기본값: 50)
- `--region`: 지역 코드 (기본값: US)
- `--no-sentiment`: 감정 분석 건너뛰기
- `--no-database`: DB 저장 건너뛰기

### 2. 키워드 관리

키워드 추가:
```bash
python manage_keywords.py add "Samsung TV" --max-posts 30 --max-comments 50
```

키워드 목록 보기:
```bash
python manage_keywords.py list
```

키워드 비활성화:
```bash
python manage_keywords.py deactivate "Samsung TV"
```

키워드 삭제:
```bash
python manage_keywords.py delete "Samsung TV"
```

### 3. 배치 수집

등록된 모든 활성 키워드에 대해 자동으로 데이터 수집:

```bash
python batch_collect.py
```

드라이런 (실제 수집 없이 확인만):
```bash
python batch_collect.py --dry-run
```

### 4. 데이터베이스 관리

연결 테스트:
```bash
python test_db.py
```

테이블 생성:
```bash
python create_database.py
```

## 데이터 구조

### instagram_keywords 테이블 (키워드 관리)
- keyword: 검색 키워드
- status: 활성/비활성 상태
- max_posts: 최대 게시물 수
- max_comments_per_post: 게시물당 최대 댓글 수
- region_code: 지역 코드
- last_collected_at: 마지막 수집 시간
- total_posts_collected: 총 수집된 게시물 수
- total_comments_collected: 총 수집된 댓글 수

### instagram_posts 테이블 (게시물 정보)
- post_id: 게시물 고유 ID (Primary Key)
- search_keyword: 검색 키워드
- author_username: 사용자명
- caption: 게시물 텍스트
- media_type: 미디어 타입 (IMAGE/VIDEO)
- like_count: 좋아요 수
- comment_count: 댓글 수
- play_count: 재생 수 (비디오)
- video_content_summary: OpenAI로 추출한 영상 내용
- comment_text_summary: OpenAI로 추출한 댓글 내용
- published_at: 게시 시간

### instagram_comments 테이블 (댓글 정보)
- comment_id: 댓글 ID (Primary Key)
- post_id: 게시물 ID (Foreign Key)
- comment_text: 댓글 내용
- author_username: 작성자 사용자명
- like_count: 좋아요 수
- sentiment: 감정 분석 결과
- sentiment_score: 감정 점수
- sentiment_label: 감정 라벨

자세한 내용은 `storage/data_structure.txt` 참조

## API 제약사항

Instagram API는 엄격한 속도 제한이 있습니다:
- Basic Display API: 200 requests/hour, 1000 requests/day
- Graph API: 200 requests/hour, 4800 requests/day

파이프라인에는 자동 속도 제한이 포함되어 있습니다:
- 요청 간 2초 대기
- 배치 수집 시 해시태그 간 30초 대기

## 참고사항

1. Instagram API 토큰이 없으면 자동으로 데모 모드로 전환됩니다
2. 데모 모드에서는 샘플 데이터가 생성됩니다
3. 모든 데이터는 PostgreSQL에 저장되어 분석에 사용할 수 있습니다
4. 증분 업데이트를 지원하여 중복 데이터를 방지합니다
