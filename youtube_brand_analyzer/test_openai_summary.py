"""
OpenAI API 테스트 스크립트
Samsung 4K TV 샘플 댓글 50개를 생성하고 OpenAI로 요약합니다.
"""

import json
from datetime import datetime
from openai import OpenAI
from config.settings import OPENAI_API_KEY


# Samsung 4K TV에 대한 샘플 댓글 50개
SAMPLE_COMMENTS = [
    # 긍정적인 댓글들 (25개)
    "This Samsung 4K TV is absolutely stunning! The picture quality is amazing.",
    "Best TV I've ever owned. The colors are so vivid and the blacks are deep.",
    "Worth every penny. The smart features work flawlessly.",
    "The 4K upscaling on this Samsung is incredible. Even 1080p content looks great.",
    "I compared this with LG and Sony. Samsung wins hands down for the price.",
    "Game mode is fantastic. No lag at all, perfect for PS5 gaming.",
    "The QLED technology really makes a difference. HDR content is breathtaking.",
    "Setup was super easy. Remote is intuitive and well-designed.",
    "Sound quality is surprisingly good for a TV this thin.",
    "Love the ambient mode feature. Makes the TV look like art when not watching.",
    "Customer service was excellent when I had a question about settings.",
    "This TV has completely transformed my movie watching experience.",
    "The anti-reflection coating works great. Can watch during the day without glare.",
    "Smart hub is fast and responsive. No lag when switching apps.",
    "Build quality feels premium. Very solid construction.",
    "The 120Hz refresh rate is perfect for sports. Everything is so smooth.",
    "Voice control with Bixby works well. Very convenient.",
    "Energy efficient too. Lower power consumption than my old TV.",
    "Viewing angles are excellent. Looks good from anywhere in the room.",
    "The One Connect box is genius. Keeps all cables organized and hidden.",
    "Netflix and YouTube apps work perfectly. 4K streaming is flawless.",
    "I've had this for 6 months and still amazed every time I turn it on.",
    "Great value for money compared to other premium brands.",
    "The quantum processor really does make content look better.",
    "Universal guide feature makes finding content across apps so easy.",

    # 중립적인 댓글들 (15개)
    "Decent TV for the price. Does what it's supposed to do.",
    "It's good but not mind-blowing. Expected a bit more for the price.",
    "Picture quality is nice but the sound could be better. Consider a soundbar.",
    "Smart features are okay. I mainly use my Apple TV anyway.",
    "The menu system takes some getting used to. Not the most intuitive.",
    "It's pretty thin but not the thinnest I've seen.",
    "Remote could be better. Too many buttons I never use.",
    "Streaming works fine but the built-in apps aren't as good as Roku.",
    "Good TV but I wish it came with a better stand. Had to buy a wall mount.",
    "The default settings weren't great. Had to spend time calibrating.",
    "It's a solid TV but nothing revolutionary. Standard Samsung quality.",
    "HDR is nice but you really need 4K content to see the difference.",
    "Voice control is hit or miss. Sometimes it doesn't understand me.",
    "The ads on the home screen are annoying. Wish I could disable them.",
    "It's fine for the living room but maybe overkill for a bedroom.",

    # 부정적인 댓글들 (10개)
    "Disappointed with the blooming in dark scenes. Not true black like OLED.",
    "Had issues with screen uniformity. One corner is slightly darker.",
    "The TV died after just 8 months. Very poor reliability.",
    "Too expensive for what you get. Should have gone with TCL.",
    "The smart features are slow and buggy. Constantly freezing.",
    "Motion blur is noticeable in fast action scenes. 120Hz doesn't help much.",
    "Build quality feels cheap despite the premium price tag.",
    "Customer support was terrible when I tried to get help.",
    "The viewing angle is poor. Colors wash out if you're not dead center.",
    "Lots of input lag even in game mode. Not recommended for serious gaming.",
]


def summarize_comments_with_openai(comments, model="gpt-4o-mini"):
    """
    OpenAI API를 사용하여 댓글 요약

    Args:
        comments (list): 댓글 리스트
        model (str): 사용할 OpenAI 모델

    Returns:
        dict: 요약 결과
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    # 댓글을 하나의 텍스트로 결합
    combined_text = "\n".join([f"{i+1}. {comment}" for i, comment in enumerate(comments)])

    # 프롬프트 구성
    prompt = f"""다음은 Samsung 4K TV에 대한 YouTube 댓글 {len(comments)}개입니다.
이 댓글들을 분석하여 다음 정보를 JSON 형식으로 제공해주세요:

댓글 내용:
{combined_text}

