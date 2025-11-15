"""
Check timestamps of raw data to understand when data was collected
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def check_timestamps():
    """Check collection timestamps for Samsung QLED"""
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
        print("Samsung QLED Raw Data Collection Timestamps")
        print("="*80)

        # Check collection timestamps grouped
        query = """
        SELECT
            DATE_TRUNC('minute', created_at) as collection_time,
            COUNT(*) as total,
            SUM(CASE WHEN quality_filter_passed THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN NOT quality_filter_passed THEN 1 ELSE 0 END) as failed
        FROM youtube_videos_raw
        WHERE keyword = 'samsung qled'
        GROUP BY DATE_TRUNC('minute', created_at)
        ORDER BY collection_time DESC
        LIMIT 20
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"\n{'Collection Time':<25} {'Total':<10} {'Passed':<10} {'Failed':<10}")
        print("-"*80)

        for row in results:
            collection_time, total, passed, failed = row
            print(f"{str(collection_time):<25} {total:<10} {passed:<10} {failed:<10}")

        # Check sample of "passed" videos with wrong attributes
        print("\n" + "="*80)
        print("Sample of 'Passed' Videos with Non-US or Non-Category-28")
        print("="*80)

        query = """
        SELECT
            video_id,
            channel_country,
            category_id,
            engagement_rate,
            created_at
        FROM youtube_videos_raw
        WHERE keyword = 'samsung qled'
        AND quality_filter_passed = TRUE
        AND (channel_country != 'US' OR category_id != '28')
        ORDER BY created_at DESC
        LIMIT 10
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"\n{'Video ID':<20} {'Country':<10} {'Category':<10} {'Eng Rate':<12} {'Created At':<25}")
        print("-"*80)

        for row in results:
            video_id, country, category, eng_rate, created = row
            print(f"{video_id:<20} {country:<10} {category:<10} {eng_rate:<12.2f} {str(created):<25}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_timestamps()
