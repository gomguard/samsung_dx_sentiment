# TikTok API 데이터 구조 분석

## 전체 필드 목록 (Complete Field List)

| 인덱스 | 필드 구분 | 필드명 | 타입 | 설명 | 수집 필요 |
|--------|-----------|--------|------|------|----------|
| 1 | API 응답 메타 | `status_code` | integer | API 응답 상태 코드 (0=성공) | 필수 |
| 2 | API 응답 메타 | `cursor` | integer | 다음 페이지 커서 (페이지네이션용) | 필수 |
| 3 | API 응답 메타 | `has_more` | integer | 추가 결과 존재 여부 (1=있음, 0=없음) | 필수 |
| 4 | API 응답 메타 | `qc` | string | 쿼리 컨텍스트 | 불필요 |
| 5 | 검색 결과 항목 | `data` | array | 검색 결과 배열 (각 항목은 비디오 객체) | 필수 |
| 6 | 검색 결과 항목 | `data[].type` | integer | 항목 타입 (1=일반 비디오) | 권장 |
| 7 | 비디오 기본 정보 | `item` | object | 비디오 아이템 객체 | 필수 |
| 8 | 비디오 기본 정보 | `item.id` | string | 비디오 고유 ID | 필수 |
| 9 | 비디오 기본 정보 | `item.desc` | string | 비디오 설명/캡션 (해시태그 포함) | 필수 |
| 10 | 비디오 기본 정보 | `item.createTime` | integer | 생성 시간 (Unix Timestamp) | 필수 |
| 11 | 비디오 상세 정보 | `item.video` | object | 비디오 상세 정보 객체 | 필수 |
| 12 | 비디오 상세 정보 | `item.video.id` | string | 비디오 ID (item.id와 동일) | 불필요 |
| 13 | 비디오 상세 정보 | `item.video.height` | integer | 비디오 높이 (픽셀) | 권장 |
| 14 | 비디오 상세 정보 | `item.video.width` | integer | 비디오 너비 (픽셀) | 권장 |
| 15 | 비디오 상세 정보 | `item.video.duration` | integer | 비디오 길이 (초) | 필수 |
| 16 | 비디오 상세 정보 | `item.video.ratio` | string | 화면 비율 (540p, 720p, 1080p 등) | 권장 |
| 17 | 비디오 상세 정보 | `item.video.cover` | string | 커버 이미지 URL | 필수 |
| 18 | 비디오 상세 정보 | `item.video.originCover` | string | 원본 커버 이미지 URL | 권장 |
| 19 | 비디오 상세 정보 | `item.video.dynamicCover` | string | 동적 커버 이미지 URL (움짤) | 권장 |
| 20 | 비디오 상세 정보 | `item.video.playAddr` | string | 비디오 재생 URL | 필수 |
| 21 | 비디오 상세 정보 | `item.video.downloadAddr` | string | 비디오 다운로드 URL | 필수 |
| 22 | 비디오 상세 정보 | `item.video.bitrate` | integer | 비트레이트 (bps) | 권장 |
| 23 | 비디오 상세 정보 | `item.video.encodedType` | string | 인코딩 타입 (normal 등) | 불필요 |
| 24 | 비디오 상세 정보 | `item.video.format` | string | 비디오 포맷 (mp4 등) | 권장 |
| 25 | 비디오 상세 정보 | `item.video.videoQuality` | string | 비디오 품질 (normal, high 등) | 권장 |
| 26 | 비디오 상세 정보 | `item.video.codecType` | string | 코덱 타입 (h264, h265 등) | 불필요 |
| 27 | 비디오 상세 정보 | `item.video.definition` | string | 해상도 정의 (540p, 720p, 1080p) | 권장 |
| 28 | 비디오 상세 정보 | `item.video.size` | integer | 비디오 파일 크기 (바이트) | 권장 |
| 29 | 비디오 상세 정보 | `item.video.videoID` | string | 비디오 파일 ID | 불필요 |
| 30 | 비디오 품질 옵션 | `item.video.bitrateInfo` | array | 다양한 품질의 비디오 정보 배열 | 권장 |
| 31 | 비디오 품질 옵션 | `item.video.bitrateInfo[].GearName` | string | 품질 프리셋 이름 (normal_540_0, adapt_1080_1 등) | 권장 |
| 32 | 비디오 품질 옵션 | `item.video.bitrateInfo[].Bitrate` | integer | 해당 품질의 비트레이트 | 권장 |
| 33 | 비디오 품질 옵션 | `item.video.bitrateInfo[].QualityType` | integer | 품질 타입 코드 | 불필요 |
| 34 | 비디오 품질 옵션 | `item.video.bitrateInfo[].CodecType` | string | 코덱 타입 (h264, h265_hvc1) | 불필요 |
| 35 | 비디오 품질 옵션 | `item.video.bitrateInfo[].PlayAddr` | object | 재생 주소 정보 | 권장 |
| 36 | 비디오 품질 옵션 | `item.video.bitrateInfo[].PlayAddr.Uri` | string | 비디오 URI | 불필요 |
| 37 | 비디오 품질 옵션 | `item.video.bitrateInfo[].PlayAddr.UrlList` | array | 다운로드 URL 목록 (CDN 서버별) | 권장 |
| 38 | 비디오 품질 옵션 | `item.video.bitrateInfo[].PlayAddr.DataSize` | integer | 파일 크기 (바이트) | 불필요 |
| 39 | 비디오 품질 옵션 | `item.video.bitrateInfo[].PlayAddr.Width` | integer | 해당 품질의 너비 | 권장 |
| 40 | 비디오 품질 옵션 | `item.video.bitrateInfo[].PlayAddr.Height` | integer | 해당 품질의 높이 | 권장 |
| 41 | 비디오 품질 옵션 | `item.video.bitrateInfo[].PlayAddr.FileHash` | string | 파일 해시값 | 불필요 |
| 42 | 비디오 썸네일 | `item.video.zoomCover` | object | 다양한 크기의 줌 커버 이미지 | 권장 |
| 43 | 비디오 썸네일 | `item.video.zoomCover.240` | string | 240x240 커버 이미지 URL | 불필요 |
| 44 | 비디오 썸네일 | `item.video.zoomCover.480` | string | 480x480 커버 이미지 URL | 권장 |
| 45 | 비디오 썸네일 | `item.video.zoomCover.720` | string | 720x720 커버 이미지 URL | 권장 |
| 46 | 비디오 썸네일 | `item.video.zoomCover.960` | string | 960x960 커버 이미지 URL | 불필요 |
| 47 | 오디오 정보 | `item.video.volumeInfo` | object | 볼륨 정보 | 불필요 |
| 48 | 오디오 정보 | `item.video.volumeInfo.Loudness` | float | 라우드니스 (dB) | 불필요 |
| 49 | 오디오 정보 | `item.video.volumeInfo.Peak` | float | 피크 볼륨 | 불필요 |
| 50 | 자막 정보 | `item.video.claInfo` | object | 자막 관련 정보 | 불필요 |
| 51 | 자막 정보 | `item.video.claInfo.hasOriginalAudio` | boolean | 원본 오디오 포함 여부 | 불필요 |
| 52 | 자막 정보 | `item.video.claInfo.enableAutoCaption` | boolean | 자동 자막 활성화 여부 | 불필요 |
| 53 | 자막 정보 | `item.video.claInfo.noCaptionReason` | integer | 자막 없는 이유 코드 | 불필요 |
| 54 | 작성자 정보 | `item.author` | object | 작성자 정보 객체 | 필수 |
| 55 | 작성자 정보 | `item.author.id` | string | 작성자 고유 ID | 필수 |
| 56 | 작성자 정보 | `item.author.uniqueId` | string | 작성자 고유 아이디 (사용자명) | 필수 |
| 57 | 작성자 정보 | `item.author.nickname` | string | 작성자 닉네임 (표시 이름) | 필수 |
| 58 | 작성자 정보 | `item.author.signature` | string | 작성자 프로필 설명 | 권장 |
| 59 | 작성자 정보 | `item.author.verified` | boolean | 인증 계정 여부 | 필수 |
| 60 | 작성자 정보 | `item.author.secUid` | string | 보안 UID | 불필요 |
| 61 | 작성자 정보 | `item.author.secret` | boolean | 비밀 계정 여부 | 권장 |
| 62 | 작성자 정보 | `item.author.ftc` | boolean | FTC 광고 공개 여부 | 필수 |
| 63 | 작성자 정보 | `item.author.privateAccount` | boolean | 비공개 계정 여부 | 권장 |
| 64 | 작성자 아바타 | `item.author.avatarThumb` | string | 작성자 아바타 썸네일 URL | 권장 |
| 65 | 작성자 아바타 | `item.author.avatarMedium` | string | 작성자 아바타 중간 크기 URL | 권장 |
| 66 | 작성자 아바타 | `item.author.avatarLarger` | string | 작성자 아바타 큰 크기 URL | 불필요 |
| 67 | 작성자 설정 | `item.author.relation` | integer | 팔로우 관계 (0=없음, 1=팔로잉, 2=팔로워) | 불필요 |
| 68 | 작성자 설정 | `item.author.commentSetting` | integer | 댓글 설정 | 불필요 |
| 69 | 작성자 설정 | `item.author.duetSetting` | integer | 듀엣 설정 | 불필요 |
| 70 | 작성자 설정 | `item.author.stitchSetting` | integer | 스티치 설정 | 불필요 |
| 71 | 작성자 설정 | `item.author.downloadSetting` | integer | 다운로드 설정 | 불필요 |
| 72 | 음악 정보 | `item.music` | object | 음악 정보 객체 | 권장 |
| 73 | 음악 정보 | `item.music.id` | string | 음악 ID | 권장 |
| 74 | 음악 정보 | `item.music.title` | string | 음악 제목 | 권장 |
| 75 | 음악 정보 | `item.music.playUrl` | string | 음악 재생 URL | 불필요 |
| 76 | 음악 정보 | `item.music.authorName` | string | 음악 작가명 | 권장 |
| 77 | 음악 정보 | `item.music.original` | boolean | 오리지널 사운드 여부 | 권장 |
| 78 | 음악 정보 | `item.music.duration` | integer | 음악 길이 (초) | 불필요 |
| 79 | 음악 정보 | `item.music.isCopyrighted` | boolean | 저작권 보호 음악 여부 | 권장 |
| 80 | 음악 커버 | `item.music.coverThumb` | string | 음악 커버 썸네일 URL | 불필요 |
| 81 | 음악 커버 | `item.music.coverMedium` | string | 음악 커버 중간 크기 URL | 불필요 |
| 82 | 음악 커버 | `item.music.coverLarge` | string | 음악 커버 큰 크기 URL | 불필요 |
| 83 | 해시태그 정보 | `item.challenges` | array | 해시태그(챌린지) 배열 | 필수 |
| 84 | 해시태그 정보 | `item.challenges[].id` | string | 해시태그 ID | 필수 |
| 85 | 해시태그 정보 | `item.challenges[].title` | string | 해시태그 제목 | 필수 |
| 86 | 해시태그 정보 | `item.challenges[].desc` | string | 해시태그 설명 | 권장 |
| 87 | 해시태그 정보 | `item.challenges[].profileThumb` | string | 해시태그 프로필 썸네일 | 불필요 |
| 88 | 해시태그 정보 | `item.challenges[].profileMedium` | string | 해시태그 프로필 중간 크기 | 불필요 |
| 89 | 해시태그 정보 | `item.challenges[].profileLarger` | string | 해시태그 프로필 큰 크기 | 불필요 |
| 90 | 인게이지먼트 지표 | `item.stats` | object | 통계 정보 객체 | 필수 |
| 91 | 인게이지먼트 지표 | `item.stats.diggCount` | integer | 좋아요 수 | 필수 |
| 92 | 인게이지먼트 지표 | `item.stats.shareCount` | integer | 공유 수 | 필수 |
| 93 | 인게이지먼트 지표 | `item.stats.commentCount` | integer | 댓글 수 | 필수 |
| 94 | 인게이지먼트 지표 | `item.stats.playCount` | integer | 재생 수 | 필수 |
| 95 | 인게이지먼트 지표 | `item.stats.collectCount` | integer | 즐겨찾기/저장 수 | 필수 |
| 96 | 인게이지먼트 지표 V2 | `item.statsV2` | object | 통계 정보 V2 (문자열 형식) | 권장 |
| 97 | 인게이지먼트 지표 V2 | `item.statsV2.diggCount` | string | 좋아요 수 (문자열) | 권장 |
| 98 | 인게이지먼트 지표 V2 | `item.statsV2.shareCount` | string | 공유 수 (문자열) | 권장 |
| 99 | 인게이지먼트 지표 V2 | `item.statsV2.commentCount` | string | 댓글 수 (문자열) | 권장 |
| 100 | 인게이지먼트 지표 V2 | `item.statsV2.playCount` | string | 재생 수 (문자열) | 권장 |
| 101 | 인게이지먼트 지표 V2 | `item.statsV2.collectCount` | string | 즐겨찾기 수 (문자열) | 권장 |
| 102 | 인게이지먼트 지표 V2 | `item.statsV2.repostCount` | string | 리포스트 수 (문자열) | 권장 |
| 103 | 작성자 통계 | `item.authorStats` | object | 작성자 통계 정보 | 필수 |
| 104 | 작성자 통계 | `item.authorStats.followingCount` | integer | 팔로잉 수 | 권장 |
| 105 | 작성자 통계 | `item.authorStats.followerCount` | integer | 팔로워 수 | 필수 |
| 106 | 작성자 통계 | `item.authorStats.heartCount` | integer | 총 받은 좋아요 수 | 필수 |
| 107 | 작성자 통계 | `item.authorStats.videoCount` | integer | 작성한 비디오 수 | 필수 |
| 108 | 작성자 통계 | `item.authorStats.diggCount` | integer | 작성자가 좋아요한 수 | 불필요 |
| 109 | 작성자 통계 | `item.authorStats.friendCount` | integer | 친구 수 | 불필요 |
| 110 | 작성자 통계 V2 | `item.authorStatsV2` | object | 작성자 통계 V2 (문자열 형식) | 권장 |
| 111 | 작성자 통계 V2 | `item.authorStatsV2.followingCount` | string | 팔로잉 수 (문자열) | 권장 |
| 112 | 작성자 통계 V2 | `item.authorStatsV2.followerCount` | string | 팔로워 수 (문자열) | 권장 |
| 113 | 작성자 통계 V2 | `item.authorStatsV2.heartCount` | string | 총 받은 좋아요 수 (문자열) | 권장 |
| 114 | 작성자 통계 V2 | `item.authorStatsV2.videoCount` | string | 작성한 비디오 수 (문자열) | 권장 |
| 115 | 작성자 통계 V2 | `item.authorStatsV2.diggCount` | string | 작성자가 좋아요한 수 (문자열) | 불필요 |
| 116 | 텍스트 추출 정보 | `item.textExtra` | array | 텍스트 내 추출된 해시태그/멘션 정보 | 필수 |
| 117 | 텍스트 추출 정보 | `item.textExtra[].start` | integer | 텍스트 시작 위치 | 불필요 |
| 118 | 텍스트 추출 정보 | `item.textExtra[].end` | integer | 텍스트 끝 위치 | 불필요 |
| 119 | 텍스트 추출 정보 | `item.textExtra[].hashtagName` | string | 해시태그 이름 | 필수 |
| 120 | 텍스트 추출 정보 | `item.textExtra[].hashtagId` | string | 해시태그 ID | 필수 |
| 121 | 텍스트 추출 정보 | `item.textExtra[].type` | integer | 타입 (1=해시태그, 0=멘션) | 권장 |
| 122 | 텍스트 추출 정보 | `item.textExtra[].isCommerce` | boolean | 커머스 관련 여부 | 필수 |
| 123 | 비디오 설정 | `item.originalItem` | boolean | 원본 아이템 여부 | 권장 |
| 124 | 비디오 설정 | `item.officalItem` | boolean | 공식 아이템 여부 | 권장 |
| 125 | 비디오 설정 | `item.secret` | boolean | 비밀 게시물 여부 | 권장 |
| 126 | 비디오 설정 | `item.forFriend` | boolean | 친구 전용 여부 | 권장 |
| 127 | 비디오 설정 | `item.privateItem` | boolean | 비공개 아이템 여부 | 권장 |
| 128 | 비디오 설정 | `item.isAd` | boolean | 광고 여부 | 필수 |
| 129 | 상호작용 설정 | `item.digged` | boolean | 현재 사용자가 좋아요 했는지 | 불필요 |
| 130 | 상호작용 설정 | `item.collected` | boolean | 현재 사용자가 저장했는지 | 불필요 |
| 131 | 상호작용 설정 | `item.duetEnabled` | boolean | 듀엣 활성화 여부 | 불필요 |
| 132 | 상호작용 설정 | `item.stitchEnabled` | boolean | 스티치 활성화 여부 | 불필요 |
| 133 | 상호작용 설정 | `item.shareEnabled` | boolean | 공유 활성화 여부 | 불필요 |
| 134 | 상호작용 설정 | `item.itemCommentStatus` | integer | 댓글 상태 | 권장 |
| 135 | 상호작용 설정 | `item.duetDisplay` | integer | 듀엣 표시 설정 | 불필요 |
| 136 | 상호작용 설정 | `item.stitchDisplay` | integer | 스티치 표시 설정 | 불필요 |
| 137 | 스티커/효과 | `item.stickersOnItem` | array | 비디오에 적용된 스티커 목록 | 권장 |
| 138 | 스티커/효과 | `item.stickersOnItem[].stickerType` | integer | 스티커 타입 | 권장 |
| 139 | 스티커/효과 | `item.stickersOnItem[].stickerText` | array | 스티커 텍스트 배열 | 권장 |
| 140 | 콘텐츠 정보 | `item.contents` | array | 콘텐츠 배열 | 불필요 |
| 141 | 콘텐츠 정보 | `item.contents[].desc` | string | 콘텐츠 설명 | 불필요 |
| 142 | 콘텐츠 정보 | `item.contents[].textExtra` | array | 콘텐츠 내 텍스트 추출 정보 | 불필요 |
| 143 | 추천 검색어 | `item.videoSuggestWordsList` | object | 비디오 추천 검색어 목록 | 권장 |
| 144 | 추천 검색어 | `item.videoSuggestWordsList.video_suggest_words_struct` | array | 추천 검색어 구조 배열 | 권장 |
| 145 | 추천 검색어 | `item.videoSuggestWordsList.video_suggest_words_struct[].words` | array | 추천 단어 목록 | 권장 |
| 146 | 추천 검색어 | `item.videoSuggestWordsList.video_suggest_words_struct[].scene` | string | 표시 위치 (comment_top, feed_bar 등) | 불필요 |
| 147 | AI 정보 | `item.AIGCDescription` | string | AI 생성 콘텐츠 설명 | 권장 |
| 148 | 카테고리 정보 | `item.CategoryType` | integer | 카테고리 타입 코드 | 권장 |
| 149 | 언어 정보 | `item.textLanguage` | string | 텍스트 언어 코드 (en, un 등) | 필수 |
| 150 | 언어 정보 | `item.textTranslatable` | boolean | 번역 가능 여부 | 불필요 |
| 151 | 기타 | `item.diversificationId` | integer | 다양화 ID | 불필요 |
| 152 | 기타 | `item.item_control` | object | 아이템 제어 설정 | 불필요 |
| 153 | 기타 | `item.item_control.can_repost` | boolean | 리포스트 가능 여부 | 불필요 |
| 154 | 기타 | `common` | object | 공통 정보 | 불필요 |
| 155 | 기타 | `common.doc_id_str` | string | 문서 ID 문자열 | 불필요 |
| 156 | 로그 정보 | `extra` | object | 추가 정보 객체 | 불필요 |
| 157 | 로그 정보 | `extra.now` | integer | 현재 타임스탬프 (밀리초) | 불필요 |
| 158 | 로그 정보 | `extra.logid` | string | 로그 ID | 불필요 |
| 159 | 로그 정보 | `extra.search_request_id` | string | 검색 요청 ID | 불필요 |
| 160 | 페이지네이션 | `log_pb` | object | 로그 프로토콜 버퍼 | 필수 |
| 161 | 페이지네이션 | `log_pb.impr_id` | string | 노출 ID (다음 요청의 search_id로 사용) | 필수 |
| 162 | 광고 정보 | `ad_info` | object | 광고 정보 | 권장 |
| 163 | 기타 설정 | `global_doodle_config` | object | 글로벌 두들 설정 | 불필요 |
| 164 | 기타 설정 | `backtrace` | string | 백트레이스 정보 | 불필요 |

