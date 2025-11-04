"""
다중 소스를 사용한 채널 국가 추론 (채널명 + 제목/설명 키워드 + 언어 감지)
"""
import sys
import os
import re
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from db_manager import TikTokDBManager

# 언어 감지를 위한 langdetect (있으면 사용)
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("[INFO] langdetect not available, skipping language detection")

# 국가 패턴 및 점수
COUNTRY_PATTERNS = {
    # 채널명 패턴 (높은 신뢰도: 5점)
    'channel_name': {
        r'\.ph\b': ('Philippines', 5),
        r'\.uk\b': ('United Kingdom', 5),
        r'\.jp\b': ('Japan', 5),
        r'\.kr\b': ('South Korea', 5),
        r'\.mx\b': ('Mexico', 5),
        r'_uk\b': ('United Kingdom', 5),
        r'uk_': ('United Kingdom', 5),
        r'_ug\b': ('Uganda', 5),
        r'ug_': ('Uganda', 5),
        r'mx\b': ('Mexico', 5),
        r'japan': ('Japan', 5),
        r'korea': ('South Korea', 5),
        r'kenya': ('Kenya', 5),
        r'uganda': ('Uganda', 5),
        r'australia': ('Australia', 5),
        r'philippines': ('Philippines', 5),
        r'mexico': ('Mexico', 5),
    },

    # 제목/설명 키워드 (중간 신뢰도: 3점)
    'content': {
        # 명확한 위치 표현
        r'\bin japan\b': ('Japan', 3),
        r'\bin uk\b': ('United Kingdom', 3),
        r'\bin korea\b': ('South Korea', 3),
        r'\bin kenya\b': ('Kenya', 3),
        r'\bin philippines\b': ('Philippines', 3),
        r'\bin australia\b': ('Australia', 3),
        r'\bin india\b': ('India', 3),
        r'\bin singapore\b': ('Singapore', 3),
        r'\bin thailand\b': ('Thailand', 3),
        r'\bin malaysia\b': ('Malaysia', 3),
        r'\bin indonesia\b': ('Indonesia', 3),

        # "from X" 패턴
        r'from japan': ('Japan', 3),
        r'from uk': ('United Kingdom', 3),
        r'from korea': ('South Korea', 3),
        r'from philippines': ('Philippines', 3),
        r'from india': ('India', 3),

        # 도시명 및 지역명
        r'\btokyo\b': ('Japan', 3),
        r'\bosaka\b': ('Japan', 3),
        r'\bseoul\b': ('South Korea', 3),
        r'\blondon\b': ('United Kingdom', 3),
        r'\bessex\b': ('United Kingdom', 3),
        r'\bmanchester\b': ('United Kingdom', 3),
        r'\bliverpool\b': ('United Kingdom', 3),
        r'\bmanila\b': ('Philippines', 3),
        r'\bbangkok\b': ('Thailand', 3),
        r'\bmumbai\b': ('India', 3),
        r'\bdelhi\b': ('India', 3),
        r'\bsingapore\b': ('Singapore', 3),
        r'\bsydney\b': ('Australia', 3),
        r'\bmelbourne\b': ('Australia', 3),
        r'\bmexico city\b': ('Mexico', 3),

        # "X launch" / "X exclusive" 패턴
        r'japan launch': ('Japan', 2),
        r'uk launch': ('United Kingdom', 2),
        r'korean launch': ('South Korea', 2),
        r'philippines exclusive': ('Philippines', 2),
    }
}

# 언어 → 국가 매핑 (낮은 신뢰도: 2점)
LANGUAGE_TO_COUNTRY = {
    'ja': ('Japan', 2),
    'ko': ('South Korea', 2),
    'th': ('Thailand', 2),
    'vi': ('Vietnam', 2),
    'id': ('Indonesia', 2),
    'tl': ('Philippines', 2),  # Tagalog
    'hi': ('India', 2),
    'ta': ('India', 2),
    'te': ('India', 2),
}


def detect_country_from_channel_name(channel_name):
    """채널명에서 국가 감지 (5점)"""
    if not channel_name:
        return []

    channel_lower = channel_name.lower()
    detected = []

    for pattern, (country, score) in COUNTRY_PATTERNS['channel_name'].items():
        if re.search(pattern, channel_lower):
            detected.append((country, score, 'channel_name'))

    return detected


