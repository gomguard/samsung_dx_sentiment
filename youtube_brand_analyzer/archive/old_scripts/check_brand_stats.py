import sys
import os
sys.path.insert(0, '..')

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

# 전체 통계
cursor.execute('''
    SELECT
        COUNT(*) as total,
        COUNT(CASE WHEN reviewed_brand IS NOT NULL THEN 1 END) as with_brand,
        COUNT(CASE WHEN reviewed_brand IS NULL THEN 1 END) as without_brand
    FROM youtube_videos
''')
total, with_brand, without_brand = cursor.fetchone()
print(f'전체 비디오: {total}개')
print(f'  브랜드 있음: {with_brand}개')
print(f'  브랜드 없음 (None): {without_brand}개')
print()

# 카테고리별 통계
cursor.execute('''
    SELECT category, keyword, COUNT(*) as count,
           COUNT(CASE WHEN reviewed_brand IS NOT NULL THEN 1 END) as with_brand
    FROM youtube_videos
    GROUP BY category, keyword
    ORDER BY category NULLS LAST, keyword
''')
print('카테고리별 통계:')
print('-'*100)
for cat, kw, count, with_brand in cursor.fetchall():
    cat_str = cat if cat else 'NULL'
    print(f'{cat_str:5} | {kw:45} | 총:{count:2}개 | 브랜드:{with_brand:2}개')

print()
print('브랜드가 채워진 비디오들:')
print('-'*80)
cursor.execute('''
    SELECT reviewed_brand, reviewed_series, COUNT(*) as count
    FROM youtube_videos
    WHERE reviewed_brand IS NOT NULL
    GROUP BY reviewed_brand, reviewed_series
    ORDER BY reviewed_brand, reviewed_series NULLS LAST
''')
for brand, series, count in cursor.fetchall():
    series_str = series if series else 'None'
    print(f'{brand:15} | {series_str:20} | {count}개')

print()
print('브랜드 없는 비디오 샘플 (키워드별):')
print('-'*100)
cursor.execute('''
    SELECT keyword, title
    FROM youtube_videos
    WHERE reviewed_brand IS NULL
    LIMIT 10
''')
for kw, title in cursor.fetchall():
    title_short = title[:60] if title else 'N/A'
    print(f'{kw:45} | {title_short}')

cursor.close()
conn.close()
