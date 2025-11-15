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

cursor.execute('''
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'youtube_videos'
    ORDER BY ordinal_position
''')
columns = cursor.fetchall()

print('youtube_videos 테이블 컬럼:')
print('='*60)
for col_name, col_type in columns:
    print(f'{col_name:40} {col_type}')

cursor.close()
conn.close()
