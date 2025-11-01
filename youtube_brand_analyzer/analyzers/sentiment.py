import pandas as pd
import re
from textblob import TextBlob
from datetime import datetime
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SENTIMENT_THRESHOLD_POSITIVE, SENTIMENT_THRESHOLD_NEGATIVE

class SentimentAnalyzer:
    def __init__(self):
        """감정 분석기 초기화"""
        self.positive_keywords = [
            'love', 'great', 'amazing', 'awesome', 'excellent', 'perfect', 'best', 'good',
            'fantastic', 'wonderful', 'brilliant', 'outstanding', 'impressive', 'beautiful',
            'recommend', 'happy', 'satisfied', 'pleased', 'quality', 'value'
        ]
        
        self.negative_keywords = [
            'hate', 'terrible', 'awful', 'horrible', 'worst', 'bad', 'disappointing',
            'useless', 'broken', 'problem', 'issue', 'fail', 'poor', 'cheap',
            'waste', 'regret', 'angry', 'frustrated', 'disappointed', 'overpriced'
        ]
        
        self.brand_competitors = {
            'samsung': ['apple', 'iphone', 'lg', 'sony', 'xiaomi', 'huawei'],
            'apple': ['samsung', 'galaxy', 'lg', 'sony', 'google', 'pixel'],
            'lg': ['samsung', 'apple', 'sony', 'tcl', 'hisense'],
            'sony': ['samsung', 'lg', 'panasonic', 'apple', 'bose']
        }
    
    def analyze_comment_sentiment(self, comments_data):
        """댓글 감정 분석"""
        if not comments_data:
            return []
        
        sentiment_results = []
        
        for comment in comments_data:
            text = comment.get('comment_text', '')
            if not text:
                continue
                
            # 텍스트 전처리
            cleaned_text = self._clean_text(text)
            
            # TextBlob 감정 분석
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity  # -1(부정) ~ 1(긍정)
            subjectivity = blob.sentiment.subjectivity  # 0(객관) ~ 1(주관)
            
            # 키워드 기반 감정 점수 조정
            keyword_sentiment = self._analyze_keywords(cleaned_text)
            
            # 최종 감정 점수 계산 (TextBlob + 키워드)
            final_sentiment = (polarity + keyword_sentiment) / 2
            
            # 감정 카테고리 결정
            if final_sentiment > SENTIMENT_THRESHOLD_POSITIVE:
                sentiment_category = 'positive'
            elif final_sentiment < SENTIMENT_THRESHOLD_NEGATIVE:
                sentiment_category = 'negative'
            else:
                sentiment_category = 'neutral'
            
            # 브랜드 언급 추출
            brand_mentions = self._extract_brand_mentions(cleaned_text)
            
            # 경쟁사 언급 확인
            competitor_mentions = self._extract_competitor_mentions(cleaned_text)
            
            sentiment_results.append({
                'video_id': comment.get('video_id'),
                'comment_id': comment.get('comment_id'),
                'comment_text': text[:200],  # 처음 200자만 저장
                'sentiment_score': round(final_sentiment, 3),
                'sentiment_category': sentiment_category,
                'subjectivity_score': round(subjectivity, 3),
                'brand_mentions': ', '.join(brand_mentions),
                'competitor_mentions': ', '.join(competitor_mentions),
                'comment_length': len(text),
                'like_count': comment.get('like_count', 0),
                'published_at': comment.get('published_at'),
                'analyzed_at': datetime.now().isoformat()
            })
        
        print(f"감정 분석 완료: {len(sentiment_results)}개 댓글")
        return sentiment_results
    
    def analyze_video_sentiment_summary(self, sentiment_data):
        """비디오별 감정 요약 분석"""
        if not sentiment_data:
            return []
        
        df = pd.DataFrame(sentiment_data)
        
        summary_results = []
        
        # 비디오별 그룹화
        for video_id, group in df.groupby('video_id'):
            total_comments = len(group)
            
            # 감정 분포 계산
            positive_count = len(group[group['sentiment_category'] == 'positive'])
            negative_count = len(group[group['sentiment_category'] == 'negative'])
            neutral_count = len(group[group['sentiment_category'] == 'neutral'])
            
            # 평균 감정 점수
            avg_sentiment = group['sentiment_score'].mean()
            
            # 좋아요가 많은 댓글의 감정
            top_liked_comments = group.nlargest(5, 'like_count')
            top_sentiment = top_liked_comments['sentiment_score'].mean() if len(top_liked_comments) > 0 else 0
            
            # 브랜드 언급 통계
            brand_mention_count = len(group[group['brand_mentions'] != ''])
            competitor_mention_count = len(group[group['competitor_mentions'] != ''])
            
            summary_results.append({
                'video_id': video_id,
                'total_comments_analyzed': total_comments,
                'positive_comments': positive_count,
                'negative_comments': negative_count,
                'neutral_comments': neutral_count,
                'positive_ratio': round(positive_count / total_comments, 3),
                'negative_ratio': round(negative_count / total_comments, 3),
                'neutral_ratio': round(neutral_count / total_comments, 3),
                'avg_sentiment_score': round(avg_sentiment, 3),
                'top_liked_sentiment': round(top_sentiment, 3),
                'brand_mention_count': brand_mention_count,
                'competitor_mention_count': competitor_mention_count,
                'sentiment_volatility': round(group['sentiment_score'].std(), 3),
                'analyzed_at': datetime.now().isoformat()
            })
        
        print(f"비디오 감정 요약 완료: {len(summary_results)}개 비디오")
        return summary_results
    
    def _clean_text(self, text):
        """텍스트 전처리"""
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # URL 제거
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 이메일 제거
        text = re.sub(r'\S+@\S+', '', text)
        
        # 특수문자 정리 (기본 문장부호 유지)
        text = re.sub(r'[^\w\s\.\!\?\,\-\:]', ' ', text)
        
        # 연속 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _analyze_keywords(self, text):
        """키워드 기반 감정 분석"""
        text_lower = text.lower()
        
        positive_score = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_score = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        
        # 정규화 (-1 ~ 1 범위)
        total_keywords = positive_score + negative_score
        if total_keywords == 0:
            return 0
        
        return (positive_score - negative_score) / max(total_keywords, 1)
    
    def _extract_brand_mentions(self, text):
        """브랜드 언급 추출"""
        text_lower = text.lower()
        mentions = []
        
        # 주요 브랜드 키워드
        brand_keywords = [
            'samsung', 'galaxy', 'apple', 'iphone', 'ipad', 'lg', 'sony', 
            'xiaomi', 'huawei', 'google', 'pixel', 'oneplus', 'oppo', 'vivo'
        ]
        
        for brand in brand_keywords:
            if brand in text_lower:
                mentions.append(brand)
        
        return list(set(mentions))  # 중복 제거
    
    def _extract_competitor_mentions(self, text):
        """경쟁사 언급 추출"""
        text_lower = text.lower()
        mentions = []
        
        # 비교 표현과 함께 언급된 브랜드들 찾기
        comparison_patterns = [
            r'better than (\w+)',
            r'worse than (\w+)',
            r'compared to (\w+)',
            r'vs (\w+)',
            r'versus (\w+)'
        ]
        
        for pattern in comparison_patterns:
            matches = re.findall(pattern, text_lower)
            mentions.extend(matches)
        
        return list(set(mentions))  # 중복 제거
    
    def analyze_single_comment(self, comment_text):
        """단일 댓글 감정 분석 (새로운 댓글 구조용)"""
        if not comment_text:
            return {
                'sentiment_score': 0.0,
                'sentiment_category': 'neutral',
                'subjectivity_score': 0.0,
                'brand_mentions': '',
                'competitor_mentions': ''
            }
        
        # 텍스트 전처리
        cleaned_text = self._clean_text(comment_text)
        
        # TextBlob 감정 분석
        blob = TextBlob(cleaned_text)
        polarity = blob.sentiment.polarity  # -1(부정) ~ 1(긍정)
        subjectivity = blob.sentiment.subjectivity  # 0(객관) ~ 1(주관)
        
        # 키워드 기반 감정 점수 조정
        keyword_sentiment = self._analyze_keywords(cleaned_text)
        
        # 최종 감정 점수 계산 (TextBlob + 키워드)
        final_sentiment = (polarity + keyword_sentiment) / 2
        
        # 감정 카테고리 결정
        if final_sentiment > SENTIMENT_THRESHOLD_POSITIVE:
            sentiment_category = 'positive'
        elif final_sentiment < SENTIMENT_THRESHOLD_NEGATIVE:
            sentiment_category = 'negative'
        else:
            sentiment_category = 'neutral'
        
        # 브랜드 언급 추출
        brand_mentions = self._extract_brand_mentions(cleaned_text)
        
        # 경쟁사 언급 확인
        competitor_mentions = self._extract_competitor_mentions(cleaned_text)
        
        return {
            'sentiment_score': round(final_sentiment, 3),
            'sentiment_category': sentiment_category,
            'subjectivity_score': round(subjectivity, 3),
            'brand_mentions': ', '.join(brand_mentions),
            'competitor_mentions': ', '.join(competitor_mentions)
        }