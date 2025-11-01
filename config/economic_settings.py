# Country codes and names mapping
COUNTRIES = {
    'USA': 'United States',
    'GBR': 'United Kingdom',
    'DEU': 'Germany',
    'FRA': 'France',
    'ITA': 'Italy',
    'CAN': 'Canada',
    'JPN': 'Japan',
    'KOR': 'Korea, Rep.',
    'CHN': 'China',
    'IND': 'India',
    'BRA': 'Brazil',
    'AUS': 'Australia',
    'MEX': 'Mexico',
    'IDN': 'Indonesia',
    'TUR': 'Turkey',
    'SAU': 'Saudi Arabia',
    'ESP': 'Spain',
    'NLD': 'Netherlands',
    'CHE': 'Switzerland',
    'POL': 'Poland'
}

# API Base URLs
WORLD_BANK_BASE_URL = "http://api.worldbank.org/v2"
IMF_BASE_URL = "https://www.imf.org/external/datamapper/api/v1"
OECD_BASE_URL = "https://stats.oecd.org/sdmx-json"
FRED_BASE_URL = "https://api.stlouisfed.org/fred"

# Data collection settings
START_YEAR = 1960
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Output settings
OUTPUT_DIR = "data"
CSV_HEADERS = ["year", "country_code", "country_name", "value", "unit", "source"]
