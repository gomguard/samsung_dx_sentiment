#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 브랜드 감정 분석 도구
사용법: python main.py
"""

import sys
import os
from datetime import datetime
from collectors.data_collector import YouTubeBrandCollector

# Windows 콘솔 인코딩 설정
if sys.platform.startswith('win'):
    os.system('chcp 65001')
    sys.stdout.reconfigure(encoding='utf-8')

# 수집할 키워드 목록
KEYWORDS = [
    "Samsung TV",
    "Samsung OLED",
    "Samsung QLED",
    "Samsung 4K TV",
    "Samsung 8K",
    "LG TV",
    "LG OLED",
    "LG QNED",
    "LG 4K TV",
    "LG 8K"
]

def main():
    """메인 실행 함수"""
    regions = ['US']
    max_results = 50

    print("🎬 YouTube 브랜드 감정 분석 도구")
    print("=" * 60)
    print(f"수집 키워드 수: {len(KEYWORDS)}개")
    print(f"키워드 목록: {', '.join(KEYWORDS)}")
    print(f"대상 지역: {regions}")
    print(f"키워드당 최대 결과 수: {max_results}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 데이터 수집기 초기화
        collector = YouTubeBrandCollector()

        # 각 키워드별로 데이터 수집
        for idx, keyword in enumerate(KEYWORDS, 1):
            print(f"\n[{idx}/{len(KEYWORDS)}] '{keyword}' 수집 중...")

            try:
                collected_data = collector.collect_brand_data(
                    keyword=keyword,
                    regions=regions,
                    max_results=max_results
                )
                print(f"✓ '{keyword}' 수집 완료")
            except Exception as e:
                print(f"✗ '{keyword}' 수집 실패: {e}")
                continue

        print("\n" + "=" * 60)
        print("🎉 전체 분석 완료!")
        print(f"data/ 폴더에 결과 파일들이 저장되었습니다.")
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def quick_analysis(keyword):
    """간단한 분석 함수 (대화형 사용)"""
    collector = YouTubeBrandCollector()
    return collector.collect_brand_data(keyword, regions=['US'], max_results=20)

if __name__ == "__main__":
    main()