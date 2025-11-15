"""
Check and update YouTube database schema
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager

db = YouTubeDBManager()
if db.connect():
    # 현재 테이블 스키마 확인
    db.cursor.execute('''
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'youtube_videos'
        ORDER BY ordinal_position
    ''')
    columns = db.cursor.fetchall()
    print('youtube_videos 현재 컬럼:')
    for col, dtype in columns:
        print(f'  - {col}: {dtype}')

    db.disconnect()
