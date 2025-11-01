"""
OpenAI API로 비디오 파일 직접 처리 테스트

GPT-4o는 비디오 파일을 입력으로 받을 수 있습니다.
하지만 몇 가지 제한사항이 있습니다:
1. 비디오를 프레임으로 샘플링
2. 최대 길이 제한
3. 파일 크기 제한
"""
from openai import OpenAI
from config.settings import OPENAI_API_KEY
import base64
import os

client = OpenAI(api_key=OPENAI_API_KEY)

print("="*80)
print("OpenAI API Video File Test")
print("="*80)
print()

print("OpenAI GPT-4o는 비디오 입력을 지원합니다!")
print()
print("방법:")
print("1. 비디오 파일을 base64로 인코딩")
print("2. GPT-4o에 전달")
print("3. 비디오 내용 분석 (프레임 샘플링 + 오디오)")
print()

print("하지만 YouTube 비디오의 경우:")
print("1. 비디오 파일을 먼저 다운로드해야 함")
print("2. 파일 크기/길이 제한 있음")
print("3. 다운로드 + 업로드 시간 소요")
print("4. 비용이 비쌈 (비디오는 이미지보다 훨씬 많은 토큰 사용)")
print()

print("="*80)
print("실제 구현 예시")
print("="*80)
print()

# 비디오 파일이 있다고 가정한 코드 예시
example_code = '''
from openai import OpenAI
import base64

client = OpenAI(api_key="your-api-key")

# 1. 비디오 파일 읽기
with open("video.mp4", "rb") as video_file:
    video_data = base64.b64encode(video_file.read()).decode('utf-8')

# 2. GPT-4o Vision에 전달
response = client.chat.completions.create(
    model="gpt-4o",  # 또는 gpt-4o-mini
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Summarize this video"
                },
                {
                    "type": "video",  # 비디오 타입
                    "video": video_data
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
'''

print("코드 예시:")
print(example_code)
print()

print("="*80)
print("YouTube 비디오 요약을 위한 비교")
print("="*80)
print()

comparison = """
방법 1: 자막 추출 (현재 사용 중)
✅ 장점:
  - 빠름 (자막 API는 즉시 응답)
  - 저렴 (텍스트 토큰만 사용)
  - 정확 (실제 음성 내용)
  - 파일 다운로드 불필요
❌ 단점:
  - 자막이 없으면 사용 불가
  - 시각적 내용은 분석 못함

방법 2: 비디오 파일 다운로드 + OpenAI
✅ 장점:
  - 자막 없어도 가능
  - 시각적 내용도 분석 가능
  - 오디오도 분석 가능
❌ 단점:
  - 느림 (다운로드 + 업로드 시간)
  - 비쌈 (비디오 처리 비용 높음)
  - 파일 크기 제한
  - 스토리지 필요

방법 3: 제목 + 설명 요약 (Fallback)
✅ 장점:
  - 항상 가능
  - 빠르고 저렴
❌ 단점:
  - 정확도 낮음
  - 추측 기반
"""

print(comparison)
print()

print("="*80)
print("권장사항")
print("="*80)
print()
print("YouTube 비디오 대량 수집의 경우:")
print("✅ 방법 1 (자막) + 방법 3 (제목+설명) 조합 = 최적")
print("  - 빠르고 저렴")
print("  - 대부분의 비디오 커버 가능")
print("  - 현재 우리가 사용하는 방식!")
print()
print("비디오 파일 방식은:")
print("❌ 소수의 중요한 비디오만 분석할 때 적합")
print("❌ 대량 처리에는 부적합 (느리고 비쌈)")
