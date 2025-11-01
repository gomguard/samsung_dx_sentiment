#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram JSON 데이터를 CSV로 변환
"""

import json
import pandas as pd
import sys
import os

# Windows 콘솔 인코딩 설정
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

def parse_instagram_json(json_file):
    """Instagram JSON 파일 파싱"""
    print(f"📖 JSON 파일 읽는 중: {json_file}")

    posts = []

    # 전체 파일을 문자열로 읽기
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # JSON 배열들을 분리 (여러 JSON 배열이 연속으로 있을 수 있음)
    json_arrays = []
    depth = 0
    start = 0

    for i, char in enumerate(content):
        if char == '[':
            if depth == 0:
                start = i
            depth += 1
        elif char == ']':
            depth -= 1
            if depth == 0:
                json_arrays.append(content[start:i+1])

    print(f"📦 {len(json_arrays)}개의 JSON 배열 발견")

    # 각 JSON 배열 파싱
    for array_idx, json_str in enumerate(json_arrays, 1):
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 배열 {array_idx} 파싱 실패: {e}")
            continue

        if not isinstance(data, list):
            print(f"⚠️  JSON 배열 {array_idx}가 배열 형태가 아닙니다.")
            continue

        for idx, item in enumerate(data, 1):
            # item이 딕셔너리가 아니면 스킵
            if not isinstance(item, dict):
                continue

            # 게시물 기본 정보
            post_info = {
                'post_id': item.get('pk', ''),
                'post_code': item.get('code', ''),
                'post_url': f"https://instagram.com/p/{item.get('code', '')}" if item.get('code') else '',
                'taken_at': item.get('taken_at', ''),
                'taken_at_ts': item.get('taken_at_ts', 0),
                'media_type': item.get('media_type', 0),  # 1=이미지, 2=비디오, 8=캐러셀
                'product_type': item.get('product_type', ''),
            }

            # 미디어 정보
            post_info.update({
                'thumbnail_url': item.get('thumbnail_url', ''),
                'video_url': item.get('video_url', ''),
                'video_duration': item.get('video_duration', 0),
                'view_count': item.get('view_count', 0),
                'play_count': item.get('play_count', 0),
            })

            # 이미지 버전 (첫 번째 이미지만)
            image_versions = item.get('image_versions', [])
            if image_versions:
                first_image = image_versions[0]
                post_info.update({
                    'image_width': first_image.get('width', 0),
                    'image_height': first_image.get('height', 0),
                    'image_url': first_image.get('url', ''),
                })
            else:
                post_info.update({
                    'image_width': 0,
                    'image_height': 0,
                    'image_url': '',
                })

            # 사용자 정보
            user = item.get('user', {})
            post_info.update({
                'user_id': user.get('pk', ''),
                'username': user.get('username', ''),
                'full_name': user.get('full_name', ''),
                'profile_pic_url': user.get('profile_pic_url', ''),
                'is_private': user.get('is_private', False),
                'is_verified': user.get('is_verified', False),
            })

            # 인게이지먼트 지표
            post_info.update({
                'like_count': item.get('like_count', 0),
                'comment_count': item.get('comment_count', 0),
                'comments_disabled': item.get('comments_disabled', False),
                'has_liked': item.get('has_liked', False),
            })

            # 콘텐츠 정보
            post_info.update({
                'caption_text': item.get('caption_text', ''),
                'title': item.get('title', ''),
                'accessibility_caption': item.get('accessibility_caption', ''),
            })

            # 태그 정보
            usertags = item.get('usertags', [])
            tagged_users = []
            for tag in usertags:
                if 'user' in tag and 'username' in tag['user']:
                    tagged_users.append(tag['user']['username'])
            post_info['tagged_users'] = ', '.join(tagged_users)

            # 스폰서 태그
            sponsor_tags = item.get('sponsor_tags', [])
            sponsors = []
            for sponsor in sponsor_tags:
                if 'sponsor' in sponsor and 'username' in sponsor['sponsor']:
                    sponsors.append(sponsor['sponsor']['username'])
            post_info['sponsors'] = ', '.join(sponsors)

            # 비즈니스/광고
            post_info.update({
                'is_paid_partnership': item.get('is_paid_partnership', False),
            })

            # 위치 정보
            location = item.get('location', None)
            if location:
                post_info['location_name'] = location.get('name', '')
                post_info['location_address'] = location.get('address', '')
            else:
                post_info['location_name'] = ''
                post_info['location_address'] = ''

            # 캐러셀 게시물인 경우 리소스 개수
            resources = item.get('resources', [])
            post_info['resources_count'] = len(resources)

            posts.append(post_info)

        if len(posts) % 100 == 0:
            print(f"  처리 중: {len(posts)}개 게시물...")

    print(f"✅ 총 {len(posts)}개 게시물 파싱 완료")
    return pd.DataFrame(posts)

def main():
    """메인 실행 함수"""
    json_file = 'data/sample_data_json.txt'
    output_csv = 'data/instagram_data_converted_new.csv'

    print("🔄 Instagram JSON → CSV 변환 시작")
    print("=" * 60)

    # JSON 파싱
    df = parse_instagram_json(json_file)

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
    print(f"   총 좋아요: {df['like_count'].sum():,}개")
    print(f"   총 댓글: {df['comment_count'].sum():,}개")

    # 미디어 타입별 카운트
    media_type_map = {1: '이미지', 2: '비디오', 8: '캐러셀'}
    print("\n   미디어 타입별:")
    for media_type, count in df['media_type'].value_counts().items():
        type_name = media_type_map.get(media_type, f'기타({media_type})')
        print(f"   - {type_name}: {count}개")

    # 비디오가 있는 경우
    videos = df[df['video_url'].notna() & (df['video_url'] != '')]
    if len(videos) > 0:
        print(f"\n   총 조회수 (비디오): {videos['view_count'].sum():,}회")
        print(f"   평균 조회수: {videos['view_count'].mean():,.0f}회")

    print(f"\n   평균 좋아요: {df['like_count'].mean():,.0f}개")
    print(f"   평균 댓글: {df['comment_count'].mean():,.0f}개")

    # 인증 계정
    verified = df[df['is_verified'] == True]
    print(f"\n   인증 계정: {len(verified)}개 ({len(verified)/len(df)*100:.1f}%)")

    # 유료 파트너십
    paid = df[df['is_paid_partnership'] == True]
    print(f"   유료 파트너십: {len(paid)}개 ({len(paid)/len(df)*100:.1f}%)")

    print("\n📋 컬럼 목록:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")

    print("\n" + "=" * 60)
    print("✅ 변환 완료!")

if __name__ == "__main__":
    main()