### 수집 필요 표시 설명
- **필수**: Samsung 브랜드 분석에 반드시 필요한 데이터
- **권장**: 심화 분석 시 유용한 데이터
- **불필요**: 수집하지 않아도 되는 데이터

---

## Samsung 브랜드 모니터링 핵심 수집 데이터

### 우선순위 1 (필수)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 비디오 ID | `item.id` | 고유 식별 |
| 비디오 URL | `item.video.playAddr` 또는 `downloadAddr` | 비디오 다운로드 |
| 생성 시간 | `item.createTime` | 시계열 분석 |
| 설명/캡션 | `item.desc` | 해시태그, 키워드 분석 |
| 작성자 정보 | `item.author.uniqueId`, `nickname` | 인플루언서 추적 |
| 재생 수 | `item.stats.playCount` | 인기도 측정 |
| 좋아요 수 | `item.stats.diggCount` | 인게이지먼트 측정 |
| 댓글 수 | `item.stats.commentCount` | 인게이지먼트 측정 |
| 공유 수 | `item.stats.shareCount` | 바이럴 정도 측정 |
| 해시태그 목록 | `item.challenges`, `textExtra` | 트렌드 분석 |

### 우선순위 2 (중요)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 커버 이미지 | `item.video.cover` | 썸네일 수집 |
| 비디오 품질 옵션 | `item.video.bitrateInfo` | 다양한 화질 다운로드 |
| 작성자 팔로워 | `item.authorStats.followerCount` | 인플루언서 영향력 분석 |
| 작성자 비디오 수 | `item.authorStats.videoCount` | 활동성 분석 |
| 음악 정보 | `item.music.title`, `authorName` | 트렌드 음악 파악 |
| 광고 여부 | `item.isAd` | 광고/유기적 콘텐츠 구분 |
| 인증 여부 | `item.author.verified` | 공식 계정 필터링 |

