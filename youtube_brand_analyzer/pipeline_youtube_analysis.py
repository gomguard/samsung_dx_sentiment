"""
YouTube 데이터 수집 및 분석 통합 파이프라인

이 스크립트는 다음 작업을 수행합니다:
1. YouTube API로 영상 정보 수집
2. YouTube API로 댓글 수집
3. 댓글 요약 (comment_text_summary)
4. 최종 테이블 생성
   - videos_final.csv: 영상 정보 + 댓글 요약
   - comments_final.csv: 댓글 정보

사용법:
    python pipeline_youtube_analysis.py --keyword "Samsung TV" --max-videos 10
"""

import os
import sys

# Add current directory first, then parent directory for config imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from datetime import datetime
import time
import json

from collectors.youtube_api import YouTubeAnalyzer
from analyzers.comment_summarizer import CommentSummarizer
from analyzers.comment_sentiment_analyzer import CommentSentimentAnalyzer
from analyzers.video_content_analyzer import VideoContentAnalyzer
from config.db_manager import YouTubeDBManager


class YouTubePipeline:
    """YouTube 데이터 수집 및 분석 통합 파이프라인"""

    def __init__(
        self, output_dir="data", use_database=True, save_raw_data=False, save_csv=False
    ):
        """
        파이프라인 초기화

        Args:
            output_dir (str): 출력 디렉토리
            use_database (bool): PostgreSQL 데이터베이스 사용 여부
            save_raw_data (bool): API 원본 데이터 저장 여부
            save_csv (bool): CSV 파일 저장 여부
        """
        self.output_dir = output_dir
        self.use_database = use_database
        self.save_raw_data = save_raw_data
        self.save_csv = save_csv

        # 디렉토리 구조 생성
        os.makedirs(output_dir, exist_ok=True)
        self.raw_data_dir = os.path.join(output_dir, "raw_data")
        self.processed_data_dir = os.path.join(output_dir, "processed_data")
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)

        # Analyzer 초기화
        self.youtube_api = YouTubeAnalyzer()
        self.comment_summarizer = CommentSummarizer()
        self.sentiment_analyzer = CommentSentimentAnalyzer()
        self.video_content_analyzer = VideoContentAnalyzer()

        # Database 초기화
        if self.use_database:
            self.db_manager = YouTubeDBManager()
        else:
            self.db_manager = None

    def run(
        self,
        keyword,
        max_videos=50,
        max_comments_per_video=100,
        region_code="US",
        category=None,
        summarize_comments=True,
        analyze_sentiment=False,
    ):
        """
        전체 파이프라인 실행

        Args:
            keyword (str): 검색 키워드
            max_videos (int): 최대 영상 수
            max_comments_per_video (int): 영상당 최대 댓글 수
            region_code (str): 지역 코드
            summarize_comments (bool): 댓글 요약 여부
            analyze_sentiment (bool): 댓글 감정 분석 여부 (OpenAI 사용, 비용 발생)

        Returns:
            tuple: (videos_df, comments_df)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("=" * 80)
        print("YouTube Data Collection & Analysis Pipeline")
        print("=" * 80)
        print(f"Keyword: {keyword}")
        print(f"Max videos: {max_videos}")
        print(f"Max comments per video: {max_comments_per_video}")
        print(f"Region: {region_code}")
        print(f"Summarize comments: {summarize_comments}")
        print(f"Analyze sentiment: {analyze_sentiment}")
        print("=" * 80)
        print()

        # Step 1: 영상 데이터 수집 (필터 적용: US, category 28, engagement >= 2%, subscribers >= 10k)
        print(
            f"[Step 1/4] Collecting video data from YouTube API ({max_videos} videos with quality filter)..."
        )
        video_data, video_ids, raw_video_data = (
            self.youtube_api.get_comprehensive_video_data(
                keyword=keyword.lower(),
                region_code=region_code,
                max_results=max_videos,
                apply_quality_filter=True,
            )
        )

        if not video_data:
            print("No videos found!")
            return None, None

        videos_df = pd.DataFrame(video_data)
        raw_videos_df = (
            pd.DataFrame(raw_video_data) if raw_video_data else pd.DataFrame()
        )

        # Add keyword and category to videos_df
        videos_df["keyword"] = keyword
        if category:
            videos_df["category"] = category

        print(f"Collected {len(videos_df)} filtered videos")
        if len(raw_videos_df) > 0:
            print(f"Raw data: {len(raw_videos_df)} total videos")

        # Step 1.2: Analyze video content (brand/series extraction + sentiment)
        print()
        print("[Step 1.2/5] Analyzing video content (brand, series, sentiment)...")

        for idx, row in videos_df.iterrows():
            video_id = row['video_id']
            title = row.get('title', '')
            description = row.get('description', '')
            video_category = row.get('category', None)

            print(f"  Analyzing video {idx+1}/{len(videos_df)}: {video_id[:20]}...")

            # Extract brand and series (category 전달)
            brand_info = self.video_content_analyzer.extract_brand_and_series(
                title, description, category=video_category
            )
            videos_df.at[idx, 'reviewed_brand'] = brand_info['reviewed_brand']
            videos_df.at[idx, 'reviewed_series'] = brand_info['reviewed_series']
            videos_df.at[idx, 'reviewed_item'] = brand_info['reviewed_item']

            # Analyze sentiment
            sentiment_score = self.video_content_analyzer.analyze_product_sentiment(
                title, description,
                brand_info['reviewed_brand'],
                brand_info['reviewed_series']
            )
            videos_df.at[idx, 'product_sentiment_score'] = sentiment_score

            # Rate limiting
            time.sleep(2)

            # Every 10 videos, extra delay
            if (idx + 1) % 10 == 0:
                print(f"  >>> Processed {idx+1} videos, waiting 10 seconds...")
                time.sleep(10)

        print(f"Video content analysis completed for {len(videos_df)} videos")

        # Step 1.5: Raw 데이터 즉시 저장 (댓글 수집 전)
        print()
        print("[Step 1.5/5] Saving raw and filtered videos to database...")

        if self.use_database and self.db_manager:
            if self.db_manager.connect():
                # 테이블 생성
                self.db_manager.create_tables()

                # videos_final 준비 (댓글 요약 없이)
                video_columns = [
                    "video_id",
                    "keyword",
                    "title",
                    "description",
                    "published_at",
                    "channel_country",
                    "channel_custom_url",
                    "channel_subscriber_count",
                    "channel_video_count",
                    "view_count",
                    "like_count",
                    "comment_count",
                    "category_id",
                    "engagement_rate",
                    "reviewed_brand",
                    "reviewed_series",
                    "reviewed_item",
                    "product_sentiment_score",
                ]

                available_video_cols = [
                    col for col in video_columns if col in videos_df.columns
                ]
                videos_final_initial = videos_df[available_video_cols].copy()

                # Raw 데이터 삽입 (필터링 전 모든 데이터)
                raw_count = 0
                if len(raw_videos_df) > 0:
                    # Add category to raw_videos_df
                    if category:
                        raw_videos_df['category'] = category
                    raw_count = self.db_manager.insert_raw_videos(
                        raw_videos_df, keyword
                    )

                # 필터링된 영상 데이터 삽입 (댓글 없이)
                video_count = self.db_manager.insert_videos(videos_final_initial)

                print(f"  [OK] Saved to PostgreSQL:")
                print(f"    - {raw_count} raw videos (all collected)")
                print(f"    - {video_count} filtered videos")
                print(f"  => Videos are now safely stored in database!")

                self.db_manager.disconnect()
            else:
                print("  [WARNING] Failed to connect to database")
        else:
            print("  Database storage is disabled")

        # Step 2: 댓글 데이터 수집
        print()
        print("[Step 2/5] Collecting comments from YouTube API...")
        comments_data = self.youtube_api.get_comprehensive_comments(
            video_ids=video_ids, max_comments_per_video=max_comments_per_video
        )

        comments_df = pd.DataFrame(comments_data)
        print(f"Collected {len(comments_df)} comments")

        # Step 2.5: 댓글 감정 분석 (선택적)
        if analyze_sentiment and len(comments_df) > 0:
            print()
            print("[Step 2.5/5] Analyzing sentiment for comments (OpenAI)...")
            print(
                f"  WARNING: This will make {len(comments_df)} OpenAI API calls and may incur costs."
            )

            # 감정 분석 (최적화된 배치 방식 사용)
            comments_with_sentiment = (
                self.sentiment_analyzer.analyze_comments_batch_optimized(
                    comments=comments_df.to_dict("records"),
                    text_field="comment_text_display",
                    batch_size=10,
                    rate_limit_delay=2.0,
                )
            )

            # sentiment_score를 comments_df에 추가
            comments_df = pd.DataFrame(comments_with_sentiment)
            print(
                f"Sentiment analysis completed: {comments_df['sentiment_score'].notna().sum()} comments analyzed"
            )
        else:
            if analyze_sentiment:
                print()
                print("[Step 2.5/5] Skipping sentiment analysis (no comments)")

        # Step 3: 댓글 요약 (비디오별)
        if summarize_comments and len(comments_df) > 0:
            print()
            print("[Step 3/5] Summarizing comments (per video)...")

            comment_summaries = []

            for video_id in videos_df["video_id"]:
                video_comments = comments_df[comments_df["video_id"] == video_id]

                if len(video_comments) == 0:
                    continue

                print(
                    f"  Summarizing comments for video: {video_id} ({len(video_comments)} comments)"
                )

                # 댓글을 딕셔너리 리스트로 변환
                comments_list = video_comments.to_dict("records")

                # 요약 생성
                summary = self.comment_summarizer.summarize_comments_for_video(
                    comments_list
                )
                summary["video_id"] = video_id

                comment_summaries.append(summary)
                time.sleep(2)  # OpenAI API rate limit

                # 10개마다 추가 대기
                if len(comment_summaries) % 10 == 0:
                    print(
                        f"  >>> Processed {len(comment_summaries)} videos, waiting 10 seconds..."
                    )
                    time.sleep(10)

            # 댓글 요약 데이터프레임
            comment_summaries_df = pd.DataFrame(comment_summaries)

            # comment_text_summary 컬럼 생성 (data_structure.txt 기준)
            comment_summaries_df["comment_text_summary"] = comment_summaries_df[
                "summary"
            ]

            # 영상 데이터와 병합
            videos_df = videos_df.merge(
                comment_summaries_df[
                    [
                        "video_id",
                        "comment_text_summary",
                        "key_themes",
                        "sentiment_summary",
                    ]
                ],
                on="video_id",
                how="left",
                suffixes=("", "_comments"),
            )

            print(f"Summarized comments for {len(comment_summaries)} videos")
        else:
            print()
            print("[Step 3/5] Skipping comment summarization...")

        # Step 4: 댓글 데이터 저장 및 영상 업데이트
        print()
        print("[Step 4/5] Saving comments and updating videos with summaries...")

        # 4-1: API 원본 데이터 저장 (raw_data)
        if self.save_raw_data:
            raw_data_file = os.path.join(
                self.raw_data_dir,
                f'youtube_raw_{keyword.replace(" ", "_")}_{timestamp}.json',
            )

            raw_data = {
                "keyword": keyword,
                "region_code": region_code,
                "created_at": timestamp,
                "videos": video_data,  # API에서 받은 원본 데이터
                "comments": comments_data,  # API에서 받은 원본 데이터
                "metadata": {
                    "total_videos": len(video_data),
                    "total_comments": len(comments_data),
                    "max_videos": max_videos,
                    "max_comments_per_video": max_comments_per_video,
                },
            }

            with open(raw_data_file, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=2, default=str)

            print(f"  Raw data saved: {raw_data_file}")

        # videos_final: data_structure.txt 기준 컬럼 선택
        video_columns = [
            "video_id",
            "keyword",
            "title",
            "description",
            "published_at",
            "channel_country",
            "channel_custom_url",
            "channel_subscriber_count",
            "channel_video_count",
            "view_count",
            "like_count",
            "comment_count",
            "category_id",
            "engagement_rate",
            "reviewed_brand",
            "reviewed_series",
            "reviewed_item",
            "product_sentiment_score",
            "comment_text_summary",
        ]

        # 존재하는 컬럼만 선택
        available_video_cols = [
            col for col in video_columns if col in videos_df.columns
        ]
        videos_final = videos_df[available_video_cols].copy()

        # comments_final: data_structure.txt 기준 컬럼 선택
        comment_columns = [
            "video_id",
            "comment_id",
            "comment_type",
            "parent_comment_id",
            "comment_text_display",
            "like_count",
            "reply_count",
            "published_at",
            "sentiment_score",
        ]

        # 존재하는 컬럼만 선택
        available_comment_cols = [
            col for col in comment_columns if col in comments_df.columns
        ]
        comments_final = comments_df[available_comment_cols].copy()

        # 4-2: 가공된 데이터 저장 (processed_data) - 선택적
        if self.save_csv:
            videos_csv_file = os.path.join(
                self.processed_data_dir,
                f'youtube_videos_{keyword.replace(" ", "_")}_{timestamp}.csv',
            )
            comments_csv_file = os.path.join(
                self.processed_data_dir,
                f'youtube_comments_{keyword.replace(" ", "_")}_{timestamp}.csv',
            )

            videos_final.to_csv(videos_csv_file, index=False, encoding="utf-8-sig")
            comments_final.to_csv(comments_csv_file, index=False, encoding="utf-8-sig")

            print(f"  Processed videos saved: {videos_csv_file}")
            print(f"  Processed comments saved: {comments_csv_file}")
        else:
            print(f"  CSV saving disabled (save_csv=False)")

        # 4-3: PostgreSQL에 저장 (댓글 및 영상 업데이트)
        if self.use_database and self.db_manager:
            if self.db_manager.connect():
                # 댓글 삽입
                comment_count = self.db_manager.insert_comments(comments_final)

                # 영상 업데이트 (comment_text_summary 포함)
                video_count = self.db_manager.insert_videos(videos_final)

                print(f"  [OK] Updated PostgreSQL:")
                print(f"    - {video_count} videos updated (with comment summaries)")
                print(f"    - {comment_count} comments inserted")

                self.db_manager.disconnect()
            else:
                print("  [WARNING] Failed to connect to database")
        else:
            print("  Database storage is disabled")

        print()
        print("=" * 80)
        print("Pipeline completed successfully!")
        print("=" * 80)
        print(f"Total videos processed: {len(videos_final)}")
        print(f"Total comments processed: {len(comments_final)}")
        if "comment_text_summary" in videos_final.columns:
            print(
                f"Videos with comment summary: {videos_final['comment_text_summary'].notna().sum()}"
            )

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
        description="YouTube 데이터 수집 및 분석 통합 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--keyword", type=str, required=True, help='검색 키워드 (예: "Samsung TV")'
    )

    parser.add_argument(
        "--max-videos", type=int, default=100, help="최대 영상 수 (기본값: 100)"
    )

    parser.add_argument(
        "--max-comments",
        type=int,
        default=100,
        help="영상당 최대 댓글 수 (기본값: 100)",
    )

    parser.add_argument(
        "--region", type=str, default="US", help="지역 코드 (기본값: US)"
    )

    parser.add_argument(
        "--no-comment-summary", action="store_true", help="댓글 요약 건너뛰기"
    )

    parser.add_argument(
        "--output-dir", type=str, default="data", help="출력 디렉토리 (기본값: data)"
    )

    parser.add_argument(
        "--no-database",
        action="store_true",
        help="PostgreSQL 데이터베이스에 저장하지 않음",
    )

    parser.add_argument(
        "--analyze-sentiment",
        action="store_true",
        help="댓글 감정 분석 수행 (OpenAI 사용, 비용 발생 주의)",
    )

    args = parser.parse_args()

    # 파이프라인 실행
    pipeline = YouTubePipeline(
        output_dir=args.output_dir, use_database=not args.no_database
    )

    videos_df, comments_df = pipeline.run(
        keyword=args.keyword,
        max_videos=args.max_videos,
        max_comments_per_video=args.max_comments,
        region_code=args.region,
        summarize_comments=not args.no_comment_summary,
        analyze_sentiment=args.analyze_sentiment,
    )


if __name__ == "__main__":
    main()
