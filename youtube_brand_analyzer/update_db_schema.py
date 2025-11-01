"""
Update database schema to add comment_text_summary to videos table
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

print("="*80)
print("Updating Database Schema")
print("="*80)

try:
    # Connect to database
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )

    cursor = conn.cursor()

    # Check if column exists
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='youtube_videos' AND column_name='comment_text_summary'
    """)

    exists = cursor.fetchone()

    if exists:
        print("Column 'comment_text_summary' already exists in youtube_videos table")
    else:
        print("Adding column 'comment_text_summary' to youtube_videos table...")
        cursor.execute("""
            ALTER TABLE youtube_videos
            ADD COLUMN comment_text_summary TEXT
        """)
        conn.commit()
        print("Column added successfully!")

    # Remove comment_text_summary from comments table if it exists
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='youtube_comments' AND column_name='comment_text_summary'
    """)

    exists = cursor.fetchone()

    if exists:
        print("Removing column 'comment_text_summary' from youtube_comments table...")
        cursor.execute("""
            ALTER TABLE youtube_comments
            DROP COLUMN comment_text_summary
        """)
        conn.commit()
        print("Column removed successfully!")
    else:
        print("Column 'comment_text_summary' does not exist in youtube_comments table")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("Schema update completed!")
    print("="*80)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
