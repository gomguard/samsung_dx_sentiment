"""
US로 남아있는 비디오들의 제목/설명 확인
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from db_manager import TikTokDBManager

db = TikTokDBManager()
if db.connect():
    # US로 남아있는 비디오들의 제목/설명 샘플 확인
    db.cursor.execute('''
        SELECT
            channel_title,
            title,
            description
        FROM tiktok_videos
        WHERE channel_country = 'US'
        LIMIT 10
    ''')

    # 파일로 저장 (이모지 때문에 콘솔 출력 불가)
    with open('us_videos_check.txt', 'w', encoding='utf-8') as f:
        f.write('US로 남아있는 비디오 샘플 (제목/설명 확인):\n')
        f.write('='*80 + '\n\n')

        for i, (channel, title, desc) in enumerate(db.cursor.fetchall(), 1):
            f.write(f'[{i}] 채널: {channel}\n')
            f.write(f'    제목: {title[:100] if title else "N/A"}\n')
            f.write(f'    설명: {desc[:150] if desc else "N/A"}\n')
            f.write('\n')

    print('[OK] us_videos_check.txt 파일로 저장 완료')

    db.disconnect()
