"""
Google Gemini API로 YouTube URL 직접 처리 테스트 #2
다른 비디오로 재테스트
"""
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyDNMhNDsZK1D-1Xu7dNk_0Gr6svrw3MNnE"
genai.configure(api_key=GEMINI_API_KEY)

# 테스트할 YouTube URL
youtube_url = "https://www.youtube.com/watch?v=k-qj7JinXSw"

print("="*80)
print("Google Gemini API YouTube URL Test #2")
print("="*80)
print(f"Testing with video: {youtube_url}")
print()

# 테스트 1: Gemini 2.5 Flash - 짧은 요약
print("[Test 1] Gemini 2.5 Flash - Short Summary")
print("-"*80)
try:
    model = genai.GenerativeModel('gemini-2.5-flash')

    response = model.generate_content([
        f"Summarize this YouTube video in 2-3 sentences: {youtube_url}"
    ])

    print("SUCCESS!")
    print(f"Response:")
    print(response.text)
    print()

except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    print()

# 테스트 2: Gemini 2.5 Flash - 상세 요약
print("[Test 2] Gemini 2.5 Flash - Detailed Summary")
print("-"*80)
try:
    model = genai.GenerativeModel('gemini-2.5-flash')

    response = model.generate_content([
        f"What is this YouTube video about? Please provide details: {youtube_url}"
    ])

    print("SUCCESS!")
    print(f"Response:")
    print(response.text)
    print()

except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    print()

# 테스트 3: Gemini 2.5 Pro
print("[Test 3] Gemini 2.5 Pro - Analysis")
print("-"*80)
try:
    model = genai.GenerativeModel('gemini-2.5-pro')

    response = model.generate_content([
        f"Please analyze this YouTube video and tell me what products or topics are discussed: {youtube_url}"
    ])

    print("SUCCESS!")
    print(f"Response:")
    print(response.text[:500])
    print()

except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    print()

# 테스트 4: 비디오 제목 확인 요청
print("[Test 4] Ask for video title")
print("-"*80)
try:
    model = genai.GenerativeModel('gemini-2.5-flash')

    response = model.generate_content([
        f"What is the title of this YouTube video? {youtube_url}"
    ])

    print("SUCCESS!")
    print(f"Response:")
    print(response.text)
    print()

except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    print()

print("="*80)
print("Test completed")
print("="*80)
print()
print("분석:")
print("Gemini가 실제로 비디오 내용을 분석할 수 있는지,")
print("아니면 URL 기반으로 추측하거나 학습 데이터를 사용하는지 확인")
