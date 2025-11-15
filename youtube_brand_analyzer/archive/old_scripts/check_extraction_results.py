"""
brand_series_info 기반 추출 결과 확인
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

    db.cursor.execute('''
        SELECT video_id, title, reviewed_brand, reviewed_series, reviewed_item, product_sentiment_score
        FROM youtube_videos
        ORDER BY video_id
    ''')

    print("="*120)
    print("비디오 분석 결과 (brand_series_info 기반)")
    print("="*120)
    print()

    for row in db.cursor.fetchall():
        video_id, title, brand, series, item, sentiment = row

        # 제품명 구성
        product_name = brand or "Unknown"
        if series:
            product_name = f"{brand} {series}"

        print(f"Video ID: {video_id}")
        print(f"  Title: {title[:80]}...")
        print(f"  Product: {product_name}")
        print(f"  Brand: {brand or 'N/A'}")
        print(f"  Series: {series or 'N/A'}")
        print(f"  Item: {item or 'N/A'}")
        print(f"  Product Sentiment: {sentiment:+.1f}" if sentiment else "  Product Sentiment: N/A")
        print()

    # 통계
    db.cursor.execute('''
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN reviewed_brand IS NOT NULL THEN 1 END) as with_brand,
            COUNT(CASE WHEN reviewed_series IS NOT NULL THEN 1 END) as with_series,
            COUNT(CASE WHEN reviewed_item IS NOT NULL THEN 1 END) as with_item
        FROM youtube_videos
    ''')
    stats = db.cursor.fetchone()

    print("="*120)
    print("통계")
    print("="*120)
    print(f"전체 비디오: {stats[0]}개")
    print(f"  브랜드 정보: {stats[1]}개 ({stats[1]/stats[0]*100:.1f}%)")
    print(f"  시리즈 정보: {stats[2]}개 ({stats[2]/stats[0]*100:.1f}%)")
    print(f"  아이템 정보: {stats[3]}개 ({stats[3]/stats[0]*100:.1f}%)")
    print("="*120)

    db.disconnect()


if __name__ == "__main__":
    main()
