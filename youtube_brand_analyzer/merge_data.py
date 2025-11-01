#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 수집 데이터 병합 스크립트
"""

import os
import sys
import pandas as pd
from datetime import datetime
from glob import glob

# Windows 콘솔 인코딩 설정
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

def merge_csv_files(pattern, output_filename):
    """CSV 파일들을 하나로 병합"""
    data_dir = "data"

    # 패턴에 맞는 모든 파일 찾기
    files = glob(os.path.join(data_dir, pattern))

    if not files:
        print(f"⚠️  '{pattern}' 패턴에 맞는 파일이 없습니다.")
        return

    print(f"📁 {len(files)}개 파일 발견:")
    for f in files:
        print(f"   - {os.path.basename(f)}")

    # 모든 CSV 파일 읽어서 병합
    dfs = []
    for file in files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig')
            dfs.append(df)
            print(f"   ✓ {os.path.basename(file)} 읽기 완료 ({len(df)}행)")
        except Exception as e:
            print(f"   ✗ {os.path.basename(file)} 읽기 실패: {e}")

    if not dfs:
        print("❌ 읽을 수 있는 파일이 없습니다.")
        return

    # 데이터프레임 병합
    merged_df = pd.concat(dfs, ignore_index=True)

    # 중복 제거 (video_id 기준 또는 comment_id 기준)
    if 'video_id' in merged_df.columns:
        before_count = len(merged_df)
        merged_df = merged_df.drop_duplicates(subset=['video_id'], keep='first')
        after_count = len(merged_df)
        print(f"\n🔄 중복 제거: {before_count}행 → {after_count}행 ({before_count - after_count}개 중복 제거)")
    elif 'comment_id' in merged_df.columns:
        before_count = len(merged_df)
        merged_df = merged_df.drop_duplicates(subset=['comment_id'], keep='first')
        after_count = len(merged_df)
        print(f"\n🔄 중복 제거: {before_count}행 → {after_count}행 ({before_count - after_count}개 중복 제거)")

    # 저장
    output_path = os.path.join(data_dir, output_filename)
    merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 병합 완료: {output_path} ({len(merged_df)}행)")

    return merged_df

def main():
    """메인 실행 함수"""
    print("🔗 YouTube 데이터 병합 시작")
    print("=" * 60)

    # Videos 파일 병합 (최신 수집본만)
    print("\n[1/2] Videos 파일 병합 중...")
    videos_df = merge_csv_files("videos_*_20251012_13*.csv", "all_videos_merged.csv")

    # Comments 파일 병합 (최신 수집본만)
    print("\n[2/2] Comments 파일 병합 중...")
    comments_df = merge_csv_files("comments_*_20251012_13*.csv", "all_comments_merged.csv")

    print("\n" + "=" * 60)
    print("🎉 병합 완료!")

    if videos_df is not None:
        print(f"   📹 총 비디오: {len(videos_df)}개")
        print(f"   👀 총 조회수: {videos_df['view_count'].sum():,}회")
        print(f"   👍 총 좋아요: {videos_df['like_count'].sum():,}개")

    if comments_df is not None:
        print(f"   💬 총 댓글: {len(comments_df)}개")
        if 'sentiment_label' in comments_df.columns:
            positive = len(comments_df[comments_df['sentiment_label'] == 'positive'])
            negative = len(comments_df[comments_df['sentiment_label'] == 'negative'])
            neutral = len(comments_df[comments_df['sentiment_label'] == 'neutral'])
            print(f"   😊 긍정: {positive}개 ({positive/len(comments_df)*100:.1f}%)")
            print(f"   😐 중립: {neutral}개 ({neutral/len(comments_df)*100:.1f}%)")
            print(f"   😞 부정: {negative}개 ({negative/len(comments_df)*100:.1f}%)")

if __name__ == "__main__":
    main()
