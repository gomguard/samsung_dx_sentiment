"""
OpenAI를 사용한 YouTube 비디오 콘텐츠 분석
1. 리뷰 대상 브랜드/시리즈 추출 (brand_series_info 참조)
2. 삼성 제품에 대한 감성 점수 분석 (-5 ~ +5)
3. 댓글 요약 (영문)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from typing import Dict, List, Tuple
import json

from config.settings import OPENAI_API_KEY


class VideoContentAnalyzer:
    """YouTube 비디오 콘텐츠 분석 클래스"""

    def __init__(self, api_key=OPENAI_API_KEY, model="gpt-4o-mini"):
        """
        초기화

        Args:
            api_key: OpenAI API 키
            model: 사용할 모델
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.brand_series_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'brand_series_info'
        )
        self.brand_series_data = self._load_brand_series_info()

    def _load_brand_series_info(self) -> List[Dict]:
        """
        brand_series_info 파일 로드

        Returns:
            List[Dict]: [{'brand': str, 'series': str, 'item': str}, ...]
        """
        data = []
        try:
            with open(self.brand_series_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Skip header
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        data.append({
                            'brand': parts[0].strip(),
                            'series': parts[1].strip().strip('"'),
                            'item': parts[2].strip()
                        })
            print(f"[INFO] Loaded {len(data)} products from brand_series_info")
        except Exception as e:
            print(f"[WARNING] Failed to load brand_series_info: {e}")
        return data

    def _add_to_brand_series_info(self, brand: str, series: str, item: str):
        """
        brand_series_info 파일에 새 제품 추가

        Args:
            brand: 브랜드명
            series: 시리즈명
            item: 모델명
        """
        try:
            # 중복 체크
            for entry in self.brand_series_data:
                if (entry['brand'] == brand and
                    entry['series'] == series and
                    entry['item'] == item):
                    return  # 이미 존재

            # 파일에 추가
            with open(self.brand_series_file, 'a', encoding='utf-8') as f:
                f.write(f"{brand}\t{series}\t{item}\n")

            # 메모리에도 추가
            self.brand_series_data.append({
                'brand': brand,
                'series': series,
                'item': item
            })
            print(f"[INFO] Added new product: {brand} {series} {item}")
        except Exception as e:
            print(f"[ERROR] Failed to add to brand_series_info: {e}")

    def _match_from_reference(self, brand: str, series: str, item: str) -> Tuple[str, str, str]:
        """
        추출된 정보를 레퍼런스 파일과 매칭

        Args:
            brand: 추출된 브랜드
            series: 추출된 시리즈
            item: 추출된 아이템

        Returns:
            Tuple[str, str, str]: (매칭된 brand, series, item)
        """
        # 1. 정확한 매칭 시도 (brand + series + item)
        if brand and series and item:
            for entry in self.brand_series_data:
                if (entry['brand'].lower() == brand.lower() and
                    entry['series'].lower() == series.lower() and
                    entry['item'].lower() == item.lower()):
                    return entry['brand'], entry['series'], entry['item']

        # 2. Brand + Series 매칭
        if brand and series:
            for entry in self.brand_series_data:
                if (entry['brand'].lower() == brand.lower() and
                    entry['series'].lower() == series.lower()):
                    return entry['brand'], entry['series'], entry['item']

        # 3. Brand + Item 매칭
        if brand and item:
            for entry in self.brand_series_data:
                if (entry['brand'].lower() == brand.lower() and
                    entry['item'].lower() == item.lower()):
                    return entry['brand'], entry['series'], entry['item']

        # 매칭 실패 - 원본 반환
        return brand, series, item

    def extract_brand_and_series(self, title: str, description: str, category: str = None) -> Dict:
        """
        비디오 제목과 설명에서 리뷰 대상 브랜드, 시리즈, 아이템 추출
        brand_series_info 파일을 참조하여 표준화된 정보 반환

        Args:
            title: 비디오 제목
            description: 비디오 설명
            category: 제품 카테고리 (TV, HHP 등)

        Returns:
            Dict: {
                'reviewed_brand': 브랜드명 (Samsung, LG, Sony 등),
                'reviewed_series': 시리즈명 (QN90F, C4, Galaxy S25 등),
                'reviewed_item': 아이템명 (QN85QN90FAFXZA, OLED83C4PUA 등)
            }
        """
        # Category에 따라 다른 프롬프트 사용
        if category == "TV":
            product_type = "TV product"
            brand_examples = "Samsung, LG, Sony, TCL-Digital, Hisense"
            series_examples = '"QN90F", "C4", "Q80D", "U8N"'
            series_instruction = "Use ONLY the model code WITHOUT technology prefix (QLED/OLED/Neo QLED)"
            item_examples = '"QN85QN90FAFXZA", "OLED83C4PUA", "QN65Q80DAFXZA"'
        elif category == "HHP":
            product_type = "smartphone, tablet, or mobile device"
            brand_examples = "Samsung, Apple, Google, Motorola, Lenovo"
            series_examples = '"Galaxy S25", "iPhone 17", "Pixel 10", "Galaxy Tab S11"'
            series_instruction = "Use the full model name including series (e.g., 'Galaxy S25 FE', 'iPhone 17 Pro', 'Pixel 10 Pro')"
            item_examples = '"SM-S931U", "A3294", "GF5KQ"'
        else:
            product_type = "product"
            brand_examples = "Samsung, LG, Sony, Apple, Google, etc."
            series_examples = '"QN90F", "Galaxy S25", "iPhone 17", "Pixel 10"'
            series_instruction = "Use the specific model/series name"
            item_examples = '"QN85QN90FAFXZA", "SM-S931U", "A3294"'

        prompt = f"""Analyze this YouTube video title and description to extract information about the {product_type} being reviewed.

Title: {title}

Description: {description[:500]}

Extract the following information:
1. **reviewed_brand**: The main brand being reviewed (e.g., {brand_examples}).
   - Use exact brand names
   - If multiple brands are compared, list the primary brand being reviewed.

2. **reviewed_series**: The specific series/model being reviewed (e.g., {series_examples}).
   - {series_instruction}

3. **reviewed_item**: The exact full model number if mentioned (e.g., {item_examples}).
   - This is usually a longer alphanumeric code that includes size/storage/region information
   - If not explicitly mentioned, use null

Return ONLY a JSON object with these three keys. If information is not found, use null.

Example output 1:
{{
    "reviewed_brand": "Samsung",
    "reviewed_series": "QN90F",
    "reviewed_item": "QN85QN90FAFXZA"
}}

Example output 2 (no full item number):
{{
    "reviewed_brand": "LG",
    "reviewed_series": "C4",
    "reviewed_item": null
}}
"""

        # Category에 따른 시스템 메시지
        if category == "TV":
            system_msg = "You are an expert at analyzing TV review videos and extracting product information."
        elif category == "HHP":
            system_msg = "You are an expert at analyzing smartphone and mobile device review videos and extracting product information."
        else:
            system_msg = "You are an expert at analyzing product review videos and extracting product information."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # OpenAI로부터 추출된 정보
            extracted_brand = result.get('reviewed_brand')
            extracted_series = result.get('reviewed_series')
            extracted_item = result.get('reviewed_item')

            # brand_series_info 파일과 매칭
            matched_brand, matched_series, matched_item = self._match_from_reference(
                extracted_brand, extracted_series, extracted_item
            )

            # 매칭되지 않았고 모든 정보가 있으면 새로 추가
            if (extracted_brand and extracted_series and extracted_item and
                not any(e['brand'] == matched_brand and
                       e['series'] == matched_series and
                       e['item'] == matched_item
                       for e in self.brand_series_data)):
                self._add_to_brand_series_info(
                    matched_brand or extracted_brand,
                    matched_series or extracted_series,
                    matched_item or extracted_item
                )

            return {
                'reviewed_brand': matched_brand,
                'reviewed_series': matched_series,
                'reviewed_item': matched_item
            }

        except Exception as e:
            print(f"[ERROR] 브랜드/시리즈 추출 실패: {e}")
            return {
                'reviewed_brand': None,
                'reviewed_series': None,
                'reviewed_item': None
            }

    def analyze_product_sentiment(self, title: str, description: str,
                                   reviewed_brand: str, reviewed_series: str) -> float:
        """
        비디오 제목과 설명에서 리뷰 대상 제품에 대한 감성 점수 분석

        Args:
            title: 비디오 제목
            description: 비디오 설명
            reviewed_brand: 리뷰 대상 브랜드 (Samsung, LG 등)
            reviewed_series: 리뷰 대상 시리즈 (QN90F, C4 등)

        Returns:
            float: 감성 점수 (-5.0 ~ +5.0)
                  -5: 매우 부정적
                   0: 중립적
                  +5: 매우 긍정적
        """
        # 브랜드와 시리즈 정보가 없으면 0 반환
        if not reviewed_brand:
            return 0.0

        # 제품명 구성
        product_name = reviewed_brand
        if reviewed_series:
            product_name = f"{reviewed_brand} {reviewed_series}"

        prompt = f"""Analyze the sentiment towards the reviewed product in this YouTube video title and description.

Title: {title}

Description: {description[:500]}

Reviewed Product: {product_name}

Rate the sentiment towards THIS SPECIFIC PRODUCT ({product_name}) on a scale from -5 to +5:
- **-5**: Very negative (Product is heavily criticized, major flaws highlighted, strongly NOT recommended)
- **-3**: Negative (More cons than pros, disappointing performance)
- **0**: Neutral (Balanced review, or product not significantly discussed)
- **+3**: Positive (More pros than cons, recommended with minor caveats)
- **+5**: Very positive (Product is highly praised, excellent performance, strongly recommended)

Consider:
1. Direct mentions of the product
2. Comparisons with other products (is this product portrayed favorably?)
3. Overall tone when discussing this product
4. Specific praise or criticism
5. Value proposition and recommendation

If the product is not mentioned or discussed, return 0.

Return ONLY a JSON object with a single key "sentiment_score" containing a number between -5 and +5.

Example output:
{{
    "sentiment_score": 3.5
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing sentiment towards specific TV products in review videos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            score = result.get('sentiment_score', 0)

            # 범위 제한
            return max(-5.0, min(5.0, float(score)))

        except Exception as e:
            print(f"[ERROR] 감성 점수 분석 실패: {e}")
            return 0.0

    def summarize_comments_english(self, comments: List[Dict], max_comments=100) -> str:
        """
        댓글을 영문으로 요약

        Args:
            comments: 댓글 리스트 (Dict 형태)
            max_comments: 최대 댓글 수

        Returns:
            str: 영문 요약
        """
        if not comments:
            return "No comments available"

        # 좋아요 순으로 정렬
        sorted_comments = sorted(comments, key=lambda x: x.get('like_count', 0), reverse=True)
        top_comments = sorted_comments[:max_comments]

        # 댓글 텍스트 추출
        comment_texts = [c.get('comment_text_display', '') for c in top_comments if c.get('comment_text_display')]

        if not comment_texts:
            return "No comments available"

        # 모든 댓글을 하나의 문자열로 결합 (줄바꿈 구분)
        comments_text = '\n'.join(comment_texts[:50])  # 최대 50개만 사용

        prompt = f"""Summarize the following YouTube comments about a TV product review in 2-3 sentences in English.

Focus on:
1. Main opinions and feedback
2. Common themes or concerns
3. Overall sentiment

Comments:
{comments_text}

Provide a concise summary in English (2-3 sentences).
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing YouTube comments concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )

            summary = response.choices[0].message.content.strip()
            return summary

        except Exception as e:
            print(f"[ERROR] 댓글 요약 실패: {e}")
            return "Failed to generate summary"


# 테스트용
if __name__ == "__main__":
    analyzer = VideoContentAnalyzer()

    # 테스트 1: 브랜드/시리즈 추출
    test_title = "Samsung QN90D vs LG C4 OLED - Which TV is Better?"
    test_desc = "In this video, we compare the Samsung QN90D Neo QLED with the LG C4 OLED..."

    result = analyzer.extract_brand_and_series(test_title, test_desc)
    print("브랜드/시리즈 추출:", result)

    # 테스트 2: 제품 감성 점수
    if result['reviewed_brand']:
        score = analyzer.analyze_product_sentiment(
            test_title, test_desc,
            result['reviewed_brand'],
            result['reviewed_series']
        )
        print(f"제품 감성 점수: {score}")
