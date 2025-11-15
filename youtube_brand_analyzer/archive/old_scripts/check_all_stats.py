"""
Check all collection statistics
"""
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

print('='*80)
print('All Collection Statistics')
print('='*80)

# Total raw videos
cursor.execute('''
    SELECT COUNT(*) as total_raw,
           COUNT(CASE WHEN quality_filter_passed THEN 1 END) as passed
    FROM youtube_videos_raw
''')
total_raw, passed = cursor.fetchone()

print(f'\nTotal Raw Videos: {total_raw}')
print(f'Quality Filter Passed: {passed}')
print(f'Filter Rejection Rate: {(total_raw - passed) / total_raw * 100:.1f}%' if total_raw > 0 else 'N/A')

# Recent created_at timestamps
cursor.execute('''
    SELECT MAX(created_at) as latest, MIN(created_at) as earliest, COUNT(DISTINCT keyword) as num_keywords
    FROM youtube_videos_raw
''')
latest, earliest, num_keywords = cursor.fetchone()
print(f'\nTimestamp Range: {earliest} to {latest}')
print(f'Number of keywords in raw: {num_keywords}')

# Breakdown by keyword (top 10 most recent)
print('\n' + '='*80)
print('Recent Keywords (Top 15)')
print('='*80)

cursor.execute('''
    SELECT keyword,
           COUNT(*) as total,
           COUNT(CASE WHEN quality_filter_passed THEN 1 END) as passed,
           MAX(created_at) as latest_collection
    FROM youtube_videos_raw
    GROUP BY keyword
    ORDER BY MAX(created_at) DESC
    LIMIT 15
''')

keywords = cursor.fetchall()
for keyword, total, passed, latest_time in keywords:
    print(f'\n{keyword}:')
    print(f'  Total: {total}, Passed: {passed}, Latest: {latest_time}')

# Total videos in final table
cursor.execute('SELECT COUNT(*), COUNT(DISTINCT keyword) FROM youtube_videos')
final_count, final_keywords = cursor.fetchone()

print('\n' + '='*80)
print(f'youtube_videos (final): {final_count} videos, {final_keywords} keywords')
print('='*80)

cursor.close()
conn.close()
