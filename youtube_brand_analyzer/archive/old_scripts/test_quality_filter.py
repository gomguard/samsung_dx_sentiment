"""
Test the quality filtering feature
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from collectors.youtube_api import YouTubeAnalyzer

print("="*80)
print("YouTube Quality Filter Test")
print("="*80)
print()

analyzer = YouTubeAnalyzer()

# Test with quality filter enabled
print("Testing quality filter with 'Samsung TV' keyword...")
print("This will collect 200 videos at a time and filter by:")
print("  - Category: 28 (Science & Technology)")
print("  - Subscribers > 10k OR Channel Views > 100M")
print("  - Engagement Rate > 2%")
print("  - Target: 10 quality videos")
print()

video_data, video_ids = analyzer.get_comprehensive_video_data(
    keyword='Samsung TV',
    region_code='US',
    max_results=10,  # Just collect 10 to test quickly
    order='viewCount',
    apply_quality_filter=True
)

print()
print("="*80)
print("Test Results")
print("="*80)
print(f"Total videos returned: {len(video_data)}")
print(f"Total video IDs: {len(video_ids)}")
print()

if video_data:
    print("Sample video details:")
    for i, video in enumerate(video_data[:3], 1):  # Show first 3
        print(f"\n{i}. {video.get('title', 'N/A')}")
        print(f"   Video ID: {video.get('video_id', 'N/A')}")
        print(f"   Category: {video.get('category_id', 'N/A')}")
        print(f"   Channel: {video.get('channel_title', 'N/A')}")
        print(f"   Subscribers: {video.get('channel_subscriber_count', 0):,}")
        print(f"   Channel Views: {video.get('channel_total_view_count', 0):,}")
        print(f"   Views: {video.get('view_count', 0):,}")
        print(f"   Likes: {video.get('like_count', 0):,}")
        print(f"   Comments: {video.get('comment_count', 0):,}")
        print(f"   Engagement Rate: {video.get('engagement_rate', 0):.4f}%")

        # Verify filters
        passed_category = video.get('category_id') == '28'
        passed_channel = (video.get('channel_subscriber_count', 0) > 10000 or
                         video.get('channel_total_view_count', 0) > 100000000)
        passed_engagement = video.get('engagement_rate', 0) > 2.0

        print(f"   Filter Check: Category={passed_category}, Channel={passed_channel}, Engagement={passed_engagement}")

print()
print("="*80)
print("Test Complete")
print("="*80)
