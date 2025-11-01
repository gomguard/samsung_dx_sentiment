"""
Verify database schema and data
"""
import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

print("="*80)
print("Verifying Database Schema and Data")
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

    # Check videos table columns
    print("\n[1/3] Videos Table Schema:")
    print("-"*80)
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'youtube_videos'
        ORDER BY ordinal_position
    """)

    columns = cursor.fetchall()
    for col_name, col_type in columns:
        print(f"  {col_name:<30} {col_type}")

    # Check comments table columns
    print("\n[2/3] Comments Table Schema:")
    print("-"*80)
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'youtube_comments'
        ORDER BY ordinal_position
    """)

    columns = cursor.fetchall()
    for col_name, col_type in columns:
        print(f"  {col_name:<30} {col_type}")

    # Sample data from videos table
    print("\n[3/3] Sample Video Data:")
    print("-"*80)
    cursor.execute("""
        SELECT
            video_id,
            title,
            view_count,
            CASE WHEN video_content_summary IS NOT NULL THEN 'YES' ELSE 'NO' END as has_video_summary,
            CASE WHEN comment_text_summary IS NOT NULL THEN 'YES' ELSE 'NO' END as has_comment_summary
        FROM youtube_videos
        LIMIT 5
    """)

    videos = cursor.fetchall()
    print(f"{'Video ID':<15} {'Title':<40} {'Views':<10} {'Video Summary':<15} {'Comment Summary':<15}")
    print("-"*80)
    for row in videos:
        video_id, title, views, has_video_sum, has_comment_sum = row
        title_short = title[:37] + '...' if len(title) > 40 else title
        print(f"{video_id:<15} {title_short:<40} {views:<10} {has_video_sum:<15} {has_comment_sum:<15}")

    # Show one full example
    print("\n[Example] Full Video Record:")
    print("-"*80)
    cursor.execute("""
        SELECT
            video_id,
            title,
            video_content_summary,
            comment_text_summary
        FROM youtube_videos
        LIMIT 1
    """)

    example = cursor.fetchone()
    if example:
        video_id, title, video_sum, comment_sum = example
        print(f"Video ID: {video_id}")
        print(f"Title: {title}")
        print(f"\nVideo Content Summary:")
        print(f"  {video_sum[:200] if video_sum else 'None'}...")
        print(f"\nComment Text Summary:")
        print(f"  {comment_sum[:200] if comment_sum else 'None'}...")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("Verification completed!")
    print("="*80)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
