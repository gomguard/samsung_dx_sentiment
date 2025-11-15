"""
필터링 단계별 통계 확인
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
    print("필터링 단계별 통계")
    print("="*80)
    print()

    # 전체
    db.cursor.execute("SELECT COUNT(*) FROM youtube_videos_raw")
    total = db.cursor.fetchone()[0]
    print(f"1. 전체 수집 비디오: {total}개")

    # US 채널만
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos_raw
        WHERE channel_country = 'US'
    """)
    us_only = db.cursor.fetchone()[0]
    print(f"2. US 채널만: {us_only}개 ({us_only/total*100:.1f}%)")

    # US + category 28
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND category_id = '28'
    """)
    us_tech = db.cursor.fetchone()[0]
    print(f"3. US + Science&Tech: {us_tech}개 ({us_tech/total*100:.1f}%)")

    # US + category 28 + subscribers >= 10k
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
    """)
    us_tech_subs = db.cursor.fetchone()[0]
    print(f"4. US + Tech + Subscribers>=10k: {us_tech_subs}개 ({us_tech_subs/total*100:.1f}%)")

    # 최종 (모든 필터)
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
          AND engagement_rate >= 2.0
    """)
    final = db.cursor.fetchone()[0]
    print(f"5. 모든 필터 통과: {final}개 ({final/total*100:.1f}%)")

    print()
    print("="*80)
    print("engagement_rate 분포 (US + Tech + Subs>=10k)")
    print("="*80)

    db.cursor.execute("""
        SELECT
            COUNT(CASE WHEN engagement_rate >= 0 AND engagement_rate < 0.5 THEN 1 END) as "0-0.5%",
            COUNT(CASE WHEN engagement_rate >= 0.5 AND engagement_rate < 1.0 THEN 1 END) as "0.5-1%",
            COUNT(CASE WHEN engagement_rate >= 1.0 AND engagement_rate < 2.0 THEN 1 END) as "1-2%",
            COUNT(CASE WHEN engagement_rate >= 2.0 AND engagement_rate < 5.0 THEN 1 END) as "2-5%",
            COUNT(CASE WHEN engagement_rate >= 5.0 THEN 1 END) as "5%+"
        FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
    """)

    dist = db.cursor.fetchone()
    print(f"  0-0.5%: {dist[0]}개")
    print(f"  0.5-1%: {dist[1]}개")
    print(f"  1-2%: {dist[2]}개")
    print(f"  2-5%: {dist[3]}개")
    print(f"  5%+: {dist[4]}개")

    print()
    print("="*80)
    print("필터 완화 시나리오")
    print("="*80)

    # engagement >= 1%로 완화
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
          AND engagement_rate >= 1.0
    """)
    relaxed_1 = db.cursor.fetchone()[0]
    print(f"  Engagement >= 1%로 완화: {relaxed_1}개")

    # engagement >= 0.5%로 완화
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
          AND engagement_rate >= 0.5
    """)
    relaxed_05 = db.cursor.fetchone()[0]
    print(f"  Engagement >= 0.5%로 완화: {relaxed_05}개")

    # subscribers >= 5000으로 완화
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 5000
          AND engagement_rate >= 2.0
    """)
    relaxed_subs = db.cursor.fetchone()[0]
    print(f"  Subscribers >= 5k로 완화: {relaxed_subs}개")

    # category 제거
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND channel_subscriber_count >= 10000
          AND engagement_rate >= 2.0
    """)
    no_category = db.cursor.fetchone()[0]
    print(f"  카테고리 제한 제거: {no_category}개")

    print()

    db.disconnect()


if __name__ == "__main__":
    main()
