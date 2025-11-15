"""
youtube_videos_raw 데이터를 기반으로 youtube_videos 테이블 재구성 및 댓글 수집

1. youtube_videos_raw에서 필터링 (US, category 28, engagement >= 2%, subscribers >= 10k)
2. 필터링된 비디오의 댓글 수집
3. youtube_videos 테이블에 삽입
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

from config.db_manager import YouTubeDBManager
from collectors.youtube_api import YouTubeAnalyzer
from analyzers.comment_summarizer import CommentSummarizer
import time
from datetime import datetime


def main():
    print("="*80)
    print("YouTube Videos 테이블 재구성")
    print("="*80)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. DB 연결
    db = YouTubeDBManager()
    if not db.connect():
        print("[ERROR] DB 연결 실패")
        return

    # 2. youtube_videos_raw 통계 확인
    print("[Step 1/5] youtube_videos_raw 테이블 통계")
    db.cursor.execute('''
        SELECT COUNT(*) as total,
               COUNT(DISTINCT channel_id) as unique_channels,
               COUNT(CASE WHEN channel_country = 'US' THEN 1 END) as us_videos,
               COUNT(CASE WHEN category_id = '28' THEN 1 END) as tech_category
        FROM youtube_videos_raw
    ''')
    stats = db.cursor.fetchone()
    print(f"  총 비디오: {stats[0]}")
    print(f"  고유 채널: {stats[1]}")
    print(f"  US 채널 비디오: {stats[2]}")
    print(f"  Science & Tech 카테고리: {stats[3]}")
    print()

    # 3. 필터링 기준에 맞는 비디오 선택
    print("[Step 2/5] 필터링 기준 적용 (US + category 28 + engagement >= 2% + subscribers >= 10k)")
    db.cursor.execute('''
        SELECT video_id, keyword, title, description, published_at,
               channel_country, channel_custom_url, channel_subscriber_count,
               channel_video_count, view_count, like_count, comment_count,
               category_id, engagement_rate
        FROM youtube_videos_raw
        WHERE channel_country = 'US'
          AND category_id = '28'
          AND channel_subscriber_count >= 10000
          AND engagement_rate >= 2.0
        ORDER BY engagement_rate DESC
    ''')

    filtered_videos = db.cursor.fetchall()
    print(f"  필터링 통과: {len(filtered_videos)}개 비디오")

    if len(filtered_videos) == 0:
        print("[WARNING] 필터링 통과한 비디오가 없습니다.")
        db.disconnect()
        return

    # video_id 리스트 추출
    video_ids = [row[0] for row in filtered_videos]
    print(f"  비디오 ID: {video_ids[:5]}... (처음 5개)")
    print()

    # 4. 댓글 수집
    print(f"[Step 3/5] {len(video_ids)}개 비디오의 댓글 수집 중...")
    youtube_api = YouTubeAnalyzer()
    comments_data = youtube_api.get_comprehensive_comments(
        video_ids=video_ids,
        max_comments_per_video=20
    )
    print(f"  수집된 댓글: {len(comments_data)}개")
    print()

    # 5. 댓글 요약 생성
    print(f"[Step 4/5] 댓글 요약 생성 중...")
    comment_summarizer = CommentSummarizer()

    # 비디오별로 댓글 그룹화
    video_comments_map = {}
    for comment in comments_data:
        vid = comment['video_id']
        if vid not in video_comments_map:
            video_comments_map[vid] = []
        video_comments_map[vid].append(comment)

    video_summaries = {}
    for video_id in video_ids:
        if video_id in video_comments_map:
            comments_list = video_comments_map[video_id]
            print(f"  Summarizing: {video_id} ({len(comments_list)} comments)")

            summary = comment_summarizer.summarize_comments_for_video(comments_list)
            video_summaries[video_id] = summary.get('summary', '')

            time.sleep(1)  # API rate limit
        else:
            video_summaries[video_id] = ''

    print(f"  생성된 요약: {len(video_summaries)}개")
    print()

    # 6. youtube_videos 테이블에 삽입
    print(f"[Step 5/5] youtube_videos 테이블에 데이터 삽입...")

    # 기존 데이터 삭제 (재구성이므로)
    db.cursor.execute("DELETE FROM youtube_videos")
    db.conn.commit()
    print("  기존 youtube_videos 테이블 데이터 삭제 완료")

    # 데이터 삽입
    insert_count = 0
    for row in filtered_videos:
        video_id = row[0]
        keyword = row[1]
        title = row[2]
        description = row[3]
        published_at = row[4]
        channel_country = row[5]
        channel_custom_url = row[6]
        channel_subscriber_count = row[7]
        channel_video_count = row[8]
        view_count = row[9]
        like_count = row[10]
        comment_count = row[11]
        category_id = row[12]
        engagement_rate = row[13]

        comment_text_summary = video_summaries.get(video_id, '')

        db.cursor.execute('''
            INSERT INTO youtube_videos (
                video_id, keyword, title, description, published_at,
                channel_country, channel_custom_url, channel_subscriber_count,
                channel_video_count, view_count, like_count, comment_count,
                category_id, engagement_rate, comment_text_summary
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO UPDATE SET
                keyword = EXCLUDED.keyword,
                comment_text_summary = EXCLUDED.comment_text_summary,
                view_count = EXCLUDED.view_count,
                like_count = EXCLUDED.like_count,
                comment_count = EXCLUDED.comment_count,
                engagement_rate = EXCLUDED.engagement_rate
        ''', (
            video_id, keyword, title, description, published_at,
            channel_country, channel_custom_url, channel_subscriber_count,
            channel_video_count, view_count, like_count, comment_count,
            category_id, engagement_rate, comment_text_summary
        ))
        insert_count += 1

    db.conn.commit()
    print(f"  삽입 완료: {insert_count}개 비디오")

    # 댓글 데이터도 삽입
    print(f"  댓글 데이터 삽입 중...")
    comment_insert_count = 0
    for comment in comments_data:
        try:
            db.cursor.execute('''
                INSERT INTO youtube_comments (
                    comment_id, video_id, comment_type, parent_comment_id,
                    comment_text_display,
                    like_count, reply_count, published_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (comment_id) DO NOTHING
            ''', (
                comment['comment_id'], comment['video_id'], comment['comment_type'],
                comment['parent_comment_id'],
                comment['comment_text_display'],
                comment['like_count'], comment['reply_count'], comment['published_at']
            ))
            comment_insert_count += 1
        except Exception as e:
            print(f"  [WARNING] 댓글 삽입 실패: {e}")

    db.conn.commit()
    print(f"  댓글 삽입 완료: {comment_insert_count}개")
    print()

    # 최종 통계
    print("="*80)
    print("완료 요약")
    print("="*80)
    print(f"youtube_videos 테이블: {insert_count}개 비디오")
    print(f"youtube_comments 테이블: {comment_insert_count}개 댓글")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    db.disconnect()


if __name__ == "__main__":
    main()
