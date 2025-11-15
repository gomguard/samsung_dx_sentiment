"""
YouTube 테이블 스키마 업데이트 v2
1. youtube_videos에 컬럼 추가: reviewed_brand, reviewed_series, samsung_sentiment_score
2. youtube_comments에서 sentiment_score 삭제
3. 모든 테이블에서 updated_at 삭제
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def main():
    print("="*80)
    print("YouTube 테이블 스키마 업데이트 v2")
    print("="*80)
    print()

    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    try:
        # Step 1: youtube_videos 테이블에 새 컬럼 추가
        print("[Step 1/5] youtube_videos 테이블에 새 컬럼 추가...")

        # reviewed_brand
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_videos
                ADD COLUMN reviewed_brand TEXT
            """)
            print("  [OK] reviewed_brand 컬럼 추가")
        except Exception as e:
            print(f"  [SKIP] reviewed_brand: {e}")

        # reviewed_series
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_videos
                ADD COLUMN reviewed_series TEXT
            """)
            print("  [OK] reviewed_series 컬럼 추가")
        except Exception as e:
            print(f"  [SKIP] reviewed_series: {e}")

        # samsung_sentiment_score
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_videos
                ADD COLUMN samsung_sentiment_score DECIMAL(3, 1)
            """)
            print("  [OK] samsung_sentiment_score 컬럼 추가")
        except Exception as e:
            print(f"  [SKIP] samsung_sentiment_score: {e}")

        db.conn.commit()
        print()

        # Step 2: youtube_comments에서 sentiment_score 삭제
        print("[Step 2/5] youtube_comments에서 sentiment_score 삭제...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_comments
                DROP COLUMN sentiment_score
            """)
            db.conn.commit()
            print("  [OK] sentiment_score 컬럼 삭제 완료")
        except Exception as e:
            print(f"  [SKIP] sentiment_score 삭제: {e}")
        print()

        # Step 3: youtube_videos에서 updated_at 삭제
        print("[Step 3/5] youtube_videos에서 updated_at 삭제...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_videos
                DROP COLUMN updated_at
            """)
            db.conn.commit()
            print("  [OK] updated_at 컬럼 삭제 완료")
        except Exception as e:
            print(f"  [SKIP] updated_at 삭제: {e}")
        print()

        # Step 4: youtube_comments에서 updated_at 삭제
        print("[Step 4/5] youtube_comments에서 updated_at 삭제...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_comments
                DROP COLUMN updated_at
            """)
            db.conn.commit()
            print("  [OK] updated_at 컬럼 삭제 완료")
        except Exception as e:
            print(f"  [SKIP] updated_at 삭제: {e}")
        print()

        # Step 5: 최종 스키마 확인
        print("[Step 5/5] 최종 스키마 확인...")

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

        db.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'youtube_comments'
            ORDER BY ordinal_position
        """)
        print("  youtube_comments 컬럼:")
        for col, dtype in db.cursor.fetchall():
            print(f"    - {col}: {dtype}")
        print()

        print("="*80)
        print("스키마 업데이트 완료!")
        print("="*80)
        print("추가된 컬럼:")
        print("  - reviewed_brand: 리뷰 대상 브랜드")
        print("  - reviewed_series: 리뷰 대상 시리즈명")
        print("  - samsung_sentiment_score: 삼성 제품 감성 점수 (-5 ~ +5)")
        print()
        print("삭제된 컬럼:")
        print("  - sentiment_score (youtube_comments)")
        print("  - updated_at (youtube_videos, youtube_comments)")
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
