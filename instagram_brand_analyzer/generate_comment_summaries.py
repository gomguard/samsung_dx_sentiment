"""
Generate comment summaries for existing Instagram posts in database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config.db_manager import InstagramDBManager
from analyzers.comment_summarizer import CommentSummarizer
import time

def main():
    db = InstagramDBManager()
    if not db.connect():
        print('Failed to connect to database')
        return

    # Get posts with comments that don't have summaries yet
    db.cursor.execute('''
        SELECT p.post_id, p.author_username, p.search_keyword,
               COUNT(c.comment_id) as comment_count
        FROM instagram_posts p
        JOIN instagram_comments c ON p.post_id = c.post_id
        WHERE p.comment_text_summary IS NULL
        GROUP BY p.post_id, p.author_username, p.search_keyword
        HAVING COUNT(c.comment_id) > 0
        ORDER BY comment_count DESC
    ''')

    posts_to_process = db.cursor.fetchall()

    if not posts_to_process:
        print('No posts need comment summaries')
        db.disconnect()
        return

    print(f'Found {len(posts_to_process)} posts that need comment summaries')
    print('='*80)

    summarizer = CommentSummarizer()
    success_count = 0
    error_count = 0

    for idx, (post_id, author, keyword, comment_count) in enumerate(posts_to_process, 1):
        print(f'\n[{idx}/{len(posts_to_process)}] Processing: @{author} ({keyword})')
        print(f'  Post ID: {post_id}')
        print(f'  Comments: {comment_count}')

        try:
            # Get comments for this post
            db.cursor.execute('''
                SELECT comment_id, comment_text, author_username, like_count, published_at
                FROM instagram_comments
                WHERE post_id = %s
                ORDER BY like_count DESC
            ''', (post_id,))

            comments = []
            for row in db.cursor.fetchall():
                comments.append({
                    'comment_id': row[0],
                    'comment_text': row[1],
                    'author_username': row[2],
                    'like_count': row[3],
                    'published_at': row[4]
                })

            # Generate summary
            print(f'  Generating summary for {len(comments)} comments...')
            summary = summarizer.summarize_comments_for_video(comments)

            # Update DB
            db.cursor.execute('''
                UPDATE instagram_posts
                SET comment_text_summary = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE post_id = %s
            ''', (summary['summary'], post_id))

            db.conn.commit()
            success_count += 1
            summary_preview = summary["summary"][:80].encode('ascii', 'ignore').decode('ascii')
            print(f'  [OK] Summary saved: {summary_preview}...')

            # Rate limiting
            time.sleep(2)

            # Extra delay every 10 posts
            if idx % 10 == 0:
                print(f'\n  >>> Processed {idx} posts, waiting 10 seconds...')
                time.sleep(10)

        except Exception as e:
            error_count += 1
            error_msg = str(e)[:100].encode('ascii', 'ignore').decode('ascii')
            print(f'  [ERROR] {error_msg}')
            continue

    print('\n' + '='*80)
    print('Comment Summary Generation Complete')
    print('='*80)
    print(f'Successfully processed: {success_count}/{len(posts_to_process)}')
    print(f'Errors: {error_count}')

    # Final stats
    db.cursor.execute('''
        SELECT COUNT(*) FROM instagram_posts
        WHERE comment_text_summary IS NOT NULL
    ''')
    total_with_summaries = db.cursor.fetchone()[0]

    print(f'\nTotal posts with comment summaries in DB: {total_with_summaries}')

    db.disconnect()

if __name__ == '__main__':
    main()
