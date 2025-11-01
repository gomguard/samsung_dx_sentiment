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
    def __init__(self, api_key=YOUTUBE_API_KEY):
        """YouTube API 클라이언트 초기화"""
        self.api_key = api_key
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)
        self.request_count = 0
        
    def get_comprehensive_video_data(self, keyword, region_code="US", max_results=MAX_RESULTS_PER_SEARCH, 
                                   published_after=None, order="relevance"):
        """키워드로 비디오 검색 후 모든 정보를 한번에 수집 (최대 100개까지 페이지네이션 지원)"""
        try:
            all_video_ids = []
            next_page_token = None
            collected_count = 0
            
            # 페이지네이션으로 최대 100개까지 수집
            while collected_count < max_results:
                remaining = min(50, max_results - collected_count)  # API 한계: 50개
                
                # 1단계: 비디오 검색
                search_params = {
                    'part': 'snippet',
                    'q': keyword,
                    'type': 'video',
                    'regionCode': region_code,
                    'maxResults': remaining,
                    'order': order,
                    'relevanceLanguage': 'en' if region_code == 'US' else None
                }
                
                # 게시 날짜 필터 (최근 90일로 확장)
                if published_after:
                    search_params['publishedAfter'] = published_after.isoformat() + 'Z'
                else:
                    ninety_days_ago = datetime.now() - timedelta(days=90)
                    search_params['publishedAfter'] = ninety_days_ago.isoformat() + 'Z'
                
                # 페이지 토큰 추가
                if next_page_token:
                    search_params['pageToken'] = next_page_token
                
                search_response = self.youtube.search().list(**search_params).execute()
                self.request_count += 1
                
                # 비디오 ID 수집
                page_video_ids = [item['id']['videoId'] for item in search_response['items']]
                all_video_ids.extend(page_video_ids)
                collected_count += len(page_video_ids)
                
                # 다음 페이지 토큰 확인
                next_page_token = search_response.get('nextPageToken')
                
                # 더 이상 결과가 없거나 목표 달성 시 중단
                if not next_page_token or len(page_video_ids) == 0:
                    break
            
            if not all_video_ids:
                return [], []
            
            # 2단계: 상세 비디오 정보 수집 (videos API로 모든 정보 한번에)
            video_data = []
            channel_ids = []
            
            for i in range(0, len(all_video_ids), 50):
                batch_ids = all_video_ids[i:i+50]
                ids_string = ','.join(batch_ids)
                
                # 모든 video 정보를 한번에 가져오기
                video_response = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails,status,topicDetails,recordingDetails,localizations',
                    id=ids_string
                ).execute()
                self.request_count += 1
                
                for item in video_response['items']:
                    snippet = item['snippet']
                    stats = item.get('statistics', {})
                    content_details = item.get('contentDetails', {})
                    status = item.get('status', {})
                    topic_details = item.get('topicDetails', {})
                    recording_details = item.get('recordingDetails', {})
                    
                    # 지속시간을 초로 변환
                    duration = self._parse_duration(content_details.get('duration', 'PT0S'))
                    
                    # 채널 ID 수집
                    channel_ids.append(snippet['channelId'])
                    
                    video_data.append({
                        # 검색 관련 정보
                        'video_id': item['id'],
                        'search_keyword': keyword,
                        'search_region': region_code,
                        'search_order': order,
                        'collected_at': datetime.now().isoformat(),
                        
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
            channel_data = self.get_channel_info(list(set(channel_ids)))
            
            # 4단계: 비디오 데이터에 채널 정보 병합
            channel_dict = {ch['channel_id']: ch for ch in channel_data}
            
            for video in video_data:
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
            
            print(f"포괄적 검색 완료: {keyword} in {region_code} - {len(video_data)}개 비디오")
            return video_data, all_video_ids
            
        except HttpError as e:
            print(f"YouTube API 오류: {e}")
            return [], []
    
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
                
                stats_response = self.youtube.videos().list(
                    part='statistics,contentDetails,snippet',
                    id=ids_string
                ).execute()
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
                
                channel_response = self.youtube.channels().list(
                    part='snippet,statistics,brandingSettings',
                    id=ids_string
                ).execute()
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
                # 댓글 스레드 수집 (최상위 댓글 + 답글)
                comments_response = self.youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=min(max_comments_per_video, 100),
                    order='relevance'
                ).execute()
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
                                'collected_at': datetime.now().isoformat(),
                                
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