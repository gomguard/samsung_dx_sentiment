import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

conn = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    dbname=POSTGRES_DB
)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM youtube_videos')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM youtube_videos WHERE reviewed_brand IS NULL OR product_sentiment_score IS NULL')
need_update = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM youtube_videos WHERE reviewed_brand IS NOT NULL AND product_sentiment_score IS NOT NULL')
already_updated = cursor.fetchone()[0]

print(f'Total videos in DB: {total}')
print(f'Videos needing update: {need_update}')
print(f'Videos already updated: {already_updated}')

# Show sample of videos needing update
cursor.execute('''
    SELECT video_id, keyword, title
    FROM youtube_videos
    WHERE reviewed_brand IS NULL OR product_sentiment_score IS NULL
    LIMIT 5
''')

print('\nSample videos needing update:')
for video_id, keyword, title in cursor.fetchall():
    print(f'  - {video_id}: {title[:60]}...')

cursor.close()
conn.close()