### 우선순위 3 (참고)

| 데이터 | 필드명 | 용도 |
|--------|--------|------|
| 비디오 길이 | `item.video.duration` | 콘텐츠 길이 분석 |
| 즐겨찾기 수 | `item.stats.collectCount` | 저장 가치 측정 |
| 스티커 정보 | `item.stickersOnItem` | 비디오 효과 분석 |
| 추천 검색어 | `item.videoSuggestWordsList` | 관련 키워드 발굴 |
| 언어 정보 | `item.textLanguage` | 지역별 분류 |

---

## 데이터 수집 전략

### 검색 키워드 기반 수집
```python
# 추천 Samsung 검색 키워드
samsung_keywords = [
    "samsung",
    "samsungtv",
    "samsung galaxy",
    "samsung phone",
    "galaxy s25",
    "samsung fold",
    "samsung flip"
]
```

### 페이지네이션 구현
```python
def collect_tiktok_videos(keyword):
    cursor = 0
    search_id = 0
    all_videos = []

    while True:
        response = api.get("/search", params={
            "keyword": keyword,
            "cursor": cursor,
            "search_id": search_id
        })

        # 비디오 데이터 수집
        for item in response["data"]:
            video_data = extract_video_info(item["item"])
            all_videos.append(video_data)

        # 더 이상 결과가 없으면 종료
        if response["has_more"] == 0:
            break

        # 다음 페이지 정보 업데이트
        cursor = response["cursor"]
        search_id = response["log_pb"]["impr_id"]

    return all_videos
```

