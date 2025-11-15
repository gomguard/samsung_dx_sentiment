"""
Update youtube_videos table to use composite primary key (video_id, keyword)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

def update_schema():
    """Update youtube_videos to use (video_id, keyword) as primary key"""
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
        print("Updating youtube_videos PRIMARY KEY")
        print("="*80)
        print("\nCurrent PRIMARY KEY: video_id")
        print("New PRIMARY KEY: (video_id, keyword)")
        print()

        # Check current data
        cursor.execute("SELECT COUNT(*) FROM youtube_videos")
        current_count = cursor.fetchone()[0]
        print(f"Current rows in youtube_videos: {current_count}")

        # Check for duplicates that would exist with new key
        cursor.execute("""
            SELECT video_id, keyword, COUNT(*) as count
            FROM youtube_videos
            GROUP BY video_id, keyword
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()

        if duplicates:
            print(f"\nWARNING: Found {len(duplicates)} duplicate (video_id, keyword) combinations:")
            for vid, kw, cnt in duplicates[:10]:
                print(f"  {vid} + '{kw}': {cnt} times")
        else:
            print("\nNo duplicates found - safe to proceed")

        print("\n" + "="*80)
        print("Step 1: Drop Foreign Key constraint from youtube_comments")
        print("="*80)

        # Find and drop foreign key constraint
        cursor.execute("""
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'youtube_comments'::regclass
            AND contype = 'f'
            AND confrelid = 'youtube_videos'::regclass
        """)
        fk_result = cursor.fetchone()
        if fk_result:
            fk_name = fk_result[0]
            print(f"Found FOREIGN KEY constraint: {fk_name}")
            cursor.execute(f"ALTER TABLE youtube_comments DROP CONSTRAINT {fk_name}")
            print(f"[OK] Dropped FOREIGN KEY: {fk_name}")
        else:
            print("No FOREIGN KEY constraint found")

        print("\n" + "="*80)
        print("Step 2: Drop existing PRIMARY KEY constraint")
        print("="*80)

        # Find and drop the primary key constraint
        cursor.execute("""
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'youtube_videos'::regclass
            AND contype = 'p'
        """)
        pk_result = cursor.fetchone()
        if pk_result:
            pk_name = pk_result[0]
            print(f"Found PRIMARY KEY constraint: {pk_name}")
            cursor.execute(f"ALTER TABLE youtube_videos DROP CONSTRAINT {pk_name}")
            print(f"[OK] Dropped PRIMARY KEY: {pk_name}")
        else:
            print("No PRIMARY KEY constraint found")

        print("\n" + "="*80)
        print("Step 2: Make keyword column NOT NULL (required for PRIMARY KEY)")
        print("="*80)

        # First, check if there are any NULL keywords
        cursor.execute("SELECT COUNT(*) FROM youtube_videos WHERE keyword IS NULL")
        null_keywords = cursor.fetchone()[0]

        if null_keywords > 0:
            print(f"WARNING: {null_keywords} rows have NULL keyword")
            print("Setting NULL keywords to 'unknown'...")
            cursor.execute("UPDATE youtube_videos SET keyword = 'unknown' WHERE keyword IS NULL")
            print(f"[OK] Updated {null_keywords} rows")

        cursor.execute("""
            ALTER TABLE youtube_videos
            ALTER COLUMN keyword SET NOT NULL
        """)
        print("[OK] keyword column set to NOT NULL")

        print("\n" + "="*80)
        print("Step 3: Add new composite PRIMARY KEY (video_id, keyword)")
        print("="*80)

        cursor.execute("""
            ALTER TABLE youtube_videos
            ADD PRIMARY KEY (video_id, keyword)
        """)
        print("[OK] Added composite PRIMARY KEY (video_id, keyword)")

        print("\n" + "="*80)
        print("Step 4: Foreign Key handling")
        print("="*80)

        print("[INFO] Foreign Key NOT re-created")
        print("Reason: video_id is no longer unique (part of composite key)")
        print("Same video can exist with multiple keywords")
        print("Referential integrity will be maintained at application level")

        # Commit changes
        conn.commit()

        print("\n" + "="*80)
        print("Schema Update Complete!")
        print("="*80)
        print("\nNow youtube_videos can store:")
        print("  - Same video with different keywords as separate rows")
        print("  - Example: video ABC with 'Samsung TV' and 'OLED TV' = 2 rows")

        # Show current data
        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT video_id) FROM youtube_videos")
        total, unique_videos = cursor.fetchone()
        print(f"\nCurrent data:")
        print(f"  Total rows: {total}")
        print(f"  Unique video_ids: {unique_videos}")
        print(f"  Average keywords per video: {total/unique_videos:.2f}" if unique_videos > 0 else "")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()

if __name__ == "__main__":
    update_schema()
