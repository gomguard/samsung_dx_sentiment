import os
import sys
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from openai import OpenAI
import time
from typing import Dict, List
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import OPENAI_API_KEY


class VideoSummarizer:
    """YouTube 비디오 자막을 추출하고 OpenAI로 요약하는 클래스"""

    def __init__(self, api_key=OPENAI_API_KEY, model="gpt-4o-mini"):
        """
        VideoSummarizer 초기화

        Args:
            api_key (str): OpenAI API 키
            model (str): 사용할 OpenAI 모델
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def get_transcript(self, video_id: str, languages=['en', 'ko', 'ja', 'es', 'pt', 'fr', 'de', 'it']) -> str:
        """
        YouTube 비디오의 자막 추출

        Args:
            video_id (str): YouTube 비디오 ID
            languages (list): 선호 언어 리스트 (순서대로 시도)

        Returns:
            str: 자막 텍스트
        """
        try:
            # API 인스턴스 생성
            api = YouTubeTranscriptApi()

            # 자막 가져오기 (언어 우선순위대로)
            # Rate limit 방지를 위해 여러 언어 시도 시 대기
            transcript_result = api.fetch(video_id, languages=languages)

            # 자막 텍스트 결합 (snippets는 FetchedTranscriptSnippet 객체의 리스트)
            transcript_text = ' '.join([snippet.text for snippet in transcript_result.snippets])

            return transcript_text

        except TranscriptsDisabled:
            raise Exception(f"Transcripts are disabled for video {video_id}")
        except NoTranscriptFound:
            raise Exception(f"No transcript found for video {video_id} in languages {languages}")
        except Exception as e:
            raise Exception(f"Error getting transcript for video {video_id}: {str(e)}")

    def summarize_video(self, video_id: str, title: str = "", description: str = "",
                       max_transcript_length: int = 8000) -> Dict:
        """
        비디오 자막을 추출하고 요약

        Args:
            video_id (str): YouTube 비디오 ID
            title (str): 비디오 제목 (선택)
            description (str): 비디오 설명 (선택)
            max_transcript_length (int): 자막 최대 길이 (토큰 절약)

        Returns:
            Dict: 요약 결과
        """
        try:
            # 1. 자막 추출
            print(f"Extracting transcript for video: {video_id}")
            transcript = self.get_transcript(video_id)

            # 자막이 너무 길면 앞부분만 사용
            if len(transcript) > max_transcript_length:
                transcript = transcript[:max_transcript_length] + "..."
                truncated = True
            else:
                truncated = False

            # 2. OpenAI로 요약
            print(f"Summarizing video content... (transcript length: {len(transcript)})")
            summary_result = self._summarize_with_openai(
                transcript=transcript,
                title=title,
                description=description
            )

            # 3. 메타데이터 추가
            summary_result['video_id'] = video_id
            summary_result['has_transcript'] = True
            summary_result['transcript_truncated'] = truncated
            summary_result['transcript_length'] = len(transcript)

            return summary_result

        except Exception as e:
            print(f"Transcript not available for {video_id}: {e}")

            # Fallback: 자막이 없으면 제목과 설명만으로 요약
            if title or description:
                print(f"Using title and description for summary...")
                try:
                    summary_result = self._summarize_with_title_description(
                        title=title,
                        description=description
                    )

                    summary_result['video_id'] = video_id
                    summary_result['has_transcript'] = False
                    summary_result['error'] = str(e)

                    return summary_result

                except Exception as e2:
                    print(f"Error summarizing with title/description: {e2}")

            # 완전 실패한 경우
            return {
                'video_id': video_id,
                'has_transcript': False,
                'error': str(e),
                'summary': 'Summary not available',
                'key_topics': [],
                'product_mentions': [],
                'sentiment': 'Unknown'
            }

    def _summarize_with_openai(self, transcript: str, title: str = "",
                               description: str = "") -> Dict:
        """
        OpenAI API로 비디오 내용 요약

        Args:
            transcript (str): 자막 텍스트
            title (str): 비디오 제목
            description (str): 비디오 설명

        Returns:
            Dict: 요약 결과
        """
        # 프롬프트 구성
        context = f"""