### 저장 형식 예시
```json
{
  "video_id": "7509290776015179039",
  "video_url": "https://www.tiktok.com/@krossavvv/video/7509290776015179039",
  "download_url": "https://v16-webapp-prime.tiktok.com/video/...",
  "collected_at": "2025-10-12T11:09:47Z",
  "author": {
    "unique_id": "krossavvv",
    "nickname": "Krossav",
    "follower_count": 2285,
    "verified": false
  },
  "metrics": {
    "play_count": 7300000,
    "digg_count": 603100,
    "comment_count": 5126,
    "share_count": 36600,
    "engagement_rate": 8.79
  },
  "content": {
    "description": "#techtok #tech #samsung #tv #nostalgia",
    "hashtags": ["techtok", "tech", "samsung", "tv", "nostalgia"],
    "duration": 13,
    "create_time": 1748393019
  }
}
```

---

## API 응답 구조 요약

```
TikTok Search Response
├── status_code (0=성공)
├── cursor (다음 페이지)
├── has_more (더 있는지)
└── data[] (검색 결과 배열)
    ├── type (항목 타입)
    └── item
        ├── Basic Info (id, desc, createTime)
        ├── video
        │   ├── URLs (playAddr, downloadAddr)
        │   ├── Quality (bitrateInfo[])
        │   ├── Covers (cover, originCover, dynamicCover)
        │   └── Meta (duration, size, format, codec)
        ├── author
        │   ├── Profile (uniqueId, nickname, signature)
        │   ├── Avatar (avatarThumb, avatarMedium, avatarLarger)
        │   └── Status (verified, privateAccount)
        ├── music
        │   ├── Info (id, title, authorName)
        │   └── Audio (playUrl, duration)
        ├── challenges[] (해시태그 배열)
        ├── stats (인게이지먼트 지표)
        ├── authorStats (작성자 통계)
        └── textExtra[] (해시태그 추출 정보)
```

---

## 참고사항

1. **URL 만료:** 비디오 URL은 일정 시간 후 만료되므로 즉시 다운로드 권장
2. **Rate Limiting:** API 호출 제한 준수 필요
3. **페이지네이션:** `cursor`와 `search_id` 모두 필수로 사용
4. **통계 데이터:** `stats`와 `statsV2` 중 하나 선택 (V2는 문자열 형식)
5. **비디오 품질:** `bitrateInfo` 배열에서 원하는 화질 선택 가능 (540p, 720p, 1080p)
6. **해시태그 추출:** `challenges` 배열과 `textExtra` 배열 모두 확인 권장
