import os
import pandas as pd
from datetime import datetime
from config import OUTPUT_DIR, CSV_HEADERS, COUNTRIES
from collectors.worldbank import collect_worldbank_data
from collectors.imf import collect_imf_data
from collectors.oecd import collect_oecd_data
from collectors.fred import collect_fred_data

def save_to_csv(data_rows, filename):
    """Save data to CSV file"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    if data_rows:
        df = pd.DataFrame(data_rows)
        df = df.sort_values(['country_code', 'year'])
        filepath = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"  → {len(data_rows)}개 데이터포인트 저장: {filepath}")
        return len(data_rows)
    else:
        # Create empty CSV with headers
        df = pd.DataFrame(columns=CSV_HEADERS)
        filepath = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"  → 빈 파일 생성: {filepath}")
        return 0

def fetch_indicator_1():
    """1. GDP PPP 명목 1인당 → World Bank API → gdp_ppp_nominal_per_capita.csv"""
    print("[1/10] GDP PPP 명목 1인당 수집 중...")
    data = collect_worldbank_data("NY.GDP.PCAP.PP.CD", "USD (PPP)", "World Bank")
    return save_to_csv(data, "gdp_ppp_nominal_per_capita.csv")

def fetch_indicator_2():
    """2. GDP PPP 실질 1인당 → World Bank API → gdp_ppp_real_per_capita.csv"""
    print("[2/10] GDP PPP 실질 1인당 수집 중...")
    data = collect_worldbank_data("NY.GDP.PCAP.PP.KD", "USD (constant 2017 PPP)", "World Bank")
    return save_to_csv(data, "gdp_ppp_real_per_capita.csv")

def fetch_indicator_3():
    """3. 자본 스톡 (실질 PPP) → 데이터 없음 → capital_stock_real_ppp.csv (빈 파일)"""
    print("[3/10] 자본 스톡 (실질 PPP) 수집 중...")
    print("  → 데이터 소스 없음, 빈 파일 생성")
    return save_to_csv([], "capital_stock_real_ppp.csv")

def fetch_indicator_4():
    """4. 잠재 산출량 (PPP) → IMF DataMapper API → potential_output_ppp.csv"""
    print("[4/10] 잠재 산출량 (PPP) 수집 중...")
    # IMF DataMapper potential output indicator (this may need adjustment based on actual IMF API)
    data = collect_imf_data("PPPGDP", "USD (PPP)", "IMF DataMapper")
    return save_to_csv(data, "potential_output_ppp.csv")

def fetch_indicator_5():
    """5. 가처분소득 (실질 PPP) → World Bank API (GNI per capita PPP) → disposable_income_real_ppp.csv"""
    print("[5/10] 가처분소득 (실질 PPP) 수집 중...")
    print("  → World Bank GNI per capita PPP를 가처분소득 대리지표로 사용")
    data = collect_worldbank_data("NY.GNP.PCAP.PP.CD", "USD (PPP)", "World Bank")
    return save_to_csv(data, "disposable_income_real_ppp.csv")

def fetch_indicator_6():
    """6. CPI → World Bank API → cpi.csv"""
    print("[6/10] CPI 수집 중...")
    data = collect_worldbank_data("FP.CPI.TOTL", "Index (2010=100)", "World Bank")
    return save_to_csv(data, "cpi.csv")

def fetch_indicator_7():
    """7. RPI → FRED API → rpi.csv"""
    print("[7/10] RPI 수집 중...")
    data = collect_fred_data("RPI", "Index", "FRED")
    return save_to_csv(data, "rpi.csv")

def fetch_indicator_8():
    """8. 가처분소득 (명목 LCU) → World Bank API (GNI per capita LCU) → disposable_income_nominal_lcu.csv"""
    print("[8/10] 가처분소득 (명목 LCU) 수집 중...")
    print("  → World Bank GNI per capita LCU를 가처분소득 대리지표로 사용")
    data = collect_worldbank_data("NY.GNP.PCAP.CN", "LCU per capita", "World Bank")
    return save_to_csv(data, "disposable_income_nominal_lcu.csv")

def fetch_indicator_9():
    """9. 가계부채 (LCU) → World Bank API (Domestic Credit % of GDP) → household_debt_lcu.csv"""
    print("[9/10] 가계부채 (LCU) 수집 중...")
    print("  → World Bank 국내신용(% of GDP)를 가계부채 대리지표로 사용")
    data = collect_worldbank_data("FS.AST.DOMS.GD.ZS", "% of GDP", "World Bank")
    return save_to_csv(data, "household_debt_lcu.csv")

def fetch_indicator_10():
    """10. 민간부문 순이자수입 (LCU) → 데이터 없음 → private_sector_net_interest_lcu.csv (빈 파일)"""
    print("[10/10] 민간부문 순이자수입 (LCU) 수집 중...")
    print("  → 데이터 소스 없음, 빈 파일 생성")
    return save_to_csv([], "private_sector_net_interest_lcu.csv")

def main():
    """Main execution function"""
    print(f"거시경제 지표 수집 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"대상 국가: {len(COUNTRIES)}개국")
    print("=" * 60)
    
    # Track results
    results = []
    total_data_points = 0
    
    # Execute all indicator collection functions
    indicators = [
        fetch_indicator_1, fetch_indicator_2, fetch_indicator_3, fetch_indicator_4, fetch_indicator_5,
        fetch_indicator_6, fetch_indicator_7, fetch_indicator_8, fetch_indicator_9, fetch_indicator_10
    ]
    
    for i, indicator_func in enumerate(indicators, 1):
        try:
            data_points = indicator_func()
            results.append({"indicator": i, "success": True, "data_points": data_points})
            total_data_points += data_points
            print()
        except Exception as e:
            print(f"  오류 발생: {e}")
            results.append({"indicator": i, "success": False, "data_points": 0})
            print()
    
    # Print summary
    print("=" * 60)
    print("수집 완료 요약:")
    successful = sum(1 for r in results if r["success"] and r["data_points"] > 0)
    empty_files = sum(1 for r in results if r["success"] and r["data_points"] == 0)
    failed = sum(1 for r in results if not r["success"])
    
    print(f"  성공: {successful}개 지표")
    print(f"  빈 파일: {empty_files}개 지표")
    print(f"  실패: {failed}개 지표")
    print(f"  총 데이터포인트: {total_data_points:,}개")
    print(f"  출력 폴더: {OUTPUT_DIR}/")
    
    print("\n생성된 파일:")
    for i, result in enumerate(results, 1):
        status = "O" if result["success"] else "X"
        points = f"({result['data_points']:,} points)" if result["data_points"] > 0 else "(empty)"
        print(f"  {status} indicator_{i}.csv {points}")

if __name__ == "__main__":
    main()