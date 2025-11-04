"""
기존 비디오들의 Comment Summary와 Video Summary 생성
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, '..'))

import time
import pandas as pd

# Import comment summarizer
parent_dir = os.path.dirname(os.path.dirname(__file__))
youtube_analyzer_path = os.path.join(parent_dir, 'youtube_brand_analyzer', 'analyzers')
instagram_analyzer_path = os.path.join(parent_dir, 'instagram_brand_analyzer', 'analyzers')

CommentSummarizer = None
for analyzer_path in [youtube_analyzer_path, instagram_analyzer_path]:
    if analyzer_path not in sys.path:
        sys.path.insert(0, analyzer_path)
    try:
        from comment_summarizer import CommentSummarizer
        print(f"[OK] Loaded CommentSummarizer")
        break
    except Exception as e:
        continue

# Import video summarizer
try:
    from openai import OpenAI
    from config.secrets import OPENAI_API_KEY
    client = OpenAI(api_key=OPENAI_API_KEY)
    print(f"[OK] Loaded OpenAI client")
except Exception as e:
    print(f"[ERROR] Failed to load OpenAI: {e}")
    client = None

sys.path.insert(0, os.path.join(current_dir, 'config'))
from db_manager import TikTokDBManager


def generate_video_summary(title, description):
    """비디오 제목과 설명을 기반으로 영상 요약 생성"""
    if not client:
        return "Video summarization not available"

    try:
        prompt = f"""다음 TikTok 비디오의 제목과 설명을 바탕으로 영상 내용을 2-3문장으로 요약해주세요.

제목: {title}
설명: {description}

요약 (한글 2-3문장):"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 TikTok 비디오 내용을 요약하는 전문가입니다. 제목과 설명을 바탕으로 비디오의 핵심 내용을 간결하게 요약합니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"      [ERROR] Video summary failed: {e}")
        return "Video summarization failed"


def generate_missing_summaries():
    """Comment Summary와 Video Summary 생성"""

    db = TikTokDBManager()
    if not db.connect():
        print("DB 연결 실패")
        return

    summarizer = CommentSummarizer() if CommentSummarizer else None

    print("="*80)
    print("TikTok Summary 생성")
    print("="*80)
    print()

    # 1. Comment Summary 생성 (댓글이 있지만 summary 없는 비디오)
    print("[1/2] Comment Summary 생성 중...")
    print()

    db.cursor.execute('''
        SELECT v.video_id, v.title
        FROM tiktok_videos v
        INNER JOIN tiktok_comments c ON v.video_id = c.video_id
        WHERE (v.comment_text_summary IS NULL OR v.comment_text_summary = '')
        GROUP BY v.video_id, v.title, v.collected_at
        HAVING COUNT(c.comment_id) > 0
        ORDER BY v.collected_at DESC
    ''')

    videos_need_comment_summary = db.cursor.fetchall()
    print(f"Comment Summary 생성 필요: {len(videos_need_comment_summary)}개")

    if summarizer and len(videos_need_comment_summary) > 0:
        for i, (video_id, title) in enumerate(videos_need_comment_summary, 1):
            try:
                title_short = title[:40] if title else 'N/A'
                print(f"[{i}/{len(videos_need_comment_summary)}] {video_id[:15]}... | {title_short}")
            except:
                print(f"[{i}/{len(videos_need_comment_summary)}] {video_id[:15]}...")

            # 댓글 가져오기
            db.cursor.execute('''
                SELECT comment_text_original, like_count, sentiment
                FROM tiktok_comments
                WHERE video_id = %s
                ORDER BY like_count DESC
            ''', (video_id,))

            comments = []
            for text, likes, sentiment in db.cursor.fetchall():
                comments.append({
                    'comment_text_original': text,
                    'like_count': likes,
                    'sentiment': sentiment
                })

            if len(comments) == 0:
                print(f"  [SKIP] 댓글 없음")
                continue

            # Summary 생성
            try:
                summary_result = summarizer.summarize_comments_for_video(comments)

                # DB 업데이트
                db.cursor.execute('''
                    UPDATE tiktok_videos
                    SET
                        comment_text_summary = %s,
                        key_themes = %s,
                        sentiment_summary = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE video_id = %s
                ''', (
                    summary_result.get('summary', ''),
                    summary_result.get('key_themes', ''),
                    summary_result.get('sentiment_summary', ''),
                    video_id
                ))
                db.conn.commit()

                print(f"  [OK] Comment summary 생성 ({len(comments)}개 댓글)")

            except Exception as e:
                print(f"  [ERROR] {e}")

            time.sleep(2)  # OpenAI rate limit

            if i % 10 == 0:
                print(f"  >>> {i}개 완료, 10초 대기...")
                time.sleep(10)

    # 2. Video Summary 생성 (모든 비디오)
    print()
    print("[2/2] Video Summary 생성 중...")
    print()

    db.cursor.execute('''
        SELECT video_id, title, description
        FROM tiktok_videos
        WHERE video_content_summary IS NULL OR video_content_summary = ''
        ORDER BY collected_at DESC
    ''')

    videos_need_video_summary = db.cursor.fetchall()
    print(f"Video Summary 생성 필요: {len(videos_need_video_summary)}개")

    if client and len(videos_need_video_summary) > 0:
        for i, (video_id, title, description) in enumerate(videos_need_video_summary, 1):
            try:
                title_short = title[:40] if title else 'N/A'
                print(f"[{i}/{len(videos_need_video_summary)}] {video_id[:15]}... | {title_short}")
            except:
                print(f"[{i}/{len(videos_need_video_summary)}] {video_id[:15]}...")

            # Video summary 생성
            try:
                video_summary = generate_video_summary(title, description)

                # DB 업데이트
                db.cursor.execute('''
                    UPDATE tiktok_videos
                    SET
                        video_content_summary = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE video_id = %s
                ''', (video_summary, video_id))
                db.conn.commit()

                print(f"  [OK] Video summary: {video_summary[:60]}...")

            except Exception as e:
                print(f"  [ERROR] {e}")

            time.sleep(2)  # OpenAI rate limit

            if i % 10 == 0:
                print(f"  >>> {i}개 완료, 10초 대기...")
                time.sleep(10)

    # 최종 통계
    print()
    print("="*80)
    print("생성 완료!")
    print("="*80)

    db.cursor.execute('''
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN comment_text_summary IS NOT NULL AND comment_text_summary <> '' THEN 1 END) as comment_summary,
            COUNT(CASE WHEN video_content_summary IS NOT NULL AND video_content_summary <> '' THEN 1 END) as video_summary
        FROM tiktok_videos
    ''')

    stats = db.cursor.fetchone()
    print(f"총 비디오: {stats[0]}개")
    print(f"Comment Summary: {stats[1]}개")
    print(f"Video Summary: {stats[2]}개")

    db.disconnect()


if __name__ == "__main__":
    generate_missing_summaries()
