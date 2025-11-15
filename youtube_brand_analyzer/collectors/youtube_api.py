import os
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime, timedelta
import time
import re

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

class YouTubeAnalyzer:
    def __init__(self, api_keys=None):
        """
        YouTube API 클라이언트 초기화

        Args:
            api_keys (list): API 키 리스트 (None이면 YOUTUBE_API_KEYS 사용)
        """
        # API 키 리스트 초기화
        if api_keys is None:
            self.api_keys = YOUTUBE_API_KEYS if isinstance(YOUTUBE_API_KEYS, list) else [YOUTUBE_API_KEY]
        else:
            self.api_keys = api_keys if isinstance(api_keys, list) else [api_keys]

        self.current_key_index = 0
        self.api_key = self.api_keys[self.current_key_index]
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.api_key)
        self.request_count = 0

        print(f"YouTubeAnalyzer 초기화: {len(self.api_keys)}개 API 키 사용 가능")

    def _rotate_api_key(self):
        """
        다음 API 키로 로테이션

        Returns:
            bool: 로테이션 성공 여부 (더 이상 사용 가능한 키가 없으면 False)
        """
        if self.current_key_index >= len(self.api_keys) - 1:
            print(f"\n[ERROR] 모든 API 키의 할당량이 소진되었습니다 ({len(self.api_keys)}개 키 모두 사용)")
            return False

        self.current_key_index += 1
        self.api_key = self.api_keys[self.current_key_index]

        # YouTube 클라이언트 재생성
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.api_key)

        print(f"\n[KEY ROTATION] API 키 #{self.current_key_index + 1}로 전환됨 (잔여 키: {len(self.api_keys) - self.current_key_index - 1}개)")
        return True

    def _execute_with_retry(self, api_call_func, max_retries=3):
        """
        API 호출을 실행하고 quota exceeded 에러 시 자동으로 키 로테이션

        Args:
            api_call_func: 실행할 API 호출 함수
            max_retries: 최대 재시도 횟수 (다른 에러의 경우)

        Returns:
            API 응답 결과
        """
        retries = 0
        while retries < max_retries:
            try:
                return api_call_func()
            except HttpError as e:
                error_content = str(e.content) if hasattr(e, 'content') else str(e)

                # Quota exceeded 에러 확인
                if 'quotaExceeded' in error_content or 'quota' in error_content.lower():
                    print(f"\n[QUOTA EXCEEDED] API 할당량 초과 감지")
                    if self._rotate_api_key():
                        print(f"[RETRY] 새 API 키로 재시도...")
                        retries = 0  # 키 로테이션 성공 시 재시도 카운트 리셋
                        continue
                    else:
                        # 모든 키 소진
                        raise Exception("모든 API 키의 할당량이 소진되었습니다") from e
                else:
                    # 다른 에러는 재시도
                    retries += 1
                    if retries < max_retries:
                        print(f"\n[API ERROR] 에러 발생, 재시도 중... ({retries}/{max_retries})")
                        time.sleep(2)
                        continue
                    else:
                        raise

    def get_comprehensive_video_data(self, keyword, region_code="US", max_results=MAX_RESULTS_PER_SEARCH,
                                   published_after=None, order="viewCount",
                                   apply_quality_filter=True):
        """
        키워드로 비디오 검색 후 모든 정보를 한번에 수집

        Args:
            keyword: 검색 키워드
            region_code: 지역 코드
            max_results: 필터링 후 원하는 최대 비디오 수
            published_after: 게시 날짜 필터
            order: 정렬 순서 (viewCount, relevance, date 등)
            apply_quality_filter: True면 품질 필터 적용 (카테고리, 구독자, 참여율)

        Returns:
            (video_data, video_ids): 비디오 데이터 리스트와 비디오 ID 리스트
        """
        try:
            # 품질 필터 기준
            TARGET_CATEGORY = "28"  # Science & Technology
            TARGET_CHANNEL_COUNTRY = "US"  # US 채널만
            MIN_SUBSCRIBER_COUNT = 10000
            MIN_CHANNEL_TOTAL_VIEWS = 100000000  # 100M
            MIN_ENGAGEMENT_RATE = 2.0  # 2%

            BATCH_SIZE = 50  # 한번에 50개씩 수집

            filtered_videos = []
            filtered_video_ids = set()  # 중복 방지를 위한 ID 세트
            all_raw_videos = []  # 모든 수집 데이터 (필터링 전)
            all_collected_video_ids = set()  # 중복 체크를 위해 set으로 변경
            next_page_token = None
            total_api_calls = 0

            print(f"\n{'='*80}")
            if apply_quality_filter:
                print(f"품질 필터링 모드 활성화:")
                print(f"  - 채널 국가: {TARGET_CHANNEL_COUNTRY} (US 채널만)")
                print(f"  - 카테고리: {TARGET_CATEGORY} (Science & Technology)")
                print(f"  - 최소 구독자: {MIN_SUBSCRIBER_COUNT:,} OR 채널 총 조회수: {MIN_CHANNEL_TOTAL_VIEWS:,}")
                print(f"  - 최소 참여율: {MIN_ENGAGEMENT_RATE}%")
                print(f"  - 목표 비디오 수: {max_results}개")
                print(f"  - 배치 크기: {BATCH_SIZE}개씩 수집")
            else:
                print(f"일반 수집 모드 (필터링 없음)")
                print(f"  - 목표 비디오 수: {max_results}개")
            print(f"{'='*80}\n")

            batch_number = 0
            consecutive_empty_batches = 0  # 연속으로 새 비디오가 없는 배치 수 (중복만 나오는 경우)
            MAX_EMPTY_BATCHES = 3  # 3번 연속 중복만 나오면 중단

            # 필터링된 비디오가 max_results에 도달할 때까지 반복
            while len(filtered_videos) < max_results:
                batch_number += 1
                print(f"\n[배치 {batch_number}] {BATCH_SIZE}개 비디오 수집 중...")

                # 배치 시작 전 현재까지 수집된 비디오 ID 개수 기록 (중복 체크용)
                prev_collected_count = len(all_collected_video_ids)

                # 1단계: 비디오 ID 수집 (한 배치당 200개)
                batch_video_ids = []
                batch_video_ids_set = set()  # 배치 내 중복 방지
                batch_collected_count = 0

                while batch_collected_count < BATCH_SIZE:
                    remaining = min(50, BATCH_SIZE - batch_collected_count)  # API 한계: 50개

                    # 비디오 검색
                    search_params = {
                        'part': 'snippet',
                        'q': keyword,
                        'type': 'video',
                        'regionCode': region_code,
                        'maxResults': remaining,
                        'order': order,
                        'relevanceLanguage': 'en' if region_code == 'US' else None
                    }

                    # 게시 날짜 필터 (최근 90일)
                    if published_after:
                        search_params['publishedAfter'] = published_after.isoformat() + 'Z'
                    else:
                        ninety_days_ago = datetime.now() - timedelta(days=90)
                        search_params['publishedAfter'] = ninety_days_ago.isoformat() + 'Z'

                    # 페이지 토큰 추가
                    if next_page_token:
                        search_params['pageToken'] = next_page_token

                    # API 호출 with automatic key rotation
                    search_response = self._execute_with_retry(
                        lambda: self.youtube.search().list(**search_params).execute()
                    )
                    self.request_count += 1
                    total_api_calls += 1

                    # 비디오 ID 수집 (중복 제거)
                    page_video_ids = [item['id']['videoId'] for item in search_response['items']]

                    # 이미 수집한 ID는 제외
                    new_video_ids = [vid for vid in page_video_ids if vid not in batch_video_ids_set]

                    if len(new_video_ids) < len(page_video_ids):
                        duplicates = len(page_video_ids) - len(new_video_ids)
                        print(f"  [중복 감지] 이번 페이지에서 {duplicates}개 중복 비디오 제외")

                    batch_video_ids.extend(new_video_ids)
                    batch_video_ids_set.update(new_video_ids)
                    batch_collected_count += len(new_video_ids)

                    # 다음 페이지 토큰 확인
                    next_page_token = search_response.get('nextPageToken')

                    # 더 이상 결과가 없으면 중단
                    if not next_page_token or len(page_video_ids) == 0:
                        print(f"  더 이상 수집할 비디오가 없습니다 (총 {batch_collected_count}개 수집)")
                        break

                    # 새로운 비디오가 없으면 (모두 중복이면) 중단
                    if len(new_video_ids) == 0:
                        print(f"  더 이상 새로운 비디오가 없습니다 (모두 중복)")
                        break

                if not batch_video_ids:
                    print("  이 배치에서 수집된 비디오가 없습니다.")
                    break

                all_collected_video_ids.update(batch_video_ids)
                print(f"  비디오 ID {len(batch_video_ids)}개 수집 완료")

                # 2단계: 상세 비디오 정보 수집
                print(f"  비디오 상세 정보 수집 중...")
                batch_video_data = []
                channel_ids = set()  # 중복 방지를 위해 set 사용

                for i in range(0, len(batch_video_ids), 50):
                    batch_ids = batch_video_ids[i:i+50]
                    ids_string = ','.join(batch_ids)

                    # 모든 video 정보를 한번에 가져오기 with automatic key rotation
                    video_response = self._execute_with_retry(
                        lambda ids=ids_string: self.youtube.videos().list(
                            part='snippet,statistics,contentDetails,status,topicDetails,recordingDetails,localizations',
                            id=ids
                        ).execute()
                    )
                    self.request_count += 1
                    total_api_calls += 1

                    for item in video_response['items']:
                        snippet = item['snippet']
                        stats = item.get('statistics', {})
                        content_details = item.get('contentDetails', {})
                        status = item.get('status', {})
                        topic_details = item.get('topicDetails', {})
                        recording_details = item.get('recordingDetails', {})

                        # 지속시간을 초로 변환
                        duration = self._parse_duration(content_details.get('duration', 'PT0S'))

                        # 채널 ID 수집 (set에 추가하여 자동 중복 제거)
                        channel_ids.add(snippet['channelId'])

                        batch_video_data.append({
                            # 검색 관련 정보
                            'video_id': item['id'],
                            'search_keyword': keyword,
                            'search_region': region_code,
                            'search_order': order,
                            'created_at': datetime.now().isoformat(),

                            # 기본 정보 (snippet)
                            'title': snippet.get('title', '').replace('\n', ' ').replace('\r', ' '),
                            'description': snippet.get('description', '').replace('\n', ' ').replace('\r', ' '),
                            'channel_id': snippet.get('channelId', ''),
                            'channel_title': snippet.get('channelTitle', ''),
                            'published_at': snippet.get('publishedAt', ''),
                            'category_id': snippet.get('categoryId', ''),
                            'default_language': snippet.get('defaultLanguage', ''),
                            'default_audio_language': snippet.get('defaultAudioLanguage', ''),
                            'live_broadcast_content': snippet.get('liveBroadcastContent', ''),
                            'tags': ','.join(snippet.get('tags', [])),

                            # 썸네일 정보
                            'thumbnail_default': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                            'thumbnail_medium': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                            'thumbnail_high': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                            'thumbnail_standard': snippet.get('thumbnails', {}).get('standard', {}).get('url', ''),
                            'thumbnail_maxres': snippet.get('thumbnails', {}).get('maxres', {}).get('url', ''),

                            # 통계 정보 (statistics)
                            'view_count': int(stats.get('viewCount', 0)),
                            'like_count': int(stats.get('likeCount', 0)),
                            'dislike_count': int(stats.get('dislikeCount', 0)),
                            'favorite_count': int(stats.get('favoriteCount', 0)),
                            'comment_count': int(stats.get('commentCount', 0)),

                            # 콘텐츠 상세 정보 (contentDetails)
                            'duration_seconds': duration,
                            'duration_iso': content_details.get('duration', ''),
                            'dimension': content_details.get('dimension', ''),
                            'definition': content_details.get('definition', ''),
                            'caption': content_details.get('caption', ''),
                            'licensed_content': content_details.get('licensedContent', False),
                            'content_rating': str(content_details.get('contentRating', {})),
                            'projection': content_details.get('projection', ''),
                            'has_custom_thumbnail': content_details.get('hasCustomThumbnail', False),

                            # 상태 정보 (status)
                            'upload_status': status.get('uploadStatus', ''),
                            'privacy_status': status.get('privacyStatus', ''),
                            'license': status.get('license', ''),
                            'embeddable': status.get('embeddable', False),
                            'public_stats_viewable': status.get('publicStatsViewable', False),
                            'made_for_kids': status.get('madeForKids', False),
                            'self_declared_made_for_kids': status.get('selfDeclaredMadeForKids', False),

                            # 주제 정보 (topicDetails)
                            'topic_ids': ','.join(topic_details.get('topicIds', [])),
                            'relevant_topic_ids': ','.join(topic_details.get('relevantTopicIds', [])),
                            'topic_categories': ','.join(topic_details.get('topicCategories', [])),

                            # 녹화 정보 (recordingDetails)
                            'recording_date': recording_details.get('recordingDate', ''),
                            'location_latitude': recording_details.get('location', {}).get('latitude', ''),
                            'location_longitude': recording_details.get('location', {}).get('longitude', ''),
                            'location_altitude': recording_details.get('location', {}).get('altitude', ''),
                        })

                # 3단계: 채널 정보 수집
                print(f"  채널 정보 수집 중...")
                batch_channel_data = self.get_channel_info(list(channel_ids))
                channel_dict = {ch['channel_id']: ch for ch in batch_channel_data}
                total_api_calls += (len(channel_ids) + 49) // 50  # 채널 정보 API 호출 추정

                # 4단계: 비디오 데이터에 채널 정보 및 engagement_rate 추가
                for video in batch_video_data:
                    channel_info = channel_dict.get(video['channel_id'], {})
                    video.update({
                        'channel_subscriber_count': channel_info.get('subscriber_count', 0),
                        'channel_video_count': channel_info.get('video_count', 0),
                        'channel_total_view_count': channel_info.get('view_count', 0),
                        'channel_description': channel_info.get('description', '').replace('\n', ' ').replace('\r', ' '),
                        'channel_country': channel_info.get('country', ''),
                        'channel_custom_url': channel_info.get('custom_url', ''),
                        'channel_published_at': channel_info.get('published_at', ''),
                    })

                    # Engagement rate 계산: (좋아요 + 댓글) / 조회수 * 100
                    view_count = video.get('view_count', 0)
                    like_count = video.get('like_count', 0)
                    comment_count = video.get('comment_count', 0)
                    engagement_rate = ((like_count + comment_count) / view_count * 100) if view_count > 0 else 0.0
                    video['engagement_rate'] = round(engagement_rate, 4)

                print(f"  비디오 상세 정보 완료: {len(batch_video_data)}개")

                # 5단계: 품질 필터 적용
                if apply_quality_filter:
                    print(f"  품질 필터 적용 중...")
                    batch_passed_count = 0
                    batch_new_raw_count = 0  # 새로운 raw 비디오 개수 (중복 제외)
                    batch_failed_category = 0
                    batch_failed_channel = 0
                    batch_failed_engagement = 0
                    batch_failed_country = 0

                    for video in batch_video_data:
                        fail_reason = []

                        # 필터 1: 채널 국가 (US만)
                        if video.get('channel_country') != TARGET_CHANNEL_COUNTRY:
                            batch_failed_country += 1
                            fail_reason.append(f"채널 국가 불일치 (실제: {video.get('channel_country')})")

                        # 필터 2: 카테고리
                        if video.get('category_id') != TARGET_CATEGORY:
                            batch_failed_category += 1
                            fail_reason.append(f"카테고리 불일치 (실제: {video.get('category_id')})")

                        # 필터 3: 채널 규모 (구독자 10k+ OR 총 조회수 100M+)
                        subscriber_count = video.get('channel_subscriber_count', 0)
                        channel_total_views = video.get('channel_total_view_count', 0)
                        if subscriber_count < MIN_SUBSCRIBER_COUNT and channel_total_views < MIN_CHANNEL_TOTAL_VIEWS:
                            batch_failed_channel += 1
                            fail_reason.append(f"채널 규모 미달 (구독자: {subscriber_count:,}, 총조회: {channel_total_views:,})")

                        # 필터 4: 참여율
                        if video.get('engagement_rate', 0) < MIN_ENGAGEMENT_RATE:
                            batch_failed_engagement += 1
                            fail_reason.append(f"참여율 미달 ({video.get('engagement_rate', 0):.2f}%)")

                        # 필터 결과 기록
                        video['quality_filter_passed'] = len(fail_reason) == 0
                        video['filter_fail_reason'] = '; '.join(fail_reason) if fail_reason else None

                        # Raw 데이터에 추가 (모든 비디오)
                        all_raw_videos.append(video.copy())

                        # 통과한 비디오만 filtered_videos에 추가 (중복 제외)
                        if len(fail_reason) == 0:
                            if video['video_id'] not in filtered_video_ids:
                                filtered_videos.append(video)
                                filtered_video_ids.add(video['video_id'])
                                batch_passed_count += 1

                    # 새로운 raw 비디오 개수 계산 (중복 제외)
                    batch_new_raw_count = len(all_collected_video_ids) - prev_collected_count

                    print(f"  필터 결과: {batch_passed_count}개 통과 / {len(batch_video_data)}개")
                    print(f"    - 채널 국가 불일치: {batch_failed_country}개")
                    print(f"    - 카테고리 불일치: {batch_failed_category}개")
                    print(f"    - 채널 규모 미달: {batch_failed_channel}개")
                    print(f"    - 참여율 미달: {batch_failed_engagement}개")
                    print(f"  누적 필터링된 비디오: {len(filtered_videos)}개 / 목표: {max_results}개")
                    print(f"  새로운 raw 비디오: {batch_new_raw_count}개 (중복 제외)")

                    # 새로운 raw 비디오가 없으면 (모두 중복) 카운터 증가
                    if batch_new_raw_count == 0:
                        consecutive_empty_batches += 1
                        print(f"  [경고] 연속 {consecutive_empty_batches}번째 빈 배치 (모두 중복 비디오)")
                    else:
                        consecutive_empty_batches = 0  # 새 raw 비디오 있으면 리셋
                else:
                    # 필터 비활성화 시 모든 비디오 추가 (중복 제외)
                    batch_new_count = 0
                    for video in batch_video_data:
                        video['quality_filter_passed'] = True
                        video['filter_fail_reason'] = None
                        all_raw_videos.append(video.copy())

                        # 중복 체크 후 추가
                        if video['video_id'] not in filtered_video_ids:
                            filtered_videos.append(video)
                            filtered_video_ids.add(video['video_id'])
                            batch_new_count += 1

                    print(f"  누적 수집된 비디오: {len(filtered_videos)}개 / 목표: {max_results}개")

                    # 새 비디오가 없으면 카운터 증가
                    if batch_new_count == 0:
                        consecutive_empty_batches += 1
                        print(f"  [경고] 연속 {consecutive_empty_batches}번째 빈 배치 (새 비디오 없음)")
                    else:
                        consecutive_empty_batches = 0  # 새 비디오 있으면 리셋

                # 목표 달성 확인
                if len(filtered_videos) >= max_results:
                    print(f"\n[목표 달성] {len(filtered_videos)}개 비디오 수집 완료!")
                    break

                # 연속으로 중복만 나오면 조기 종료
                if consecutive_empty_batches >= MAX_EMPTY_BATCHES:
                    print(f"\n[조기 종료] {MAX_EMPTY_BATCHES}번 연속 중복 비디오만 수집 - 더 이상 새로운 비디오 없음")
                    print(f"수집된 비디오: {len(filtered_videos)}개 (목표: {max_results}개)")
                    break

                # API 할당량 경고
                if total_api_calls > 100:
                    print(f"\n  [주의] API 호출 수: {total_api_calls} (할당량: 10,000/day)")

            # 최종 결과 반환
            final_video_data = filtered_videos[:max_results]  # 정확히 max_results개만 반환
            final_video_ids = [v['video_id'] for v in final_video_data]

            print(f"\n{'='*80}")
            print(f"수집 완료: {keyword} in {region_code}")
            print(f"  - 총 수집 비디오 수: {len(all_collected_video_ids)}개")
            if apply_quality_filter:
                print(f"  - 필터링 후: {len(filtered_videos)}개")
                print(f"  - Raw 데이터: {len(all_raw_videos)}개")
            print(f"  - 최종 반환: {len(final_video_data)}개")
            print(f"  - 총 API 호출 수: {total_api_calls}")
            print(f"{'='*80}\n")

            return final_video_data, final_video_ids, all_raw_videos
            
        except HttpError as e:
            print(f"YouTube API 오류: {e}")
            return [], [], []
    
    def get_video_statistics(self, video_ids):
        """비디오 통계 정보 수집"""
        if not video_ids:
            return []
            
        try:
            # 비디오 ID를 50개씩 배치로 처리 (API 제한)
            statistics_data = []
            
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                ids_string = ','.join(batch_ids)

                # API 호출 with automatic key rotation
                stats_response = self._execute_with_retry(
                    lambda ids=ids_string: self.youtube.videos().list(
                        part='statistics,contentDetails,snippet',
                        id=ids
                    ).execute()
                )
                self.request_count += 1
                
                for item in stats_response['items']:
                    stats = item['statistics']
                    content_details = item['contentDetails']
                    snippet = item['snippet']
                    
                    # 지속시간을 초로 변환
                    duration = self._parse_duration(content_details.get('duration', 'PT0S'))
                    
                    statistics_data.append({
                        'video_id': item['id'],
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'duration_seconds': duration,
                        'definition': content_details.get('definition', 'sd'),
                        'dimension': content_details.get('dimension', '2d'),
                        'tags': snippet.get('tags', []),
                        'category_id': snippet.get('categoryId', ''),
                        'default_language': snippet.get('defaultLanguage', ''),
                        'collected_at': datetime.now().isoformat()
                    })
                
                # API 제한 방지를 위한 지연
                time.sleep(0.1)
            
            print(f"통계 수집 완료: {len(statistics_data)}개 비디오")
            return statistics_data
            
        except HttpError as e:
            print(f"통계 수집 오류: {e}")
            return []
    
    def get_channel_info(self, channel_ids):
        """채널 정보 수집"""
        if not channel_ids:
            return []
            
        try:
            # 중복 제거
            unique_channel_ids = list(set(channel_ids))
            channel_data = []
            
            for i in range(0, len(unique_channel_ids), 50):
                batch_ids = unique_channel_ids[i:i+50]
                ids_string = ','.join(batch_ids)

                # API 호출 with automatic key rotation
                channel_response = self._execute_with_retry(
                    lambda ids=ids_string: self.youtube.channels().list(
                        part='snippet,statistics,brandingSettings',
                        id=ids
                    ).execute()
                )
                self.request_count += 1
                
                for item in channel_response['items']:
                    snippet = item['snippet']
                    stats = item['statistics']
                    
                    channel_data.append({
                        'channel_id': item['id'],
                        'channel_title': snippet['title'],
                        'description': snippet['description'][:300],
                        'custom_url': snippet.get('customUrl', ''),
                        'published_at': snippet['publishedAt'],
                        'subscriber_count': int(stats.get('subscriberCount', 0)),
                        'video_count': int(stats.get('videoCount', 0)),
                        'view_count': int(stats.get('viewCount', 0)),
                        'country': snippet.get('country', ''),
                        'collected_at': datetime.now().isoformat()
                    })
            
            print(f"채널 정보 수집 완료: {len(channel_data)}개 채널")
            return channel_data
            
        except HttpError as e:
            print(f"채널 정보 수집 오류: {e}")
            return []
    
    def get_comprehensive_comments(self, video_ids, max_comments_per_video=MAX_COMMENTS_PER_VIDEO):
        """비디오 댓글 포괄적 수집 (모든 API 필드 포함)"""
        if not video_ids:
            return []
            
        comments_data = []
        
        for video_id in video_ids:
            try:
                # 댓글 스레드 수집 (최상위 댓글 + 답글) with automatic key rotation
                comments_response = self._execute_with_retry(
                    lambda vid=video_id, max_c=max_comments_per_video: self.youtube.commentThreads().list(
                        part='snippet,replies',
                        videoId=vid,
                        maxResults=min(max_c, 100),
                        order='relevance'
                    ).execute()
                )
                self.request_count += 1
                
                for item in comments_response['items']:
                    # 최상위 댓글
                    top_comment = item['snippet']['topLevelComment']['snippet']
                    
                    comments_data.append({
                        # 기본 식별 정보
                        'video_id': video_id,
                        'comment_id': item['snippet']['topLevelComment']['id'],
                        'comment_type': 'top_level',
                        'parent_comment_id': '',
                        'collected_at': datetime.now().isoformat(),
                        
                        # 작성자 정보
                        'author_display_name': top_comment.get('authorDisplayName', ''),
                        'author_profile_image_url': top_comment.get('authorProfileImageUrl', ''),
                        'author_channel_url': top_comment.get('authorChannelUrl', ''),
                        'author_channel_id': top_comment.get('authorChannelId', {}).get('value', ''),
                        
                        # 댓글 내용
                        'comment_text_display': top_comment.get('textDisplay', ''),
                        'comment_text_original': top_comment.get('textOriginal', ''),
                        'comment_text_length': len(top_comment.get('textDisplay', '')),
                        
                        # 상호작용 정보
                        'like_count': int(top_comment.get('likeCount', 0)),
                        'reply_count': int(item['snippet'].get('totalReplyCount', 0)),
                        'moderation_status': top_comment.get('moderationStatus', ''),
                        
                        # 시간 정보
                        'published_at': top_comment.get('publishedAt', ''),
                        'updated_at': top_comment.get('updatedAt', ''),
                        
                        # 추가 메타데이터
                        'viewer_rating': top_comment.get('viewerRating', ''),
                        'can_rate': top_comment.get('canRate', False),
                    })
                    
                    # 답글이 있는 경우 답글도 수집
                    if 'replies' in item and 'comments' in item['replies']:
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            
                            comments_data.append({
                                # 기본 식별 정보
                                'video_id': video_id,
                                'comment_id': reply['id'],
                                'comment_type': 'reply',
                                'parent_comment_id': item['snippet']['topLevelComment']['id'],
                                'created_at': datetime.now().isoformat(),
                                
                                # 작성자 정보
                                'author_display_name': reply_snippet.get('authorDisplayName', ''),
                                'author_profile_image_url': reply_snippet.get('authorProfileImageUrl', ''),
                                'author_channel_url': reply_snippet.get('authorChannelUrl', ''),
                                'author_channel_id': reply_snippet.get('authorChannelId', {}).get('value', ''),
                                
                                # 댓글 내용
                                'comment_text_display': reply_snippet.get('textDisplay', ''),
                                'comment_text_original': reply_snippet.get('textOriginal', ''),
                                'comment_text_length': len(reply_snippet.get('textDisplay', '')),
                                
                                # 상호작용 정보
                                'like_count': int(reply_snippet.get('likeCount', 0)),
                                'reply_count': 0,  # 답글의 답글은 없음
                                'moderation_status': reply_snippet.get('moderationStatus', ''),
                                
                                # 시간 정보
                                'published_at': reply_snippet.get('publishedAt', ''),
                                'updated_at': reply_snippet.get('updatedAt', ''),
                                
                                # 추가 메타데이터
                                'viewer_rating': reply_snippet.get('viewerRating', ''),
                                'can_rate': reply_snippet.get('canRate', False),
                            })
                
                print(f"댓글 수집: {video_id} - {len(comments_response['items'])}개 스레드")
                time.sleep(0.1)  # API 제한 방지
                
            except HttpError as e:
                if 'commentsDisabled' in str(e):
                    print(f"댓글 비활성화: {video_id}")
                elif 'quotaExceeded' in str(e):
                    print(f"API 할당량 초과: {video_id}")
                    break
                else:
                    print(f"댓글 수집 오류 {video_id}: {e}")
                continue
        
        print(f"전체 댓글 수집 완료: {len(comments_data)}개")
        return comments_data
    
    def _parse_duration(self, duration_str):
        """YouTube 지속시간 형식을 초로 변환"""
        # PT4M13S -> 253초
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        return 0
    
    def get_quota_usage(self):
        """현재 API 사용량 반환"""
        return self.request_count