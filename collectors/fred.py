import requests
import time
import pandas as pd
from datetime import datetime
from config import FRED_BASE_URL, FRED_API_KEY, COUNTRIES, MAX_RETRIES, RETRY_DELAY, START_YEAR

# FRED series mapping for countries (limited availability)
FRED_COUNTRY_SERIES = {
    'USA': {
        'RPI': 'CPIAUCSL'  # US Consumer Price Index for All Urban Consumers (proxy for RPI)
    },
    'GBR': {
        'RPI': 'GBRRPIMONQ'  # UK Retail Price Index (if available)
    }
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

def collect_fred_data(indicator_name, unit, source_name="FRED"):
    """Collect data from FRED API for a specific indicator"""
    data_rows = []
    current_year = datetime.now().year
    
    for i, (country_code, country_name) in enumerate(COUNTRIES.items(), 1):
        print(f"  {country_name} [{i}/{len(COUNTRIES)}]", end=" ")
        
        # Check if country has data for this indicator
        if country_code not in FRED_COUNTRY_SERIES or indicator_name not in FRED_COUNTRY_SERIES[country_code]:
            print("FRED 데이터 없음")
            continue
            
        series_id = FRED_COUNTRY_SERIES[country_code][indicator_name]
        
        # FRED API URL format
        url = f"{FRED_BASE_URL}/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&observation_start={START_YEAR}-01-01&observation_end={current_year}-12-31"
        
        response = make_request_with_retry(url)
        if not response:
            print("실패")
            continue
            
        try:
            json_data = response.json()
            
            if 'observations' not in json_data:
                print("관측값 없음")
                continue
                
            observations = json_data['observations']
            
            for obs in observations:
                if obs['value'] != '.' and obs['value'] is not None:
                    try:
                        # Extract year from date (YYYY-MM-DD format)
                        year = int(obs['date'][:4])
                        value = float(obs['value'])
                        
                        if year >= START_YEAR:
                            data_rows.append({
                                'year': year,
                                'country_code': country_code,
                                'country_name': country_name,
                                'value': value,
                                'unit': unit,
                                'source': source_name
                            })
                    except (ValueError, TypeError):
                        continue
            
            print("완료")
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"데이터 파싱 오류: {e}")
            continue
    
    return data_rows