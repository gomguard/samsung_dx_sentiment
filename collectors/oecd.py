import requests
import time
import pandas as pd
from datetime import datetime
from config import COUNTRIES, MAX_RETRIES, RETRY_DELAY, START_YEAR

# OECD API Base URLs (New Data Explorer API)
OECD_API_URL = "https://sdmx.oecd.org/public/rest/data"

# OECD country code mapping - only OECD member countries have data
OECD_COUNTRY_MAPPING = {
    'USA': 'USA',
    'GBR': 'GBR', 
    'DEU': 'DEU',
    'FRA': 'FRA',
    'ITA': 'ITA',
    'CAN': 'CAN',
    'JPN': 'JPN',
    'KOR': 'KOR',
    'AUS': 'AUS',
    'MEX': 'MEX',
    'TUR': 'TUR',
    'ESP': 'ESP',
    'NLD': 'NLD',
    'CHE': 'CHE',
    'POL': 'POL'
    # Note: CHN, IND, BRA, IDN, SAU are not OECD members
}

def make_request_with_retry(url, max_retries=MAX_RETRIES):
    """Make HTTP request with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed to fetch data after {max_retries} attempts: {e}")
                return None
            print(f"Attempt {attempt + 1} failed, retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    return None

def collect_oecd_household_income(indicator_code, unit, source_name="OECD"):
    """Collect household disposable income data using OECD CSV API"""
    import pandas as pd
    
    data_rows = []
    
    print(f"  OECD CSV API를 통한 가처분소득 데이터 수집...")
    
    try:
        # OECD의 간단한 CSV API 사용
        # HH_DASH 데이터셋에서 실질 가처분소득 데이터
        oecd_countries = [code for code in OECD_COUNTRY_MAPPING.values()]
        countries_str = "+".join(oecd_countries)
        
        # OECD CSV API URL - 실질 가처분소득 per capita
        if indicator_code == "RHHGDI":
            # Real household gross disposable income per capita
            url = f"https://stats.oecd.org/SDMX-JSON/data/HH_DASH/{countries_str}.RHHGDI._T.A/all?contentType=csv&startPeriod={START_YEAR}"
        elif indicator_code == "HHGDI":
            # Nominal household gross disposable income per capita  
            url = f"https://stats.oecd.org/SDMX-JSON/data/HH_DASH/{countries_str}.HHGDI._T.A/all?contentType=csv&startPeriod={START_YEAR}"
        elif indicator_code == "HHDEBT":
            # Household debt per capita
            url = f"https://stats.oecd.org/SDMX-JSON/data/HH_DASH/{countries_str}.HHDEBT._T.A/all?contentType=csv&startPeriod={START_YEAR}"
        else:
            print(f"  알 수 없는 지표 코드: {indicator_code}")
            return data_rows
        
        print(f"  요청 URL: {url[:100]}...")
        
        # Pandas로 CSV 직접 읽기
        df = pd.read_csv(url)
        
        if df.empty:
            print("  데이터 없음")
            return data_rows
            
        # 데이터 변환
        for _, row in df.iterrows():
            try:
                location = row.get('LOCATION', '')
                time_period = row.get('TIME_PERIOD', '')
                value = row.get('ObsValue', None)
                
                if pd.isna(value) or value == '':
                    continue
                    
                # OECD 국가 코드를 원래 코드로 변환
                original_country_code = None
                for orig_code, oecd_code in OECD_COUNTRY_MAPPING.items():
                    if oecd_code == location:
                        original_country_code = orig_code
                        break
                        
                if original_country_code and original_country_code in COUNTRIES:
                    year = int(time_period)
                    if year >= START_YEAR:
                        data_rows.append({
                            'year': year,
                            'country_code': original_country_code,
                            'country_name': COUNTRIES[original_country_code],
                            'value': float(value),
                            'unit': unit,
                            'source': source_name
                        })
            except (ValueError, KeyError, TypeError):
                continue
                
        print(f"  완료 ({len(data_rows)}개 데이터포인트)")
        
    except Exception as e:
        print(f"  오류: {e}")
        print("  → OECD 데이터 수집 실패, 빈 결과 반환")
        
    return data_rows

def collect_oecd_data(dataset_code, indicator_code, unit, source_name="OECD"):
    """Generic OECD data collector (legacy function for compatibility)"""
    if dataset_code == "HH_DASH":
        return collect_oecd_household_income(indicator_code, unit, source_name)
    else:
        # Original implementation for other datasets
        data_rows = []
        print("  레거시 OECD API 사용 (데이터 제한적)")
        return data_rows