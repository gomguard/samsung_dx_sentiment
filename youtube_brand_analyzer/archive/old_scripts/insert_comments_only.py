"""
youtube_videos 테이블의 비디오들에 대한 댓글만 수집 및 삽입
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager
from collectors.youtube_api import YouTubeAnalyzer
from datetime import datetime


def main():
    print("="*80)
    print("YouTube 댓글 삽입")
    print("="*80)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. DB 연결
    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    # 2. youtube_videos 테이블에서 비디오 ID 가져오기
    print("[Step 1/3] youtube_videos 테이블에서 비디오 ID 가져오기...")
    db.cursor.execute('SELECT video_id FROM youtube_videos')
    video_ids = [row[0] for row in db.cursor.fetchall()]
    print(f"  비디오 수: {len(video_ids)}개")
    print()

    if len(video_ids) == 0:
        print("[WARNING] youtube_videos 테이블에 비디오가 없습니다.")
        db.disconnect()
        return

    # 3. 댓글 수집
    print(f"[Step 2/3] {len(video_ids)}개 비디오의 댓글 수집 중...")
    youtube_api = YouTubeAnalyzer()
    comments_data = youtube_api.get_comprehensive_comments(
        video_ids=video_ids,
        max_comments_per_video=20
    )
    print(f"  수집된 댓글: {len(comments_data)}개")
    print()

    # 4. 댓글 삽입
    print(f"[Step 3/3] youtube_comments 테이블에 댓글 삽입 중...")
    comment_insert_count = 0
    for comment in comments_data:
        try:
            db.cursor.execute('''
                INSERT INTO youtube_comments (
                    comment_id, video_id, comment_type, parent_comment_id,
                    comment_text_display,
                    like_count, reply_count, published_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (comment_id) DO NOTHING
            ''', (
                comment['comment_id'], comment['video_id'], comment['comment_type'],
                comment['parent_comment_id'],
                comment['comment_text_display'],
                comment['like_count'], comment['reply_count'], comment['published_at']
            ))
            comment_insert_count += 1
        except Exception as e:
            print(f"  [WARNING] 댓글 삽입 실패: {e}")
            break

    db.conn.commit()
    print(f"  댓글 삽입 완료: {comment_insert_count}개")
    print()

    # 최종 통계
    print("="*80)
    print("완료 요약")
    print("="*80)
    print(f"youtube_comments 테이블: {comment_insert_count}개 댓글")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    db.disconnect()


if __name__ == "__main__":
    main()
