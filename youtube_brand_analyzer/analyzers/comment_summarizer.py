import os
import sys
import pandas as pd
from openai import OpenAI
import time
from typing import List, Dict
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import OPENAI_API_KEY


class CommentSummarizer:
    """OpenAI API를 사용하여 YouTube 댓글을 요약하는 클래스"""

    def __init__(self, api_key=OPENAI_API_KEY, model="gpt-4o-mini"):
        """
        CommentSummarizer 초기화

        Args:
            api_key (str): OpenAI API 키
            model (str): 사용할 OpenAI 모델 (기본값: gpt-4o-mini, 더 저렴하고 빠름)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def summarize_comments_for_video(self, comments: List[Dict], max_comments=100) -> Dict:
        """
        단일 비디오의 댓글들을 요약

        Args:
            comments (List[Dict]): 댓글 리스트
            max_comments (int): 요약에 사용할 최대 댓글 수

        Returns:
            Dict: 요약 결과
        """
        if not comments:
            return {
                'summary': 'No comments available',
                'key_themes': [],
                'sentiment_summary': 'N/A',
                'total_comments': 0
            }

        # 좋아요 순으로 정렬하여 상위 댓글만 사용
        sorted_comments = sorted(comments, key=lambda x: x.get('like_count', 0), reverse=True)
        top_comments = sorted_comments[:max_comments]

        # 댓글 텍스트 추출
        comment_texts = []
        for comment in top_comments:
            # comment_text_display 또는 comment_text_original 둘 다 시도
            text = comment.get('comment_text_display', '') or comment.get('comment_text_original', '')
            if text and len(text) > 0:
                comment_texts.append(text)

        if not comment_texts:
            return {
                'summary': 'No valid comment text available',
                'key_themes': [],
                'sentiment_summary': 'N/A',
                'total_comments': len(comments)
            }

        # OpenAI API로 요약 요청
        try:
            summary_result = self._call_openai_api(comment_texts)
            summary_result['total_comments'] = len(comments)
            summary_result['analyzed_comments'] = len(comment_texts)
            return summary_result

        except Exception as e:
            print(f"Error summarizing comments: {e}")
            return {
                'summary': f'Error: {str(e)}',
                'key_themes': [],
                'sentiment_summary': 'Error',
                'total_comments': len(comments),
                'error': str(e)
            }

    def _call_openai_api(self, comment_texts: List[str]) -> Dict:
        """
        OpenAI API를 호출하여 댓글 요약

        Args:
            comment_texts (List[str]): 댓글 텍스트 리스트

        Returns:
            Dict: 요약 결과
        """
        # 댓글을 하나의 텍스트로 결합 (너무 길면 잘라냄)
        combined_text = "\n".join([f"- {text[:200]}" for text in comment_texts[:50]])

        # 프롬프트 구성 (영어로 요약)
        prompt = f"""Analyze the following YouTube video comments and provide a summary in JSON format (in English):

Comments:
{combined_text}

Please respond in the following JSON format:
{{
    "summary": "Overall summary of comments in 2-3 sentences (in English)",
    "key_themes": ["Main theme 1", "Main theme 2", "Main theme 3"],
    "sentiment_summary": "Overall sentiment (positive, negative, neutral, mixed)",
    "positive_points": ["Positive point 1", "Positive point 2"],
    "negative_points": ["Negative point 1", "Negative point 2"],
    "common_questions": ["Common question 1", "Common question 2"]
}}

