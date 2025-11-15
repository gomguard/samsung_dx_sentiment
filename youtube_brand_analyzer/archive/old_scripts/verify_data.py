"""
Verify that raw data, keyword, and comment_text_summary are properly saved
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager

db = YouTubeDBManager()
if db.connect():
    print("="*80)
    print("Database Verification")
    print("="*80)
    print()

    # 1. Raw videos 테이블 확인
    db.cursor.execute("""
        SELECT COUNT(*),
               COUNT(DISTINCT keyword),
               COUNT(CASE WHEN quality_filter_passed = true THEN 1 END) as passed,
               COUNT(CASE WHEN quality_filter_passed = false THEN 1 END) as failed
        FROM youtube_videos_raw
    """)
    total, keywords, passed, failed = db.cursor.fetchone()
    print("1. youtube_videos_raw 테이블:")
    print(f"   - 총 레코드: {total}개")
    print(f"   - 고유 키워드: {keywords}개")
    print(f"   - 필터 통과: {passed}개")
    print(f"   - 필터 실패: {failed}개")

    # Raw 샘플 데이터
    db.cursor.execute("""
        SELECT keyword, video_id, title, quality_filter_passed, filter_fail_reason
        FROM youtube_videos_raw
        LIMIT 3
    """)
    print("\n   샘플 데이터:")
    for keyword, vid, title, passed, reason in db.cursor.fetchall():
        print(f"   - [{keyword}] {vid}: {title[:50]}...")
        print(f"     통과: {passed}, 이유: {reason}")

    # 2. youtube_videos 테이블 확인
    print()
    db.cursor.execute("""
        SELECT COUNT(*),
               COUNT(keyword),
               COUNT(comment_text_summary)
        FROM youtube_videos
    """)
    total, with_keyword, with_summary = db.cursor.fetchone()
    print("2. youtube_videos 테이블:")
    print(f"   - 총 레코드: {total}개")
    print(f"   - keyword 있음: {with_keyword}개")
    print(f"   - comment_text_summary 있음: {with_summary}개")

    # Sample data
    db.cursor.execute("""
        SELECT keyword, video_id, title, comment_text_summary
        FROM youtube_videos
        WHERE keyword IS NOT NULL
        LIMIT 3
    """)
    print("\n   샘플 데이터:")
    for keyword, vid, title, summary in db.cursor.fetchall():
        summary_preview = summary[:50] if summary else "NULL"
        print(f"   - [{keyword}] {vid}: {title[:40]}...")
        print(f"     요약: {summary_preview}")

    # 3. 키워드별 통계
    print()
    db.cursor.execute("""
        SELECT keyword, COUNT(*) as count
        FROM youtube_videos
        WHERE keyword IS NOT NULL
        GROUP BY keyword
        ORDER BY count DESC
    """)
    print("3. 키워드별 비디오 수:")
    for keyword, count in db.cursor.fetchall():
        print(f"   - {keyword}: {count}개")

    print()
    print("="*80)

    db.disconnect()
