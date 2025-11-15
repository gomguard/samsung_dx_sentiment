"""
Check current collection statistics
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    dbname=POSTGRES_DB
)
cursor = conn.cursor()

# Get stats for last 2 hours
two_hours_ago = datetime.now() - timedelta(hours=2)

print('='*80)
print('Current Collection Statistics (Last 2 Hours)')
print('='*80)

# Total raw videos
cursor.execute('''
    SELECT COUNT(*) as total_raw,
           COUNT(CASE WHEN quality_filter_passed THEN 1 END) as passed
    FROM youtube_videos_raw
    WHERE created_at > %s
''', (two_hours_ago,))
total_raw, passed = cursor.fetchone()

print(f'\nRaw Videos Collected: {total_raw}')
print(f'Quality Filter Passed: {passed}')
print(f'Filter Rejection Rate: {(total_raw - passed) / total_raw * 100:.1f}%' if total_raw > 0 else 'N/A')

# Breakdown by keyword
print('\n' + '='*80)
print('Breakdown by Keyword (Last 2 Hours)')
print('='*80)

cursor.execute('''
    SELECT keyword,
           COUNT(*) as total,
           COUNT(CASE WHEN quality_filter_passed THEN 1 END) as passed,
           COUNT(DISTINCT video_id) as unique_videos
    FROM youtube_videos_raw
    WHERE created_at > %s
    GROUP BY keyword
    ORDER BY MAX(created_at) DESC
''', (two_hours_ago,))

keywords = cursor.fetchall()
for keyword, total, passed, unique in keywords:
    print(f'\n{keyword}:')
    print(f'  Total raw: {total}, Passed: {passed}, Unique videos: {unique}')

# Total videos in final table
cursor.execute('SELECT COUNT(*) FROM youtube_videos')
final_count = cursor.fetchone()[0]

print('\n' + '='*80)
print(f'Total videos in youtube_videos (final): {final_count}')
print('='*80)

cursor.close()
conn.close()
