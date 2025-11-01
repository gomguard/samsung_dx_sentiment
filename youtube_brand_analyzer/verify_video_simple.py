"""
실제 YouTube 비디오 제목 확인 (간단 버전)
"""
from googleapiclient.discovery import build
from config.settings import YOUTUBE_API_KEY

# YouTube API 클라이언트
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# 테스트한 비디오들
videos = {
    "lL78TL3NaDU": "첫 번째 테스트 비디오",
    "k-qj7JinXSw": "두 번째 테스트 비디오"
}

print("="*80)
print("실제 YouTube 비디오 내용 확인")
print("="*80)
print()

for video_id, desc in videos.items():
    print(f"{desc}")
    print(f"Video ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    print("-"*80)

    try:
        # YouTube API로 비디오 정보 가져오기
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()

        if response['items']:
            video = response['items'][0]['snippet']
            print(f"실제 제목: {video['title']}")
            print(f"채널: {video['channelTitle']}")
            print(f"설명 (앞부분):")
            description = video['description']
            print(description[:300] if len(description) > 300 else description)
            print()

    except Exception as e:
        print(f"Error: {e}")

    print()

print("="*80)
print("Gemini 답변 비교")
print("="*80)
print()

print("[Video 1: lL78TL3NaDU]")
print("Gemini 답변: 'investment banking guide for students'")
print()

print("[Video 2: k-qj7JinXSw]")
print("Gemini 답변들:")
print("  1. Graf von Faber-Castell Perfect Pencil (고급 연필)")
print("  2. Lex Fridman Podcast - AI Laggard")
print("  3. Linus Tech Tips - Fake Tech")
print("  4. What I Think About This YouTube Channel")
