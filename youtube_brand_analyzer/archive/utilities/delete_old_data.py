"""
Delete data collected on 2025-11-10 (with faulty quality filter)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def delete_old_data():
    """Delete 2025-11-10 data from all tables"""
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
        print("Checking 2025-11-10 Data Before Deletion")
        print("="*80)

        # Check youtube_videos_raw
        cursor.execute("""
            SELECT COUNT(*)
            FROM youtube_videos_raw
            WHERE created_at::date = '2025-11-10'
        """)
        raw_count = cursor.fetchone()[0]
        print(f"\nyoutube_videos_raw: {raw_count} rows")

        # Check youtube_videos
        cursor.execute("""
            SELECT COUNT(*)
            FROM youtube_videos
            WHERE created_at::date = '2025-11-10'
        """)
        videos_count = cursor.fetchone()[0]
        print(f"youtube_videos: {videos_count} rows")

        # Check youtube_comments (for videos created on 2025-11-10)
        cursor.execute("""
            SELECT COUNT(*)
            FROM youtube_comments
            WHERE video_id IN (
                SELECT video_id
                FROM youtube_videos
                WHERE created_at::date = '2025-11-10'
            )
        """)
        comments_count = cursor.fetchone()[0]
        print(f"youtube_comments: {comments_count} rows (linked to 11/10 videos)")

        if raw_count == 0 and videos_count == 0 and comments_count == 0:
            print("\n[INFO] No 2025-11-10 data found. Nothing to delete.")
            cursor.close()
            conn.close()
            return

        print("\n" + "="*80)
        print("Deleting 2025-11-10 Data")
        print("="*80)

        # Delete from youtube_comments first (foreign key constraint)
        cursor.execute("""
            DELETE FROM youtube_comments
            WHERE video_id IN (
                SELECT video_id
                FROM youtube_videos
                WHERE created_at::date = '2025-11-10'
            )
        """)
        deleted_comments = cursor.rowcount
        print(f"\n[1/3] Deleted {deleted_comments} comments from youtube_comments")

        # Delete from youtube_videos
        cursor.execute("""
            DELETE FROM youtube_videos
            WHERE created_at::date = '2025-11-10'
        """)
        deleted_videos = cursor.rowcount
        print(f"[2/3] Deleted {deleted_videos} videos from youtube_videos")

        # Delete from youtube_videos_raw
        cursor.execute("""
            DELETE FROM youtube_videos_raw
            WHERE created_at::date = '2025-11-10'
        """)
        deleted_raw = cursor.rowcount
        print(f"[3/3] Deleted {deleted_raw} raw videos from youtube_videos_raw")

        conn.commit()

        print("\n" + "="*80)
        print("Deletion Summary")
        print("="*80)
        print(f"Total deleted:")
        print(f"  - Raw videos: {deleted_raw}")
        print(f"  - Videos: {deleted_videos}")
        print(f"  - Comments: {deleted_comments}")
        print("\n[OK] All 2025-11-10 data deleted successfully!")

        # Check remaining data
        print("\n" + "="*80)
        print("Remaining Data After Deletion")
        print("="*80)

        cursor.execute("SELECT COUNT(*) FROM youtube_videos_raw")
        print(f"youtube_videos_raw: {cursor.fetchone()[0]} rows")

        cursor.execute("SELECT COUNT(*) FROM youtube_videos")
        print(f"youtube_videos: {cursor.fetchone()[0]} rows")

        cursor.execute("SELECT COUNT(*) FROM youtube_comments")
        print(f"youtube_comments: {cursor.fetchone()[0]} rows")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()

if __name__ == "__main__":
    delete_old_data()
