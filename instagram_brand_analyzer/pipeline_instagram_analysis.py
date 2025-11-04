"""
Instagram 데이터 수집 및 분석 통합 파이프라인

이 스크립트는 다음 작업을 수행합니다:
1. Instagram API로 게시물 정보 수집
2. Instagram API로 댓글 수집
3. 감정 분석 수행
4. 최종 테이블 생성
   - instagram_posts_final.csv: 게시물 정보
   - instagram_comments_final.csv: 댓글 정보 + 감정 분석

사용법:
    python pipeline_instagram_analysis.py --hashtag "samsungtv" --max-posts 20
"""

import os
import sys
# Add current directory first, then parent directory for config imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from datetime import datetime
import time

from collectors.instagram_api import InstagramAPI
from analyzers.sentiment import SentimentAnalyzer
from analyzers.comment_summarizer import CommentSummarizer

# Import from local config directory
current_dir = os.path.dirname(os.path.abspath(__file__))
local_config_path = os.path.join(current_dir, 'config')
if local_config_path not in sys.path:
    sys.path.insert(0, local_config_path)

from db_manager import InstagramDBManager


class InstagramPipeline:
    """Instagram 데이터 수집 및 분석 통합 파이프라인"""

    def __init__(self, output_dir='data', use_database=True):
        """
        파이프라인 초기화

        Args:
            output_dir (str): 출력 디렉토리
            use_database (bool): PostgreSQL 데이터베이스 사용 여부
        """
        self.output_dir = output_dir
        self.use_database = use_database
        os.makedirs(output_dir, exist_ok=True)

        # Analyzer 초기화
        self.instagram_api = InstagramAPI()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.comment_summarizer = CommentSummarizer()

        # Database 초기화
        if self.use_database:
            self.db_manager = InstagramDBManager()
        else:
            self.db_manager = None

    def run(self, keyword, max_posts=30, max_comments_per_post=50,
            analyze_sentiment=True):
        """
        전체 파이프라인 실행

        Args:
            keyword (str): 검색 키워드
            max_posts (int): 최대 게시물 수
            max_comments_per_post (int): 게시물당 최대 댓글 수
            analyze_sentiment (bool): 감정 분석 여부

        Returns:
            tuple: (posts_df, comments_df)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("="*80)
        print("Instagram Data Collection & Analysis Pipeline")
        print("="*80)
        print(f"Keyword: {keyword}")
        print(f"Max posts: {max_posts}")
        print(f"Max comments per post: {max_comments_per_post}")
        print(f"Analyze sentiment: {analyze_sentiment}")
        print("="*80)
        print()

        # Step 1: 게시물 데이터 수집
        print("[Step 1/4] Collecting post data from Instagram RapidAPI...")
        post_data, post_ids = self.instagram_api.get_comprehensive_post_data(
            keyword=keyword,
            max_results=max_posts
        )

        if not post_data:
            print("No posts found!")
            return None, None

        posts_df = pd.DataFrame(post_data)
        print(f"Collected {len(posts_df)} posts")

        # Step 2: 댓글 데이터 수집
        print()
        print("[Step 2/4] Collecting comments from Instagram API...")
        comments_data = self.instagram_api.get_comprehensive_comments(
            post_pks=post_ids,  # post_ids are actually PKs returned from API
            max_comments_per_post=max_comments_per_post
        )

        if not comments_data:
            print("No comments found!")
            comments_df = pd.DataFrame()
        else:
            comments_df = pd.DataFrame(comments_data)
            print(f"Collected {len(comments_df)} comments")

        # Step 3: 감정 분석
        if analyze_sentiment and len(comments_df) > 0:
            print()
            print("[Step 3/4] Analyzing comment sentiment...")

            # 댓글 데이터를 sentiment analyzer 형식으로 변환
            formatted_comments = []
            for _, row in comments_df.iterrows():
                formatted_comment = {
                    'video_id': row['post_id'],  # Instagram에서는 post_id를 video_id로 매핑
                    'comment_id': row['comment_id'],
                    'comment_text': row['comment_text'],
                    'like_count': row['like_count'],
                    'published_at': row['published_at']
                }
                formatted_comments.append(formatted_comment)

            # 감정 분석 수행
            sentiment_results = self.sentiment_analyzer.analyze_comment_sentiment(formatted_comments)

            if sentiment_results:
                # 감정 분석 결과를 데이터프레임으로 변환
                sentiment_df = pd.DataFrame(sentiment_results)

                # 컬럼명 매핑 (sentiment_category -> sentiment/sentiment_label)
                if 'sentiment_category' in sentiment_df.columns:
                    sentiment_df['sentiment'] = sentiment_df['sentiment_category']
                    sentiment_df['sentiment_label'] = sentiment_df['sentiment_category']

                # 기존 댓글 데이터와 병합
                merge_columns = ['comment_id']
                if 'sentiment' in sentiment_df.columns:
                    merge_columns.extend(['sentiment', 'sentiment_score', 'sentiment_label'])
                elif 'sentiment_score' in sentiment_df.columns:
                    merge_columns.append('sentiment_score')

                comments_df = comments_df.merge(
                    sentiment_df[merge_columns],
                    on='comment_id',
                    how='left'
                )

                print(f"Analyzed sentiment for {len(sentiment_results)} comments")
        else:
            print()
            print("[Step 3/4] Skipping sentiment analysis...")

        # Step 3.5: 댓글 요약 (OpenAI)
        if len(comments_df) > 0:
            print()
            print("[Step 3.5/5] Summarizing comments using OpenAI...")

            # 게시물별로 댓글 그룹화
            post_groups = comments_df.groupby('post_id')
            comment_summaries = []

            for post_id, post_comments in post_groups:
                print(f"  Summarizing {len(post_comments)} comments for post {post_id[:10]}...")

                # 댓글을 딕셔너리 리스트로 변환
                comments_list = post_comments.to_dict('records')

                # 요약 생성
                summary = self.comment_summarizer.summarize_comments_for_video(comments_list)
                summary['post_id'] = post_id

                comment_summaries.append(summary)
                time.sleep(2)  # OpenAI API rate limit

                # 10개마다 추가 대기
                if len(comment_summaries) % 10 == 0:
                    print(f"  >>> Processed {len(comment_summaries)} posts, waiting 10 seconds...")
                    time.sleep(10)

            # 댓글 요약 데이터프레임
            comment_summaries_df = pd.DataFrame(comment_summaries)

            # comment_text_summary 컬럼 생성
            comment_summaries_df['comment_text_summary'] = comment_summaries_df['summary']

            # 게시물 데이터와 병합
            posts_df = posts_df.merge(
                comment_summaries_df[['post_id', 'comment_text_summary',
                                     'key_themes', 'sentiment_summary']],
                on='post_id',
                how='left',
                suffixes=('', '_comments')
            )

            print(f"Summarized comments for {len(comment_summaries)} posts")
        else:
            print()
            print("[Step 3.5/5] Skipping comment summarization (no comments)...")

        # Step 4: 최종 테이블 생성 및 저장
        print()
        print("[Step 5/5] Saving data to database...")

        # Debug: Check if comment_text_summary is in posts_df
        if 'comment_text_summary' in posts_df.columns:
            non_null_summaries = posts_df['comment_text_summary'].notna().sum()
            print(f"  [DEBUG] comment_text_summary column found: {non_null_summaries}/{len(posts_df)} posts have summaries")
        else:
            print(f"  [DEBUG] comment_text_summary column NOT found in posts_df!")
            print(f"  [DEBUG] Available columns: {list(posts_df.columns)}")

        # posts_final: 게시물 정보 (결과 테이블 구조 반영)
        post_columns = [
            'post_id', 'search_keyword', 'collected_at',
            'author_username', 'author_id', 'caption', 'media_type', 'media_url',
            'permalink', 'published_at', 'like_count', 'comment_count', 'play_count',
            'share_count', 'hashtags', 'mentions', 'is_video',
            'video_content_summary', 'comment_text_summary', 'platform'
        ]

        # 존재하는 컬럼만 선택
        available_post_cols = [col for col in post_columns if col in posts_df.columns]
        print(f"  [DEBUG] Columns to save: {available_post_cols}")
        posts_final = posts_df[available_post_cols].copy()

        # comments_final: 댓글 정보 + 감정 분석
        if len(comments_df) > 0:
            comment_columns = [
                'post_id', 'comment_id', 'comment_text', 'author_username',
                'like_count', 'published_at', 'platform'
            ]

            # 감정 분석 결과가 있으면 추가
            if 'sentiment' in comments_df.columns:
                comment_columns.extend(['sentiment', 'sentiment_score', 'sentiment_label'])

            # 존재하는 컬럼만 선택
            available_comment_cols = [col for col in comment_columns if col in comments_df.columns]
            comments_final = comments_df[available_comment_cols].copy()
        else:
            comments_final = pd.DataFrame()

        # PostgreSQL에 저장
        if self.use_database and self.db_manager:
            if self.db_manager.connect():
                # 테이블 생성
                self.db_manager.create_tables()

                # 데이터 삽입
                post_count = self.db_manager.insert_posts(posts_final)
                if len(comments_final) > 0:
                    comment_count = self.db_manager.insert_comments(comments_final)
                else:
                    comment_count = 0

                print(f"Saved to PostgreSQL:")
                print(f"  - {post_count} posts")
                print(f"  - {comment_count} comments")

                self.db_manager.disconnect()
            else:
                print("Warning: Failed to connect to database")
        else:
            print("Database storage is disabled")

        print()
        print("="*80)
        print("Pipeline completed successfully!")
        print("="*80)
        print(f"Total posts processed: {len(posts_final)}")
        print(f"Total comments processed: {len(comments_final)}")
        if 'sentiment' in comments_final.columns:
            print(f"Comments with sentiment analysis: {comments_final['sentiment'].notna().sum()}")

        # 데이터베이스 통계 출력
        if self.use_database and self.db_manager:
            if self.db_manager.connect():
                print()
                print("Database Statistics:")
                print(f"  Total posts in DB: {self.db_manager.get_post_count()}")
                print(f"  Total comments in DB: {self.db_manager.get_comment_count()}")
                self.db_manager.disconnect()

        return posts_final, comments_final


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Instagram 데이터 수집 및 분석 통합 파이프라인',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--keyword',
        type=str,
        required=True,
        help='검색 키워드 (예: "Samsung TV")'
    )

    parser.add_argument(
        '--max-posts',
        type=int,
        default=30,
        help='최대 게시물 수 (기본값: 30)'
    )

    parser.add_argument(
        '--max-comments',
        type=int,
        default=50,
        help='게시물당 최대 댓글 수 (기본값: 50)'
    )

    parser.add_argument(
        '--no-sentiment',
        action='store_true',
        help='감정 분석 건너뛰기'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='출력 디렉토리 (기본값: data)'
    )

    parser.add_argument(
        '--no-database',
        action='store_true',
        help='PostgreSQL 데이터베이스에 저장하지 않음'
    )

    args = parser.parse_args()

    # 파이프라인 실행
    pipeline = InstagramPipeline(
        output_dir=args.output_dir,
        use_database=not args.no_database
    )

    posts_df, comments_df = pipeline.run(
        keyword=args.keyword,
        max_posts=args.max_posts,
        max_comments_per_post=args.max_comments,
        analyze_sentiment=not args.no_sentiment
    )


if __name__ == "__main__":
    main()
