"""
TikTok Data Collection & Analysis Pipeline

This script performs:
1. Collect TikTok video data via RapidAPI
2. Collect comments (currently dummy comments - no real API available)
3. Perform sentiment analysis
4. Save to PostgreSQL database
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from datetime import datetime
import time

from collectors.tiktok_api import TikTokAPI
from analyzers.sentiment import SentimentAnalyzer

# Import from parent directory for comment summarizer
parent_dir = os.path.dirname(os.path.dirname(__file__))
youtube_analyzer_path = os.path.join(parent_dir, 'youtube_brand_analyzer', 'analyzers')
instagram_analyzer_path = os.path.join(parent_dir, 'instagram_brand_analyzer', 'analyzers')

CommentSummarizer = None
for analyzer_path in [youtube_analyzer_path, instagram_analyzer_path]:
    if analyzer_path not in sys.path:
        sys.path.insert(0, analyzer_path)
    try:
        from comment_summarizer import CommentSummarizer
        print(f"[OK] Loaded CommentSummarizer from {analyzer_path}")
        break
    except Exception as e:
        print(f"[WARN] Could not load from {analyzer_path}: {e}")
        continue

if CommentSummarizer is None:
    # Fallback: create a dummy summarizer
    print("[ERROR] CommentSummarizer not found, using fallback")
    class CommentSummarizer:
        def summarize_comments_for_video(self, comments):
            return {
                'summary': 'Comment summarization not available',
                'key_themes': [],
                'sentiment_summary': 'N/A',
                'total_comments': len(comments)
            }

# Import local config
current_dir = os.path.dirname(os.path.abspath(__file__))
local_config_path = os.path.join(current_dir, 'config')
if local_config_path not in sys.path:
    sys.path.insert(0, local_config_path)

from db_manager import TikTokDBManager


class TikTokPipeline:
    """TikTok Data Collection & Analysis Pipeline"""

    def __init__(self, output_dir='data', use_database=True):
        """
        Initialize pipeline

        Args:
            output_dir (str): Output directory
            use_database (bool): Use PostgreSQL database
        """
        self.output_dir = output_dir
        self.use_database = use_database
        os.makedirs(output_dir, exist_ok=True)

        # Initialize analyzers
        self.tiktok_api = TikTokAPI()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.comment_summarizer = CommentSummarizer()

        # Initialize database
        if self.use_database:
            self.db_manager = TikTokDBManager()
        else:
            self.db_manager = None

    def run(self, keyword, region_code="US", max_videos=30, max_comments_per_video=50,
            analyze_sentiment=True):
        """
        Execute full pipeline

        Args:
            keyword (str): Search keyword
            region_code (str): Region code (US, KR, etc.)
            max_videos (int): Maximum number of videos
            max_comments_per_video (int): Maximum comments per video
            analyze_sentiment (bool): Perform sentiment analysis

        Returns:
            tuple: (videos_df, comments_df)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("="*80)
        print("TikTok Data Collection & Analysis Pipeline")
        print("="*80)
        print(f"Keyword: {keyword}")
        print(f"Region: {region_code}")
        print(f"Max videos: {max_videos}")
        print(f"Max comments per video: {max_comments_per_video}")
        print(f"Analyze sentiment: {analyze_sentiment}")
        print("="*80)
        print()

        # Step 1: Collect video data
        print("[Step 1/5] Collecting video data from TikTok API...")
        video_data, video_ids = self.tiktok_api.get_comprehensive_video_data(
            keyword=keyword,
            region_code=region_code,
            max_results=max_videos
        )

        if not video_data:
            print("No videos found!")
            return None, None

        videos_df = pd.DataFrame(video_data)
        print(f"Collected {len(videos_df)} videos")

        # Step 1.5: Update channel statistics with real data
        print()
        print("[Step 1.5/5] Fetching real channel statistics...")
        unique_channels = videos_df[['channel_id', 'channel_custom_url']].drop_duplicates()

        updated_count = 0
        for idx, row in unique_channels.iterrows():
            channel_id = row['channel_id']
            channel_url = row['channel_custom_url']

            # Extract uniqueId from channel_custom_url (format: @username)
            unique_id = channel_url.replace('@', '') if channel_url else None

            if unique_id:
                print(f"  Fetching stats for @{unique_id}...")
                user_info = self.tiktok_api.get_user_info(unique_id)

                if user_info:
                    # Update all videos from this channel
                    mask = videos_df['channel_id'] == channel_id
                    videos_df.loc[mask, 'channel_subscriber_count'] = user_info.get('follower_count', 0)
                    videos_df.loc[mask, 'channel_video_count'] = user_info.get('video_count', 0)
                    videos_df.loc[mask, 'channel_total_view_count'] = user_info.get('heart_count', 0)

                    # Update channel description if available
                    if user_info.get('signature'):
                        videos_df.loc[mask, 'channel_description'] = user_info['signature']

                    print(f"    [OK] {user_info['follower_count']:,} followers, {user_info['video_count']} videos")
                    updated_count += 1
                    time.sleep(0.5)  # Rate limiting

        print(f"Updated channel stats for {updated_count}/{len(unique_channels)} channels")

        # Step 2: Collect comment data
        print()
        print("[Step 2/5] Collecting comments from TikTok API...")
        comments_data = self.tiktok_api.get_comprehensive_comments(
            video_ids=video_ids,
            max_comments_per_video=max_comments_per_video
        )

        if not comments_data:
            print("No comments found!")
            comments_df = pd.DataFrame()
        else:
            comments_df = pd.DataFrame(comments_data)
            print(f"Collected {len(comments_df)} comments")

        # Step 3: Sentiment analysis
        if analyze_sentiment and len(comments_df) > 0:
            print()
            print("[Step 3/5] Analyzing comment sentiment...")

            # Convert to sentiment analyzer format
            formatted_comments = []
            for _, row in comments_df.iterrows():
                formatted_comment = {
                    'video_id': row['video_id'],
                    'comment_id': row['comment_id'],
                    'comment_text': row['comment_text_original'],
                    'like_count': row['like_count'],
                    'published_at': row['published_at']
                }
                formatted_comments.append(formatted_comment)

            # Perform sentiment analysis
            sentiment_results = self.sentiment_analyzer.analyze_comment_sentiment(formatted_comments)

            if sentiment_results:
                sentiment_df = pd.DataFrame(sentiment_results)

                # Map sentiment_category to sentiment/sentiment_label
                if 'sentiment_category' in sentiment_df.columns:
                    sentiment_df['sentiment'] = sentiment_df['sentiment_category']
                    sentiment_df['sentiment_label'] = sentiment_df['sentiment_category']

                # Merge with comments
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
            print("[Step 3/5] Skipping sentiment analysis...")

        # Step 4: Comment summarization (OpenAI)
        if len(comments_df) > 0:
            print()
            print("[Step 4/5] Summarizing comments using OpenAI...")

            # Group comments by video_id
            video_groups = comments_df.groupby('video_id')
            comment_summaries = []

            for video_id, video_comments in video_groups:
                print(f"  Summarizing {len(video_comments)} comments for video {video_id[:10]}...")

                # Convert comments to dict list
                comments_list = video_comments.to_dict('records')

                # Generate summary
                summary = self.comment_summarizer.summarize_comments_for_video(comments_list)
                summary['video_id'] = video_id

                comment_summaries.append(summary)
                time.sleep(2)  # OpenAI API rate limit

                # Wait every 10 posts
                if len(comment_summaries) % 10 == 0:
                    print(f"  >>> Processed {len(comment_summaries)} videos, waiting 10 seconds...")
                    time.sleep(10)

            # Create comment summaries DataFrame
            comment_summaries_df = pd.DataFrame(comment_summaries)

            # Create comment_text_summary column
            comment_summaries_df['comment_text_summary'] = comment_summaries_df['summary']

            # Merge with videos data
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
            print("[Step 4/5] Skipping comment summarization (no comments)...")

        # Step 5: Save to database
        print()
        print("[Step 5/5] Saving data to database...")

        if self.use_database and self.db_manager:
            if self.db_manager.connect():
                # Create tables
                self.db_manager.create_tables()

                # Insert videos
                video_count = self.db_manager.insert_videos(videos_df)

                # Insert comments
                if len(comments_df) > 0:
                    comment_count = self.db_manager.insert_comments(comments_df)
                else:
                    comment_count = 0

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
        print(f"Total videos processed: {len(videos_df)}")
        print(f"Total comments processed: {len(comments_df)}")
        if 'sentiment' in comments_df.columns:
            print(f"Comments with sentiment analysis: {comments_df['sentiment'].notna().sum()}")

        # Database statistics
        if self.use_database and self.db_manager:
            if self.db_manager.connect():
                print()
                print("Database Statistics:")
                print(f"  Total videos in DB: {self.db_manager.get_video_count()}")
                print(f"  Total comments in DB: {self.db_manager.get_comment_count()}")
                self.db_manager.disconnect()

        return videos_df, comments_df


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='TikTok Data Collection & Analysis Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--keyword',
        type=str,
        required=True,
        help='Search keyword (e.g., "Samsung TV")'
    )

    parser.add_argument(
        '--region',
        type=str,
        default='US',
        help='Region code (default: US)'
    )

    parser.add_argument(
        '--max-videos',
        type=int,
        default=30,
        help='Maximum number of videos (default: 30)'
    )

    parser.add_argument(
        '--max-comments',
        type=int,
        default=50,
        help='Maximum comments per video (default: 50)'
    )

    parser.add_argument(
        '--no-sentiment',
        action='store_true',
        help='Skip sentiment analysis'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory (default: data)'
    )

    parser.add_argument(
        '--no-database',
        action='store_true',
        help='Do not save to PostgreSQL database'
    )

    args = parser.parse_args()

    # Execute pipeline
    pipeline = TikTokPipeline(
        output_dir=args.output_dir,
        use_database=not args.no_database
    )

    videos_df, comments_df = pipeline.run(
        keyword=args.keyword,
        region_code=args.region,
        max_videos=args.max_videos,
        max_comments_per_video=args.max_comments,
        analyze_sentiment=not args.no_sentiment
    )


if __name__ == "__main__":
    main()
