"""
Generate comment_text_summary for videos that don't have one

For each video without comment_text_summary:
1. Fetch all comments for that video
2. Combine all comments into one text
3. Generate summary using GPT-4
4. Update the youtube_videos table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager
from config.secrets import OPENAI_API_KEY
from openai import OpenAI
import time

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_comment_summary(comments_text_list):
    """
    Generate summary from multiple comments

    Args:
        comments_text_list (list): List of comment texts

    Returns:
        str: Summary of all comments
    """
    if not comments_text_list:
        return None

    # Combine all comments
    combined_comments = "\n\n".join([f"- {comment}" for comment in comments_text_list])

    prompt = f"""다음은 하나의 YouTube 비디오에 달린 댓글들입니다.
이 댓글들을 읽고 전체적인 의견을 3-5문장으로 요약해주세요.

댓글들:
{combined_comments}

요약 (한글로, 3-5문장):"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 YouTube 댓글을 분석하고 요약하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"  [ERROR] GPT-4 요약 실패: {e}")
        return None


def main():
    """Main function"""
    print("="*80)
    print("YouTube Comment Summary Generation")
    print("="*80)
    print()

    db = YouTubeDBManager()

    if not db.connect():
        print("Failed to connect to database")
        return

    # Get videos without comment_text_summary
    db.cursor.execute("""
        SELECT video_id, title, keyword
        FROM youtube_videos
        WHERE comment_text_summary IS NULL
        AND channel_country = 'US'
        ORDER BY video_id
    """)

    videos_without_summary = db.cursor.fetchall()

    print(f"Found {len(videos_without_summary)} videos without comment_text_summary")
    print()

    if len(videos_without_summary) == 0:
        print("All videos already have summaries!")
        db.disconnect()
        return

    # Process each video
    success_count = 0
    fail_count = 0

    for idx, (video_id, title, keyword) in enumerate(videos_without_summary, 1):
        print(f"[{idx}/{len(videos_without_summary)}] Processing video_id: {video_id}")
        try:
            print(f"  Title: {title[:60]}...")
            print(f"  Keyword: {keyword}")
        except UnicodeEncodeError:
            print(f"  Title: [Unicode title]")
            print(f"  Keyword: {keyword}")

        # Get all comments for this video
        db.cursor.execute("""
            SELECT comment_text_display
            FROM youtube_comments
            WHERE video_id = %s
            ORDER BY like_count DESC
        """, (video_id,))

        comments = db.cursor.fetchall()
        comments_text_list = [comment[0] for comment in comments if comment[0]]

        print(f"  Found {len(comments_text_list)} comments")

        if len(comments_text_list) == 0:
            print(f"  [SKIP] No comments to summarize")
            fail_count += 1
            continue

        # Generate summary
        summary = generate_comment_summary(comments_text_list)

        if summary:
            # Update database
            db.cursor.execute("""
                UPDATE youtube_videos
                SET comment_text_summary = %s, updated_at = CURRENT_TIMESTAMP
                WHERE video_id = %s
            """, (summary, video_id))
            db.conn.commit()

            try:
                print(f"  [OK] Summary: {summary[:80]}...")
            except UnicodeEncodeError:
                print(f"  [OK] Summary generated (Unicode content)")
            success_count += 1
        else:
            print(f"  [FAIL] Failed to generate summary")
            fail_count += 1

        # Wait to avoid rate limits
        if idx < len(videos_without_summary):
            time.sleep(2)  # 2 seconds between requests

        print()

    # Summary
    print("="*80)
    print("Summary Generation Complete")
    print("="*80)
    print(f"Success: {success_count}/{len(videos_without_summary)}")
    print(f"Failed: {fail_count}/{len(videos_without_summary)}")
    print("="*80)

    db.disconnect()


if __name__ == "__main__":
    main()
