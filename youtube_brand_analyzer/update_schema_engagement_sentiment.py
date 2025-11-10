"""
DB 스키마 업데이트 스크립트

추가되는 컬럼:
1. youtube_videos.category_id - 영상 카테고리 ID
2. youtube_videos.engagement_rate - 참여율 (좋아요+댓글)/조회수*100
3. youtube_comments.published_at - 댓글 작성 시간
4. youtube_comments.sentiment_score - 감정 점수 (-1.0 ~ +1.0)

실행 방법:
    python update_schema_engagement_sentiment.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def update_schema():
    """스키마 업데이트 실행"""

    db = YouTubeDBManager()

    if not db.connect():
        print("DB 연결 실패")
        return False

    print("="*80)
    print("YouTube DB 스키마 업데이트")
    print("="*80)
    print()

    try:
        # 1. youtube_videos 테이블에 category_id 추가
        print("[1/4] youtube_videos.category_id 추가 중...")
        db.cursor.execute("""
            ALTER TABLE youtube_videos
            ADD COLUMN IF NOT EXISTS category_id VARCHAR(50);
        """)
        print("  [OK] category_id 컬럼 추가 완료")

        # 2. youtube_videos 테이블에 engagement_rate 추가
        print("[2/4] youtube_videos.engagement_rate 추가 중...")
        db.cursor.execute("""
            ALTER TABLE youtube_videos
            ADD COLUMN IF NOT EXISTS engagement_rate DECIMAL(10, 4);
        """)
        print("  [OK] engagement_rate 컬럼 추가 완료")

        # 3. youtube_comments 테이블에 published_at 추가
        print("[3/4] youtube_comments.published_at 추가 중...")
        db.cursor.execute("""
            ALTER TABLE youtube_comments
            ADD COLUMN IF NOT EXISTS published_at TIMESTAMP;
        """)
        print("  [OK] published_at 컬럼 추가 완료")

        # 4. youtube_comments 테이블에 sentiment_score 추가
        print("[4/4] youtube_comments.sentiment_score 추가 중...")
        db.cursor.execute("""
            ALTER TABLE youtube_comments
            ADD COLUMN IF NOT EXISTS sentiment_score DECIMAL(5, 4);
        """)
        print("  [OK] sentiment_score 컬럼 추가 완료")

        # 커밋
        db.conn.commit()

        print()
        print("="*80)
        print("스키마 업데이트 완료!")
        print("="*80)

        # 현재 테이블 구조 확인
        print()
        print("현재 youtube_videos 컬럼:")
        db.cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'youtube_videos'
            ORDER BY ordinal_position;
        """)
        for col_name, data_type, max_length in db.cursor.fetchall():
            length_str = f"({max_length})" if max_length else ""
            print(f"  - {col_name}: {data_type}{length_str}")

        print()
        print("현재 youtube_comments 컬럼:")
        db.cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'youtube_comments'
            ORDER BY ordinal_position;
        """)
        for col_name, data_type, max_length in db.cursor.fetchall():
            length_str = f"({max_length})" if max_length else ""
            print(f"  - {col_name}: {data_type}{length_str}")

        db.disconnect()
        return True

    except Exception as e:
        print(f"[ERROR] 스키마 업데이트 실패: {e}")
        db.conn.rollback()
        db.disconnect()
        return False


if __name__ == "__main__":
    success = update_schema()
    sys.exit(0 if success else 1)
