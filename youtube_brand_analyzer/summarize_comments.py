"""
YouTube 댓글 요약 스크립트

이 스크립트는 수집된 YouTube 댓글을 OpenAI API를 사용하여 비디오별로 요약합니다.

사용법:
    python summarize_comments.py

또는 특정 파일 지정:
    python summarize_comments.py --comments data/comments_Samsung_TV_20251012_130818.csv
    python summarize_comments.py --comments data/all_comments_merged.csv --videos data/all_videos_merged.csv
"""

import os
import sys
from analyzers.comment_summarizer import CommentSummarizer
import glob


def find_latest_comments_file(data_dir='data'):
    """
    data 디렉토리에서 가장 최근 댓글 파일 찾기
    """
    # comments_*.csv 파일 찾기
    comment_files = glob.glob(os.path.join(data_dir, 'comments_*.csv'))

    # all_comments_merged.csv가 있으면 그것을 우선 사용
    merged_file = os.path.join(data_dir, 'all_comments_merged.csv')
    if os.path.exists(merged_file):
        return merged_file

    if not comment_files:
        return None

    # 가장 최근 파일 반환
    latest_file = max(comment_files, key=os.path.getmtime)
    return latest_file


def find_latest_videos_file(data_dir='data'):
    """
    data 디렉토리에서 가장 최근 비디오 파일 찾기
    """
    # all_videos_merged.csv가 있으면 그것을 우선 사용
    merged_file = os.path.join(data_dir, 'all_videos_merged.csv')
    if os.path.exists(merged_file):
        return merged_file

    # videos_*.csv 파일 찾기
    video_files = glob.glob(os.path.join(data_dir, 'videos_*.csv'))

    if not video_files:
        return None

    # 가장 최근 파일 반환
    latest_file = max(video_files, key=os.path.getmtime)
    return latest_file


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='YouTube 댓글을 OpenAI API로 요약합니다',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:

  1. 기본 사용 (data 폴더에서 자동으로 최신 파일 찾기):
     python summarize_comments.py

  2. 특정 댓글 파일 지정:
     python summarize_comments.py --comments data/all_comments_merged.csv

  3. 댓글 파일과 비디오 파일 모두 지정 (병합):
     python summarize_comments.py --comments data/all_comments_merged.csv --videos data/all_videos_merged.csv

  4. 다른 OpenAI 모델 사용:
     python summarize_comments.py --model gpt-4o

  5. 출력 파일명 지정:
     python summarize_comments.py --output data/my_summary.csv

주의사항:
  - OpenAI API 키가 config/settings.py에 설정되어 있어야 합니다
  - 비디오가 많을 경우 시간이 오래 걸리고 비용이 발생할 수 있습니다
  - gpt-4o-mini 모델이 기본값이며 가장 저렴합니다
        """
    )

    parser.add_argument(
        '--comments',
        type=str,
        help='댓글 CSV 파일 경로 (지정하지 않으면 data 폴더에서 자동으로 찾음)'
    )

    parser.add_argument(
        '--videos',
        type=str,
        help='비디오 CSV 파일 경로 (선택사항, 지정하면 비디오 정보와 병합)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='출력 CSV 파일 경로 (지정하지 않으면 자동 생성)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o-mini',
        choices=['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'],
        help='사용할 OpenAI 모델 (기본: gpt-4o-mini)'
    )

    args = parser.parse_args()

    # 댓글 파일 결정
    comments_file = args.comments
    if not comments_file:
        print("댓글 파일이 지정되지 않았습니다. data 폴더에서 자동으로 찾습니다...")
        comments_file = find_latest_comments_file()
        if not comments_file:
            print("ERROR: data 폴더에서 댓글 파일을 찾을 수 없습니다.")
            print("다음 중 하나를 수행하세요:")
            print("  1. --comments 옵션으로 파일 경로를 직접 지정")
            print("  2. data 폴더에 comments_*.csv 또는 all_comments_merged.csv 파일이 있는지 확인")
            sys.exit(1)
        print(f"찾은 파일: {comments_file}")

    # 파일 존재 확인
    if not os.path.exists(comments_file):
        print(f"ERROR: 댓글 파일을 찾을 수 없습니다: {comments_file}")
        sys.exit(1)

    # 비디오 파일 결정 (선택사항)
    videos_file = args.videos
    if not videos_file and not args.videos:
        # 자동으로 찾기 시도
        videos_file = find_latest_videos_file()
        if videos_file:
            print(f"비디오 파일 발견: {videos_file}")
            print("비디오 정보와 함께 병합하여 저장됩니다.")

    # 설정 확인
    from config.settings import OPENAI_API_KEY
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        print("ERROR: OpenAI API 키가 설정되지 않았습니다.")
        print("config/settings.py 파일에서 OPENAI_API_KEY를 설정해주세요.")
        print("\n설정 방법:")
        print("1. https://platform.openai.com/api-keys 에서 API 키 발급")
        print("2. config/settings.py 파일을 열어 다음 줄을 수정:")
        print('   OPENAI_API_KEY = "your-api-key-here"')
        sys.exit(1)

    print("="*80)
    print("YouTube 댓글 요약 시작")
    print("="*80)
    print(f"댓글 파일: {comments_file}")
    if videos_file:
        print(f"비디오 파일: {videos_file}")
    print(f"OpenAI 모델: {args.model}")
    print(f"출력 파일: {args.output or '자동 생성'}")
    print("="*80)
    print()

    # 사용자 확인
    response = input("계속하시겠습니까? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("취소되었습니다.")
        sys.exit(0)

    print()

    # Summarizer 초기화
    try:
        summarizer = CommentSummarizer(model=args.model)
    except Exception as e:
        print(f"ERROR: CommentSummarizer 초기화 실패: {e}")
        sys.exit(1)

    # 요약 실행
    try:
        result_df = summarizer.summarize_comments_from_csv(
            csv_path=comments_file,
            output_path=args.output,
            video_csv_path=videos_file
        )

        print()
        print("="*80)
        print("요약 완료!")
        print("="*80)
        print(f"요약된 비디오 수: {len(result_df)}")
        if 'total_comments' in result_df.columns:
            print(f"총 댓글 수: {result_df['total_comments'].sum():.0f}")
            print(f"비디오당 평균 댓글 수: {result_df['total_comments'].mean():.1f}")

        # 감성 분포 출력
        if 'sentiment_summary' in result_df.columns:
            print("\n감성 분포:")
            sentiment_counts = result_df['sentiment_summary'].value_counts()
            for sentiment, count in sentiment_counts.items():
                print(f"  {sentiment}: {count}개 ({count/len(result_df)*100:.1f}%)")

    except Exception as e:
        print(f"ERROR: 요약 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
