# 🎬 YouTube 브랜드 감정 분석 도구

특정 키워드에 대한 YouTube 비디오와 댓글을 수집하여 브랜드 감정을 분석하는 도구입니다.

## 🚀 주요 기능

- **키워드 기반 비디오 검색**: 지역별로 관련 비디오 검색
- **메타데이터 수집**: 조회수, 좋아요, 댓글 수 등 통계 정보
- **댓글 감정 분석**: 긍정/부정/중립 감정 자동 분류
- **채널 정보 수집**: 구독자 수, 채널 통계 정보
- **브랜드 언급 추출**: 경쟁사 비교 언급 추출
- **8개 파일별 정리된 데이터 출력**

## 📦 설치 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
`config/settings.py`에서 YouTube API 키가 이미 설정되어 있습니다.

## 🎯 사용 방법

### 기본 사용법
```bash
python main.py "samsung tv"
```

### 고급 옵션
```bash
python main.py "samsung tv" --regions US KR JP --max-results 100
```

### 파라미터 설명
- `keyword`: 분석할 키워드 (필수)
- `--regions`: 분석할 지역 코드 (기본값: US KR)
- `--max-results`: 지역당 최대 비디오 수 (기본값: 50)

## 📊 출력 파일 구조

분석 완료 후 `data/` 폴더에 다음 8개 파일이 생성됩니다:

| 파일명 | 설명 | 주요 컬럼 |
|--------|------|-----------|
| `01_video_metadata_*.csv` | 비디오 기본 정보 | 제목, 설명, 채널명, 업로드일 |
| `02_video_statistics_*.csv` | 비디오 통계 정보 | 조회수, 좋아요, 댓글수, 길이 |
| `03_channel_info_*.csv` | 채널 정보 | 구독자수, 총 조회수, 비디오수 |
| `04_comments_raw_*.csv` | 원본 댓글 데이터 | 댓글 텍스트, 작성자, 좋아요수 |
| `05_comments_sentiment_*.csv` | 댓글 감정 분석 | 감정점수, 카테고리, 브랜드언급 |
| `06_trend_analysis_*.csv` | 비디오별 감정 요약 | 긍정비율, 부정비율, 평균감정 |
| `07_keyword_mentions_*.csv` | 키워드 언급 분석 | (향후 구현) |
| `08_competitor_comparison_*.csv` | 경쟁사 비교 분석 | (향후 구현) |

## 📈 분석 지표

### 감정 분석 지표
- **감정 점수**: -1 (매우 부정) ~ +1 (매우 긍정)
- **감정 카테고리**: positive, negative, neutral
- **주관성 점수**: 0 (객관적) ~ 1 (주관적)

### 비디오 통계
- 조회수, 좋아요, 댓글수
- 비디오 길이, 업로드 시간
- 채널 구독자 수

### 브랜드 분석
- 브랜드 언급 빈도
- 경쟁사 비교 언급
- 긍정/부정 반응 비율

## 🎛️ 설정 변경

`config/settings.py`에서 다음 설정들을 변경할 수 있습니다:

```python
MAX_RESULTS_PER_SEARCH = 50        # 검색당 최대 결과 수
MAX_COMMENTS_PER_VIDEO = 100       # 비디오당 최대 댓글 수
SEARCH_REGIONS = ["US", "KR", "GB"] # 기본 검색 지역
SENTIMENT_THRESHOLD_POSITIVE = 0.1  # 긍정 판단 임계값
SENTIMENT_THRESHOLD_NEGATIVE = -0.1 # 부정 판단 임계값
```

## 📝 사용 예시

### 삼성 TV 분석
```bash
python main.py "samsung tv"
```

### 아이폰 분석 (다지역)
```bash
python main.py "iphone review" --regions US KR JP CN --max-results 30
```

### LG 냉장고 분석
```bash
python main.py "lg refrigerator" --regions US --max-results 20
```

## ⚠️ 주의사항

### API 제한
- **일일 할당량**: 10,000 units
- **권장**: 키워드당 50개 미만 비디오
- **비용**: 초과 시 유료 ($0.05/1,000 units)

### 법적 고려사항
- 개인정보보호법 준수
- YouTube 이용약관 준수
- 상업적 이용 시 추가 승인 필요

## 🛠️ 기술 스택

- **API**: YouTube Data API v3
- **언어**: Python 3.8+
- **주요 라이브러리**: 
  - google-api-python-client (YouTube API)
  - textblob (감정 분석)
  - pandas (데이터 처리)
  - streamlit (대시보드, 향후)

## 📞 문제 해결

### 일반적인 오류

1. **API 키 오류**
   - `config/settings.py`에서 올바른 API 키 확인

2. **할당량 초과**
   - `--max-results` 값을 줄여서 재시도

3. **지역 코드 오류**
   - 올바른 ISO 국가 코드 사용 (US, KR, JP 등)

### 로그 확인
프로그램 실행 중 실시간 진행상황이 출력됩니다.

## 🔮 향후 계획

- [ ] Streamlit 대시보드 추가
- [ ] 실시간 감정 트렌드 추적
- [ ] TikTok, Instagram API 통합
- [ ] 경쟁사 자동 비교 분석
- [ ] 알림 시스템 (급격한 감정 변화 감지)

## 📄 라이선스

이 프로젝트는 브랜드 모니터링 및 시장 조사 목적으로 제작되었습니다.