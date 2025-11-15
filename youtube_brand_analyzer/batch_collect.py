"""
Batch YouTube Data Collection Script

Automatically collects data for all active keywords in the database.

Usage:
    python batch_collect.py
    python batch_collect.py --dry-run  # Show what would be collected without actually running
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

import argparse
import time
from datetime import datetime
from manage_keywords import KeywordManager
from pipeline_youtube_analysis import YouTubePipeline


class BatchCollector:
    """Batch collector for all active keywords"""

    def __init__(self, dry_run=False, filter_country=None):
        """
        Initialize batch collector

        Args:
            dry_run (bool): If True, only show what would be collected
            filter_country (str): Filter videos by channel country (e.g., 'US', 'JP')
        """
        self.dry_run = dry_run
        self.filter_country = filter_country
        self.keyword_manager = KeywordManager()
        self.pipeline = YouTubePipeline(output_dir='data', use_database=True, save_raw_data=False, save_csv=False)

    def run(self):
        """Run batch collection for all active keywords"""
        print("="*80)
        print("YouTube Batch Data Collection")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Dry run: {self.dry_run}")
        print("="*80)
        print()

        # Connect to database
        if not self.keyword_manager.connect():
            print("Failed to connect to database")
            return

        # Get active keywords
        active_keywords = self.keyword_manager.get_active_keywords()

        if not active_keywords:
            print("No active keywords found")
            print("\nTo add keywords, use:")
            print('  python manage_keywords.py add "Samsung TV"')
            self.keyword_manager.disconnect()
            return

        print(f"Found {len(active_keywords)} active keywords:\n")
        for idx, (keyword, max_videos, max_comments, region, category) in enumerate(active_keywords, 1):
            print(f"  {idx}. '{keyword}' - {max_videos} videos, {max_comments} comments/video, region: {region}, category: {category}")

        print("\n" + "="*80)

        if self.dry_run:
            print("\n[DRY RUN] Exiting without collecting data")
            self.keyword_manager.disconnect()
            return

        # Process each keyword
        total_videos = 0
        total_comments = 0
        successful_keywords = 0
        failed_keywords = []

        for idx, (keyword, max_videos, max_comments, region, category) in enumerate(active_keywords, 1):
            print("\n" + "="*80)
            print(f"Processing keyword {idx}/{len(active_keywords)}: '{keyword}' (category: {category})")
            print("="*80)

            try:
                # Run pipeline for this keyword
                videos_df, comments_df = self.pipeline.run(
                    keyword=keyword,
                    max_videos=max_videos,
                    max_comments_per_video=max_comments,
                    region_code=region,
                    category=category,
                    summarize_comments=True
                )

                if videos_df is not None and comments_df is not None:
                    # Filter by channel_country if specified
                    if self.filter_country:
                        original_video_count = len(videos_df)
                        videos_df = videos_df[videos_df['channel_country'] == self.filter_country]

                        if len(videos_df) == 0:
                            print(f"  [INFO] No videos from country '{self.filter_country}' (filtered out {original_video_count} videos)")
                            print(f"\n[WARN] '{keyword}' returned no videos after country filtering")
                            failed_keywords.append((keyword, f"No videos from {self.filter_country}"))
                            continue

                        # Filter comments to match filtered videos
                        video_ids_filtered = videos_df['video_id'].tolist()
                        comments_df = comments_df[comments_df['video_id'].isin(video_ids_filtered)]

                        print(f"  [INFO] Country filter: {original_video_count} → {len(videos_df)} videos ({self.filter_country} only)")

                    video_count = len(videos_df)
                    comment_count = len(comments_df)

                    # Update keyword column for collected videos
                    video_ids = videos_df['video_id'].tolist()
                    if video_ids:
                        cursor = self.keyword_manager.cursor
                        for video_id in video_ids:
                            cursor.execute(
                                "UPDATE youtube_videos SET keyword = %s WHERE video_id = %s",
                                (keyword, video_id)
                            )
                        self.keyword_manager.conn.commit()
                        print(f"  Updated keyword for {len(video_ids)} videos")

                    # Update statistics
                    self.keyword_manager.update_collection_stats(
                        keyword=keyword,
                        videos_count=video_count,
                        comments_count=comment_count
                    )

                    total_videos += video_count
                    total_comments += comment_count
                    successful_keywords += 1

                    print(f"\n[OK] '{keyword}' completed: {video_count} videos, {comment_count} comments")
                else:
                    print(f"\n[WARN] '{keyword}' returned no data")
                    failed_keywords.append((keyword, "No data returned"))

            except Exception as e:
                print(f"\n[ERROR] Failed to process '{keyword}': {e}")
                failed_keywords.append((keyword, str(e)))

            # Wait between keywords to avoid rate limits
            if idx < len(active_keywords):
                wait_time = 30
                print(f"\nWaiting {wait_time} seconds before next keyword...")
                time.sleep(wait_time)

        # Summary
        print("\n" + "="*80)
        print("Batch Collection Summary")
        print("="*80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nKeywords processed: {successful_keywords}/{len(active_keywords)}")
        print(f"Total videos collected: {total_videos}")
        print(f"Total comments collected: {total_comments}")

        if failed_keywords:
            print(f"\nFailed keywords ({len(failed_keywords)}):")
            for keyword, reason in failed_keywords:
                print(f"  - '{keyword}': {reason}")

        print("\n" + "="*80)

        self.keyword_manager.disconnect()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Batch collect YouTube data for all active keywords',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run batch collection
  python batch_collect.py

  # Dry run (show what would be collected)
  python batch_collect.py --dry-run

Notes:
  - This will process ALL active keywords in the database
  - Each keyword will use its own settings (max_videos, max_comments, region)
  - There will be a 30-second wait between keywords to avoid rate limits
  - Data is automatically saved to PostgreSQL database
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be collected without actually running'
    )

    parser.add_argument(
        '--filter-country',
        type=str,
        default=None,
        help='Filter videos by channel country (e.g., US, JP, KR)'
    )

    args = parser.parse_args()

    # Run batch collection
    collector = BatchCollector(
        dry_run=args.dry_run,
        filter_country=args.filter_country
    )
    collector.run()


if __name__ == "__main__":
    main()
