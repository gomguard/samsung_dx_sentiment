"""
YouTube 테이블 스키마 업데이트 v3
1. youtube_videos에 reviewed_item 컬럼 추가
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def main():
    print("="*80)
    print("YouTube 테이블 스키마 업데이트 v3")
    print("="*80)
    print()

    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    try:
        # youtube_videos 테이블에 reviewed_item 컬럼 추가
        print("[Step 1/2] youtube_videos 테이블에 reviewed_item 컬럼 추가...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_videos
                ADD COLUMN reviewed_item TEXT
            """)
            db.conn.commit()
            print("  [OK] reviewed_item 컬럼 추가 완료")
        except Exception as e:
            print(f"  [SKIP] reviewed_item: {e}")
        print()

        # 최종 스키마 확인
        print("[Step 2/2] 최종 스키마 확인...")
        db.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'youtube_videos'
            ORDER BY ordinal_position
        """)
        print("  youtube_videos 컬럼:")
        for col, dtype in db.cursor.fetchall():
            print(f"    - {col}: {dtype}")
        print()

        print("="*80)
        print("스키마 업데이트 완료!")
        print("="*80)
        print("추가된 컬럼:")
        print("  - reviewed_item: 리뷰 대상 제품의 정확한 모델명")
        print("="*80)

    except Exception as e:
        print(f"[ERROR] 스키마 업데이트 실패: {e}")
        import traceback
        traceback.print_exc()
        db.conn.rollback()

    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
