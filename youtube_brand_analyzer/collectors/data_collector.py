import pandas as pd
import os
from datetime import datetime
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import *
from collectors.youtube_api import YouTubeAnalyzer
from analyzers.sentiment import SentimentAnalyzer

class YouTubeBrandCollector:
    def __init__(self):
        """YouTube 브랜드 데이터 수집기 초기화"""
        self.youtube_analyzer = YouTubeAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.collected_data = {
            'videos': [],      # 포괄적인 비디오 정보 (메타데이터 + 통계 + 채널정보)
            'comments': []     # 포괄적인 댓글 정보 (원본 + 감정분석)
        }
    
    def collect_brand_data(self, keyword, regions=None, max_results=50):
        """브랜드 키워드로 전체 데이터 수집 (2테이블 구조)"""
        if regions is None:
            regions = SEARCH_REGIONS
        
        print(f"\n🔍 브랜드 분석 시작: '{keyword}'")
        print(f"대상 지역: {regions}")
        print("=" * 60)
        
        all_video_ids = []
        
        for region in regions:
            print(f"\n📍 지역: {region}")
            
            # 1. 포괄적인 비디오 데이터 수집 (모든 정보 한번에)
            video_data, video_ids = self.youtube_analyzer.get_comprehensive_video_data(
                keyword=keyword,
                region_code=region,
                max_results=max_results
            )
            
            if not video_ids:
                print(f"  ❌ {region}에서 검색 결과 없음")
                continue
            
            # 비디오 데이터 저장
            self.collected_data['videos'].extend(video_data)
            all_video_ids.extend(video_ids)
        
        # 2. 포괄적인 댓글 데이터 수집
        if all_video_ids:
            print(f"\n💬 댓글 수집 중...")
            # API 절약을 위해 상위 30개 비디오만 댓글 수집
            top_video_ids = all_video_ids[:30] 
            comments_data = self.youtube_analyzer.get_comprehensive_comments(top_video_ids)
            
            # 3. 댓글에 감정 분석 추가
            if comments_data:
                print(f"\n🧠 댓글 감정 분석 중...")
                comments_with_sentiment = self._add_sentiment_to_comments(comments_data)
                self.collected_data['comments'] = comments_with_sentiment
        
        # 4. 데이터 저장
        self._save_comprehensive_data(keyword)
        
        # 5. 수집 요약 출력
        self._print_comprehensive_summary(keyword)
        
        print(f"\n✅ 브랜드 분석 완료: '{keyword}'")
        print(f"API 사용량: {self.youtube_analyzer.get_quota_usage()} 요청")
        
        return self.collected_data
    
    def _add_sentiment_to_comments(self, comments_data):
        """댓글 데이터에 감정 분석 결과 추가"""
        # 기존 감정 분석 함수를 사용하되, 새로운 필드 구조에 맞게 조정
        comments_with_sentiment = []
        
        for comment in comments_data:
            # 감정 분석 수행
            sentiment_result = self.sentiment_analyzer.analyze_single_comment(
                comment['comment_text_display']
            )
            
            # 기존 댓글 데이터에 감정 분석 결과 추가
            comment_with_sentiment = comment.copy()
            comment_with_sentiment.update({
                'sentiment_score': sentiment_result.get('sentiment_score', 0.0),
                'sentiment_category': sentiment_result.get('sentiment_category', 'neutral'),
                'subjectivity_score': sentiment_result.get('subjectivity_score', 0.0),
                'brand_mentions': sentiment_result.get('brand_mentions', ''),
                'competitor_mentions': sentiment_result.get('competitor_mentions', ''),
                'analyzed_at': datetime.now().isoformat()
            })
            
            comments_with_sentiment.append(comment_with_sentiment)
        
        return comments_with_sentiment
    
    def _save_comprehensive_data(self, keyword):
        """2테이블 구조로 데이터 저장"""
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 비디오 테이블 (모든 비디오 정보 통합)
        if self.collected_data['videos']:
            filename = f"videos_{keyword.replace(' ', '_')}_{date_str}.csv"
            df_videos = pd.DataFrame(self.collected_data['videos'])
            df_videos.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding=CSV_ENCODING)
            print(f"  💾 videos 테이블 저장: {len(df_videos)}개 비디오")
        
        # 2. 댓글 테이블 (모든 댓글 정보 + 감정분석)
        if self.collected_data['comments']:
            filename = f"comments_{keyword.replace(' ', '_')}_{date_str}.csv"
            df_comments = pd.DataFrame(self.collected_data['comments'])
            df_comments.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding=CSV_ENCODING)
            print(f"  💾 comments 테이블 저장: {len(df_comments)}개 댓글")
    
    def _print_comprehensive_summary(self, keyword):
        """2테이블 구조 수집 결과 요약 출력"""
        print(f"\n📋 수집 결과 요약 - '{keyword}'")
        print("=" * 50)
        
        # 비디오 요약
        videos = self.collected_data['videos']
        if videos:
            df_videos = pd.DataFrame(videos)
            total_videos = len(videos)
            regions = list(set([v['search_region'] for v in videos]))
            total_views = df_videos['view_count'].sum()
            total_likes = df_videos['like_count'].sum()
            avg_views = df_videos['view_count'].mean()
            total_subscribers = df_videos['channel_subscriber_count'].sum()
            
            print(f"🎬 비디오: {total_videos}개 (지역: {', '.join(regions)})")
            print(f"👀 총 조회수: {total_views:,}회")
            print(f"👍 총 좋아요: {total_likes:,}개")
            print(f"📊 평균 조회수: {avg_views:,.0f}회")
            print(f"📺 총 구독자: {total_subscribers:,}명")
        
        # 댓글 요약
        comments = self.collected_data['comments']
        if comments:
            df_comments = pd.DataFrame(comments)
            total_comments = len(comments)
            top_level_comments = len(df_comments[df_comments['comment_type'] == 'top_level'])
            replies = len(df_comments[df_comments['comment_type'] == 'reply'])
            
            print(f"💬 댓글: {total_comments}개 (최상위: {top_level_comments}, 답글: {replies})")
            
            # 감정 분석 요약
            positive_ratio = len(df_comments[df_comments['sentiment_category'] == 'positive']) / len(df_comments)
            negative_ratio = len(df_comments[df_comments['sentiment_category'] == 'negative']) / len(df_comments)
            avg_sentiment = df_comments['sentiment_score'].mean()
            
            print(f"😊 긍정 댓글: {positive_ratio:.1%}")
            print(f"😞 부정 댓글: {negative_ratio:.1%}")
            print(f"🎯 평균 감정 점수: {avg_sentiment:.3f}")
    
    def _save_all_data(self, keyword):
        """수집된 모든 데이터를 파일별로 저장"""
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        region_str = "_".join(SEARCH_REGIONS)
        
        # 01. 비디오 메타데이터
        if self.collected_data['videos']:
            filename = FILE_TEMPLATES['01_video_metadata'].format(
                keyword=keyword.replace(' ', '_'),
                region=region_str,
                date=date_str
            )
            df = pd.DataFrame(self.collected_data['videos'])
            df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding=CSV_ENCODING)
            print(f"  💾 01_video_metadata 저장: {len(df)}개 비디오")
        
        # 02. 비디오 통계
        if self.collected_data['statistics']:
            filename = FILE_TEMPLATES['02_video_statistics'].format(
                keyword=keyword.replace(' ', '_'),
                region=region_str,
                date=date_str
            )
            df = pd.DataFrame(self.collected_data['statistics'])
            df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding=CSV_ENCODING)
            print(f"  💾 02_video_statistics 저장: {len(df)}개 비디오")
        
        # 03. 채널 정보
        if self.collected_data['channels']:
            filename = FILE_TEMPLATES['03_channel_info'].format(
                keyword=keyword.replace(' ', '_'),
                region=region_str,
                date=date_str
            )
            df = pd.DataFrame(self.collected_data['channels'])
            df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding=CSV_ENCODING)
            print(f"  💾 03_channel_info 저장: {len(df)}개 채널")
        
        # 04. 원본 댓글
        if self.collected_data['comments']:
            filename = FILE_TEMPLATES['04_comments_raw'].format(
                keyword=keyword.replace(' ', '_'),
                region=region_str,
                date=date_str
            )
            df = pd.DataFrame(self.collected_data['comments'])
            df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding=CSV_ENCODING)
            print(f"  💾 04_comments_raw 저장: {len(df)}개 댓글")
        
        # 05. 감정 분석 결과
        if self.collected_data['sentiments']:
            filename = FILE_TEMPLATES['05_comments_sentiment'].format(
                keyword=keyword.replace(' ', '_'),
                region=region_str,
                date=date_str
            )
            df = pd.DataFrame(self.collected_data['sentiments'])
            df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding=CSV_ENCODING)
            print(f"  💾 05_comments_sentiment 저장: {len(df)}개 댓글")
        
        # 06. 비디오별 감정 요약
        if self.collected_data['video_sentiment_summary']:
            filename = FILE_TEMPLATES['06_trend_analysis'].format(
                keyword=keyword.replace(' ', '_'),
                region=region_str,
                date=date_str
            )
            df = pd.DataFrame(self.collected_data['video_sentiment_summary'])
            df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding=CSV_ENCODING)
            print(f"  💾 06_trend_analysis 저장: {len(df)}개 비디오")
    
    def _print_collection_summary(self, keyword):
        """수집 결과 요약 출력"""
        print(f"\n📋 수집 결과 요약 - '{keyword}'")
        print("=" * 50)
        
        # 비디오 수집 요약
        videos = self.collected_data['videos']
        if videos:
            total_videos = len(videos)
            regions = list(set([v['search_region'] for v in videos]))
            print(f"🎬 비디오: {total_videos}개 (지역: {', '.join(regions)})")
        
        # 통계 요약
        statistics = self.collected_data['statistics']
        if statistics:
            df_stats = pd.DataFrame(statistics)
            total_views = df_stats['view_count'].sum()
            total_likes = df_stats['like_count'].sum()
            avg_views = df_stats['view_count'].mean()
            print(f"👀 총 조회수: {total_views:,}회")
            print(f"👍 총 좋아요: {total_likes:,}개")
            print(f"📊 평균 조회수: {avg_views:,.0f}회")
        
        # 채널 요약
        channels = self.collected_data['channels']
        if channels:
            df_channels = pd.DataFrame(channels)
            total_subscribers = df_channels['subscriber_count'].sum()
            print(f"📺 채널: {len(channels)}개 (총 구독자: {total_subscribers:,}명)")
        
        # 댓글 및 감정 요약
        comments = self.collected_data['comments']
        sentiments = self.collected_data['sentiments']
        if comments:
            print(f"💬 댓글: {len(comments)}개")
            
        if sentiments:
            df_sentiment = pd.DataFrame(sentiments)
            positive_ratio = len(df_sentiment[df_sentiment['sentiment_category'] == 'positive']) / len(df_sentiment)
            negative_ratio = len(df_sentiment[df_sentiment['sentiment_category'] == 'negative']) / len(df_sentiment)
            avg_sentiment = df_sentiment['sentiment_score'].mean()
            
            print(f"😊 긍정 댓글: {positive_ratio:.1%}")
            print(f"😞 부정 댓글: {negative_ratio:.1%}")
            print(f"🎯 평균 감정 점수: {avg_sentiment:.3f}")
    
    def get_collection_data(self):
        """수집된 데이터 반환"""
        return self.collected_data