import requests
import time
import pandas as pd
from datetime import datetime
from config import WORLD_BANK_BASE_URL, COUNTRIES, MAX_RETRIES, RETRY_DELAY, START_YEAR

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

def collect_worldbank_data(indicator_code, unit, source_name="World Bank"):
    """Collect data from World Bank API for a specific indicator"""
    data_rows = []
    current_year = datetime.now().year
    
    for i, (country_code, country_name) in enumerate(COUNTRIES.items(), 1):
        print(f"  {country_name} [{i}/{len(COUNTRIES)}]", end=" ")
        
        # World Bank API URL format
        url = f"{WORLD_BANK_BASE_URL}/country/{country_code}/indicator/{indicator_code}?format=json&date={START_YEAR}:{current_year}&per_page=500"
        
        response = make_request_with_retry(url)
        if not response:
            print("실패")
            continue
            
        try:
            json_data = response.json()
            if len(json_data) < 2 or not json_data[1]:
                print("데이터 없음")
                continue
                
            # Extract data points
            for data_point in json_data[1]:
                if data_point['value'] is not None:
                    data_rows.append({
                        'year': int(data_point['date']),
                        'country_code': country_code,
                        'country_name': country_name,
                        'value': float(data_point['value']),
                        'unit': unit,
                        'source': source_name
                    })
            
            print("완료")
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"데이터 파싱 오류: {e}")
            continue
    
    return data_rows