"""
Test API key rotation functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from collectors.youtube_api import YouTubeAnalyzer

def test_key_rotation():
    """Test that YouTubeAnalyzer initializes with multiple keys"""

    print("="*80)
    print("Testing YouTube API Key Rotation")
    print("="*80)
    print()

    # Initialize analyzer (should load all 3 keys)
    analyzer = YouTubeAnalyzer()

    print(f"\nKey information:")
    print(f"  Total keys available: {len(analyzer.api_keys)}")
    print(f"  Current key index: {analyzer.current_key_index}")
    print(f"  Current key (first 20 chars): {analyzer.api_key[:20]}...")

    # Test a simple API call
    print("\nTesting simple API call...")
    try:
        video_data, video_ids, raw_data = analyzer.get_comprehensive_video_data(
            keyword="Samsung TV",
            region_code="US",
            max_results=5,  # Small test
            apply_quality_filter=False  # No filter for quick test
        )

        print(f"\n[OK] API call successful!")
        print(f"  Collected {len(video_data)} videos")
        print(f"  Request count: {analyzer.request_count}")

    except Exception as e:
        print(f"\n[ERROR] API call failed: {e}")

    print("\n" + "="*80)
    print("Test completed")
    print("="*80)

if __name__ == "__main__":
    test_key_rotation()
