"""
youtube_videos 테이블 재구성
youtube_videos_raw에서 가장 최신 데이터만 가져와서 필터링
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager


def main():
    print("="*80)
    print("youtube_videos 테이블 재구성")
    print("="*80)
    print()

    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    # Step 1: 현재 상태 확인
    print("[Step 1/4] 현재 테이블 상태 확인...")
    db.cursor.execute('SELECT COUNT(*) FROM youtube_videos_raw')
    raw_count = db.cursor.fetchone()[0]
    db.cursor.execute('SELECT COUNT(*) FROM youtube_videos')
    videos_count = db.cursor.fetchone()[0]
    print(f"  youtube_videos_raw: {raw_count}개")
    print(f"  youtube_videos: {videos_count}개")
    print()

    # Step 2: 각 video_id의 최신 데이터만 선택해서 필터링
    print("[Step 2/4] youtube_videos_raw에서 최신 데이터 필터링...")
    db.cursor.execute("""
        WITH latest_videos AS (
            SELECT DISTINCT ON (video_id)
                video_id, keyword, title, description, published_at,
                category_id, channel_id, channel_title, channel_country,
                channel_custom_url, channel_subscriber_count, channel_video_count,
                view_count, like_count, comment_count,
                engagement_rate, collected_at
            FROM youtube_videos_raw
            ORDER BY video_id, collected_at DESC
        )
        SELECT COUNT(*) FROM latest_videos
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
          AND engagement_rate >= 2.0
    """)
    filtered_count = db.cursor.fetchone()[0]
    print(f"  필터 조건 만족 (최신 데이터): {filtered_count}개")
    print()

    # Step 3: youtube_videos 테이블 비우기
    print("[Step 3/4] youtube_videos 테이블 비우기...")
    db.cursor.execute('DELETE FROM youtube_videos')
    db.conn.commit()
    print(f"  삭제 완료: {videos_count}개 삭제됨")
    print()

    # Step 4: 최신 데이터만 필터링해서 youtube_videos에 삽입
    print("[Step 4/4] 필터링된 최신 데이터를 youtube_videos에 삽입...")
    db.cursor.execute("""
        WITH latest_videos AS (
            SELECT DISTINCT ON (video_id)
                video_id, keyword, title, description, published_at,
                category_id, channel_id, channel_title, channel_country,
                channel_custom_url, channel_subscriber_count, channel_video_count,
                view_count, like_count, comment_count,
                engagement_rate, collected_at
            FROM youtube_videos_raw
            ORDER BY video_id, collected_at DESC
        )
        INSERT INTO youtube_videos (
            video_id, keyword, title, description, published_at,
            channel_country, channel_custom_url, channel_subscriber_count, channel_video_count,
            view_count, like_count, comment_count,
            category_id, engagement_rate
        )
        SELECT
            video_id, keyword, title, description, published_at,
            channel_country, channel_custom_url, channel_subscriber_count, channel_video_count,
            view_count, like_count, comment_count,
            category_id, engagement_rate
        FROM latest_videos
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
          AND engagement_rate >= 2.0
        ON CONFLICT (video_id) DO UPDATE SET
            title = EXCLUDED.title,
            channel_custom_url = EXCLUDED.channel_custom_url,
            channel_subscriber_count = EXCLUDED.channel_subscriber_count,
            channel_video_count = EXCLUDED.channel_video_count,
            view_count = EXCLUDED.view_count,
            like_count = EXCLUDED.like_count,
            comment_count = EXCLUDED.comment_count,
            engagement_rate = EXCLUDED.engagement_rate
    """)
    db.conn.commit()
    print(f"  삽입 완료: {filtered_count}개")
    print()

    # 최종 확인
    print("="*80)
    print("완료 요약")
    print("="*80)
    db.cursor.execute('SELECT COUNT(*) FROM youtube_videos')
    final_count = db.cursor.fetchone()[0]
    print(f"youtube_videos 테이블:")
    print(f"  이전: {videos_count}개 (불량 데이터 포함)")
    print(f"  이후: {final_count}개 (필터링된 고품질 데이터만)")
    print()
    print(f"youtube_videos_raw 테이블: {raw_count}개 (시계열 데이터 전체)")
    print()
    print("필터 조건:")
    print("  - channel_country = 'US'")
    print("  - category_id = '28' (Science & Technology)")
    print("  - channel_subscriber_count >= 10,000")
    print("  - engagement_rate >= 2.0%")
    print()
    print("데이터 수집 방식:")
    print("  - youtube_videos_raw: 모든 수집 데이터 시계열로 저장")
    print("  - youtube_videos: 필터링된 최신 데이터만 저장")
    print("="*80)

    db.disconnect()


if __name__ == "__main__":
    main()
