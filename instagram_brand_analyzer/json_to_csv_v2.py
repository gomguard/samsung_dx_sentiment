#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram v2 API JSON 데이터를 CSV로 변환
"""

import json
import pandas as pd
import sys
import os

# Windows 콘솔 인코딩 설정
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

def extract_media_from_v2_response(data):
    """v2 API 응답에서 media 객체들 추출"""
    media_list = []

    if 'response' not in data or 'sections' not in data['response']:
        return media_list

    sections = data['response']['sections']

    for section in sections:
        if 'layout_content' not in section:
            continue

        layout_content = section['layout_content']

        # medias 직접 구조 (리스트 또는 딕셔너리)
        if 'medias' in layout_content:
            medias = layout_content['medias']

            # medias가 리스트인 경우
            if isinstance(medias, list):
                for media_item in medias:
                    if isinstance(media_item, dict) and 'media' in media_item:
                        media_list.append(media_item['media'])

            # medias가 딕셔너리인 경우
            elif isinstance(medias, dict) and 'items' in medias:
                for media_item in medias['items']:
                    if 'media' in media_item:
                        media_list.append(media_item['media'])

        # one_by_two_item 구조
        if 'one_by_two_item' in layout_content:
            item = layout_content['one_by_two_item']

            # clips
            if 'clips' in item and 'items' in item['clips']:
                for clip_item in item['clips']['items']:
                    if 'media' in clip_item:
                        media_list.append(clip_item['media'])

            # medias
            if 'medias' in item and 'items' in item['medias']:
                for media_item in item['medias']['items']:
                    if 'media' in media_item:
                        media_list.append(media_item['media'])

        # two_by_two_item 구조
        if 'two_by_two_item' in layout_content:
            item = layout_content['two_by_two_item']
            if 'medias' in item and 'items' in item['medias']:
                for media_item in item['medias']['items']:
                    if 'media' in media_item:
                        media_list.append(media_item['media'])

    return media_list

def parse_instagram_v2_json(json_file):
    """Instagram v2 JSON 파일 파싱 (line-delimited JSON)"""
    print(f"📖 JSON 파일 읽는 중: {json_file}")

    posts = []
    line_count = 0
    valid_json_count = 0

    # 파일을 줄 단위로 읽기 (line-delimited JSON)
    with open(json_file, 'r', encoding='utf-8') as f:
        for line_idx, line in enumerate(f, 1):
            line_count += 1
            line = line.strip()

            if not line or not (line.startswith('{') or line.startswith('[')):
                continue

            try:
                data = json.loads(line)
                valid_json_count += 1
            except json.JSONDecodeError as e:
                if line_idx <= 10:  # 처음 10개만 에러 출력
                    print(f"⚠️  줄 {line_idx} 파싱 실패: {str(e)[:50]}")
                continue

            # v2 API 응답에서 media 추출
            media_list = extract_media_from_v2_response(data)

            if not media_list:
                continue

            for media in media_list:
            # 게시물 기본 정보
            post_info = {
                'post_id': str(media.get('pk', '')),
                'post_code': media.get('code', ''),
                'post_url': f"https://instagram.com/p/{media.get('code', '')}" if media.get('code') else '',
                'taken_at': media.get('taken_at', ''),
                'taken_at_ts': media.get('taken_at_ts', 0),
                'media_type': media.get('media_type', 0),
                'product_type': media.get('product_type', ''),
            }

            # 미디어 정보
            post_info.update({
                'thumbnail_url': media.get('thumbnail_url', ''),
                'video_url': media.get('video_url', ''),
                'video_duration': media.get('video_duration', 0),
                'view_count': media.get('view_count', 0),
                'play_count': media.get('play_count', 0),
                'ig_play_count': media.get('ig_play_count', 0),
            })

            # image_versions2 (v2 구조)
            image_versions2 = media.get('image_versions2', {})
            candidates = image_versions2.get('candidates', [])
            if candidates:
                first_image = candidates[0]
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
            user = media.get('user', {})
            post_info.update({
                'user_id': str(user.get('pk', '')),
                'username': user.get('username', ''),
                'full_name': user.get('full_name', ''),
                'profile_pic_url': user.get('profile_pic_url', ''),
                'is_private': user.get('is_private', False),
                'is_verified': user.get('is_verified', False),
            })

            # 인게이지먼트 지표
            post_info.update({
                'like_count': media.get('like_count', 0),
                'comment_count': media.get('comment_count', 0),
                'comments_disabled': media.get('comments_disabled', False),
                'has_liked': media.get('has_liked', False),
                'reshare_count': media.get('reshare_count', 0),
            })

            # 캡션 정보 (v2 구조)
            caption = media.get('caption', {})
            if isinstance(caption, dict):
                caption_text = caption.get('text', '')
            else:
                caption_text = str(caption) if caption else ''

            post_info.update({
                'caption_text': caption_text,
                'title': media.get('title', ''),
                'accessibility_caption': media.get('accessibility_caption', ''),
            })

            # 태그 정보
            usertags = media.get('usertags', {})
            if isinstance(usertags, dict):
                in_list = usertags.get('in', [])
            else:
                in_list = []

            tagged_users = []
            for tag in in_list:
                if 'user' in tag and 'username' in tag['user']:
                    tagged_users.append(tag['user']['username'])
            post_info['tagged_users'] = ', '.join(tagged_users)

            # 스폰서 태그
            sponsor_tags = media.get('sponsor_tags', [])
            sponsors = []
            for sponsor in sponsor_tags:
                if isinstance(sponsor, dict):
                    if 'sponsor' in sponsor and 'username' in sponsor['sponsor']:
                        sponsors.append(sponsor['sponsor']['username'])
            post_info['sponsors'] = ', '.join(sponsors)

            # 비즈니스/광고
            post_info.update({
                'is_paid_partnership': media.get('is_paid_partnership', False),
            })

            # 위치 정보
            location = media.get('location', None)
            if location:
                post_info['location_name'] = location.get('name', '')
                post_info['location_address'] = location.get('address', '')
            else:
                post_info['location_name'] = ''
                post_info['location_address'] = ''

            # 캐러셀 게시물
            carousel_media = media.get('carousel_media', [])
            post_info['carousel_media_count'] = len(carousel_media)

            posts.append(post_info)

        if len(posts) % 100 == 0 and len(posts) > 0:
            print(f"  처리 중: {len(posts)}개 게시물...")

    print(f"✅ 총 {len(posts)}개 게시물 파싱 완료")
    return pd.DataFrame(posts)

def main():
    """메인 실행 함수"""
    json_file = 'data/sample_data_json.txt'
    output_csv = 'data/instagram_v2_all.csv'

    print("🔄 Instagram v2 JSON → CSV 변환 시작")
    print("=" * 60)

    # JSON 파싱
    df = parse_instagram_v2_json(json_file)

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
        print(f"\n   비디오 게시물: {len(videos)}개")
        print(f"   총 조회수: {videos['play_count'].sum():,}회")
        print(f"   평균 조회수: {videos['play_count'].mean():,.0f}회")

    print(f"\n   평균 좋아요: {df['like_count'].mean():,.0f}개")
    print(f"   평균 댓글: {df['comment_count'].mean():,.0f}개")

    # 인증 계정
    verified = df[df['is_verified'] == True]
    print(f"\n   인증 계정: {len(verified)}개 ({len(verified)/len(df)*100:.1f}%)")

    print("\n📋 컬럼 목록:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")

    print("\n" + "=" * 60)
    print("✅ 변환 완료!")

if __name__ == "__main__":
    main()
