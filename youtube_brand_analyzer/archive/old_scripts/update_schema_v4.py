"""
YouTube 테이블 스키마 업데이트 v4
samsung_sentiment_score → product_sentiment_score 로 변경
(해당 영상에서 리뷰하는 제품에 대한 감성 점수)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def main():
    print("="*80)
    print("YouTube 테이블 스키마 업데이트 v4")
    print("="*80)
    print()

    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    try:
        # samsung_sentiment_score → product_sentiment_score 컬럼명 변경
        print("[Step 1/2] samsung_sentiment_score → product_sentiment_score 변경...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_videos
                RENAME COLUMN samsung_sentiment_score TO product_sentiment_score
            """)
            db.conn.commit()
            print("  [OK] 컬럼명 변경 완료")
        except Exception as e:
            print(f"  [SKIP] 컬럼명 변경: {e}")
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
        print("변경 사항:")
        print("  - samsung_sentiment_score → product_sentiment_score")
        print("    (삼성 제품 감성 → 리뷰 대상 제품 감성)")
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
