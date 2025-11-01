"""
Query database to verify data
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
import pandas as pd

print("="*80)
print("Querying Database")
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

    # Query videos
    print("\n[1/2] Videos Table:")
    print("-"*80)
    cursor.execute("""
        SELECT video_id, title, view_count, like_count, comment_count,
               LENGTH(video_content_summary) as summary_length
        FROM youtube_videos
        ORDER BY view_count DESC
        LIMIT 10
    """)

    videos = cursor.fetchall()
    print(f"{'Video ID':<15} {'Title':<40} {'Views':<10} {'Likes':<8} {'Comments':<10} {'Summary':<10}")
    print("-"*80)
    for row in videos:
        video_id, title, views, likes, comments, summary_len = row
        title_short = title[:37] + '...' if len(title) > 40 else title
        summary_info = f"{summary_len} chars" if summary_len else "No summary"
        print(f"{video_id:<15} {title_short:<40} {views:<10} {likes:<8} {comments:<10} {summary_info:<10}")

    # Query comments
    print("\n[2/2] Comments Table:")
    print("-"*80)
    cursor.execute("""
        SELECT video_id, comment_type, COUNT(*) as count,
               COUNT(CASE WHEN comment_text_summary IS NOT NULL THEN 1 END) as with_summary
        FROM youtube_comments
        GROUP BY video_id, comment_type
        ORDER BY video_id, comment_type
    """)

    comments = cursor.fetchall()
    print(f"{'Video ID':<15} {'Type':<15} {'Count':<10} {'With Summary':<15}")
    print("-"*80)
    for row in comments:
        video_id, comment_type, count, with_summary = row
        print(f"{video_id:<15} {comment_type:<15} {count:<10} {with_summary:<15}")

    # Sample video content summary
    print("\n[Sample] Video Content Summary:")
    print("-"*80)
    cursor.execute("""
        SELECT video_id, title, video_content_summary
        FROM youtube_videos
        WHERE video_content_summary IS NOT NULL
        LIMIT 1
    """)

    sample = cursor.fetchone()
    if sample:
        video_id, title, summary = sample
        print(f"Video: {video_id}")
        print(f"Title: {title}")
        print(f"Summary: {summary[:500]}...")

    # Sample comment text summary
    print("\n[Sample] Comment Text Summary:")
    print("-"*80)
    cursor.execute("""
        SELECT c.video_id, c.comment_text_summary
        FROM youtube_comments c
        WHERE c.comment_text_summary IS NOT NULL
        LIMIT 1
    """)

    sample = cursor.fetchone()
    if sample:
        video_id, summary = sample
        print(f"Video: {video_id}")
        print(f"Summary: {summary[:500]}...")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("Query completed successfully!")
    print("="*80)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
