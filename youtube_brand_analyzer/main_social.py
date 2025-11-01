#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
소셜미디어 브랜드 감정 분석 도구
지원 플랫폼: YouTube, TikTok
사용법: python main_social.py [키워드] --platform [youtube|tiktok|all]
예시: python main_social.py "samsung tv" --platform youtube
"""

import sys
import argparse
import os
from datetime import datetime
from collectors.data_collector import YouTubeBrandCollector
from collectors.tiktok_data_collector import TikTokBrandCollector

# Windows 콘솔 인코딩 설정
if sys.platform.startswith('win'):
    os.system('chcp 65001')
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='소셜미디어 브랜드 감정 분석 도구')
    parser.add_argument('keyword', help='분석할 키워드 (예: "samsung tv")')
    parser.add_argument('--platform', choices=['youtube', 'tiktok', 'all'], default='youtube',
                       help='분석할 플랫폼 (기본값: youtube)')
    parser.add_argument('--regions', nargs='+', default=['US'], 
                       help='분석할 지역 코드 (기본값: US)')
    parser.add_argument('--max-results', type=int, default=50,
                       help='최대 비디오 수 (기본값: 50)')
    
    args = parser.parse_args()
    
    # 플랫폼별 이모지 설정
    platform_info = {
        'youtube': {'emoji': '🎬', 'name': 'YouTube'},
        'tiktok': {'emoji': '🎵', 'name': 'TikTok'},
        'all': {'emoji': '📱', 'name': '소셜미디어'}
    }
    
    info = platform_info[args.platform]
    
    print(f"{info['emoji']} {info['name']} 브랜드 감정 분석 도구")
    print("=" * 60)
    print(f"키워드: {args.keyword}")
    print(f"플랫폼: {args.platform}")
    print(f"대상 지역: {args.regions}")
    print(f"최대 결과 수: {args.max_results}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        if args.platform == 'youtube' or args.platform == 'all':
            print("\n" + "="*60)
            print("🎬 YouTube 데이터 수집 시작")
            print("="*60)
            
            # YouTube 데이터 수집
            youtube_collector = YouTubeBrandCollector()
            youtube_data = youtube_collector.collect_brand_data(
                keyword=args.keyword,
                regions=args.regions,
                max_results=args.max_results
            )
        
        if args.platform == 'tiktok' or args.platform == 'all':
            print("\n" + "="*60)
            print("🎵 TikTok 데이터 수집 시작")
            print("="*60)
            
            # TikTok 데이터 수집
            tiktok_collector = TikTokBrandCollector()
            try:
                tiktok_data = tiktok_collector.collect_brand_data(
                    keyword=args.keyword,
                    regions=args.regions,
                    max_results=args.max_results
                )
            finally:
                tiktok_collector.close()
        
        print(f"\n🎉 {info['name']} 분석 완료!")
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

def quick_analysis(keyword, platform='youtube'):
    """간단한 분석 함수 (대화형 사용)"""
    if platform == 'youtube':
        collector = YouTubeBrandCollector()
        return collector.collect_brand_data(keyword, regions=['US'], max_results=20)
    elif platform == 'tiktok':
        collector = TikTokBrandCollector()
        try:
            return collector.collect_brand_data(keyword, regions=['US'], max_results=20)
        finally:
            collector.close()

if __name__ == "__main__":
    main()