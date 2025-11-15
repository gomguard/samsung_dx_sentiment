"""
Update category in youtube_videos based on keyword patterns
"""
import sys
import os
sys.path.insert(0, '..')

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

# HHP keywords (스마트폰/태블릿)
hhp_keywords = [
    'Apple Launch Color',
    'Apple Launch Storage',
    'iPhone Launch Color',
    'iPhone Launch Storage',
    'Pixel Launch Color',
    'Samsung Galaxy A Launch Color',
    'Samsung Galaxy Launch Color',
    'Samsung Galaxy S Launch Color',
    'Samsung Galaxy A Launch Storage',
    'Samsung Galaxy Launch Storage',
    'Samsung Galaxy S Launch Storage',
    'Samsung Galaxy Z Fold Launch Storage',
    'Samsung Galaxy Z Flip Launch Storage',
    'Samsung Galaxy Note Launch Storage',
    'Samsung Galaxy Note Launch Color',
    'Samsung Flip Launch Color',
    'Samsung Fold Launch Color',
    'Samsung Galaxy Z Flip Launch Color',
    'Samsung Galaxy Z Fold Launch Color',
    'Samsung Flip Launch Storage',
    'Samsung Fold Launch Storage',
    'Lenovo Launch Color',
    'Lenovo Launch Storage',
    'moto Launch Color',
    'moto Launch Storage',
    'Google Launch Color',
    'Google Launch Storage',
]

# TV keywords (나머지 전부)
tv_keywords = [
    'LED TV Launch',
    'LG TV Launch',
    'Mini LED TV Launch',
    'Samsung 4K TV Launch',
    'Samsung 8K TV Launch',
    'Samsung HD TV Launch',
    'Samsung Neo QLED TV Launch',
    'Samsung Neo QLED 8K TV Launch',
    'Samsung OLED TV Launch',
    'Samsung QLED TV Launch',
    'Samsung Smart TV Launch',
    'Samsung UHD TV Launch',
    'Samsung FHD TV Launch',
    'TCL TV Launch',
    'QNED TV Launch',
    'Evo TV Launch',
]

# Update HHP categories
for keyword in hhp_keywords:
    cursor.execute('''
        UPDATE youtube_videos
        SET category = 'HHP'
        WHERE keyword = %s
    ''', (keyword,))
    if cursor.rowcount > 0:
        print(f'HHP: {keyword} ({cursor.rowcount} videos)')

# Update TV categories
for keyword in tv_keywords:
    cursor.execute('''
        UPDATE youtube_videos
        SET category = 'TV'
        WHERE keyword = %s
    ''', (keyword,))
    if cursor.rowcount > 0:
        print(f'TV: {keyword} ({cursor.rowcount} videos)')

conn.commit()

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
