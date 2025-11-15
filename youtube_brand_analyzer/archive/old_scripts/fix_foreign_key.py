"""
youtube_comments 테이블의 Foreign Key Constraint 수정
youtube_videos_bk → youtube_videos로 변경
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def main():
    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    print("="*80)
    print("YouTube Comments Foreign Key 수정")
    print("="*80)
    print()

    # 1. 기존 constraint 확인
    print("[Step 1/3] 기존 Foreign Key Constraint 확인...")
    db.cursor.execute("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'youtube_comments'
          AND constraint_type = 'FOREIGN KEY'
    """)
    constraints = db.cursor.fetchall()
    print(f"  찾은 Foreign Key Constraints: {len(constraints)}개")
    for constraint in constraints:
        print(f"    - {constraint[0]}")
    print()

    # 2. 기존 constraint 삭제
    print("[Step 2/3] 기존 Foreign Key Constraint 삭제...")
    for constraint in constraints:
        constraint_name = constraint[0]
        try:
            db.cursor.execute(f"""
                ALTER TABLE youtube_comments
                DROP CONSTRAINT {constraint_name}
            """)
            print(f"  삭제 완료: {constraint_name}")
        except Exception as e:
            print(f"  삭제 실패: {constraint_name} - {e}")

    db.conn.commit()
    print()

    # 3. 새로운 constraint 생성
    print("[Step 3/3] 새로운 Foreign Key Constraint 생성 (youtube_videos 참조)...")
    try:
        db.cursor.execute("""
            ALTER TABLE youtube_comments
            ADD CONSTRAINT youtube_comments_video_id_fkey
            FOREIGN KEY (video_id)
            REFERENCES youtube_videos(video_id)
            ON DELETE CASCADE
        """)
        db.conn.commit()
        print("  생성 완료: youtube_comments_video_id_fkey")
    except Exception as e:
        print(f"  생성 실패: {e}")

    print()
    print("="*80)
    print("완료")
    print("="*80)

    db.disconnect()


if __name__ == "__main__":
    main()
