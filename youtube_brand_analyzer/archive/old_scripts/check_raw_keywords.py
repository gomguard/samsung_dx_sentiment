"""
Check what keywords exist in raw table
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def check_keywords():
    """Check keywords in raw table"""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DB
        )
        cursor = conn.cursor()

        print("="*80)
        print("Keywords in youtube_videos_raw Table")
        print("="*80)

        # Check all keywords
        query = """
        SELECT
            keyword,
            COUNT(*) as total,
            SUM(CASE WHEN quality_filter_passed THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN NOT quality_filter_passed THEN 1 ELSE 0 END) as failed,
            MIN(created_at) as first_collected,
            MAX(created_at) as last_collected
        FROM youtube_videos_raw
        GROUP BY keyword
        ORDER BY keyword
        """

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("\nNo data in youtube_videos_raw table!")
        else:
            print(f"\n{'Keyword':<30} {'Total':<8} {'Passed':<8} {'Failed':<8} {'First':<20} {'Last':<20}")
            print("-"*120)

            for row in results:
                keyword, total, passed, failed, first, last = row
                first_str = str(first)[:19] if first else "N/A"
                last_str = str(last)[:19] if last else "N/A"
                print(f"{keyword:<30} {total:<8} {passed:<8} {failed:<8} {first_str:<20} {last_str:<20}")

        # Check youtube_videos table
        print("\n" + "="*80)
        print("Keywords in youtube_videos Table")
        print("="*80)

        query = """
        SELECT
            keyword,
            COUNT(*) as total,
            MIN(created_at) as first_created,
            MAX(created_at) as last_created
        FROM youtube_videos
        GROUP BY keyword
        ORDER BY keyword
        """

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("\nNo data in youtube_videos table!")
        else:
            print(f"\n{'Keyword':<30} {'Total':<8} {'First':<20} {'Last':<20}")
            print("-"*80)

            for row in results:
                keyword, total, first, last = row
                first_str = str(first)[:19] if first else "N/A"
                last_str = str(last)[:19] if last else "N/A"
                print(f"{keyword:<30} {total:<8} {first_str:<20} {last_str:<20}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_keywords()
