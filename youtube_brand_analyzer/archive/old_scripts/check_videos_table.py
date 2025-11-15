"""
youtube_videos 테이블의 실제 데이터 확인
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
    print("youtube_videos 테이블 분석")
    print("="*80)
    print()

    # youtube_videos 테이블 총 개수
    db.cursor.execute('SELECT COUNT(*) FROM youtube_videos')
    total = db.cursor.fetchone()[0]
    print(f'youtube_videos 전체: {total}개')
    print()

    # 필터 조건별 개수
    db.cursor.execute("""
        SELECT COUNT(*) FROM youtube_videos
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
          AND engagement_rate >= 2.0
    """)
    filtered = db.cursor.fetchone()[0]
    print(f'[OK] 모든 필터 조건 만족: {filtered}개 ({filtered/total*100:.1f}%)')
    print(f'[X] 필터 조건 불만족: {total - filtered}개 ({(total-filtered)/total*100:.1f}%)')
    print()

    # 상세 분석
    db.cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN channel_country = 'US' THEN 1 END) as us,
            COUNT(CASE WHEN category_id = '28' THEN 1 END) as tech,
            COUNT(CASE WHEN channel_subscriber_count >= 10000 THEN 1 END) as subs,
            COUNT(CASE WHEN engagement_rate >= 2.0 THEN 1 END) as engagement
        FROM youtube_videos
    """)
    stats = db.cursor.fetchone()

    print("="*80)
    print("필터별 통과 개수")
    print("="*80)
    print(f'  US 채널: {stats[1]}/{stats[0]} ({stats[1]/stats[0]*100:.1f}%)')
    print(f'  Category 28: {stats[2]}/{stats[0]} ({stats[2]/stats[0]*100:.1f}%)')
    print(f'  Subscribers >= 10k: {stats[3]}/{stats[0]} ({stats[3]/stats[0]*100:.1f}%)')
    print(f'  Engagement >= 2%: {stats[4]}/{stats[0]} ({stats[4]/stats[0]*100:.1f}%)')
    print()

    # 국가별 분포
    print("="*80)
    print("국가별 분포 (상위 10개)")
    print("="*80)
    db.cursor.execute("""
        SELECT channel_country, COUNT(*) as cnt
        FROM youtube_videos
        GROUP BY channel_country
        ORDER BY cnt DESC
        LIMIT 10
    """)
    countries = db.cursor.fetchall()
    for country, cnt in countries:
        print(f'  {country}: {cnt}개 ({cnt/total*100:.1f}%)')
    print()

    # 카테고리별 분포
    print("="*80)
    print("카테고리별 분포 (상위 10개)")
    print("="*80)
    db.cursor.execute("""
        SELECT category_id, COUNT(*) as cnt
        FROM youtube_videos
        GROUP BY category_id
        ORDER BY cnt DESC
        LIMIT 10
    """)
    categories = db.cursor.fetchall()
    for cat, cnt in categories:
        print(f'  Category {cat}: {cnt}개 ({cnt/total*100:.1f}%)')
    print()

    # Engagement rate 분포
    print("="*80)
    print("Engagement Rate 분포")
    print("="*80)
    db.cursor.execute("""
        SELECT
            COUNT(CASE WHEN engagement_rate >= 0 AND engagement_rate < 0.5 THEN 1 END) as "0-0.5%",
            COUNT(CASE WHEN engagement_rate >= 0.5 AND engagement_rate < 1.0 THEN 1 END) as "0.5-1%",
            COUNT(CASE WHEN engagement_rate >= 1.0 AND engagement_rate < 2.0 THEN 1 END) as "1-2%",
            COUNT(CASE WHEN engagement_rate >= 2.0 AND engagement_rate < 5.0 THEN 1 END) as "2-5%",
            COUNT(CASE WHEN engagement_rate >= 5.0 THEN 1 END) as "5%+"
        FROM youtube_videos
    """)
    dist = db.cursor.fetchone()
    print(f'  0-0.5%: {dist[0]}개 ({dist[0]/total*100:.1f}%)')
    print(f'  0.5-1%: {dist[1]}개 ({dist[1]/total*100:.1f}%)')
    print(f'  1-2%: {dist[2]}개 ({dist[2]/total*100:.1f}%)')
    print(f'  2-5%: {dist[3]}개 ({dist[3]/total*100:.1f}%)')
    print(f'  5%+: {dist[4]}개 ({dist[4]/total*100:.1f}%)')
    print()

    db.disconnect()


if __name__ == "__main__":
    main()
