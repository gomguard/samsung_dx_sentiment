"""
Investigate why some passed videos are not in final table
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def investigate_missing():
    """Investigate missing videos"""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DB
        )
        cursor = conn.cursor()

        print("="*120)
        print("Investigation: Why are passed videos missing from final table?")
        print("="*120)

        # Get all unique passed videos that are NOT in final table
        cursor.execute("""
            SELECT DISTINCT r.video_id
            FROM youtube_videos_raw r
            WHERE r.quality_filter_passed = TRUE
            AND r.video_id NOT IN (SELECT video_id FROM youtube_videos)
        """)
        missing_video_ids = [row[0] for row in cursor.fetchall()]

        print(f"\nTotal missing videos: {len(missing_video_ids)}")

        for video_id in missing_video_ids:
            print("\n" + "="*120)
            print(f"Video ID: {video_id}")
            print("="*120)

            # Get all occurrences in raw table
            cursor.execute("""
                SELECT keyword, channel_country, category_id, engagement_rate,
                       quality_filter_passed, filter_fail_reason, created_at
                FROM youtube_videos_raw
                WHERE video_id = %s
                ORDER BY created_at
            """, (video_id,))

            results = cursor.fetchall()

            print(f"\n{'Keyword':<35} {'Country':<10} {'Cat':<6} {'Eng%':<8} {'Passed':<8} {'Fail Reason':<40} {'Created':<20}")
            print("-"*120)

            for keyword, country, category, eng_rate, passed, fail_reason, created in results:
                passed_str = "YES" if passed else "NO"
                created_str = str(created)[:19] if created else "N/A"
                print(f"{keyword:<35} {country or 'NULL':<10} {category or 'NULL':<6} {eng_rate:<8.2f} {passed_str:<8} {fail_reason or 'N/A':<40} {created_str:<20}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_missing()
