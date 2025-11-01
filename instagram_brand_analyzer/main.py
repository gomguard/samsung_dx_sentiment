import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.instagram_api import InstagramAPI
from analyzers.sentiment import SentimentAnalyzer
from config.settings import BRAND_HASHTAGS, SEARCH_REGIONS, OUTPUT_DIR, CSV_ENCODING

def save_to_csv(data, filename):
    """데이터를 CSV 파일로 저장"""
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding=CSV_ENCODING)
        print(f"데이터 저장 완료: {filename}")
    except Exception as e:
        print(f"파일 저장 오류: {e}")

def main():
    print("Instagram 브랜드 분석기 시작")
    print("=" * 50)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    api = InstagramAPI()
    analyzer = SentimentAnalyzer()
    
    date_str = datetime.now().strftime("%Y%m%d")
    
    for region in SEARCH_REGIONS:
        print(f"\n지역: {region}")
        print("-" * 30)
        
        for hashtag in BRAND_HASHTAGS:
            print(f"\n해시태그 검색 중: #{hashtag}")
            
            try:
                posts_data, post_ids = api.get_comprehensive_post_data(hashtag, region)
                
                if posts_data:
                    print(f"수집된 게시물: {len(posts_data)}개")
                    posts_filename = os.path.join(OUTPUT_DIR, f"instagram_posts_{hashtag}_{region}_{date_str}.csv")
                    save_to_csv(posts_data, posts_filename)
                    
                    # 댓글 수집
                    comments_data = api.get_comprehensive_comments(post_ids)
                    
                    if comments_data:
                        print(f"수집된 댓글: {len(comments_data)}개")
                        
                        print("감정 분석 진행 중...")
                        
                        # 댓글 데이터를 sentiment analyzer 형식으로 변환
                        formatted_comments = []
                        for comment in comments_data:
                            formatted_comment = {
                                'video_id': comment['post_id'],  # Instagram에서는 post_id
                                'comment_id': comment['comment_id'],
                                'comment_text': comment['comment_text'],
                                'like_count': comment['like_count'],
                                'published_at': comment['published_at']
                            }
                            formatted_comments.append(formatted_comment)
                        
                        sentiment_results = analyzer.analyze_comment_sentiment(formatted_comments)
                        
                        if sentiment_results:
                            comments_filename = os.path.join(OUTPUT_DIR, f"instagram_comments_{hashtag}_{region}_{date_str}.csv")
                            analyzer_filename = os.path.join(OUTPUT_DIR, f"instagram_analysis_{hashtag}_{region}_{date_str}.csv")
                            
                            save_to_csv(sentiment_results, comments_filename)
                            
                            summary_results = analyzer.analyze_video_sentiment_summary(sentiment_results)
                            if summary_results:
                                save_to_csv(summary_results, analyzer_filename)
                            
                            print(f"감정 분석 완료: {len(sentiment_results)}개 댓글 분석")
                    else:
                        print("수집된 댓글이 없습니다.")
                else:
                    print("수집된 게시물이 없습니다.")
                    
            except Exception as e:
                print(f"해시태그 '#{hashtag}' 처리 중 오류: {str(e)}")
                continue
    
    print("\n" + "=" * 50)
    print("Instagram 브랜드 분석 완료!")
    print(f"API 사용량: {api.get_quota_usage()}회")

if __name__ == "__main__":
    main()