"""
Check channel data for country inference
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from db_manager import TikTokDBManager

db = TikTokDBManager()
if db.connect():
    db.cursor.execute('''
        SELECT DISTINCT
            channel_title,
            channel_subscriber_count,
            channel_country
        FROM tiktok_videos
        ORDER BY channel_subscriber_count DESC
        LIMIT 20
    ''')

    print('Current Channel Data (Top 20):')
    print('='*80)

    for channel, subs, country in db.cursor.fetchall():
        subs_str = f'{subs:,}' if subs else 'N/A'
        print(f'{channel[:40]:<40} | {subs_str:>12} | {country}')

    db.disconnect()
