"""
TikTok 비디오 메타데이터와 Summary를 JSON/CSV로 추출
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

import json
import csv
from db_manager import TikTokDBManager

def export_video_summaries():
    """비디오 메타데이터와 Summary를 파일로 추출"""

    db = TikTokDBManager()
    if not db.connect():
        print("DB 연결 실패")
        return

    print("="*80)
    print("TikTok 비디오 메타데이터 & Summary 추출")
    print("="*80)
    print()

    # 전체 비디오 데이터 가져오기
    db.cursor.execute('''
        SELECT
            video_id,
            search_keyword,
            title,
            description,
            video_content_summary,
            comment_text_summary,
            key_themes,
            sentiment_summary,
            view_count,
            like_count,
            comment_count,
            channel_title,
            channel_subscriber_count,
            channel_country,
            collected_at
        FROM tiktok_videos
        ORDER BY view_count DESC
    ''')

    videos = db.cursor.fetchall()

    print(f"총 {len(videos)}개 비디오 추출 중...")
    print()

    # JSON 형식으로 정리
    json_data = []
    csv_data = []

    for (vid, keyword, title, desc, video_summary, comment_summary,
         themes, sentiment, views, likes, comments,
         channel, subs, country, collected) in videos:

        # JSON 데이터
        video_obj = {
            "video_id": vid,
            "search_keyword": keyword,
            "metadata_from_rapidapi": {
                "title": title,
                "description": desc,
                "channel_name": channel,
                "channel_subscribers": subs,
                "channel_country": country if country else "Unknown"
            },
            "statistics": {
                "views": views,
                "likes": likes,
                "comments": comments
            },
            "ai_generated_summaries": {
                "video_summary": video_summary if video_summary else "(요약 없음)",
                "comment_summary": comment_summary if comment_summary else "(요약 없음)",
                "key_themes": themes if themes else "(테마 없음)",
                "sentiment": sentiment if sentiment else "(감정 분석 없음)"
            },
            "collected_at": str(collected) if collected else None
        }
        json_data.append(video_obj)

        # CSV 데이터
        csv_row = {
            "video_id": vid,
            "search_keyword": keyword,
            "title": title,
            "description": desc[:200] if desc else "",  # 200자로 제한
            "video_summary": video_summary if video_summary else "",
            "comment_summary": comment_summary[:200] if comment_summary else "",  # 200자로 제한
            "key_themes": themes if themes else "",
            "sentiment": sentiment if sentiment else "",
            "views": views,
            "likes": likes,
            "comments": comments,
            "channel_name": channel,
            "channel_subscribers": subs,
            "channel_country": country if country else "Unknown",
            "collected_at": str(collected) if collected else ""
        }
        csv_data.append(csv_row)

    # JSON 파일 저장
    json_filename = "tiktok_video_summaries.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] JSON 저장: {json_filename}")
    print(f"     - {len(json_data)}개 비디오")
    print()

    # CSV 파일 저장
    csv_filename = "tiktok_video_summaries_final.csv"
    if csv_data:
        with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = [
                "video_id", "search_keyword", "title", "description",
                "video_summary", "comment_summary",
                "key_themes", "sentiment",
                "views", "likes", "comments",
                "channel_name", "channel_subscribers", "channel_country", "collected_at"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)

        print(f"[OK] CSV 저장: {csv_filename}")
        print(f"     - {len(csv_data)}개 비디오")
        print()

    # 통계 출력
    with_video_summary = sum(1 for v in json_data if v['ai_generated_summaries']['video_summary'] != "(요약 없음)")
    with_comment_summary = sum(1 for v in json_data if v['ai_generated_summaries']['comment_summary'] != "(요약 없음)")

    print("="*80)
    print("추출 완료!")
    print(f"  Video Summary 있음: {with_video_summary}/{len(json_data)}개")
    print(f"  Comment Summary 있음: {with_comment_summary}/{len(json_data)}개")
    print("="*80)

    db.disconnect()

if __name__ == "__main__":
    export_video_summaries()