비디오 제목: {title}
비디오 설명: {description}

자막 내용:
{transcript}
"""

        prompt = f"""다음은 YouTube 비디오의 자막입니다. 이 비디오 내용을 분석하여 JSON 형식으로 제공해주세요:

{context}

다음 형식으로 응답해주세요:
{{
    "summary": "비디오 주요 내용을 3-4문장으로 요약",
    "key_topics": ["주요 주제1", "주요 주제2", "주요 주제3"],
    "product_mentions": {{
        "samsung": ["언급된 삼성 제품/기능1", "제품/기능2"],
        "competitors": ["언급된 경쟁사 제품/브랜드1", "제품/브랜드2"]
    }},
    "sentiment": "비디오의 전반적인 톤 (긍정적/부정적/중립적/비교)",
    "target_audience": "타겟 시청자층 (예: 일반 소비자, 게이머, 전문가 등)",
    "key_features_discussed": ["언급된 주요 기능/특징1", "기능/특징2", "기능/특징3"]
}}

응답은 반드시 유효한 JSON 형식이어야 합니다.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 YouTube 비디오 내용을 분석하는 전문가입니다. TV/전자제품 리뷰와 비교 영상을 전문적으로 분석합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )

            # 응답 파싱
            result_text = response.choices[0].message.content.strip()

            # JSON 파싱
            try:
                if result_text.startswith('```'):
                    result_text = result_text.split('```')[1]
                    if result_text.startswith('json'):
                        result_text = result_text[4:]
                    result_text = result_text.strip()

                result = json.loads(result_text)

                # 토큰 사용량 추가
                result['tokens_used'] = {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                }

                return result

            except json.JSONDecodeError:
                return {
                    'summary': result_text,
                    'key_topics': [],
                    'product_mentions': {},
                    'sentiment': 'Unknown',
                    'raw_response': result_text
                }

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _summarize_with_title_description(self, title: str = "", description: str = "") -> Dict:
        """
        제목과 설명만으로 비디오 요약 (자막이 없을 때 사용)

        Args:
            title (str): 비디오 제목
            description (str): 비디오 설명

        Returns:
            Dict: 요약 결과
        """
        # 설명이 너무 길면 앞부분만 사용
        if len(description) > 2000:
            description = description[:2000] + "..."

        context = f"""
비디오 제목: {title}

비디오 설명:
{description}
"""

        prompt = f"""다음은 YouTube 비디오의 제목과 설명입니다. 자막은 없지만 이 정보를 바탕으로 비디오 내용을 추정하여 JSON 형식으로 제공해주세요:

{context}

다음 형식으로 응답해주세요:
{{
    "summary": "제목과 설명을 바탕으로 추정한 비디오 내용 요약 (2-3문장)",
    "key_topics": ["추정되는 주요 주제1", "주제2", "주제3"],
    "product_mentions": {{
        "samsung": ["언급된 삼성 제품/기능"],
        "competitors": ["언급된 경쟁사 제품/브랜드"]
    }},
    "sentiment": "제목과 설명의 전반적인 톤 (긍정적/부정적/중립적/비교)",
    "target_audience": "타겟 시청자층",
    "key_features_discussed": ["언급된 주요 기능/특징"]
}}

주의: 자막이 없으므로 제목과 설명에서 추정 가능한 내용만 작성하세요.
응답은 반드시 유효한 JSON 형식이어야 합니다.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 YouTube 비디오의 제목과 설명을 분석하는 전문가입니다. 자막 없이도 제목과 설명만으로 비디오 내용을 정확히 추정할 수 있습니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )

            # 응답 파싱
            result_text = response.choices[0].message.content.strip()

            # JSON 파싱
            try:
                if result_text.startswith('```'):
                    result_text = result_text.split('```')[1]
                    if result_text.startswith('json'):
                        result_text = result_text[4:]
                    result_text = result_text.strip()

                result = json.loads(result_text)

                # 토큰 사용량 추가
                result['tokens_used'] = {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                }

                return result

            except json.JSONDecodeError:
                return {
                    'summary': result_text,
                    'key_topics': [],
                    'product_mentions': {},
                    'sentiment': 'Unknown',
                    'raw_response': result_text
                }

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def summarize_videos_from_csv(self, csv_path: str, output_path: str = None,
                                  video_id_column: str = 'video_id',
                                  title_column: str = 'title',
                                  description_column: str = 'description') -> pd.DataFrame:
        """
        CSV 파일에서 비디오 정보를 읽어 요약하고 결과 저장

        Args:
            csv_path (str): 비디오 정보 CSV 파일 경로
            output_path (str): 요약 결과를 저장할 CSV 파일 경로
            video_id_column (str): video_id 컬럼명
            title_column (str): title 컬럼명
            description_column (str): description 컬럼명

        Returns:
            pd.DataFrame: 요약 결과 데이터프레임
        """
        # 비디오 데이터 로드
        print(f"Loading videos from {csv_path}...")
        videos_df = pd.read_csv(csv_path, encoding='utf-8-sig')

        print(f"Found {len(videos_df)} videos")

        # 각 비디오 요약
        summaries = []
        for idx, row in videos_df.iterrows():
            video_id = row.get(video_id_column, '')
            title = row.get(title_column, '')
            description = row.get(description_column, '')

            print(f"\n[{idx+1}/{len(videos_df)}] Summarizing video: {video_id}")
            print(f"  Title: {title[:50]}...")

            # 요약 생성
            summary = self.summarize_video(
                video_id=video_id,
                title=title,
                description=description
            )

            summaries.append(summary)

            # API Rate Limit 방지
            time.sleep(1)

        # 데이터프레임으로 변환
        summaries_df = pd.DataFrame(summaries)

        # product_mentions를 문자열로 변환
        if 'product_mentions' in summaries_df.columns:
            summaries_df['product_mentions'] = summaries_df['product_mentions'].apply(
                lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else str(x)
            )

        # key_topics, key_features_discussed를 문자열로 변환
        for col in ['key_topics', 'key_features_discussed']:
            if col in summaries_df.columns:
                summaries_df[col] = summaries_df[col].apply(
                    lambda x: '; '.join(x) if isinstance(x, list) else str(x)
                )

        # 원본 데이터와 병합
        result_df = videos_df.merge(summaries_df, on='video_id', how='left')

        # 결과 저장
        if output_path is None:
            base_name = os.path.splitext(csv_path)[0]
            output_path = f"{base_name}_with_summary.csv"

        print(f"\nSaving results to {output_path}...")
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"Done! Summarized {len(summaries)} videos")
        return result_df


def main():
    """사용 예시"""
    import argparse

    parser = argparse.ArgumentParser(description='Summarize YouTube videos using transcripts and OpenAI')
    parser.add_argument('--videos', type=str, required=True, help='Path to videos CSV file')
    parser.add_argument('--output', type=str, help='Path to output CSV file (optional)')
    parser.add_argument('--model', type=str, default='gpt-4o-mini', help='OpenAI model to use')

    args = parser.parse_args()

    # Summarizer 초기화
    summarizer = VideoSummarizer(model=args.model)

    # 요약 실행
    result_df = summarizer.summarize_videos_from_csv(
        csv_path=args.videos,
        output_path=args.output
    )

    print("\nSummary statistics:")
    print(f"Total videos: {len(result_df)}")
    if 'has_transcript' in result_df.columns:
        print(f"Videos with transcripts: {result_df['has_transcript'].sum()}")
        print(f"Videos without transcripts: {(~result_df['has_transcript']).sum()}")


if __name__ == "__main__":
    main()
