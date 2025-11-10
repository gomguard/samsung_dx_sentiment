"""
Quick test of TikTok data collection with new API key
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from collectors.tiktok_api import TikTokAPI

print("="*80)
print("TikTok Collection Test")
print("="*80)

# Test with a single keyword
api = TikTokAPI()

print("\n[1] Testing video search for 'Samsung TV'...")
try:
    videos, video_ids = api.get_comprehensive_video_data(
        keyword="Samsung TV",
        region_code="US",
        max_results=5
    )

    print(f"\nResults:")
    print(f"  Videos collected: {len(videos)}")
    print(f"  Video IDs: {len(video_ids)}")

    if videos:
        print(f"\nFirst video sample:")
        first_video = videos[0]
        print(f"  Video ID: {first_video.get('video_id')}")
        print(f"  Title: {first_video.get('title', '')[:80]}")
        print(f"  Channel: {first_video.get('channel_title')}")
        print(f"  Views: {first_video.get('view_count')}")
        print(f"  Likes: {first_video.get('like_count')}")
        print(f"  Comments: {first_video.get('comment_count')}")

    print(f"\n[2] Testing comment collection (dummy comments)...")
    comments = api.get_comprehensive_comments(video_ids[:2], max_comments_per_video=5)

    print(f"\nResults:")
    print(f"  Comments collected: {len(comments)}")

    if comments:
        print(f"\nFirst comment sample:")
        first_comment = comments[0]
        print(f"  Comment ID: {first_comment.get('comment_id')}")
        print(f"  Text: {first_comment.get('comment_text_original')}")
        print(f"  Author: {first_comment.get('author_display_name')}")
        print(f"  Likes: {first_comment.get('like_count')}")

    print("\n" + "="*80)
    print("[OK] TikTok API is working correctly!")
    print("="*80)

except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
