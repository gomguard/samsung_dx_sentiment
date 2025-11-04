#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram RapidAPI 데이터 수집기
RapidAPI Instagram Scraper를 활용한 게시물 및 댓글 수집
"""

import os
import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# 프로젝트 루트를 Python 경로에 추가
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
instagram_root = current_dir

# Import from Instagram-specific config using absolute path
try:
    # Ensure we import from instagram_brand_analyzer/config, not parent config
    import importlib.util
    config_path = os.path.join(instagram_root, 'config', 'settings.py')
    spec = importlib.util.spec_from_file_location("instagram_config_settings", config_path)
    settings_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings_module)

    INSTAGRAM_RAPIDAPI_KEY = settings_module.INSTAGRAM_RAPIDAPI_KEY
    INSTAGRAM_RAPIDAPI_BASE_URL = settings_module.INSTAGRAM_RAPIDAPI_BASE_URL
    INSTAGRAM_RAPIDAPI_HOST = settings_module.INSTAGRAM_RAPIDAPI_HOST
    INSTAGRAM_KEYWORDS = settings_module.INSTAGRAM_KEYWORDS
    API_RATE_LIMITS = settings_module.API_RATE_LIMITS
except Exception as e:
    print(f"[DEBUG] Error loading config: {e}")
    # Fallback values for demo mode
    INSTAGRAM_RAPIDAPI_KEY = ""
    INSTAGRAM_RAPIDAPI_BASE_URL = "https://instagram-scraper-2023.p.rapidapi.com"
    INSTAGRAM_RAPIDAPI_HOST = "instagram-scraper-2023.p.rapidapi.com"
    INSTAGRAM_KEYWORDS = ["Samsung TV", "LG TV"]
    API_RATE_LIMITS = {
        "rapidapi": {"delay_between_requests": 2}
    }

class InstagramAPI:
    def __init__(self, api_key=None):
        """Instagram RapidAPI 클라이언트 초기화"""
        self.api_key = api_key or INSTAGRAM_RAPIDAPI_KEY
        self.base_url = INSTAGRAM_RAPIDAPI_BASE_URL
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': INSTAGRAM_RAPIDAPI_HOST
        }
        self.request_count = 0
        self.rate_limit_delay = API_RATE_LIMITS.get("rapidapi", {}).get("delay_between_requests", 2)

        # API 상태 확인
        if not self.api_key or self.api_key == "":
            raise ValueError("Instagram RapidAPI 키가 설정되지 않았습니다. config/secrets.py에 INSTAGRAM_RAPIDAPI_KEY를 추가하세요.")

        self.demo_mode = False
        print(f"Instagram RapidAPI 초기화 완료 (Host: {INSTAGRAM_RAPIDAPI_HOST})")
        print(f"API Key: {self.api_key[:20]}...")

    def get_comprehensive_post_data(self, keyword: str, max_results: int = 30) -> Tuple[List[Dict], List[str]]:
        """
        키워드로 Instagram 게시물 검색 후 모든 정보를 수집

        Args:
            keyword (str): 검색 키워드
            max_results (int): 최대 게시물 수

        Returns:
            Tuple[List[Dict], List[str]]: (게시물 데이터 리스트, 게시물 PK 리스트)
        """
        print(f"Instagram RapidAPI 검색 시작: {keyword}")

        # 키워드를 해시태그로 변환 (공백 제거, # 제거)
        hashtag = keyword.replace(' ', '').replace('#', '').lower()

        # RapidAPI로 해시태그 검색
        posts_data = self._search_by_hashtag(hashtag, max_results)

        if not posts_data:
            print(f"검색 결과가 없습니다: {keyword}")
            return [], []

        # 데이터 변환
        post_data = []
        post_pks = []

        for post in posts_data[:max_results]:
            try:
                post_info = self._convert_to_standard_format(post, keyword)
                if post_info:
                    post_data.append(post_info)
                    # Use PK (numeric ID) for comment collection - API requires numeric ID
                    post_pks.append(post_info['post_id'])
            except Exception as e:
                print(f"게시물 변환 오류: {e}")
                continue

        print(f"Instagram RapidAPI 검색 완료: {keyword} - {len(post_data)}개 게시물")
        return post_data, post_pks

    def _search_by_hashtag(self, hashtag: str, max_results: int) -> List[Dict]:
        """RapidAPI로 해시태그 검색 (Instagram Premium API 2023)"""
        try:
            print(f"  [Search] Hashtag: #{hashtag}")

            # Use v1/hashtag/medias/top for better results
            url = f"{self.base_url}/v1/hashtag/medias/top"
            params = {
                "name": hashtag,
                "amount": max_results
            }

            print(f"  Request: {url}")
            print(f"  Params: {params}")

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            self.request_count += 1

            print(f"  Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"  Search failed: {response.status_code}")
                print(f"  Response: {response.text[:500]}")
                return []

            data = response.json()

            # v1 API returns a list of media objects directly
            posts = []
            if isinstance(data, list):
                posts = data
                print(f"  [OK] Got {len(posts)} posts (list)")
            elif isinstance(data, dict) and 'items' in data:
                posts = data['items']
                print(f"  [OK] Got {len(posts)} posts (dict with items)")
            else:
                print(f"  [WARN] Unexpected response type: {type(data)}")
                print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")

            time.sleep(self.rate_limit_delay)
            return posts

        except Exception as e:
            print(f"  Search error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _convert_to_standard_format(self, media: Dict, keyword: str) -> Dict[str, Any]:
        """Instagram Premium API 2023 게시물을 표준 형식으로 변환"""
        try:
            # 게시물 ID
            post_id = str(media.get('pk', media.get('id', f"instagram_{hash(str(media))}")))
            code = media.get('code', post_id)

            # 캡션 정보 (v1 API provides caption_text directly)
            caption_text = media.get('caption_text', '')
            if not caption_text:
                # Fallback: check caption object
                caption_obj = media.get('caption')
                if caption_obj:
                    if isinstance(caption_obj, dict):
                        caption_text = caption_obj.get('text', '')
                    else:
                        caption_text = str(caption_obj)

            # 사용자 정보
            user_obj = media.get('user', {})
            author_username = user_obj.get('username', 'instagram_user')
            author_id = str(user_obj.get('pk', user_obj.get('id', 'unknown')))

            # 기본 정보
            caption = caption_text.replace('\n', ' ').replace('\r', ' ') if caption_text else f"Instagram post about {keyword}"

            # 미디어 타입 (media_type: 1=photo, 2=video, 8=carousel)
            media_type_code = media.get('media_type', 1)
            product_type = media.get('product_type', '')

            if media_type_code == 2 or product_type == 'clips':
                media_type = 'VIDEO'
            elif media_type_code == 8:
                media_type = 'CAROUSEL'
            else:
                media_type = 'IMAGE'

            # 통계 정보
            like_count = media.get('like_count', 0) or 0
            comment_count = media.get('comment_count', 0) or 0
            play_count = media.get('play_count', 0) or 0
            view_count = media.get('view_count', 0) or 0
            share_count = 0  # Not available in v1 API

            # 시간 정보
            taken_at = media.get('taken_at', media.get('taken_at_ts'))
            if taken_at:
                if isinstance(taken_at, (int, float)):
                    published_at = datetime.fromtimestamp(taken_at).isoformat() + 'Z'
                elif isinstance(taken_at, str) and 'Z' in taken_at:
                    published_at = taken_at
                else:
                    published_at = str(taken_at)
            else:
                published_at = datetime.now().isoformat() + 'Z'

            # 미디어 URL
            thumbnail_url = media.get('thumbnail_url', '')
            image_versions = media.get('image_versions2', {})
            candidates = image_versions.get('candidates', [])
            if candidates:
                media_url = candidates[0].get('url', '')
            else:
                media_url = thumbnail_url

            # Permalink
            if code:
                permalink = f"https://instagram.com/p/{code}"
            else:
                permalink = f"https://instagram.com/p/{post_id}"

            return {
                # 검색 관련 정보
                'post_id': str(post_id),
                'code': code,  # Instagram shortcode for comment collection
                'search_keyword': keyword,
                'collected_at': datetime.now().isoformat(),

                # 작성자 정보
                'author_username': author_username,
                'author_id': author_id,

                # 기본 정보
                'caption': caption[:5000],  # Limit caption length
                'media_type': media_type,
                'media_url': media_url,
                'permalink': permalink,
                'published_at': published_at,

                # 통계 정보
                'like_count': int(like_count),
                'comment_count': int(comment_count),
                'play_count': int(play_count if play_count > 0 else view_count),
                'share_count': int(share_count),

                # 해시태그 정보
                'hashtags': self._extract_hashtags(caption),
                'mentions': self._extract_mentions(caption),

                # 추가 메타데이터
                'is_video': media_type == 'VIDEO',

                # OpenAI로 추출할 필드 (초기값 None)
                'video_content_summary': None,
                'comment_text_summary': None,

                # 플랫폼
                'platform': 'instagram'
            }

        except Exception as e:
            print(f"게시물 변환 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_hashtags(self, text: str) -> str:
        """텍스트에서 해시태그 추출"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return ', '.join(hashtags[:10])  # 최대 10개만

    def _extract_mentions(self, text: str) -> str:
        """텍스트에서 멘션 추출"""
        import re
        mentions = re.findall(r'@\w+', text)
        return ', '.join(mentions[:5])  # 최대 5개만

    def get_comprehensive_comments(self, post_pks: List[str], max_comments_per_post: int = 50) -> List[Dict[str, Any]]:
        """
        Instagram 게시물의 댓글 수집

        Args:
            post_pks (List[str]): 게시물 PK 리스트 (numeric IDs)
            max_comments_per_post (int): 게시물당 최대 댓글 수

        Returns:
            List[Dict]: 댓글 데이터 리스트
        """
        print("Instagram RapidAPI collecting comments...")

        comments_data = []

        # Use PKs directly for comment collection
        for pk in post_pks[:5]:  # Limit to 5 posts
            try:
                post_comments = self._get_post_comments(pk, max_comments_per_post)
                comments_data.extend(post_comments)
                print(f"Comments collected: {pk} - {len(post_comments)} comments")
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                print(f"Failed to collect comments: {pk} - {e}")
                continue

        return comments_data

    def _get_post_comments(self, post_pk: str, max_comments: int) -> List[Dict]:
        """특정 게시물의 댓글 가져오기 (Instagram Premium API 2023)"""
        try:
            # Use v1/media/comments endpoint with id parameter (id = numeric PK)
            url = f"{self.base_url}/v1/media/comments"
            params = {'id': post_pk, 'amount': min(max_comments, 50)}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            self.request_count += 1

            if response.status_code != 200:
                print(f"  Comments API error {response.status_code}: {response.text[:200]}")
                return []

            data = response.json()

            # v1 API returns list of comments directly
            comments = data if isinstance(data, list) else data.get('comments', [])

            if not comments:
                return []

            # 표준 형식으로 변환
            formatted_comments = []
            for comment in comments:
                formatted_comment = {
                    'post_id': post_pk,
                    'comment_id': str(comment.get('pk', comment.get('id', ''))),
                    'comment_text': comment.get('text', ''),
                    'author_username': comment.get('user', {}).get('username', 'instagram_user'),
                    'like_count': comment.get('comment_like_count', 0),
                    'published_at': self._convert_timestamp(comment.get('created_at', comment.get('created_at_utc'))),
                    'platform': 'instagram'
                }
                formatted_comments.append(formatted_comment)

            return formatted_comments

        except Exception as e:
            print(f"  Comments API exception: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _convert_timestamp(self, timestamp) -> str:
        """타임스탬프를 ISO 형식으로 변환"""
        if not timestamp:
            return datetime.now().isoformat() + 'Z'

        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).isoformat() + 'Z'

        return str(timestamp)

    def _create_demo_data(self, keyword: str, max_results: int) -> Tuple[List[Dict], List[str]]:
        """데모용 Instagram 게시물 데이터 생성"""
        print(f"Instagram 데모 데이터 생성: {keyword}")

        demo_posts = []
        post_ids = []

        # 브랜드별 게시물 템플릿
        post_templates = {
            'samsung': [
                "Check out this amazing Samsung TV! #samsungtv #qled #smarttv",
                "Just unboxed my new Samsung Frame TV #theframe #samsungframe",
                "Samsung TV picture quality is incredible! #samsung #4ktv",
            ],
            'lg': [
                "LG OLED TV review! Picture perfect #lgtv #oled #television",
                "My new LG smart TV setup #lg #smarttv #hometheater",
            ],
            'general': [
                "TV shopping day! Looking at different brands #tvreview #smarttv",
                "Home theater setup complete! #4ktv #homecinema #television",
                "Best TV deals this week #tvdeals #electronics #shopping",
            ]
        }

        # 키워드에 따른 템플릿 선택
        if 'samsung' in keyword.lower():
            templates = post_templates['samsung'] + post_templates['general']
        elif any(brand in keyword.lower() for brand in ['lg', 'sony', 'tcl']):
            templates = post_templates['lg'] + post_templates['general']
        else:
            templates = post_templates['general']

        for i in range(min(max_results, 20)):
            caption = templates[i % len(templates)]
            post_id = f"instagram_demo_{keyword.replace(' ', '_')}_{i+1}"
            is_video = i % 3 == 0

            demo_post = {
                'post_id': post_id,
                'search_keyword': keyword,
                'collected_at': datetime.now().isoformat(),
                'author_username': f"instagram_user_{i+1}",
                'author_id': f"user_{i+1}",
                'caption': caption,
                'media_type': 'VIDEO' if is_video else 'IMAGE',
                'media_url': f"https://instagram.com/image_{i+1}.jpg",
                'permalink': f"https://instagram.com/p/{post_id}",
                'published_at': (datetime.now() - timedelta(hours=i*2)).isoformat() + 'Z',
                'like_count': 100 + i * 50,
                'comment_count': 10 + i * 5,
                'play_count': (50 + i * 30) if is_video else 0,
                'share_count': 5 + i * 2,
                'hashtags': f"#{keyword.replace(' ', '')}, #tv, #electronics",
                'mentions': '',
                'is_video': is_video,
                'video_content_summary': None,
                'comment_text_summary': None,
                'platform': 'instagram'
            }

            demo_posts.append(demo_post)
            post_ids.append(post_id)

        print(f"Instagram 데모 데이터 생성 완료: {len(demo_posts)}개 게시물")
        return demo_posts, post_ids

    def _create_demo_comments(self, post_ids: List[str], max_comments_per_post: int) -> List[Dict]:
        """데모용 Instagram 댓글 데이터 생성"""
        demo_comments = []

        comment_templates = [
            "Love this!",
            "Where can I buy this?",
            "Amazing quality!",
            "Thanks for sharing!",
            "This looks great!",
            "Perfect for my living room",
            "How much did this cost?",
            "Great review!",
            "I need this!",
            "Awesome setup!"
        ]

        for post_id in post_ids:
            comments_count = min(max_comments_per_post, 15)

            for i in range(comments_count):
                comment_text = comment_templates[i % len(comment_templates)]

                demo_comment = {
                    'post_id': post_id,
                    'comment_id': f"comment_{post_id}_{i+1}",
                    'comment_text': comment_text,
                    'author_username': f"user_{i+1}",
                    'like_count': i * 2 + 1,
                    'published_at': (datetime.now() - timedelta(minutes=i*10)).isoformat() + 'Z',
                    'platform': 'instagram'
                }

                demo_comments.append(demo_comment)

        return demo_comments

    def get_quota_usage(self) -> int:
        """현재 API 사용량 반환"""
        return self.request_count
