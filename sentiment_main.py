"""
Samsung DX 브랜드 감성 분석 통합 파이프라인
YouTube, Instagram, TikTok 3개 플랫폼 데이터 수집 및 분석

실행 방법:
    python sentiment_main.py

스케줄러 등록 예시 (Windows Task Scheduler):
    프로그램: python
    인수: D:\Gomguard\program\samsung_crawl\sentiment_main.py
    시작 위치: D:\Gomguard\program\samsung_crawl
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# 프로젝트 루트 디렉토리
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 각 플랫폼 설정
PLATFORMS = {
    "youtube": {
        "name": "YouTube",
        "directory": os.path.join(PROJECT_ROOT, "youtube_brand_analyzer"),
        "pipeline": "pipeline_youtube_analysis.py",
        "enabled": True,
    },
    # 'instagram': {
    #     'name': 'Instagram',
    #     'directory': os.path.join(PROJECT_ROOT, 'instagram_brand_analyzer'),
    #     'pipeline': 'pipeline_instagram_analysis.py',
    #     'enabled': True
    # },
    # 'tiktok': {
    #     'name': 'TikTok',
    #     'directory': os.path.join(PROJECT_ROOT, 'tiktok_brand_analyzer'),
    #     'pipeline': 'pipeline_tiktok_analysis.py',
    #     'enabled': True
    # }
}


def print_header(text):
    """헤더 출력"""
    print()
    print("=" * 80)
    print(f"  {text}")
    print("=" * 80)
    print()


def print_separator():
    """구분선 출력"""
    print("-" * 80)


def format_duration(seconds):
    """초를 시:분:초 형식으로 변환"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}시간 {minutes}분 {secs}초"
    elif minutes > 0:
        return f"{minutes}분 {secs}초"
    else:
        return f"{secs}초"


def run_platform_pipeline(platform_key, platform_info):
    """플랫폼 파이프라인 실행"""

    platform_name = platform_info["name"]
    directory = platform_info["directory"]
    pipeline_file = platform_info["pipeline"]
    pipeline_path = os.path.join(directory, pipeline_file)

    print_header(f"{platform_name} 데이터 수집 및 분석 시작")

    # 파일 존재 확인
    if not os.path.exists(pipeline_path):
        print(f"[ERROR] 파이프라인 파일을 찾을 수 없습니다: {pipeline_path}")
        return False, 0

    print(f"실행 파일: {pipeline_file}")
    print(f"작업 디렉토리: {directory}")
    print()

    start_time = time.time()

    try:
        # 파이프라인 실행
        result = subprocess.run(
            [sys.executable, pipeline_file],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=7200,  # 2시간 타임아웃
        )

        end_time = time.time()
        duration = end_time - start_time

        # 결과 출력
        print_separator()
        print("실행 결과:")
        print_separator()

        if result.stdout:
            # stdout을 라인별로 출력 (너무 길면 마지막 50줄만)
            stdout_lines = result.stdout.split("\n")
            if len(stdout_lines) > 50:
                print("[출력 일부 생략...]")
                print("\n".join(stdout_lines[-50:]))
            else:
                print(result.stdout)

        if result.stderr:
            print("\n[STDERR]:")
            print(result.stderr)

        print_separator()

        if result.returncode == 0:
            print(f"[OK] {platform_name} 파이프라인 완료")
            print(f"     소요 시간: {format_duration(duration)}")
            return True, duration
        else:
            print(
                f"[ERROR] {platform_name} 파이프라인 실패 (exit code: {result.returncode})"
            )
            print(f"     소요 시간: {format_duration(duration)}")
            return False, duration

    except subprocess.TimeoutExpired:
        end_time = time.time()
        duration = end_time - start_time
        print(f"[ERROR] {platform_name} 파이프라인 타임아웃 (2시간 초과)")
        print(f"     소요 시간: {format_duration(duration)}")
        return False, duration

    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"[ERROR] {platform_name} 파이프라인 실행 중 오류:")
        print(f"     {str(e)}")
        print(f"     소요 시간: {format_duration(duration)}")
        return False, duration


def main():
    """메인 함수"""

    overall_start_time = time.time()
    start_datetime = datetime.now()

    print_header("Samsung DX 브랜드 감성 분석 - 통합 파이프라인")
    print(f"시작 시간: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 활성화된 플랫폼 확인
    enabled_platforms = [(k, v) for k, v in PLATFORMS.items() if v["enabled"]]
    print(f"실행할 플랫폼: {', '.join([p[1]['name'] for p in enabled_platforms])}")
    print()

    results = {}

    # 각 플랫폼 순차 실행
    for platform_key, platform_info in enabled_platforms:
        success, duration = run_platform_pipeline(platform_key, platform_info)
        results[platform_key] = {
            "success": success,
            "duration": duration,
            "name": platform_info["name"],
        }
        print()

    # 전체 결과 요약
    overall_end_time = time.time()
    overall_duration = overall_end_time - overall_start_time
    end_datetime = datetime.now()

    print_header("전체 실행 결과 요약")

    print(f"시작 시간: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"종료 시간: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"총 소요 시간: {format_duration(overall_duration)}")
    print()

    print_separator()
    print("플랫폼별 결과:")
    print_separator()

    success_count = 0
    for platform_key, result in results.items():
        status = "[OK]" if result["success"] else "[FAIL]"
        print(f"{status} {result['name']:<15} - {format_duration(result['duration'])}")
        if result["success"]:
            success_count += 1

    print_separator()
    print(f"성공: {success_count}/{len(results)}개 플랫폼")
    print("=" * 80)

    # 실패한 플랫폼이 있으면 exit code 1
    if success_count < len(results):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("[중단] 사용자가 실행을 중단했습니다.")
        sys.exit(130)
    except Exception as e:
        print()
        print(f"[ERROR] 예상치 못한 오류 발생:")
        print(f"  {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
