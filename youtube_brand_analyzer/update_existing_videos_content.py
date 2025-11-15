"""
Update existing videos in database with brand/series/sentiment analysis
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from analyzers.video_content_analyzer import VideoContentAnalyzer
import time

def update_existing_videos():
    """Update all existing videos with brand/series/sentiment data"""

    # Connect to database
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )
    cursor = conn.cursor()

    # Initialize analyzer
    analyzer = VideoContentAnalyzer()

    # Get all videos that need updating (where reviewed_brand is NULL)
    cursor.execute('''
        SELECT video_id, keyword, title, description, category
        FROM youtube_videos
        WHERE reviewed_brand IS NULL OR product_sentiment_score IS NULL
        ORDER BY video_id
    ''')

    videos_to_update = cursor.fetchall()
    total_videos = len(videos_to_update)

    print(f'Found {total_videos} videos to update')
    print('='*80)

    if total_videos == 0:
        print('No videos to update!')
        cursor.close()
        conn.close()
        return

    updated_count = 0

    for idx, (video_id, keyword, title, description, category) in enumerate(videos_to_update):
        print(f'\n[{idx+1}/{total_videos}] Processing video: {video_id}')
        try:
            print(f'  Title: {title[:60]}...')
        except UnicodeEncodeError:
            print(f'  Title: [Unicode Error - cannot display]')

        try:
            print(f'  Category: {category}')
        except UnicodeEncodeError:
            pass

        try:
            # Extract brand and series (category 전달)
            brand_info = analyzer.extract_brand_and_series(title, description or '', category=category)

            # Analyze sentiment
            sentiment_score = analyzer.analyze_product_sentiment(
                title, description or '',
                brand_info['reviewed_brand'],
                brand_info['reviewed_series']
            )

            # Update database
            cursor.execute('''
                UPDATE youtube_videos
                SET reviewed_brand = %s,
                    reviewed_series = %s,
                    reviewed_item = %s,
                    product_sentiment_score = %s
                WHERE video_id = %s AND keyword = %s
            ''', (
                brand_info['reviewed_brand'],
                brand_info['reviewed_series'],
                brand_info['reviewed_item'],
                sentiment_score,
                video_id,
                keyword
            ))

            conn.commit()
            updated_count += 1

            print(f'  [OK] Updated: brand={brand_info["reviewed_brand"]}, series={brand_info["reviewed_series"]}, sentiment={sentiment_score:.2f}')

            # Rate limiting
            time.sleep(2)

            # Every 10 videos, extra delay
            if (idx + 1) % 10 == 0:
                print(f'\n  >>> Processed {idx+1} videos, waiting 10 seconds...')
                time.sleep(10)

        except Exception as e:
            print(f'  [ERROR] {str(e)[:100]}')
            conn.rollback()
            continue

    print('\n' + '='*80)
    print(f'Update completed!')
    print(f'  Total videos: {total_videos}')
    print(f'  Successfully updated: {updated_count}')
    print(f'  Failed: {total_videos - updated_count}')

    cursor.close()
    conn.close()

if __name__ == '__main__':
    update_existing_videos()
