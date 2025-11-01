"""
실제 YouTube 비디오 내용 확인
Gemini의 답변이 맞는지 확인
"""
from collectors.youtube_api import YouTubeAnalyzer

analyzer = YouTubeAnalyzer()

# 테스트한 비디오들
video_ids = [
    "lL78TL3NaDU",  # 첫 번째 테스트
    "k-qj7JinXSw"   # 두 번째 테스트
]

print("="*80)
print("실제 YouTube 비디오 내용 확인")
print("="*80)
print()

for video_id in video_ids:
    print(f"Video ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    print("-"*80)

    try:
        # YouTube API로 실제 비디오 정보 가져오기
        video_data, _ = analyzer.get_comprehensive_video_data(
            keyword="",
            max_results=1,
            video_ids=[video_id]
        )

        if video_data:
            video = video_data[0]
            print(f"실제 제목: {video.get('title', 'N/A')}")
            print(f"실제 설명 (앞부분):")
            description = video.get('description', 'N/A')
            print(description[:500] if len(description) > 500 else description)
            print()

    except Exception as e:
        print(f"Error: {e}")
        print()

    print()

print("="*80)
print("Gemini 답변 비교")
print("="*80)
print()

print("[Video 1: lL78TL3NaDU]")
print("Gemini 답변: investment banking guide for students")
print()

print("[Video 2: k-qj7JinXSw]")
print("Gemini 답변 1: Graf von Faber-Castell Perfect Pencil")
print("Gemini 답변 2: Lex Fridman Podcast - AI Laggard")
print("Gemini 답변 3: Linus Tech Tips - Fake Tech")
print("Gemini 답변 4: What I Think About This YouTube Channel")
print()

print("위의 실제 비디오 내용과 비교하여 Gemini가 정확한지 확인하세요.")
