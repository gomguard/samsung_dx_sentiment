"""
Infer channel country from channel name patterns
"""
import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from db_manager import TikTokDBManager

# Country detection patterns
COUNTRY_PATTERNS = {
    # Suffix patterns (.xx)
    r'\.ph\b': 'Philippines',
    r'\.uk\b': 'United Kingdom',
    r'\.jp\b': 'Japan',
    r'\.kr\b': 'South Korea',
    r'\.in\b': 'India',
    r'\.sg\b': 'Singapore',
    r'\.my\b': 'Malaysia',
    r'\.id\b': 'Indonesia',
    r'\.th\b': 'Thailand',
    r'\.vn\b': 'Vietnam',
    r'\.au\b': 'Australia',
    r'\.nz\b': 'New Zealand',
    r'\.ca\b': 'Canada',
    r'\.de\b': 'Germany',
    r'\.fr\b': 'France',
    r'\.es\b': 'Spain',
    r'\.it\b': 'Italy',
    r'\.br\b': 'Brazil',
    r'\.mx\b': 'Mexico',

    # Country name patterns (allow partial word matches)
    r'japan': 'Japan',
    r'korea': 'South Korea',
    r'kenya': 'Kenya',
    r'uganda': 'Uganda',
    r'nigeria': 'Nigeria',
    r'philippines': 'Philippines',
    r'india': 'India',
    r'singapore': 'Singapore',
    r'malaysia': 'Malaysia',
    r'indonesia': 'Indonesia',
    r'thailand': 'Thailand',
    r'vietnam': 'Vietnam',
    r'australia': 'Australia',
    r'canada': 'Canada',
    r'brazil': 'Brazil',
    r'mexico': 'Mexico',

    # UK variants
    r'_uk': 'United Kingdom',
    r'uk_': 'United Kingdom',
    r'british': 'United Kingdom',
    r'london': 'United Kingdom',

    # US variants (lower priority)
    r'usa': 'United States',
    r'_us': 'United States',
    r'us_': 'United States',

    # City/region patterns
    r'osaka': 'Japan',
    r'tokyo': 'Japan',
    r'seoul': 'South Korea',
    r'manila': 'Philippines',
    r'bangkok': 'Thailand',
    r'sydney': 'Australia',
    r'melbourne': 'Australia',

    # Uganda specific
    r'_ug\b': 'Uganda',
    r'\bug_': 'Uganda',
}

def infer_country_from_name(channel_name):
    """Infer country from channel name"""
    if not channel_name:
        return None

    channel_lower = channel_name.lower()

    # Check each pattern
    for pattern, country in COUNTRY_PATTERNS.items():
        if re.search(pattern, channel_lower):
            return country

    return None


def update_channel_countries():
    """Update channel_country field based on channel name inference"""

    db = TikTokDBManager()
    if not db.connect():
        print("DB 연결 실패")
        return

    print("="*80)
    print("TikTok 채널 국가 정보 추론 및 업데이트")
    print("="*80)
    print()

    # Get all unique channels
    db.cursor.execute('''
        SELECT DISTINCT channel_title
        FROM tiktok_videos
        WHERE channel_title IS NOT NULL
        ORDER BY channel_title
    ''')

    channels = [row[0] for row in db.cursor.fetchall()]
    print(f"총 {len(channels)}개 채널 분석 중...")
    print()

    updated_count = 0
    inference_results = []

    for channel in channels:
        inferred_country = infer_country_from_name(channel)

        if inferred_country:
            # Update database
            db.cursor.execute('''
                UPDATE tiktok_videos
                SET channel_country = %s
                WHERE channel_title = %s
            ''', (inferred_country, channel))

            updated_count += 1
            inference_results.append((channel, inferred_country))
            print(f"[OK] {channel[:40]:<40} -> {inferred_country}")
        else:
            print(f"     {channel[:40]:<40} -> (추론 불가)")

    db.conn.commit()

    print()
    print("="*80)
    print("업데이트 완료!")
    print(f"  총 채널: {len(channels)}개")
    print(f"  국가 추론 성공: {updated_count}개")
    print(f"  추론 실패: {len(channels) - updated_count}개")
    print("="*80)

    if inference_results:
        print()
        print("추론된 국가 분포:")
        country_counts = {}
        for _, country in inference_results:
            country_counts[country] = country_counts.get(country, 0) + 1

        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {country}: {count}개 채널")

    db.disconnect()


if __name__ == "__main__":
    update_channel_countries()