다음 형식으로 응답해주세요:
{{
    "summary": "댓글의 전반적인 내용을 3-4문장으로 요약",
    "key_themes": ["주요 주제1", "주요 주제2", "주요 주제3", "주요 주제4"],
    "sentiment_distribution": {{
        "positive": "긍정적 댓글 비율 (예: 50%)",
        "neutral": "중립적 댓글 비율 (예: 30%)",
        "negative": "부정적 댓글 비율 (예: 20%)"
    }},
    "positive_points": ["자주 언급되는 긍정적 의견1", "긍정적 의견2", "긍정적 의견3"],
    "negative_points": ["자주 언급되는 부정적 의견1", "부정적 의견2"],
    "common_topics": ["자주 언급되는 토픽1", "토픽2", "토픽3"],
    "purchase_recommendation": "종합적으로 구매를 추천하는지 여부와 이유 (1-2문장)"
}}

응답은 반드시 유효한 JSON 형식이어야 합니다."""

    print("OpenAI API 호출 중...")
    print(f"모델: {model}")
    print(f"분석할 댓글 수: {len(comments)}")
    print("-" * 80)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 제품 리뷰를 분석하는 전문가입니다. 댓글의 주요 내용, 감성, 테마를 파악하고 구조화된 JSON 형식으로 요약합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )

        # 응답 파싱
        result_text = response.choices[0].message.content.strip()

        # JSON 파싱
        try:
            # JSON 코드 블록 제거 (```json ... ``` 형식인 경우)
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            result = json.loads(result_text)

            # 메타데이터 추가
            result['metadata'] = {
                'total_comments': len(comments),
                'model_used': model,
                'analyzed_at': datetime.now().isoformat(),
                'tokens_used': {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                }
            }

            return result

        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"응답 내용:\n{result_text}")
            return {
                'error': 'JSON parsing failed',
                'raw_response': result_text
            }

    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return {
            'error': str(e)
        }


def main():
    """메인 실행 함수"""

    print("=" * 80)
    print("OpenAI API 테스트: Samsung 4K TV 댓글 요약")
    print("=" * 80)
    print()

    # 1. 샘플 댓글 정보 출력
    print(f"[INFO] Sample comments: {len(SAMPLE_COMMENTS)} comments")
    print(f"[INFO] Preview (first 3):")
    for i, comment in enumerate(SAMPLE_COMMENTS[:3], 1):
        print(f"   {i}. {comment}")
    print(f"   ...")
    print()

    # 2. OpenAI로 요약
    summary = summarize_comments_with_openai(SAMPLE_COMMENTS)

    # 3. 결과 출력
    print()
    print("=" * 80)
    print("SUMMARY RESULT")
    print("=" * 80)
    print()

    if 'error' in summary:
        print(f"[ERROR] {summary['error']}")
        if 'raw_response' in summary:
            print(f"\nRaw response:\n{summary['raw_response']}")
    else:
        print("[SUMMARY] Overall:")
        print(f"   {summary.get('summary', 'N/A')}")
        print()

        print("[KEY THEMES]")
        for theme in summary.get('key_themes', []):
            print(f"   - {theme}")
        print()

        print("[SENTIMENT DISTRIBUTION]")
        sentiment = summary.get('sentiment_distribution', {})
        print(f"   Positive: {sentiment.get('positive', 'N/A')}")
        print(f"   Neutral: {sentiment.get('neutral', 'N/A')}")
        print(f"   Negative: {sentiment.get('negative', 'N/A')}")
        print()

        print("[POSITIVE POINTS]")
        for point in summary.get('positive_points', []):
            print(f"   + {point}")
        print()

        print("[NEGATIVE POINTS]")
        for point in summary.get('negative_points', []):
            print(f"   - {point}")
        print()

        print("[PURCHASE RECOMMENDATION]")
        print(f"   {summary.get('purchase_recommendation', 'N/A')}")
        print()

        if 'metadata' in summary:
            meta = summary['metadata']
            print("[METADATA]")
            print(f"   Model: {meta.get('model_used')}")
            print(f"   Tokens used: {meta.get('tokens_used', {}).get('total', 'N/A')}")
            print(f"   Analyzed at: {meta.get('analyzed_at')}")
            print()

    # 4. 결과를 파일로 저장
    output = {
        'comments': SAMPLE_COMMENTS,
        'summary': summary
    }

    output_file = 'test_openai_summary_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print(f"[SUCCESS] Result saved: {output_file}")
    print("=" * 80)
    print()
    print("파일 내용:")
    print("  - comments: 샘플 댓글 50개")
    print("  - summary: OpenAI 요약 결과")
    print()


if __name__ == "__main__":
    main()
