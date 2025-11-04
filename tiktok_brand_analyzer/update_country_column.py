"""
Update channel_country column size to accommodate full country names
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from db_manager import TikTokDBManager

db = TikTokDBManager()
if db.connect():
    print("="*80)
    print("Updating channel_country column size")
    print("="*80)
    print()

    # Alter column to VARCHAR(50) to accommodate full country names
    db.cursor.execute('''
        ALTER TABLE tiktok_videos
        ALTER COLUMN channel_country TYPE VARCHAR(50)
    ''')

    db.conn.commit()
    print("[OK] channel_country column updated to VARCHAR(50)")
    print()

    db.disconnect()
