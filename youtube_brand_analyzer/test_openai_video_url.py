"""
OpenAI API로 YouTube URL 직접 처리 테스트

이 테스트는 OpenAI API가 YouTube URL을 직접 받아서
비디오를 분석할 수 있는지 확인합니다.
"""
from openai import OpenAI
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# 테스트할 YouTube URL
youtube_url = "https://www.youtube.com/watch?v=lL78TL3NaDU"

print("="*80)
print("OpenAI API YouTube URL Test")
print("="*80)
print(f"Testing with video: {youtube_url}")
print()

# 테스트 1: GPT-4o (텍스트 모델)에 URL 전달
print("[Test 1] GPT-4o (text model) with YouTube URL")
print("-"*80)
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Please summarize this YouTube video: {youtube_url}"
            }
        ],
        max_tokens=500
    )

    result = response.choices[0].message.content
    print("SUCCESS!")
    print(f"Response: {result}")

except Exception as e:
    print(f"FAILED: {e}")

print()

# 테스트 2: GPT-4o (vision 지원)에 URL을 이미지처럼 전달
print("[Test 2] GPT-4o with URL as image_url")
print("-"*80)
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Summarize this YouTube video"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": youtube_url
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )

    result = response.choices[0].message.content
    print("SUCCESS!")
    print(f"Response: {result}")

except Exception as e:
    print(f"FAILED: {e}")

print()

# 테스트 3: 비디오 embed URL로 시도
print("[Test 3] Trying with embed URL")
print("-"*80)
embed_url = "https://www.youtube.com/embed/lL78TL3NaDU"
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Summarize this video"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": embed_url
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )

    result = response.choices[0].message.content
    print("SUCCESS!")
    print(f"Response: {result}")

except Exception as e:
    print(f"FAILED: {e}")

print()
print("="*80)
print("Test completed")
print("="*80)
print()
print("결론:")
print("OpenAI API는 YouTube URL을 직접 받아서 비디오를 분석할 수 없습니다.")
print("텍스트로 URL을 전달하면 OpenAI는 URL에 대해 '이야기'할 수는 있지만,")
print("실제로 비디오 내용을 보거나 분석할 수는 없습니다.")
print()
print("해결 방법: YouTube Transcript API로 자막 추출 → OpenAI로 텍스트 요약")
