"""
Verify data flow from youtube_videos_raw to youtube_videos
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def verify_data_flow():
    """Verify that all passed videos from raw table are in final table"""
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
        print("Data Flow Verification: youtube_videos_raw → youtube_videos")
        print("="*120)

        # 1. Count passed videos in raw table
        cursor.execute("""
            SELECT COUNT(*), COUNT(DISTINCT video_id)
            FROM youtube_videos_raw
            WHERE quality_filter_passed = TRUE
        """)
        passed_total, passed_unique = cursor.fetchone()
        print(f"\n[1] youtube_videos_raw (quality_filter_passed = TRUE):")
        print(f"    Total rows: {passed_total}")
        print(f"    Unique video_ids: {passed_unique}")

        # 2. Count videos in final table
        cursor.execute("""
            SELECT COUNT(*)
            FROM youtube_videos
        """)
        final_count = cursor.fetchone()[0]
        print(f"\n[2] youtube_videos:")
        print(f"    Total rows: {final_count}")

        # 3. Check if all passed videos are in final table
        cursor.execute("""
            SELECT COUNT(DISTINCT r.video_id)
            FROM youtube_videos_raw r
            WHERE r.quality_filter_passed = TRUE
            AND r.video_id IN (SELECT video_id FROM youtube_videos)
        """)
        matched_count = cursor.fetchone()[0]
        print(f"\n[3] Matched videos (passed in raw AND exists in final):")
        print(f"    Count: {matched_count}")

        # 4. Find passed videos NOT in final table
        cursor.execute("""
            SELECT DISTINCT r.video_id, r.keyword, r.channel_country, r.category_id, r.engagement_rate
            FROM youtube_videos_raw r
            WHERE r.quality_filter_passed = TRUE
            AND r.video_id NOT IN (SELECT video_id FROM youtube_videos)
            LIMIT 20
        """)
        missing_videos = cursor.fetchall()

        if missing_videos:
            print(f"\n[4] Videos marked as PASSED in raw but NOT in final table: {len(missing_videos)} found")
            print(f"\n{'Video ID':<15} {'Keyword':<30} {'Country':<10} {'Cat':<6} {'Eng%':<8}")
            print("-"*120)
            for video_id, keyword, country, category, eng_rate in missing_videos:
                print(f"{video_id:<15} {keyword:<30} {country or 'NULL':<10} {category or 'NULL':<6} {eng_rate:<8.2f}")
        else:
            print(f"\n[4] All passed videos are in final table [OK]")

        # 5. Find videos in final table but NOT passed in raw
        cursor.execute("""
            SELECT v.video_id, v.keyword
            FROM youtube_videos v
            WHERE v.video_id NOT IN (
                SELECT DISTINCT video_id
                FROM youtube_videos_raw
                WHERE quality_filter_passed = TRUE
            )
        """)
        extra_videos = cursor.fetchall()

        if extra_videos:
            print(f"\n[5] Videos in final table but NOT marked as passed in raw: {len(extra_videos)} found")
            print(f"\n{'Video ID':<15} {'Keyword':<30}")
            print("-"*60)
            for video_id, keyword in extra_videos[:20]:
                print(f"{video_id:<15} {keyword:<30}")
        else:
            print(f"\n[5] No extra videos in final table [OK]")

        # 6. Check for duplicates in raw table (same video_id, different created_at)
        cursor.execute("""
            SELECT video_id, COUNT(*) as count
            FROM youtube_videos_raw
            WHERE quality_filter_passed = TRUE
            GROUP BY video_id
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """)
        duplicates = cursor.fetchall()

        if duplicates:
            print(f"\n[6] Duplicate video_ids in raw table (passed=true): {len(duplicates)} found")
            print(f"\n{'Video ID':<15} {'Count':<10}")
            print("-"*30)
            for video_id, count in duplicates:
                print(f"{video_id:<15} {count:<10}")
        else:
            print(f"\n[6] No duplicates in passed videos [OK]")

        # 7. Summary by keyword
        print("\n" + "="*120)
        print("Summary by Keyword")
        print("="*120)

        cursor.execute("""
            SELECT
                r.keyword,
                COUNT(*) as raw_total,
                SUM(CASE WHEN r.quality_filter_passed THEN 1 ELSE 0 END) as raw_passed,
                COUNT(DISTINCT CASE WHEN r.quality_filter_passed THEN r.video_id END) as raw_passed_unique,
                COUNT(DISTINCT v.video_id) as final_count
            FROM youtube_videos_raw r
            LEFT JOIN youtube_videos v ON v.keyword = r.keyword
            GROUP BY r.keyword
            ORDER BY r.keyword
        """)
        results = cursor.fetchall()

        print(f"\n{'Keyword':<35} {'Raw Total':<12} {'Raw Passed':<12} {'Passed Uniq':<14} {'Final':<10} {'Match':<10}")
        print("-"*120)

        for keyword, raw_total, raw_passed, raw_passed_unique, final_count in results:
            match_status = "OK" if raw_passed_unique == final_count else f"MISS ({raw_passed_unique - final_count:+d})"
            print(f"{keyword:<35} {raw_total:<12} {raw_passed:<12} {raw_passed_unique:<14} {final_count or 0:<10} {match_status:<10}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_data_flow()
