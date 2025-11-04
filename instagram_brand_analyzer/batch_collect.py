"""
Batch Instagram Data Collection Script

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
from pipeline_instagram_analysis import InstagramPipeline


class BatchCollector:
    """Batch collector for all active keywords"""

    def __init__(self, dry_run=False):
        """
        Initialize batch collector

        Args:
            dry_run (bool): If True, only show what would be collected
        """
        self.dry_run = dry_run
        self.keyword_manager = KeywordManager()
        self.pipeline = InstagramPipeline(output_dir='data', use_database=True)

    def run(self):
        """Run batch collection for all active keywords"""
        print("="*80)
        print("Instagram Batch Data Collection")
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
        for idx, (keyword, max_posts, max_comments) in enumerate(active_keywords, 1):
            print(f"  {idx}. '{keyword}' - {max_posts} posts, {max_comments} comments/post")

        print("\n" + "="*80)

        if self.dry_run:
            print("\n[DRY RUN] Exiting without collecting data")
            self.keyword_manager.disconnect()
            return

        # Process each keyword
        total_posts = 0
        total_comments = 0
        successful_keywords = 0
        failed_keywords = []

        for idx, (keyword, max_posts, max_comments) in enumerate(active_keywords, 1):
            print("\n" + "="*80)
            print(f"Processing keyword {idx}/{len(active_keywords)}: '{keyword}'")
            print("="*80)

            try:
                # Run pipeline for this keyword
                posts_df, comments_df = self.pipeline.run(
                    keyword=keyword,
                    max_posts=max_posts,
                    max_comments_per_post=max_comments,
                    analyze_sentiment=True
                )

                if posts_df is not None:
                    post_count = len(posts_df)
                    comment_count = len(comments_df) if comments_df is not None else 0

                    # Update keyword column for collected posts
                    post_ids = posts_df['post_id'].tolist()
                    if post_ids:
                        cursor = self.keyword_manager.cursor
                        for post_id in post_ids:
                            cursor.execute(
                                "UPDATE instagram_posts SET keyword = %s WHERE post_id = %s",
                                (keyword, post_id)
                            )
                        self.keyword_manager.conn.commit()
                        print(f"  Updated keyword for {len(post_ids)} posts")

                    # Update statistics
                    self.keyword_manager.update_collection_stats(
                        keyword=keyword,
                        posts_count=post_count,
                        comments_count=comment_count
                    )

                    total_posts += post_count
                    total_comments += comment_count
                    successful_keywords += 1

                    print(f"\n[OK] '{keyword}' completed: {post_count} posts, {comment_count} comments")
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
        print(f"Total posts collected: {total_posts}")
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
        description='Batch collect Instagram data for all active keywords',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run batch collection
  python batch_collect.py

  # Dry run (show what would be collected)
  python batch_collect.py --dry-run

Notes:
  - This will process ALL active keywords in the database
  - Each keyword will use its own settings (max_posts, max_comments)
  - There will be a 30-second wait between keywords to avoid rate limits
  - Data is automatically saved to PostgreSQL database
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be collected without actually running'
    )

    args = parser.parse_args()

    # Run batch collection
    collector = BatchCollector(dry_run=args.dry_run)
    collector.run()


if __name__ == "__main__":
    main()
