"""
기존 수집된 데이터에 카테고리 업데이트
키워드 기반으로 youtube_videos_raw, youtube_videos, youtube_comments에 카테고리 설정
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def main():
    print("="*80)
    print("기존 데이터 카테고리 업데이트")
    print("="*80)
    print()

    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    try:
        # Step 1: youtube_videos_raw 업데이트
        print("[Step 1/3] youtube_videos_raw 카테고리 업데이트...")
        db.cursor.execute("""
            UPDATE youtube_videos_raw vr
            SET category = k.category
            FROM youtube_keywords k
            WHERE vr.keyword = k.keyword
              AND vr.category IS NULL
        """)
        updated_raw = db.cursor.rowcount
        db.conn.commit()
        print(f"  업데이트: {updated_raw}개 행")
        print()

        # Step 2: youtube_videos 업데이트
        print("[Step 2/3] youtube_videos 카테고리 업데이트...")
        db.cursor.execute("""
            UPDATE youtube_videos v
            SET category = k.category
            FROM youtube_keywords k
            WHERE v.keyword = k.keyword
              AND v.category IS NULL
        """)
        updated_videos = db.cursor.rowcount
        db.conn.commit()
        print(f"  업데이트: {updated_videos}개 행")
        print()

        # Step 3: youtube_comments 업데이트
        print("[Step 3/3] youtube_comments 카테고리 업데이트...")
        db.cursor.execute("""
            UPDATE youtube_comments c
            SET category = v.category
            FROM youtube_videos v
            WHERE c.video_id = v.video_id
              AND c.category IS NULL
        """)
        updated_comments = db.cursor.rowcount
        db.conn.commit()
        print(f"  업데이트: {updated_comments}개 행")
        print()

        # 통계 확인
        print("="*80)
        print("카테고리별 통계")
        print("="*80)

        # youtube_videos_raw
        db.cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM youtube_videos_raw
            GROUP BY category
            ORDER BY category
        """)
        print("youtube_videos_raw:")
        for category, count in db.cursor.fetchall():
            print(f"  {category or 'NULL'}: {count}개")
        print()

        # youtube_videos
        db.cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM youtube_videos
            GROUP BY category
            ORDER BY category
        """)
        print("youtube_videos:")
        for category, count in db.cursor.fetchall():
            print(f"  {category or 'NULL'}: {count}개")
        print()

        # youtube_comments
        db.cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM youtube_comments
            GROUP BY category
            ORDER BY category
        """)
        print("youtube_comments:")
        for category, count in db.cursor.fetchall():
            print(f"  {category or 'NULL'}: {count}개")
        print()

        print("="*80)
        print("업데이트 완료!")
        print("="*80)

    except Exception as e:
        print(f"[ERROR] 업데이트 실패: {e}")
        import traceback
        traceback.print_exc()
        db.conn.rollback()

    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
