"""
youtube_videos_raw 테이블 마이그레이션
PRIMARY KEY를 video_id에서 (video_id, collected_at)로 변경
시계열 데이터 수집을 위한 스키마 변경
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def main():
    print("="*80)
    print("youtube_videos_raw 테이블 마이그레이션")
    print("PRIMARY KEY: video_id -> (video_id, collected_at)")
    print("="*80)
    print()

    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    try:
        # Step 1: 현재 데이터 개수 확인
        print("[Step 1/6] 현재 데이터 확인...")
        db.cursor.execute('SELECT COUNT(*) FROM youtube_videos_raw')
        current_count = db.cursor.fetchone()[0]
        print(f"  현재 데이터: {current_count}개")
        print()

        # Step 2: 백업 테이블 생성 및 데이터 복사
        print("[Step 2/6] 백업 테이블 생성 및 데이터 복사...")
        db.cursor.execute('DROP TABLE IF EXISTS youtube_videos_raw_backup CASCADE')
        db.cursor.execute("""
            CREATE TABLE youtube_videos_raw_backup AS
            SELECT * FROM youtube_videos_raw
        """)
        db.conn.commit()

        db.cursor.execute('SELECT COUNT(*) FROM youtube_videos_raw_backup')
        backup_count = db.cursor.fetchone()[0]
        print(f"  백업 완료: {backup_count}개")
        print()

        # Step 3: 기존 테이블 삭제
        print("[Step 3/6] 기존 youtube_videos_raw 테이블 삭제...")
        db.cursor.execute('DROP TABLE IF EXISTS youtube_videos_raw CASCADE')
        db.conn.commit()
        print("  삭제 완료")
        print()

        # Step 4: 새로운 스키마로 테이블 재생성
        print("[Step 4/6] 새로운 스키마로 테이블 재생성...")
        db.create_tables()  # 새로운 스키마로 생성 (PRIMARY KEY가 변경됨)
        print()

        # Step 5: 백업 데이터 복원
        print("[Step 5/6] 백업 데이터 복원...")
        db.cursor.execute("""
            INSERT INTO youtube_videos_raw (
                video_id, keyword, title, description, published_at,
                category_id, channel_id, channel_title, channel_country,
                channel_custom_url, channel_subscriber_count, channel_video_count,
                channel_total_view_count, view_count, like_count, comment_count,
                engagement_rate, quality_filter_passed, filter_fail_reason,
                collected_at
            )
            SELECT
                video_id, keyword, title, description, published_at,
                category_id, channel_id, channel_title, channel_country,
                channel_custom_url, channel_subscriber_count, channel_video_count,
                channel_total_view_count, view_count, like_count, comment_count,
                engagement_rate, quality_filter_passed, filter_fail_reason,
                COALESCE(collected_at, created_at, CURRENT_TIMESTAMP) as collected_at
            FROM youtube_videos_raw_backup
            ON CONFLICT (video_id, collected_at) DO NOTHING
        """)
        db.conn.commit()

        db.cursor.execute('SELECT COUNT(*) FROM youtube_videos_raw')
        restored_count = db.cursor.fetchone()[0]
        print(f"  복원 완료: {restored_count}개")
        print()

        # Step 6: 백업 테이블 삭제
        print("[Step 6/6] 백업 테이블 삭제...")
        db.cursor.execute('DROP TABLE IF EXISTS youtube_videos_raw_backup')
        db.conn.commit()
        print("  백업 테이블 삭제 완료")
        print()

        # 최종 확인
        print("="*80)
        print("마이그레이션 완료")
        print("="*80)
        print(f"원본 데이터: {current_count}개")
        print(f"복원 데이터: {restored_count}개")
        print()
        print("변경 사항:")
        print("  - PRIMARY KEY: video_id -> (video_id, collected_at)")
        print("  - 이제 같은 video_id라도 다른 시간에 수집하면 별도 행으로 저장됨")
        print("  - 시계열 분석 가능")
        print("="*80)

    except Exception as e:
        print(f"[ERROR] 마이그레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        db.conn.rollback()

        # 오류 발생 시 백업에서 복구
        print()
        print("[RECOVERY] 백업에서 복구 시도...")
        try:
            db.cursor.execute('DROP TABLE IF EXISTS youtube_videos_raw')
            db.cursor.execute("""
                CREATE TABLE youtube_videos_raw AS
                SELECT * FROM youtube_videos_raw_backup
            """)
            db.cursor.execute('ALTER TABLE youtube_videos_raw ADD PRIMARY KEY (video_id)')
            db.conn.commit()
            print("  복구 완료 (원래 스키마로 복원)")
        except Exception as e2:
            print(f"  복구 실패: {e2}")

    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
