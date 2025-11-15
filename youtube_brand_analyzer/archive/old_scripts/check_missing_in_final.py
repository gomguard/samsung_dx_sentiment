"""
Check if missing videos exist in youtube_videos with different keywords
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

missing_ids = ['i8vOs2VCmHc', 'JmIFGh1bnxo', 'rDUabFEJ6eQ']

print('Checking if missing videos exist in youtube_videos with different keywords:')
print('='*80)

for vid in missing_ids:
    cursor.execute('SELECT video_id, keyword FROM youtube_videos WHERE video_id = %s', (vid,))
    result = cursor.fetchone()
    if result:
        print(f'{vid}: FOUND with keyword "{result[1]}"')
    else:
        print(f'{vid}: NOT FOUND in youtube_videos')

print('\n' + '='*80)
print('Checking keywords in youtube_videos_raw for these videos:')
print('='*80)

for vid in missing_ids:
    cursor.execute('''
        SELECT DISTINCT keyword, quality_filter_passed
        FROM youtube_videos_raw
        WHERE video_id = %s
        ORDER BY keyword
    ''', (vid,))
    results = cursor.fetchall()
    print(f'\n{vid}:')
    for keyword, passed in results:
        passed_str = "PASSED" if passed else "FAILED"
        print(f'  - {keyword:<35} [{passed_str}]')

cursor.close()
conn.close()
