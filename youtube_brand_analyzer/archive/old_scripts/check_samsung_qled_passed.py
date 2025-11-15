"""
Check Samsung QLED passed videos in raw table
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def check_passed_videos():
    """Check passed videos for Samsung QLED"""
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
        print("Samsung QLED: 'Passed' Videos in Raw Table")
        print("="*120)

        # Check breakdown by country and category
        query = """
        SELECT
            channel_country,
            category_id,
            COUNT(*) as count
        FROM youtube_videos_raw
        WHERE keyword = 'Samsung QLED'
        AND quality_filter_passed = TRUE
        GROUP BY channel_country, category_id
        ORDER BY count DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"\n{'Country':<12} {'Category':<12} {'Count':<10}")
        print("-"*40)

        for row in results:
            country, category, count = row
            print(f"{country or 'NULL':<12} {category or 'NULL':<12} {count:<10}")

        # Check engagement rate distribution
        print("\n" + "="*120)
        print("Engagement Rate Distribution for 'Passed' Videos")
        print("="*120)

        query = """
        SELECT
            CASE
                WHEN engagement_rate = 0 THEN '0.00%'
                WHEN engagement_rate < 1 THEN '0.01%-0.99%'
                WHEN engagement_rate < 2 THEN '1.00%-1.99%'
                WHEN engagement_rate < 5 THEN '2.00%-4.99%'
                WHEN engagement_rate < 10 THEN '5.00%-9.99%'
                ELSE '10.00%+'
            END as engagement_bucket,
            COUNT(*) as count
        FROM youtube_videos_raw
        WHERE keyword = 'Samsung QLED'
        AND quality_filter_passed = TRUE
        GROUP BY engagement_bucket
        ORDER BY MIN(engagement_rate)
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"\n{'Engagement Rate':<20} {'Count':<10}")
        print("-"*40)

        for row in results:
            bucket, count = row
            print(f"{bucket:<20} {count:<10}")

        # Sample 20 passed videos
        print("\n" + "="*120)
        print("Sample of 20 'Passed' Videos (Showing Attributes)")
        print("="*120)

        query = """
        SELECT
            video_id,
            channel_country,
            category_id,
            engagement_rate,
            channel_subscriber_count,
            view_count,
            created_at
        FROM youtube_videos_raw
        WHERE keyword = 'Samsung QLED'
        AND quality_filter_passed = TRUE
        ORDER BY created_at DESC
        LIMIT 20
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"\n{'Video ID':<15} {'Country':<10} {'Cat':<6} {'Eng%':<8} {'Subs':<12} {'Views':<12} {'Created':<20}")
        print("-"*120)

        for row in results:
            video_id, country, category, eng_rate, subs, views, created = row
            subs_str = f"{subs:,}" if subs else "N/A"
            views_str = f"{views:,}" if views else "N/A"
            created_str = str(created)[:19] if created else "N/A"
            print(f"{video_id:<15} {country or 'NULL':<10} {category or 'NULL':<6} {eng_rate:<8.2f} {subs_str:<12} {views_str:<12} {created_str:<20}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_passed_videos()
