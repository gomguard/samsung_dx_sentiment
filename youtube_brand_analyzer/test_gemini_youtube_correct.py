"""
Google Gemini API로 YouTube URL 직접 처리 테스트 (올바른 모델 이름)
"""
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyDNMhNDsZK1D-1Xu7dNk_0Gr6svrw3MNnE"
genai.configure(api_key=GEMINI_API_KEY)

# 테스트할 YouTube URL
youtube_url = "https://www.youtube.com/watch?v=lL78TL3NaDU"

print("="*80)
print("Google Gemini API YouTube URL Test")
print("="*80)
print(f"Testing with video: {youtube_url}")
print()

# 테스트 1: Gemini 2.5 Flash
print("[Test 1] Gemini 2.5 Flash with YouTube URL")
print("-"*80)
try:
    model = genai.GenerativeModel('gemini-2.5-flash')

    response = model.generate_content([
        f"Please summarize this YouTube video in 3-4 sentences: {youtube_url}"
    ])

    print("SUCCESS!")
    print(f"Response: {response.text}")
    print()

except Exception as e:
    print(f"FAILED: {e}")
    print()

# 테스트 2: Gemini 2.5 Pro
print("[Test 2] Gemini 2.5 Pro with YouTube URL")
print("-"*80)
try:
    model = genai.GenerativeModel('gemini-2.5-pro')

    response = model.generate_content([
        f"Analyze this YouTube video and provide a summary: {youtube_url}"
    ])

    print("SUCCESS!")
    print(f"Response: {response.text}")
    print()

except Exception as e:
    print(f"FAILED: {e}")
    print()

# 테스트 3: Detailed JSON analysis
print("[Test 3] Detailed video analysis (JSON format)")
print("-"*80)
try:
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    Analyze this YouTube video: {youtube_url}

    Please provide a detailed analysis in JSON format:
    {{
        "title": "video title",
        "summary": "3-4 sentence summary",
        "key_topics": ["topic1", "topic2", "topic3"],
        "product_mentions": {{
            "samsung": ["Samsung products mentioned"],
            "competitors": ["Competitor products"]
        }},
        "sentiment": "positive/negative/neutral",
        "target_audience": "who is this video for"
    }}
    """

    response = model.generate_content(prompt)

    print("SUCCESS!")
    print(f"Response: {response.text}")
    print()

except Exception as e:
    print(f"FAILED: {e}")
    print()

print("="*80)
print("Test completed")
print("="*80)