IMPORTANT: All text in the JSON response must be in English. The response must be valid JSON format."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing YouTube comments. You analyze the main content, sentiment, and themes of comments and summarize them in structured JSON format. Always respond in English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            # 응답 파싱
            result_text = response.choices[0].message.content.strip()

            # JSON 파싱 시도
            try:
                # JSON 코드 블록 제거 (```json ... ``` 형식인 경우)
                if result_text.startswith('```'):
                    result_text = result_text.split('```')[1]
                    if result_text.startswith('json'):
                        result_text = result_text[4:]
                    result_text = result_text.strip()

                result = json.loads(result_text)
                return result

            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트 그대로 반환
                return {
                    'summary': result_text,
                    'key_themes': [],
                    'sentiment_summary': 'Unknown',
                    'positive_points': [],
                    'negative_points': [],
                    'common_questions': []
                }

        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")

    def summarize_comments_from_csv(self, csv_path: str, output_path: str = None,
                                   video_csv_path: str = None) -> pd.DataFrame:
        """
        CSV 파일에서 댓글을 읽어 비디오별로 요약하고 결과를 저장

        Args:
            csv_path (str): 댓글 CSV 파일 경로
            output_path (str): 요약 결과를 저장할 CSV 파일 경로 (None이면 자동 생성)
            video_csv_path (str): 비디오 정보 CSV 파일 경로 (병합용, 선택사항)

        Returns:
            pd.DataFrame: 요약 결과 데이터프레임
        """
        # 댓글 데이터 로드
        print(f"Loading comments from {csv_path}...")
        comments_df = pd.read_csv(csv_path, encoding='utf-8-sig')

        # 비디오별로 그룹화
        video_groups = comments_df.groupby('video_id')

        print(f"Found {len(video_groups)} videos with comments")

        # 각 비디오별로 요약
        summaries = []
        for video_id, group in video_groups:
            print(f"Summarizing comments for video: {video_id} ({len(group)} comments)")

            # 댓글을 딕셔너리 리스트로 변환
            comments_list = group.to_dict('records')

            # 요약 생성
            summary = self.summarize_comments_for_video(comments_list)

            # 결과에 video_id 추가
            summary['video_id'] = video_id
            summaries.append(summary)

            # API Rate Limit 방지를 위한 지연
            time.sleep(1)

        # 데이터프레임으로 변환
        summaries_df = pd.DataFrame(summaries)

        # key_themes, positive_points 등 리스트를 문자열로 변환
        for col in ['key_themes', 'positive_points', 'negative_points', 'common_questions']:
            if col in summaries_df.columns:
                summaries_df[col] = summaries_df[col].apply(
                    lambda x: '; '.join(x) if isinstance(x, list) else str(x)
                )

        # 비디오 데이터와 병합 (제공된 경우)
        if video_csv_path:
            print(f"Merging with video data from {video_csv_path}...")
            video_df = pd.read_csv(video_csv_path, encoding='utf-8-sig')
            result_df = video_df.merge(summaries_df, on='video_id', how='left')
        else:
            result_df = summaries_df

        # 결과 저장
        if output_path is None:
            # 자동으로 파일명 생성
            base_name = os.path.splitext(csv_path)[0]
            output_path = f"{base_name}_summarized.csv"

        print(f"Saving results to {output_path}...")
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"Done! Summarized {len(summaries)} videos")
        return result_df


def main():
    """
    사용 예시
    """
    import argparse

    parser = argparse.ArgumentParser(description='Summarize YouTube comments using OpenAI API')
    parser.add_argument('--comments', type=str, required=True, help='Path to comments CSV file')
    parser.add_argument('--output', type=str, help='Path to output CSV file (optional)')
    parser.add_argument('--videos', type=str, help='Path to videos CSV file for merging (optional)')
    parser.add_argument('--model', type=str, default='gpt-4o-mini', help='OpenAI model to use')

    args = parser.parse_args()

    # Summarizer 초기화
    summarizer = CommentSummarizer(model=args.model)

    # 요약 실행
    result_df = summarizer.summarize_comments_from_csv(
        csv_path=args.comments,
        output_path=args.output,
        video_csv_path=args.videos
    )

    print("\nSummary statistics:")
    print(f"Total videos: {len(result_df)}")
    print(f"Average comments per video: {result_df['total_comments'].mean():.1f}")


if __name__ == "__main__":
    main()