def detect_country_from_content(text):
    """제목/설명에서 국가 감지 (2-3점)"""
    if not text:
        return []

    text_lower = text.lower()
    detected = []

    for pattern, (country, score) in COUNTRY_PATTERNS['content'].items():
        if re.search(pattern, text_lower):
            detected.append((country, score, 'content'))

    return detected


def detect_country_from_language(text):
    """언어 감지로 국가 추론 (2점)"""
    if not LANGDETECT_AVAILABLE or not text or len(text.strip()) < 10:
        return []

    try:
        lang = detect(text)
        if lang in LANGUAGE_TO_COUNTRY:
            country, score = LANGUAGE_TO_COUNTRY[lang]
            return [(country, score, 'language')]
    except (LangDetectException, Exception):
        pass

    return []


def infer_country_comprehensive(channel_name, title, description):
    """종합 국가 추론"""
    all_detections = []

    # 1. 채널명 체크
    all_detections.extend(detect_country_from_channel_name(channel_name))

    # 2. 제목 체크
    all_detections.extend(detect_country_from_content(title))

    # 3. 설명 체크
    all_detections.extend(detect_country_from_content(description))

    # 4. 언어 감지 (제목+설명 합쳐서)
    combined_text = f"{title or ''} {description or ''}"
    all_detections.extend(detect_country_from_language(combined_text))

    if not all_detections:
        return None, []

    # 점수 합산
    country_scores = {}
    for country, score, source in all_detections:
        if country not in country_scores:
            country_scores[country] = {'score': 0, 'sources': []}
        country_scores[country]['score'] += score
        country_scores[country]['sources'].append(source)

    # 가장 높은 점수의 국가 선택
    best_country = max(country_scores.items(), key=lambda x: x[1]['score'])

    return best_country[0], all_detections


def update_channel_countries_advanced():
    """개선된 국가 추론으로 업데이트"""

    db = TikTokDBManager()
    if not db.connect():
        print("DB 연결 실패")
        return

    print("="*80)
    print("TikTok 채널 국가 정보 추론 (다중 소스)")
    print("="*80)
    print()

    # 모든 비디오 가져오기
    db.cursor.execute('''
        SELECT
            video_id,
            channel_title,
            title,
            description,
            channel_country
        FROM tiktok_videos
        ORDER BY view_count DESC
    ''')

    videos = db.cursor.fetchall()
    print(f"총 {len(videos)}개 비디오 분석 중...")
    print()

    updated_count = 0
    results = []

    for video_id, channel, title, description, current_country in videos:
        # 국가 추론
        inferred_country, detections = infer_country_comprehensive(
            channel, title, description
        )

        if inferred_country:
            # 현재 US이거나 변경이 필요한 경우만 업데이트
            if current_country in ['US', None, ''] or current_country != inferred_country:
                # 점수 계산
                total_score = sum(score for _, score, _ in detections)

                # 신뢰도가 충분히 높은 경우만 업데이트 (3점 이상)
                if total_score >= 3:
                    db.cursor.execute('''
                        UPDATE tiktok_videos
                        SET channel_country = %s
                        WHERE video_id = %s
                    ''', (inferred_country, video_id))

                    updated_count += 1
                    results.append({
                        'video_id': video_id,
                        'channel': channel,
                        'title': title[:40] if title else 'N/A',
                        'country': inferred_country,
                        'score': total_score,
                        'detections': detections
                    })

    db.conn.commit()

    # 결과 출력
    print("="*80)
    print("국가 추론 결과:")
    print("="*80)

    for r in results:
        sources = ', '.join(set(s for _, _, s in r['detections']))
        # 이모지 때문에 출력 스킵
        try:
            print(f"[OK] {r['channel'][:25]:<25} → {r['country']:<20} (점수: {r['score']}, 출처: {sources})")
        except:
            print(f"[OK] {r['channel'][:25]:<25} → {r['country']:<20}")
        print()

    print("="*80)
    print(f"업데이트 완료!")
    print(f"  총 비디오: {len(videos)}개")
    print(f"  국가 업데이트: {updated_count}개")
    print("="*80)

    # 최종 국가 분포
    db.cursor.execute('''
        SELECT channel_country, COUNT(*) as cnt
        FROM tiktok_videos
        GROUP BY channel_country
        ORDER BY cnt DESC
    ''')

    print()
    print("최종 국가 분포:")
    for country, count in db.cursor.fetchall():
        print(f"  {country:<20}: {count:>2}개 비디오")

    db.disconnect()


if __name__ == "__main__":
    update_channel_countries_advanced()
