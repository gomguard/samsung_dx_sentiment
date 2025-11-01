#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok JSON 데이터를 CSV로 변환
"""

import json
import pandas as pd
import sys
import os

# Windows 콘솔 인코딩 설정
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

def parse_tiktok_json(json_file):
    """TikTok JSON 파일 파싱"""
    print(f"📖 JSON 파일 읽는 중: {json_file}")

    videos = []

    # 전체 파일을 문자열로 읽기
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # JSON 객체들을 분리 (여러 JSON 객체가 연속으로 있을 수 있음)
    # "}\n{" 패턴을 찾아서 분리
    json_objects = []
    depth = 0
    start = 0

    for i, char in enumerate(content):
        if char == '{':
            if depth == 0:
                start = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                json_objects.append(content[start:i+1])

    print(f"📦 {len(json_objects)}개의 JSON 객체 발견")

    # 각 JSON 객체 파싱
    for json_idx, json_str in enumerate(json_objects, 1):
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 객체 {json_idx} 파싱 실패: {e}")
            continue

        if 'data' not in data:
            print(f"⚠️  JSON 객체 {json_idx}에 'data' 키가 없습니다.")
            continue

        for idx, entry in enumerate(data['data'], 1):
            if 'item' not in entry:
                continue

            item = entry['item']

            # 비디오 기본 정보
            video_info = {
                'video_id': item.get('id', ''),
                'description': item.get('desc', ''),
                'create_time': item.get('createTime', ''),
            }

            # 비디오 상세 정보
            video = item.get('video', {})
            video_info.update({
                'duration': video.get('duration', 0),
                'width': video.get('width', 0),
                'height': video.get('height', 0),
                'ratio': video.get('ratio', ''),
                'bitrate': video.get('bitrate', 0),
                'format': video.get('format', ''),
                'video_quality': video.get('videoQuality', ''),
                'codec_type': video.get('codecType', ''),
                'definition': video.get('definition', ''),
                'cover_url': video.get('cover', ''),
                'play_url': video.get('playAddr', ''),
            })

            # 작성자 정보
            author = item.get('author', {})
            video_info.update({
                'author_id': author.get('id', ''),
                'author_unique_id': author.get('uniqueId', ''),
                'author_nickname': author.get('nickname', ''),
                'author_verified': author.get('verified', False),
                'author_signature': author.get('signature', ''),
            })

            # 통계 정보
            stats = item.get('stats', {})
            video_info.update({
                'play_count': stats.get('playCount', 0),
                'digg_count': stats.get('diggCount', 0),  # 좋아요
                'comment_count': stats.get('commentCount', 0),
                'share_count': stats.get('shareCount', 0),
                'collect_count': stats.get('collectCount', 0),  # 저장
            })

            # 음악 정보
            music = item.get('music', {})
            video_info.update({
                'music_id': music.get('id', ''),
                'music_title': music.get('title', ''),
                'music_author': music.get('authorName', ''),
            })

            # 해시태그 추출
            hashtags = []
            challenges = item.get('challenges', [])
            for challenge in challenges:
                if 'title' in challenge:
                    hashtags.append(challenge['title'])
            video_info['hashtags'] = ', '.join(hashtags)

            # 위치 정보
            location = item.get('locationCreated', '')
            video_info['location'] = location

            videos.append(video_info)

        if len(videos) % 100 == 0:
            print(f"  처리 중: {len(videos)}개 비디오...")

    print(f"✅ 총 {len(videos)}개 비디오 파싱 완료")
    return pd.DataFrame(videos)

def main():
    """메인 실행 함수"""
    json_file = 'data/sample_data_json.txt'
    output_csv = 'data/tiktok_data_converted.csv'

    print("🔄 TikTok JSON → CSV 변환 시작")
    print("=" * 60)

    # JSON 파싱
    df = parse_tiktok_json(json_file)

    if df is None or len(df) == 0:
        print("❌ 변환할 데이터가 없습니다.")
        return

    # CSV 저장
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n💾 CSV 저장 완료: {output_csv}")
    print(f"   총 행 수: {len(df):,}개")
    print(f"   총 컬럼 수: {len(df.columns)}개")

    # 데이터 샘플 출력
    print("\n📊 데이터 요약:")
    print(f"   총 조회수: {df['play_count'].sum():,}회")
    print(f"   총 좋아요: {df['digg_count'].sum():,}개")
    print(f"   총 댓글: {df['comment_count'].sum():,}개")
    print(f"   총 공유: {df['share_count'].sum():,}개")

    print(f"\n   평균 조회수: {df['play_count'].mean():,.0f}회")
    print(f"   평균 좋아요: {df['digg_count'].mean():,.0f}개")
    print(f"   평균 댓글: {df['comment_count'].mean():,.0f}개")

    print("\n📋 컬럼 목록:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")

    print("\n" + "=" * 60)
    print("✅ 변환 완료!")

if __name__ == "__main__":
    main()
