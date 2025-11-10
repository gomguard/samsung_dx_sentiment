"""
YouTube 댓글 감정 분석기 (OpenAI API 사용)

개별 댓글의 감정을 -1.0 (매우 부정) ~ +1.0 (매우 긍정) 범위로 분석합니다.

사용법:
    analyzer = CommentSentimentAnalyzer()
    sentiment_score = analyzer.analyze_single_comment("Great product!")
    # Returns: 0.8

    # 배치 분석
    comments = [
        {'comment_id': '1', 'comment_text_display': 'Awesome!'},
        {'comment_id': '2', 'comment_text_display': 'Terrible quality'}
    ]
    results = analyzer.analyze_comments_batch(comments)
"""

import os
import sys
from openai import OpenAI
import time
from typing import List, Dict, Optional
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import OPENAI_API_KEY


class CommentSentimentAnalyzer:
    """OpenAI API를 사용하여 YouTube 댓글 감정을 분석하는 클래스"""

    def __init__(self, api_key=OPENAI_API_KEY, model="gpt-4o-mini"):
        """
        CommentSentimentAnalyzer 초기화

        Args:
            api_key (str): OpenAI API 키
            model (str): 사용할 OpenAI 모델 (기본값: gpt-4o-mini)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_single_comment(self, comment_text: str) -> Optional[float]:
        """
        단일 댓글의 감정 점수를 분석

        Args:
            comment_text (str): 댓글 텍스트

        Returns:
            float: 감정 점수 (-1.0 ~ +1.0), 에러 시 None
                -1.0: 매우 부정적
                -0.5: 부정적
                 0.0: 중립적
                +0.5: 긍정적
                +1.0: 매우 긍정적
        """
        if not comment_text or len(comment_text.strip()) == 0:
            return 0.0  # 빈 댓글은 중립

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a sentiment analysis expert.
Analyze the sentiment of the given comment and return ONLY a single number between -1.0 and 1.0.

Scale:
-1.0: Very negative (hate, anger, strong dissatisfaction)
-0.5: Negative (disappointment, criticism)
 0.0: Neutral (factual, no clear emotion)
+0.5: Positive (satisfaction, recommendation)
+1.0: Very positive (love, excitement, strong praise)

Return ONLY the number, no explanation."""
                    },
                    {
                        "role": "user",
                        "content": f"Comment: {comment_text}"
                    }
                ],
                temperature=0.3,  # 낮은 temperature로 일관성 있는 결과
                max_tokens=10  # 숫자만 반환하므로 짧게
            )

            # 결과 파싱
            sentiment_str = response.choices[0].message.content.strip()
            sentiment_score = float(sentiment_str)

            # 범위 제한 (-1.0 ~ +1.0)
            sentiment_score = max(-1.0, min(1.0, sentiment_score))

            return round(sentiment_score, 4)

        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return None

    def analyze_comments_batch(self, comments: List[Dict],
                               text_field='comment_text_display',
                               rate_limit_delay=0.5) -> List[Dict]:
        """
        여러 댓글의 감정을 배치로 분석

        Args:
            comments (List[Dict]): 댓글 리스트
            text_field (str): 댓글 텍스트 필드명
            rate_limit_delay (float): API 호출 간 대기 시간 (초)

        Returns:
            List[Dict]: 각 댓글에 sentiment_score가 추가된 리스트
        """
        if not comments:
            return []

        results = []
        total = len(comments)

        print(f"Analyzing sentiment for {total} comments...")

        for idx, comment in enumerate(comments, 1):
            comment_text = comment.get(text_field, '')

            # 감정 분석
            sentiment_score = self.analyze_single_comment(comment_text)

            # 결과 저장
            result = comment.copy()
            result['sentiment_score'] = sentiment_score

            results.append(result)

            # 진행 상황 출력
            if idx % 10 == 0:
                print(f"  Progress: {idx}/{total} comments analyzed")

            # Rate limit 방지
            time.sleep(rate_limit_delay)

        print(f"Sentiment analysis completed: {len(results)}/{total} comments")
        return results

    def analyze_comments_batch_optimized(self, comments: List[Dict],
                                        text_field='comment_text_display',
                                        batch_size=10,
                                        rate_limit_delay=2.0) -> List[Dict]:
        """
        여러 댓글을 배치로 묶어서 효율적으로 분석 (비용 절감)

        Args:
            comments (List[Dict]): 댓글 리스트
            text_field (str): 댓글 텍스트 필드명
            batch_size (int): 한 번에 분석할 댓글 수
            rate_limit_delay (float): 배치 간 대기 시간 (초)

        Returns:
            List[Dict]: 각 댓글에 sentiment_score가 추가된 리스트
        """
        if not comments:
            return []

        results = []
        total = len(comments)

        print(f"Analyzing sentiment for {total} comments (batch size: {batch_size})...")

        # 배치로 나누기
        for i in range(0, total, batch_size):
            batch = comments[i:i+batch_size]
            batch_texts = [c.get(text_field, '') for c in batch]

            # 배치 분석 (한 번의 API 호출로 여러 댓글 분석)
            try:
                # 배치 텍스트 준비
                numbered_texts = '\n'.join([
                    f"{idx+1}. {text}"
                    for idx, text in enumerate(batch_texts)
                ])

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a sentiment analysis expert.
Analyze the sentiment of each numbered comment and return sentiment scores in JSON format.

Scale:
-1.0: Very negative
-0.5: Negative
 0.0: Neutral
+0.5: Positive
+1.0: Very positive

Return format: {"1": 0.5, "2": -0.3, ...}
Return ONLY the JSON, no explanation."""
                        },
                        {
                            "role": "user",
                            "content": f"Comments:\n{numbered_texts}"
                        }
                    ],
                    temperature=0.3,
                    max_tokens=200
                )

                # 결과 파싱
                result_str = response.choices[0].message.content.strip()
                sentiment_dict = json.loads(result_str)

                # 결과 매칭
                for idx, comment in enumerate(batch, 1):
                    score = sentiment_dict.get(str(idx), 0.0)
                    score = max(-1.0, min(1.0, float(score)))

                    result = comment.copy()
                    result['sentiment_score'] = round(score, 4)
                    results.append(result)

                # 진행 상황 출력
                print(f"  Progress: {len(results)}/{total} comments analyzed")

                # Rate limit 방지
                time.sleep(rate_limit_delay)

            except Exception as e:
                print(f"Error analyzing batch: {e}")
                # 에러 시 개별 분석으로 폴백
                for comment in batch:
                    sentiment_score = self.analyze_single_comment(comment.get(text_field, ''))
                    result = comment.copy()
                    result['sentiment_score'] = sentiment_score
                    results.append(result)
                    time.sleep(0.5)

        print(f"Sentiment analysis completed: {len(results)}/{total} comments")
        return results


# 테스트 코드
if __name__ == "__main__":
    analyzer = CommentSentimentAnalyzer()

    # 테스트 댓글
    test_comments = [
        "This is amazing! Best product ever!",
        "Terrible quality, waste of money",
        "It's okay, nothing special",
        "I love it so much!",
        "Very disappointed with this purchase"
    ]

    print("Testing individual sentiment analysis:")
    print("="*80)
    for comment in test_comments:
        score = analyzer.analyze_single_comment(comment)
        print(f"Comment: {comment}")
        print(f"Sentiment: {score}")
        print()
