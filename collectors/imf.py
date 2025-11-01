import requests
import time
import pandas as pd
from datetime import datetime
from config import IMF_BASE_URL, COUNTRIES, MAX_RETRIES, RETRY_DELAY, START_YEAR

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

def collect_imf_data(indicator_code, unit, source_name="IMF DataMapper"):
    """Collect data from IMF DataMapper API for a specific indicator"""
    data_rows = []
    current_year = datetime.now().year
    
    for i, (country_code, country_name) in enumerate(COUNTRIES.items(), 1):
        print(f"  {country_name} [{i}/{len(COUNTRIES)}]", end=" ")
        
        # IMF DataMapper API URL format
        url = f"{IMF_BASE_URL}/{indicator_code}/{country_code}"
        
        response = make_request_with_retry(url)
        if not response:
            print("실패")
            continue
            
        try:
            json_data = response.json()
            if 'values' not in json_data or not json_data['values']:
                print("데이터 없음")
                continue
                
            # Extract data points
            values = json_data['values']
            if country_code in values:
                country_data = values[country_code]
                for year_str, value in country_data.items():
                    if value is not None and year_str.isdigit():
                        year = int(year_str)
                        if year >= START_YEAR:
                            data_rows.append({
                                'year': year,
                                'country_code': country_code,
                                'country_name': country_name,
                                'value': float(value),
                                'unit': unit,
                                'source': source_name
                            })
            
            print("완료")
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"데이터 파싱 오류: {e}")
            continue
    
    return data_rows