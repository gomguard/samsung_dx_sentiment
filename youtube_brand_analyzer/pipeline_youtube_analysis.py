"""
YouTube 데이터 수집 및 분석 통합 파이프라인

이 스크립트는 다음 작업을 수행합니다:
1. YouTube API로 영상 정보 수집
2. YouTube API로 댓글 수집
3. 영상 자막 추출 및 요약 (video_content_summary)
4. 댓글 요약 (comment_text_summary)
5. 최종 테이블 생성
   - videos_final.csv: 영상 정보 + 요약
   - comments_final.csv: 댓글 정보

사용법:
    python pipeline_youtube_analysis.py --keyword "Samsung TV" --max-videos 10
"""

import os
import sys
# Add current directory first, then parent directory for config imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from datetime import datetime
import time

from collectors.youtube_api import YouTubeAnalyzer
from analyzers.video_summarizer import VideoSummarizer
from analyzers.comment_summarizer import CommentSummarizer
from config.db_manager import YouTubeDBManager


class YouTubePipeline:
    """YouTube 데이터 수집 및 분석 통합 파이프라인"""

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
        self.youtube_api = YouTubeAnalyzer()
        self.video_summarizer = VideoSummarizer()
        self.comment_summarizer = CommentSummarizer()

        # Database 초기화
        if self.use_database:
            self.db_manager = YouTubeDBManager()
        else:
            self.db_manager = None

    def run(self, keyword, max_videos=50, max_comments_per_video=100,
            region_code="US", summarize_videos=True, summarize_comments=True):
        """
        전체 파이프라인 실행

        Args:
            keyword (str): 검색 키워드
            max_videos (int): 최대 영상 수
            max_comments_per_video (int): 영상당 최대 댓글 수
            region_code (str): 지역 코드
            summarize_videos (bool): 영상 요약 여부
            summarize_comments (bool): 댓글 요약 여부

        Returns:
            tuple: (videos_df, comments_df)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("="*80)
        print("YouTube Data Collection & Analysis Pipeline")
        print("="*80)
        print(f"Keyword: {keyword}")
        print(f"Max videos: {max_videos}")
        print(f"Max comments per video: {max_comments_per_video}")
        print(f"Region: {region_code}")
        print(f"Summarize videos: {summarize_videos}")
        print(f"Summarize comments: {summarize_comments}")
        print("="*80)
        print()

        # Step 1: 영상 데이터 수집
        print("[Step 1/5] Collecting video data from YouTube API...")
        video_data, video_ids = self.youtube_api.get_comprehensive_video_data(
            keyword=keyword.lower(),
            region_code=region_code,
            max_results=max_videos
        )

        if not video_data:
            print("No videos found!")
            return None, None

        videos_df = pd.DataFrame(video_data)
        print(f"Collected {len(videos_df)} videos")

        # Step 2: 댓글 데이터 수집
        print()
        print("[Step 2/5] Collecting comments from YouTube API...")
        comments_data = self.youtube_api.get_comprehensive_comments(
            video_ids=video_ids,
            max_comments_per_video=max_comments_per_video
        )

        comments_df = pd.DataFrame(comments_data)
        print(f"Collected {len(comments_df)} comments")

        # Step 3: 영상 요약 (자막 기반)
        if summarize_videos:
            print()
            print("[Step 3/5] Summarizing videos (transcript-based)...")
            video_summaries = []

            for idx, row in videos_df.iterrows():
                video_id = row['video_id']
                title = row.get('title', '')
                description = row.get('description', '')

                print(f"  [{idx+1}/{len(videos_df)}] Summarizing video: {video_id}")

                summary = self.video_summarizer.summarize_video(
                    video_id=video_id,
                    title=title,
                    description=description
                )

                video_summaries.append(summary)

                # Rate limiting: 자막 API와 OpenAI API 모두 고려
                time.sleep(2)  # 자막 요청 사이 2초 대기

                # 10개마다 추가 대기 (배치 처리)
                if (idx + 1) % 10 == 0:
                    print(f"  >>> Processed {idx+1} videos, waiting 10 seconds to avoid rate limits...")
                    time.sleep(10)

            # 요약 데이터프레임으로 변환
            summaries_df = pd.DataFrame(video_summaries)

            # 리스트/딕셔너리를 문자열로 변환
            for col in ['key_topics', 'key_features_discussed']:
                if col in summaries_df.columns:
                    summaries_df[col] = summaries_df[col].apply(
                        lambda x: '; '.join(x) if isinstance(x, list) else str(x)
                    )

            if 'product_mentions' in summaries_df.columns:
                import json
                summaries_df['product_mentions'] = summaries_df['product_mentions'].apply(
                    lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else str(x)
                )

            # video_content_summary 컬럼 생성 (data_structure.txt 기준)
            summaries_df['video_content_summary'] = summaries_df['summary']

            # 영상 데이터와 병합
            videos_df = videos_df.merge(
                summaries_df[['video_id', 'video_content_summary', 'has_transcript',
                             'key_topics', 'sentiment', 'target_audience']],
                on='video_id',
                how='left'
            )

            print(f"Summarized {len(video_summaries)} videos")
        else:
            print()
            print("[Step 3/5] Skipping video summarization...")

        # Step 4: 댓글 요약 (비디오별)
        if summarize_comments and len(comments_df) > 0:
            print()
            print("[Step 4/5] Summarizing comments (per video)...")

            comment_summaries = []

            for video_id in videos_df['video_id']:
                video_comments = comments_df[comments_df['video_id'] == video_id]

                if len(video_comments) == 0:
                    continue

                print(f"  Summarizing comments for video: {video_id} ({len(video_comments)} comments)")

                # 댓글을 딕셔너리 리스트로 변환
                comments_list = video_comments.to_dict('records')

                # 요약 생성
                summary = self.comment_summarizer.summarize_comments_for_video(comments_list)
                summary['video_id'] = video_id

                comment_summaries.append(summary)
                time.sleep(2)  # OpenAI API rate limit

                # 10개마다 추가 대기
                if len(comment_summaries) % 10 == 0:
                    print(f"  >>> Processed {len(comment_summaries)} videos, waiting 10 seconds...")
                    time.sleep(10)

            # 댓글 요약 데이터프레임
            comment_summaries_df = pd.DataFrame(comment_summaries)

            # comment_text_summary 컬럼 생성 (data_structure.txt 기준)
            comment_summaries_df['comment_text_summary'] = comment_summaries_df['summary']

            # 영상 데이터와 병합
            videos_df = videos_df.merge(
                comment_summaries_df[['video_id', 'comment_text_summary',
                                     'key_themes', 'sentiment_summary']],
                on='video_id',
                how='left',
                suffixes=('', '_comments')
            )

            print(f"Summarized comments for {len(comment_summaries)} videos")
        else:
            print()
            print("[Step 4/5] Skipping comment summarization...")

        # Step 5: 최종 테이블 생성 및 저장
        print()
        print("[Step 5/5] Saving data to database...")

        # videos_final: data_structure.txt 기준 컬럼 선택
        video_columns = [
            'video_id', 'title', 'description', 'published_at',
            'channel_country', 'channel_custom_url',
            'channel_subscriber_count', 'channel_video_count',
            'view_count', 'like_count', 'comment_count',
            'video_content_summary', 'comment_text_summary'
        ]

        # 존재하는 컬럼만 선택
        available_video_cols = [col for col in video_columns if col in videos_df.columns]
        videos_final = videos_df[available_video_cols].copy()

        # comments_final: data_structure.txt 기준 컬럼 선택
        comment_columns = [
            'video_id', 'comment_id', 'comment_type', 'parent_comment_id',
            'comment_text_display', 'like_count', 'reply_count'
        ]

        # 존재하는 컬럼만 선택
        available_comment_cols = [col for col in comment_columns if col in comments_df.columns]
        comments_final = comments_df[available_comment_cols].copy()

        # PostgreSQL에 저장
        if self.use_database and self.db_manager:
            if self.db_manager.connect():
                # 테이블 생성
                self.db_manager.create_tables()

                # 데이터 삽입
                video_count = self.db_manager.insert_videos(videos_final)
                comment_count = self.db_manager.insert_comments(comments_final)

                print(f"Saved to PostgreSQL:")
                print(f"  - {video_count} videos")
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
        print(f"Total videos processed: {len(videos_final)}")
        print(f"Total comments processed: {len(comments_final)}")
        if 'video_content_summary' in videos_final.columns:
            print(f"Videos with content summary: {videos_final['video_content_summary'].notna().sum()}")
        if 'comment_text_summary' in videos_final.columns:
            print(f"Videos with comment summary: {videos_final['comment_text_summary'].notna().sum()}")

        # 데이터베이스 통계 출력
        if self.use_database and self.db_manager:
            if self.db_manager.connect():
                print()
                print("Database Statistics:")
                print(f"  Total videos in DB: {self.db_manager.get_video_count()}")
                print(f"  Total comments in DB: {self.db_manager.get_comment_count()}")
                self.db_manager.disconnect()

        return videos_final, comments_final


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description='YouTube 데이터 수집 및 분석 통합 파이프라인',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--keyword',
        type=str,
        required=True,
        help='검색 키워드 (예: "Samsung TV")'
    )

    parser.add_argument(
        '--max-videos',
        type=int,
        default=50,
        help='최대 영상 수 (기본값: 50)'
    )

    parser.add_argument(
        '--max-comments',
        type=int,
        default=100,
        help='영상당 최대 댓글 수 (기본값: 100)'
    )

    parser.add_argument(
        '--region',
        type=str,
        default='US',
        help='지역 코드 (기본값: US)'
    )

    parser.add_argument(
        '--no-video-summary',
        action='store_true',
        help='영상 요약 건너뛰기'
    )

    parser.add_argument(
        '--no-comment-summary',
        action='store_true',
        help='댓글 요약 건너뛰기'
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
    pipeline = YouTubePipeline(
        output_dir=args.output_dir,
        use_database=not args.no_database
    )

    videos_df, comments_df = pipeline.run(
        keyword=args.keyword,
        max_videos=args.max_videos,
        max_comments_per_video=args.max_comments,
        region_code=args.region,
        summarize_videos=not args.no_video_summary,
        summarize_comments=not args.no_comment_summary
    )


if __name__ == "__main__":
    main()
