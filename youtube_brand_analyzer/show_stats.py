"""
Show detailed statistics from database
"""
import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

print("="*80)
print("YouTube Data Collection Statistics")
print("="*80)

try:
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )

    cursor = conn.cursor()

    # Overall stats
    print("\n[1] Overall Statistics:")
    print("-"*80)

    cursor.execute("SELECT COUNT(*) FROM youtube_videos")
    video_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM youtube_comments")
    comment_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM youtube_videos WHERE video_content_summary IS NOT NULL AND video_content_summary != 'Transcript not available'")
    videos_with_summary = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM youtube_videos WHERE comment_text_summary IS NOT NULL")
    videos_with_comment_summary = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT video_id) FROM youtube_comments")
    videos_with_comments = cursor.fetchone()[0]

    print(f"Total Videos: {video_count}")
    print(f"Total Comments: {comment_count}")
    print(f"Videos with Content Summary: {videos_with_summary}/{video_count} ({videos_with_summary*100//video_count}%)")
    print(f"Videos with Comment Summary: {videos_with_comment_summary}/{video_count} ({videos_with_comment_summary*100//video_count}%)")
    print(f"Videos with Comments: {videos_with_comments}/{video_count}")
    print(f"Average Comments per Video: {comment_count//video_count}")

    # Comment type breakdown
    print("\n[2] Comment Type Breakdown:")
    print("-"*80)
    cursor.execute("""
        SELECT comment_type, COUNT(*)
        FROM youtube_comments
        GROUP BY comment_type
        ORDER BY COUNT(*) DESC
    """)

    for comment_type, count in cursor.fetchall():
        print(f"{comment_type:<15} {count:>5} comments")

    # Top videos by engagement
    print("\n[3] Top 10 Videos by Views:")
    print("-"*80)
    cursor.execute("""
        SELECT title, view_count, like_count, comment_count
        FROM youtube_videos
        ORDER BY view_count DESC
        LIMIT 10
    """)

    print(f"{'Title':<50} {'Views':<10} {'Likes':<8} {'Comments':<10}")
    print("-"*80)
    for title, views, likes, comments in cursor.fetchall():
        title_short = title[:47] + '...' if len(title) > 50 else title
        print(f"{title_short:<50} {views:<10} {likes:<8} {comments:<10}")

    # Top videos by comments
    print("\n[4] Top 10 Videos by Comment Count:")
    print("-"*80)
    cursor.execute("""
        SELECT v.title, COUNT(c.comment_id) as comment_count
        FROM youtube_videos v
        LEFT JOIN youtube_comments c ON v.video_id = c.video_id
        GROUP BY v.video_id, v.title
        ORDER BY comment_count DESC
        LIMIT 10
    """)

    print(f"{'Title':<60} {'Comments':<10}")
    print("-"*80)
    for title, count in cursor.fetchall():
        title_short = title[:57] + '...' if len(title) > 60 else title
        print(f"{title_short:<60} {count:<10}")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("Statistics completed!")
    print("="*80)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
