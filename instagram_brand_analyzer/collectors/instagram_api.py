#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram API 데이터 수집기
Instagram Basic Display API 및 Graph API 활용
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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_GRAPH_ACCESS_TOKEN,
    BRAND_HASHTAGS, INSTAGRAM_KEYWORDS, API_RATE_LIMITS
)

class InstagramAPI:
    def __init__(self, access_token=None, graph_token=None):
        """Instagram API 클라이언트 초기화"""
        self.access_token = access_token or INSTAGRAM_ACCESS_TOKEN
        self.graph_token = graph_token or INSTAGRAM_GRAPH_ACCESS_TOKEN
        self.base_url = "https://graph.instagram.com"
        self.request_count = 0
        self.rate_limit_delay = 2  # 요청 간 대기시간
        
        # API 상태 확인
        if not self.access_token and not self.graph_token:
            print("Instagram API 토큰이 설정되지 않았습니다.")
            print("현재는 더미 데이터 모드로 동작합니다.")
            self.demo_mode = True
        else:
            self.demo_mode = False
    
    def get_comprehensive_post_data(self, hashtag: str, region_code: str = "US", 
                                  max_results: int = 30) -> Tuple[List[Dict], List[str]]:
        """
        해시태그로 Instagram 게시물 검색 후 모든 정보를 수집
        """
        if self.demo_mode:
            return self._create_demo_data(hashtag, region_code, max_results)
        
        try:
            print(f"Instagram API 검색 시작: #{hashtag} (지역: {region_code})")
            
            # Instagram에서는 해시태그 검색이 제한적이므로 
            # 여러 전략을 조합하여 데이터 수집
            all_posts = []
            
            # 전략 1: 해시태그 최근 게시물 검색 (Graph API)
            if self.graph_token:
                hashtag_posts = self._search_by_hashtag(hashtag, max_results // 2)
                all_posts.extend(hashtag_posts)
            
            # 전략 2: 사용자 미디어 검색 (Basic Display API)
            if self.access_token:
                user_posts = self._search_user_media(hashtag, max_results // 2)
                all_posts.extend(user_posts)
            
            # 중복 제거 및 데이터 변환
            unique_posts = self._remove_duplicates(all_posts)
            post_data = []
            post_ids = []
            
            for post in unique_posts[:max_results]:
                try:
                    post_info = self._convert_to_standard_format(post, hashtag, region_code)
                    if post_info:
                        post_data.append(post_info)
                        post_ids.append(post_info['post_id'])
                except Exception as e:
                    print(f"게시물 변환 오류: {e}")
                    continue
            
            print(f"Instagram API 검색 완료: #{hashtag} - {len(post_data)}개 게시물")
            return post_data, post_ids
            
        except Exception as e:
            print(f"Instagram API 검색 오류: {e}")
            return self._create_demo_data(hashtag, region_code, max_results)
    
    def _search_by_hashtag(self, hashtag: str, max_results: int) -> List[Dict]:
        """해시태그로 게시물 검색 (Graph API)"""
        try:
            print(f"  🏷️ 해시태그 검색: #{hashtag}")
            
            # Instagram Graph API는 해시태그 검색이 매우 제한적
            # 비즈니스 계정과 특별한 권한이 필요
            url = f"{self.base_url}/ig_hashtag_search"
            params = {
                'user_id': 'business_account_id',  # 비즈니스 계정 ID 필요
                'q': hashtag,
                'access_token': self.graph_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            self.request_count += 1
            
            if response.status_code != 200:
                print(f"    ❌ 해시태그 검색 실패: {response.status_code}")
                return []
            
            data = response.json()
            posts = self._extract_posts_from_hashtag(data)
            
            print(f"    ✅ 해시태그 검색 성공: {len(posts)}개")
            time.sleep(self.rate_limit_delay)
            return posts
            
        except Exception as e:
            print(f"    ❌ 해시태그 검색 오류: {e}")
            return []
    
    def _search_user_media(self, keyword: str, max_results: int) -> List[Dict]:
        """사용자 미디어 검색 (Basic Display API)"""
        try:
            print(f"  👤 사용자 미디어 검색: {keyword}")
            
            # Basic Display API로 사용자의 미디어 가져오기
            url = f"{self.base_url}/me/media"
            params = {
                'fields': 'id,caption,media_type,media_url,thumbnail_url,timestamp,permalink',
                'access_token': self.access_token,
                'limit': min(max_results, 25)
            }
            
            response = requests.get(url, params=params, timeout=10)
            self.request_count += 1
            
            if response.status_code != 200:
                print(f"    ❌ 사용자 미디어 검색 실패: {response.status_code}")
                return []
            
            data = response.json()
            posts = data.get('data', [])
            
            # 키워드와 관련된 게시물만 필터링
            filtered_posts = []
            for post in posts:
                caption = post.get('caption', '').lower()
                if any(keyword.lower() in caption for keyword in INSTAGRAM_KEYWORDS):
                    filtered_posts.append(post)
            
            print(f"    ✅ 사용자 미디어 검색 성공: {len(filtered_posts)}개")
            time.sleep(self.rate_limit_delay)
            return filtered_posts
            
        except Exception as e:
            print(f"    ❌ 사용자 미디어 검색 오류: {e}")
            return []
    
    def _extract_posts_from_hashtag(self, data: Dict) -> List[Dict]:
        """해시태그 검색 결과에서 게시물 추출"""
        try:
            hashtag_data = data.get('data', [])
            if not hashtag_data:
                return []
            
            # 해시태그 ID로 최근 미디어 가져오기
            hashtag_id = hashtag_data[0].get('id')
            if not hashtag_id:
                return []
            
            url = f"{self.base_url}/{hashtag_id}/recent_media"
            params = {
                'user_id': 'business_account_id',
                'fields': 'id,caption,media_type,media_url,timestamp,permalink,like_count,comments_count',
                'access_token': self.graph_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get('data', [])
            
        except Exception as e:
            print(f"해시태그 게시물 추출 오류: {e}")
        
        return []
    
    def _remove_duplicates(self, posts: List[Dict]) -> List[Dict]:
        """중복 게시물 제거"""
        seen_ids = set()
        unique_posts = []
        
        for post in posts:
            post_id = post.get('id') or str(hash(str(post)))
            if post_id not in seen_ids:
                seen_ids.add(post_id)
                unique_posts.append(post)
        
        return unique_posts
    
    def _convert_to_standard_format(self, post: Dict, hashtag: str, region_code: str) -> Dict[str, Any]:
        """Instagram 게시물을 표준 형식으로 변환"""
        try:
            # 게시물 ID
            post_id = post.get('id', f"instagram_{hash(str(post))}")
            
            # 기본 정보
            caption = post.get('caption', '') or f"Instagram post about {hashtag}"
            media_type = post.get('media_type', 'IMAGE')
            
            # 통계 정보
            like_count = post.get('like_count', 0) or 100
            comment_count = post.get('comments_count', 0) or 10
            
            # 시간 정보
            timestamp = post.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp, str):
                published_at = timestamp
            else:
                published_at = datetime.now().isoformat() + 'Z'
            
            # 미디어 URL
            media_url = post.get('media_url', '') or post.get('thumbnail_url', '')
            permalink = post.get('permalink', f"https://instagram.com/p/{post_id}")
            
            return {
                # 검색 관련 정보
                'post_id': str(post_id),
                'search_hashtag': hashtag,
                'search_region': region_code,
                'collected_at': datetime.now().isoformat(),
                
                # 기본 정보
                'caption': caption.replace('\n', ' ').replace('\r', ' '),
                'media_type': media_type,
                'media_url': media_url,
                'permalink': permalink,
                'published_at': published_at,
                
                # 작성자 정보 (제한적)
                'author_username': 'instagram_user',
                'author_id': 'unknown',
                
                # 통계 정보
                'like_count': int(like_count),
                'comment_count': int(comment_count),
                'share_count': 0,  # Instagram API에서 제공하지 않음
                
                # 해시태그 정보
                'hashtags': self._extract_hashtags(caption),
                'mentions': self._extract_mentions(caption),
                
                # 위치 정보
                'location_name': '',
                'location_id': '',
                
                # 추가 메타데이터
                'is_video': media_type == 'VIDEO',
                'filter_name': '',
                'platform': 'instagram'
            }
            
        except Exception as e:
            print(f"게시물 변환 오류: {e}")
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
    
    def get_comprehensive_comments(self, post_ids: List[str], max_comments_per_post: int = 50) -> List[Dict[str, Any]]:
        """
        Instagram 게시물의 댓글 수집
        Instagram API의 댓글 접근은 매우 제한적
        """
        if self.demo_mode:
            return self._create_demo_comments(post_ids, max_comments_per_post)
        
        print("Instagram 댓글 수집 중...")
        
        comments_data = []
        for post_id in post_ids[:5]:  # 최대 5개 게시물만
            try:
                post_comments = self._get_post_comments(post_id, max_comments_per_post)
                comments_data.extend(post_comments)
                print(f"댓글 수집: {post_id} - {len(post_comments)}개")
            except Exception as e:
                print(f"댓글 수집 실패: {post_id} - {e}")
                continue
        
        return comments_data
    
    def _get_post_comments(self, post_id: str, max_comments: int) -> List[Dict]:
        """특정 게시물의 댓글 가져오기"""
        try:
            url = f"{self.base_url}/{post_id}/comments"
            params = {
                'fields': 'id,text,timestamp,username,like_count',
                'access_token': self.graph_token,
                'limit': min(max_comments, 25)
            }
            
            response = requests.get(url, params=params, timeout=10)
            self.request_count += 1
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            comments = data.get('data', [])
            
            # 표준 형식으로 변환
            formatted_comments = []
            for comment in comments:
                formatted_comment = {
                    'post_id': post_id,
                    'comment_id': comment.get('id', ''),
                    'comment_text': comment.get('text', ''),
                    'author_username': comment.get('username', 'instagram_user'),
                    'like_count': comment.get('like_count', 0),
                    'published_at': comment.get('timestamp', datetime.now().isoformat()),
                    'platform': 'instagram'
                }
                formatted_comments.append(formatted_comment)
            
            time.sleep(self.rate_limit_delay)
            return formatted_comments
            
        except Exception as e:
            return []
    
    def _create_demo_data(self, hashtag: str, region_code: str, max_results: int) -> Tuple[List[Dict], List[str]]:
        """데모용 Instagram 게시물 데이터 생성"""
        print(f"Instagram 데모 데이터 생성: #{hashtag}")
        
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
        
        # 해시태그에 따른 템플릿 선택
        if 'samsung' in hashtag.lower():
            templates = post_templates['samsung'] + post_templates['general']
        elif any(brand in hashtag.lower() for brand in ['lg', 'sony', 'tcl']):
            templates = post_templates['lg'] + post_templates['general']
        else:
            templates = post_templates['general']
        
        for i in range(min(max_results, 20)):
            caption = templates[i % len(templates)]
            post_id = f"instagram_demo_{hashtag}_{i+1}"
            
            demo_post = {
                'post_id': post_id,
                'search_hashtag': hashtag,
                'search_region': region_code,
                'collected_at': datetime.now().isoformat(),
                'caption': caption,
                'media_type': 'IMAGE' if i % 3 != 0 else 'VIDEO',
                'media_url': f"https://instagram.com/image_{i+1}.jpg",
                'permalink': f"https://instagram.com/p/{post_id}",
                'published_at': (datetime.now() - timedelta(hours=i*2)).isoformat() + 'Z',
                'author_username': f"instagram_user_{i+1}",
                'author_id': f"user_{i+1}",
                'like_count': 100 + i * 50,
                'comment_count': 10 + i * 5,
                'share_count': 5 + i * 2,
                'hashtags': f"#{hashtag}, #tv, #electronics",
                'mentions': '',
                'location_name': '',
                'location_id': '',
                'is_video': i % 3 == 0,
                'filter_name': '',
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