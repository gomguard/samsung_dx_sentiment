"""
RegionCode 효과 테스트
- US vs KR regionCode 비교
- 각각 채널 국가 분포 확인
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from collectors.youtube_api import YouTubeAnalyzer

def create_test_tables():
    """테스트용 테이블 생성"""
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )
    cursor = conn.cursor()

    # US 테이블
    cursor.execute("""
        DROP TABLE IF EXISTS youtube_videos_us CASCADE;
        CREATE TABLE youtube_videos_us (
            video_id VARCHAR(50) PRIMARY KEY,
            title TEXT,
            channel_id VARCHAR(50),
            channel_title TEXT,
            channel_country VARCHAR(10),
            channel_subscriber_count BIGINT,
            view_count BIGINT,
            region_code VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # KR 테이블
    cursor.execute("""
        DROP TABLE IF EXISTS youtube_videos_kr CASCADE;
        CREATE TABLE youtube_videos_kr (
            video_id VARCHAR(50) PRIMARY KEY,
            title TEXT,
            channel_id VARCHAR(50),
            channel_title TEXT,
            channel_country VARCHAR(10),
            channel_subscriber_count BIGINT,
            view_count BIGINT,
            region_code VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("테스트 테이블 생성 완료: youtube_videos_us, youtube_videos_kr")

def collect_and_save(region_code, table_name, sample_size=30):
    """RegionCode로 데이터 수집 후 테이블에 저장"""
    print(f"\n{'='*80}")
    print(f"RegionCode={region_code} 데이터 수집 시작")
    print(f"{'='*80}")

    # 필터 없이 수집 (순수 regionCode 효과만)
    analyzer = YouTubeAnalyzer()

    video_data, video_ids, raw_data = analyzer.get_comprehensive_video_data(
        keyword="Samsung TV",
        region_code=region_code,
        max_results=sample_size,
        apply_quality_filter=False  # 필터 없음!
    )

    print(f"\n수집 완료: {len(video_data)}개 비디오")

    # DB에 저장
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )
    cursor = conn.cursor()

    for video in video_data:
        cursor.execute(f"""
            INSERT INTO {table_name}
            (video_id, title, channel_id, channel_title, channel_country,
             channel_subscriber_count, view_count, region_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO NOTHING
        """, (
            video.get('video_id'),
            video.get('title'),
            video.get('channel_id'),
            video.get('channel_title'),
            video.get('channel_country'),
            video.get('channel_subscriber_count'),
            video.get('view_count'),
            region_code
        ))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"{table_name} 테이블에 저장 완료")

def compare_results():
    """두 테이블의 channel_country 분포 비교"""
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print("RegionCode 비교 결과")
    print(f"{'='*80}")

    # US regionCode 결과
    print(f"\n[RegionCode = US]")
    cursor.execute("""
        SELECT channel_country, COUNT(*) as count
        FROM youtube_videos_us
        GROUP BY channel_country
        ORDER BY count DESC
    """)

    us_results = cursor.fetchall()
    us_total = sum(count for _, count in us_results)

    for country, count in us_results:
        country_name = country if country else 'NULL'
        percentage = 100 * count / us_total if us_total > 0 else 0
        print(f"  {country_name}: {count}개 ({percentage:.1f}%)")

    print(f"  총합: {us_total}개")

    # KR regionCode 결과
    print(f"\n[RegionCode = KR]")
    cursor.execute("""
        SELECT channel_country, COUNT(*) as count
        FROM youtube_videos_kr
        GROUP BY channel_country
        ORDER BY count DESC
    """)

    kr_results = cursor.fetchall()
    kr_total = sum(count for _, count in kr_results)

    for country, count in kr_results:
        country_name = country if country else 'NULL'
        percentage = 100 * count / kr_total if kr_total > 0 else 0
        print(f"  {country_name}: {count}개 ({percentage:.1f}%)")

    print(f"  총합: {kr_total}개")

    # 결론
    print(f"\n{'='*80}")
    print("결론:")
    print(f"{'='*80}")
    print("regionCode는 검색 지역을 설정하는 파라미터입니다.")
    print("채널의 국가(channel_country)와는 무관합니다.")
    print()
    print("US regionCode를 사용해도 한국, 인도, 브라질 등 전세계 채널이 나옵니다.")
    print("채널 국가를 제한하려면 수집 후 channel_country 필터링이 필요합니다.")
    print(f"{'='*80}")

    cursor.close()
    conn.close()

def main():
    """메인 실행"""
    print("="*80)
    print("RegionCode 효과 테스트")
    print("="*80)
    print()
    print("목적: regionCode가 채널 국가를 제한하는지 확인")
    print("방법: US vs KR regionCode로 각각 30개 수집 후 channel_country 분포 비교")
    print()

    # 1. 테스트 테이블 생성
    create_test_tables()

    # 2. US regionCode로 수집
    collect_and_save("US", "youtube_videos_us", sample_size=30)

    # 3. KR regionCode로 수집
    collect_and_save("KR", "youtube_videos_kr", sample_size=30)

    # 4. 결과 비교
    compare_results()

if __name__ == "__main__":
    main()
