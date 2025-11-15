"""
Update category in youtube_videos from keywords database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

# Connect to database
conn = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    dbname=POSTGRES_DB
)
cursor = conn.cursor()

# Get keywords from database
cursor.execute('SELECT keyword, category FROM keywords WHERE active = TRUE')
keywords = cursor.fetchall()

# Create keyword -> category mapping
keyword_category_map = {}
for keyword, category in keywords:
    keyword_category_map[keyword] = category

print(f'Loaded {len(keyword_category_map)} keyword-category mappings from database')

# Update youtube_videos table
updated_count = 0
for keyword, category in keyword_category_map.items():
    cursor.execute('''
        UPDATE youtube_videos
        SET category = %s
        WHERE keyword = %s
    ''', (category, keyword))

    count = cursor.rowcount
    if count > 0:
        print(f'Updated {count} videos for keyword "{keyword}" -> category "{category}"')
        updated_count += count

conn.commit()
print(f'\nTotal videos updated: {updated_count}')

# Verify
cursor.execute('''
    SELECT category, COUNT(*)
    FROM youtube_videos
    GROUP BY category
''')
print('\nCategory distribution after update:')
for cat, cnt in cursor.fetchall():
    cat_str = cat if cat else 'NULL'
    print(f'  {cat_str}: {cnt}개')

cursor.close()
conn.close()
