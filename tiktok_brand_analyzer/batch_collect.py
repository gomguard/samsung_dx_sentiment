"""
Batch TikTok Data Collection Script

Collects TikTok video and comment data for multiple keywords
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pipeline_tiktok_analysis import TikTokPipeline
import time

# Keywords to collect
KEYWORDS = [
    "Samsung TV",
    "Samsung QLED",
    "LG TV",
    "Sony TV"
]

# Collection settings
REGION_CODE = "US"
MAX_VIDEOS_PER_KEYWORD = 20
MAX_COMMENTS_PER_VIDEO = 30

def main():
    print("="*80)
    print("TikTok Batch Data Collection")
    print("="*80)
    print(f"Keywords: {KEYWORDS}")
    print(f"Region: {REGION_CODE}")
    print(f"Max videos per keyword: {MAX_VIDEOS_PER_KEYWORD}")
    print(f"Max comments per video: {MAX_COMMENTS_PER_VIDEO}")
    print("="*80)
    print()

    # Initialize pipeline
    pipeline = TikTokPipeline(use_database=True)

    results_summary = []

    for idx, keyword in enumerate(KEYWORDS, 1):
        print(f"\n[{idx}/{len(KEYWORDS)}] Processing keyword: '{keyword}'")
        print("-" * 80)

        try:
            videos_df, comments_df = pipeline.run(
                keyword=keyword,
                region_code=REGION_CODE,
                max_videos=MAX_VIDEOS_PER_KEYWORD,
                max_comments_per_video=MAX_COMMENTS_PER_VIDEO,
                analyze_sentiment=True
            )

            if videos_df is not None:
                video_count = len(videos_df)
                comment_count = len(comments_df) if comments_df is not None else 0

                results_summary.append({
                    'keyword': keyword,
                    'videos': video_count,
                    'comments': comment_count,
                    'status': 'success'
                })

                print(f"\n[OK] Keyword '{keyword}' completed")
                print(f"  Videos: {video_count}")
                print(f"  Comments: {comment_count}")
            else:
                results_summary.append({
                    'keyword': keyword,
                    'videos': 0,
                    'comments': 0,
                    'status': 'no data'
                })
                print(f"\n[WARN] No data collected for keyword '{keyword}'")

        except Exception as e:
            print(f"\n[ERROR] Failed to process keyword '{keyword}': {e}")
            results_summary.append({
                'keyword': keyword,
                'videos': 0,
                'comments': 0,
                'status': 'error'
            })
            continue

        # Rate limiting between keywords
        if idx < len(KEYWORDS):
            print(f"\nWaiting 3 seconds before next keyword...")
            time.sleep(3)

    # Print summary
    print("\n" + "="*80)
    print("Batch Collection Summary")
    print("="*80)

    total_videos = 0
    total_comments = 0
    success_count = 0

    for result in results_summary:
        status_symbol = "[OK]" if result['status'] == 'success' else "[FAIL]"
        print(f"{status_symbol} {result['keyword']}: {result['videos']} videos, {result['comments']} comments")
        total_videos += result['videos']
        total_comments += result['comments']
        if result['status'] == 'success':
            success_count += 1

    print("="*80)
    print(f"Total: {total_videos} videos, {total_comments} comments")
    print(f"Success rate: {success_count}/{len(KEYWORDS)} keywords")
    print("="*80)


if __name__ == "__main__":
    main()
