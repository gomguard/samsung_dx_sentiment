"""
기존 youtube_videos 테이블의 비디오들에 대해:
1. 브랜드/시리즈 추출
2. 삼성 감성 점수 분석
3. 댓글 요약 영문으로 재생성
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager
from analyzers.video_content_analyzer import VideoContentAnalyzer
from datetime import datetime


def main():
    print("="*80)
    print("기존 비디오 콘텐츠 분석")
    print("="*80)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # DB 연결
    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    # 분석기 초기화
    analyzer = VideoContentAnalyzer()

    # Step 1: 비디오 정보 가져오기
    print("[Step 1/4] youtube_videos 테이블에서 비디오 정보 가져오기...")
    db.cursor.execute('''
        SELECT video_id, title, description
        FROM youtube_videos
    ''')
    videos = db.cursor.fetchall()
    print(f"  분석할 비디오: {len(videos)}개")
    print()

    if len(videos) == 0:
        print("[WARNING] 분석할 비디오가 없습니다.")
        db.disconnect()
        return

    # Step 2: 각 비디오에 대해 브랜드/시리즈/아이템 추출
    print("[Step 2/4] 브랜드, 시리즈, 아이템 추출 중...")
    for i, (video_id, title, description) in enumerate(videos, 1):
        print(f"  [{i}/{len(videos)}] {video_id}")
        print(f"      Title: {title[:60]}...")

        # 브랜드/시리즈/아이템 추출 (brand_series_info 참조)
        brand_info = analyzer.extract_brand_and_series(title, description or "")

        # DB 업데이트
        db.cursor.execute('''
            UPDATE youtube_videos
            SET reviewed_brand = %s,
                reviewed_series = %s,
                reviewed_item = %s
            WHERE video_id = %s
        ''', (brand_info['reviewed_brand'], brand_info['reviewed_series'],
              brand_info['reviewed_item'], video_id))

        print(f"      Brand: {brand_info['reviewed_brand']}")
        print(f"      Series: {brand_info['reviewed_series']}")
        print(f"      Item: {brand_info['reviewed_item']}")

    db.conn.commit()
    print(f"  완료: {len(videos)}개 비디오")
    print()

    # Step 3: 각 비디오에 대해 제품 감성 점수 분석
    print("[Step 3/4] 리뷰 대상 제품 감성 점수 분석 중...")
    # 먼저 추출된 브랜드/시리즈 정보 가져오기
    db.cursor.execute('''
        SELECT video_id, title, description, reviewed_brand, reviewed_series
        FROM youtube_videos
    ''')
    videos_with_brand = db.cursor.fetchall()

    for i, (video_id, title, description, reviewed_brand, reviewed_series) in enumerate(videos_with_brand, 1):
        print(f"  [{i}/{len(videos_with_brand)}] {video_id}")

        # 제품명 표시
        product_name = reviewed_brand or "Unknown"
        if reviewed_series:
            product_name = f"{reviewed_brand} {reviewed_series}"
        print(f"      Product: {product_name}")

        # 감성 점수 분석 (추출된 브랜드/시리즈 정보 사용)
        sentiment_score = analyzer.analyze_product_sentiment(
            title, description or "",
            reviewed_brand, reviewed_series
        )

        # DB 업데이트
        db.cursor.execute('''
            UPDATE youtube_videos
            SET product_sentiment_score = %s
            WHERE video_id = %s
        ''', (sentiment_score, video_id))

        print(f"      Sentiment: {sentiment_score:+.1f}")

    db.conn.commit()
    print(f"  완료: {len(videos_with_brand)}개 비디오")
    print()

    # Step 4: 댓글 요약 영문으로 재생성
    print("[Step 4/4] 댓글 요약 영문으로 재생성 중...")
    for i, (video_id, title, description) in enumerate(videos, 1):
        print(f"  [{i}/{len(videos)}] {video_id}")

        # 해당 비디오의 댓글 가져오기
        db.cursor.execute('''
            SELECT comment_text_display, like_count
            FROM youtube_comments
            WHERE video_id = %s
            ORDER BY like_count DESC
            LIMIT 100
        ''', (video_id,))

        comments_data = []
        for comment_text, like_count in db.cursor.fetchall():
            comments_data.append({
                'comment_text_display': comment_text,
                'like_count': like_count
            })

        if comments_data:
            # 영문 요약 생성
            summary = analyzer.summarize_comments_english(comments_data)

            # DB 업데이트
            db.cursor.execute('''
                UPDATE youtube_videos
                SET comment_text_summary = %s
                WHERE video_id = %s
            ''', (summary, video_id))

            print(f"      Comments: {len(comments_data)}개")
            print(f"      Summary: {summary[:80]}...")
        else:
            print(f"      Comments: 0개 (스킵)")

    db.conn.commit()
    print(f"  완료: {len(videos)}개 비디오")
    print()

    # 최종 확인
    print("="*80)
    print("완료 요약")
    print("="*80)
    db.cursor.execute('''
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN reviewed_brand IS NOT NULL THEN 1 END) as with_brand,
            COUNT(CASE WHEN reviewed_series IS NOT NULL THEN 1 END) as with_series,
            COUNT(CASE WHEN reviewed_item IS NOT NULL THEN 1 END) as with_item,
            COUNT(CASE WHEN product_sentiment_score IS NOT NULL THEN 1 END) as with_sentiment,
            COUNT(CASE WHEN comment_text_summary IS NOT NULL THEN 1 END) as with_summary
        FROM youtube_videos
    ''')
    stats = db.cursor.fetchone()

    print(f"전체 비디오: {stats[0]}개")
    print(f"  브랜드 정보: {stats[1]}개 ({stats[1]/stats[0]*100:.1f}%)")
    print(f"  시리즈 정보: {stats[2]}개 ({stats[2]/stats[0]*100:.1f}%)")
    print(f"  아이템 정보: {stats[3]}개 ({stats[3]/stats[0]*100:.1f}%)")
    print(f"  제품 감성 점수: {stats[4]}개 ({stats[4]/stats[0]*100:.1f}%)")
    print(f"  댓글 요약: {stats[5]}개 ({stats[5]/stats[0]*100:.1f}%)")
    print()
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    db.disconnect()


if __name__ == "__main__":
    main()
