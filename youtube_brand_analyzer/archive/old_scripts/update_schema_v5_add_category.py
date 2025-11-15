"""
YouTube 테이블 스키마 업데이트 v5
카테고리 구분 추가 (TV, HHP)
1. youtube_keywords에 category 컬럼 추가
2. youtube_videos에 category 컬럼 추가
3. youtube_comments에 category 컬럼 추가
4. youtube_videos_raw에 category 컬럼 추가
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def main():
    print("="*80)
    print("YouTube 테이블 스키마 업데이트 v5 - 카테고리 추가")
    print("="*80)
    print()

    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    try:
        # Step 1: youtube_keywords에 category 컬럼 추가
        print("[Step 1/5] youtube_keywords 테이블에 category 컬럼 추가...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_keywords
                ADD COLUMN category VARCHAR(20) DEFAULT 'TV'
            """)
            db.conn.commit()
            print("  [OK] category 컬럼 추가 완료")
        except Exception as e:
            print(f"  [SKIP] category 컬럼: {e}")
        print()

        # Step 2: 기존 키워드들을 모두 'TV'로 설정
        print("[Step 2/5] 기존 키워드를 'TV' 카테고리로 설정...")
        try:
            db.cursor.execute("""
                UPDATE youtube_keywords
                SET category = 'TV'
                WHERE category IS NULL OR category = ''
            """)
            db.conn.commit()
            print("  [OK] 기존 키워드 카테고리 설정 완료")
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()

        # Step 3: youtube_videos_raw에 category 컬럼 추가
        print("[Step 3/5] youtube_videos_raw 테이블에 category 컬럼 추가...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_videos_raw
                ADD COLUMN category VARCHAR(20)
            """)
            db.conn.commit()
            print("  [OK] category 컬럼 추가 완료")
        except Exception as e:
            print(f"  [SKIP] category 컬럼: {e}")
        print()

        # Step 4: youtube_videos에 category 컬럼 추가
        print("[Step 4/5] youtube_videos 테이블에 category 컬럼 추가...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_videos
                ADD COLUMN category VARCHAR(20)
            """)
            db.conn.commit()
            print("  [OK] category 컬럼 추가 완료")
        except Exception as e:
            print(f"  [SKIP] category 컬럼: {e}")
        print()

        # Step 5: youtube_comments에 category 컬럼 추가
        print("[Step 5/5] youtube_comments 테이블에 category 컬럼 추가...")
        try:
            db.cursor.execute("""
                ALTER TABLE youtube_comments
                ADD COLUMN category VARCHAR(20)
            """)
            db.conn.commit()
            print("  [OK] category 컬럼 추가 완료")
        except Exception as e:
            print(f"  [SKIP] category 컬럼: {e}")
        print()

        # 최종 스키마 확인
        print("="*80)
        print("최종 스키마 확인")
        print("="*80)

        # youtube_keywords
        db.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'youtube_keywords'
            ORDER BY ordinal_position
        """)
        print("youtube_keywords 컬럼:")
        for col, dtype in db.cursor.fetchall():
            marker = " [NEW]" if col == "category" else ""
            print(f"  - {col}: {dtype}{marker}")
        print()

        # youtube_videos_raw
        db.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'youtube_videos_raw'
            ORDER BY ordinal_position
        """)
        print("youtube_videos_raw 컬럼:")
        for col, dtype in db.cursor.fetchall():
            marker = " [NEW]" if col == "category" else ""
            print(f"  - {col}: {dtype}{marker}")
        print()

        # youtube_videos
        db.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'youtube_videos'
            ORDER BY ordinal_position
        """)
        print("youtube_videos 컬럼:")
        for col, dtype in db.cursor.fetchall():
            marker = " [NEW]" if col == "category" else ""
            print(f"  - {col}: {dtype}{marker}")
        print()

        # youtube_comments
        db.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'youtube_comments'
            ORDER BY ordinal_position
        """)
        print("youtube_comments 컬럼:")
        for col, dtype in db.cursor.fetchall():
            marker = " [NEW]" if col == "category" else ""
            print(f"  - {col}: {dtype}{marker}")
        print()

        print("="*80)
        print("스키마 업데이트 완료!")
        print("="*80)
        print("추가된 컬럼:")
        print("  - category (VARCHAR(20)): TV 또는 HHP")
        print()
        print("적용된 테이블:")
        print("  - youtube_keywords")
        print("  - youtube_videos_raw")
        print("  - youtube_videos")
        print("  - youtube_comments")
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
