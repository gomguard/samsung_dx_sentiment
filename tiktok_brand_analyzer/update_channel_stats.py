"""
기존 TikTok 비디오들의 채널 통계를 실제 값으로 업데이트
"""
import sys
import os
import time

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import local modules
sys.path.insert(0, os.path.join(current_dir, 'collectors'))
sys.path.insert(0, os.path.join(current_dir, 'config'))

from tiktok_api import TikTokAPI
from db_manager import TikTokDBManager

def update_channel_statistics():
    """DB에 있는 모든 비디오의 채널 통계를 실제 값으로 업데이트"""

    api = TikTokAPI()
    db = TikTokDBManager()

    if not db.connect():
        print("DB 연결 실패")
        return

    print("="*80)
    print("TikTok 채널 통계 업데이트")
    print("="*80)
    print()

    # fallback 값을 가진 채널들 찾기
    db.cursor.execute('''
        SELECT DISTINCT
            channel_id,
            channel_custom_url,
            channel_title
        FROM tiktok_videos
        WHERE channel_subscriber_count = 1000
           OR channel_video_count = 100
        ORDER BY channel_id
    ''')

    channels_to_update = db.cursor.fetchall()

    print(f"업데이트가 필요한 채널: {len(channels_to_update)}개")
    print()

    if len(channels_to_update) == 0:
        print("업데이트할 채널이 없습니다!")
        db.disconnect()
        return

    # 각 채널의 통계 업데이트
    success_count = 0
    fail_count = 0

    for i, (channel_id, channel_url, channel_title) in enumerate(channels_to_update, 1):
        # uniqueId 추출 (@username에서 username 부분)
        unique_id = channel_url.replace('@', '') if channel_url else None

        if not unique_id:
            print(f"[{i}/{len(channels_to_update)}] {channel_title}: uniqueId 없음, 스킵")
            fail_count += 1
            continue

        print(f"[{i}/{len(channels_to_update)}] @{unique_id} 업데이트 중...", end=" ")

        # User Info API 호출
        user_info = api.get_user_info(unique_id)

        if user_info:
            # DB 업데이트
            try:
                db.cursor.execute('''
                    UPDATE tiktok_videos
                    SET
                        channel_subscriber_count = %s,
                        channel_video_count = %s,
                        channel_total_view_count = %s,
                        channel_description = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE channel_id = %s
                ''', (
                    user_info.get('follower_count', 0),
                    user_info.get('video_count', 0),
                    user_info.get('heart_count', 0),
                    user_info.get('signature', ''),
                    channel_id
                ))
                db.conn.commit()

                # 업데이트된 비디오 수 확인
                db.cursor.execute('''
                    SELECT COUNT(*) FROM tiktok_videos
                    WHERE channel_id = %s
                ''', (channel_id,))
                video_count = db.cursor.fetchone()[0]

                print(f"[OK] {user_info['follower_count']:,}명, {user_info['video_count']}개 비디오 (DB의 {video_count}개 비디오 업데이트됨)")
                success_count += 1

            except Exception as e:
                print(f"[ERROR] DB 업데이트 실패: {e}")
                db.conn.rollback()
                fail_count += 1
        else:
            print(f"[FAIL] API 호출 실패")
            fail_count += 1

        # Rate limiting
        time.sleep(0.5)

        # 10개마다 추가 대기
        if i % 10 == 0:
            print(f"  >>> {i}개 처리 완료, 5초 대기...")
            time.sleep(5)

    print()
    print("="*80)
    print("업데이트 완료!")
    print(f"  성공: {success_count}개")
    print(f"  실패: {fail_count}개")
    print(f"  총 API 호출: {api.get_quota_usage()}회")
    print("="*80)

    # 최종 통계 확인
    print()
    print("최종 채널 통계:")
    db.cursor.execute('''
        SELECT
            COUNT(*) as total_videos,
            COUNT(DISTINCT channel_id) as unique_channels,
            MIN(channel_subscriber_count) as min_subs,
            MAX(channel_subscriber_count) as max_subs,
            AVG(channel_subscriber_count)::INTEGER as avg_subs,
            COUNT(CASE WHEN channel_subscriber_count = 1000 THEN 1 END) as fallback_count
        FROM tiktok_videos
    ''')

    stats = db.cursor.fetchone()
    print(f"  총 비디오: {stats[0]}개")
    print(f"  유니크 채널: {stats[1]}개")
    print(f"  구독자수 범위: {stats[2]:,} ~ {stats[3]:,}명")
    print(f"  평균 구독자수: {stats[4]:,}명")
    print(f"  Fallback 값 남은 개수: {stats[5]}개")

    db.disconnect()

if __name__ == "__main__":
    update_channel_statistics()
