import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.tiktok_api import TikTokAPI
from analyzers.sentiment import SentimentAnalyzer
from config.settings import BRAND_KEYWORDS, SEARCH_REGIONS, OUTPUT_DIR, CSV_ENCODING

def save_to_csv(data, filename):
    """데이터를 CSV 파일로 저장"""
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding=CSV_ENCODING)
        print(f"데이터 저장 완료: {filename}")
    except Exception as e:
        print(f"파일 저장 오류: {e}")

def main():
    print("TikTok 브랜드 분석기 시작")
    print("=" * 50)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    api = TikTokAPI()
    analyzer = SentimentAnalyzer()
    
    date_str = datetime.now().strftime("%Y%m%d")
    
    for region in SEARCH_REGIONS:
        print(f"\n지역: {region}")
        print("-" * 30)
        
        for keyword in BRAND_KEYWORDS:
            print(f"\n키워드 검색 중: {keyword}")
            
            try:
                videos_data, video_ids = api.get_comprehensive_video_data(keyword, region)
                
                if videos_data:
                    print(f"수집된 비디오: {len(videos_data)}개")
                    videos_filename = os.path.join(OUTPUT_DIR, f"tiktok_videos_{keyword.replace(' ', '_')}_{region}_{date_str}.csv")
                    save_to_csv(videos_data, videos_filename)
                    
                    # 댓글 수집
                    comments_data = api.get_comprehensive_comments(video_ids)
                    
                    if comments_data:
                        print(f"수집된 댓글: {len(comments_data)}개")
                        
                        print("감정 분석 진행 중...")
                        sentiment_results = analyzer.analyze_comment_sentiment(comments_data)
                        
                        if sentiment_results:
                            comments_filename = os.path.join(OUTPUT_DIR, f"tiktok_comments_{keyword.replace(' ', '_')}_{region}_{date_str}.csv")
                            analyzer_filename = os.path.join(OUTPUT_DIR, f"tiktok_analysis_{keyword.replace(' ', '_')}_{region}_{date_str}.csv")
                            
                            save_to_csv(sentiment_results, comments_filename)
                            
                            summary_results = analyzer.analyze_video_sentiment_summary(sentiment_results)
                            if summary_results:
                                save_to_csv(summary_results, analyzer_filename)
                            
                            print(f"감정 분석 완료: {len(sentiment_results)}개 댓글 분석")
                    else:
                        print("수집된 댓글이 없습니다.")
                    
            except Exception as e:
                print(f"키워드 '{keyword}' 처리 중 오류: {str(e)}")
                continue
    
    print("\n" + "=" * 50)
    print("TikTok 브랜드 분석 완료!")

if __name__ == "__main__":
    main()