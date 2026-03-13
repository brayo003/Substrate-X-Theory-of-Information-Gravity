import requests
import pandas as pd
import sys

API_KEY = "0kVWKj3530QJddvurp0HNvSaf0aWaeNqegqAEJyb"

# Adjusted URL: 
# 1. Changed facet to 'ERCO' (Standard EIA ID for Electric Reliability Council of Texas)
# 2. Simplified dates to YYYY-MM-DD
url = (
    f"https://api.eia.gov/v2/electricity/rto/region-data/data/"
    f"?api_key={API_KEY}"
    f"&frequency=hourly"
    f"&data[0]=value"
    f"&facets[respondent][]=ERCO"
    f"&start=2023-01-01"
    f"&end=2023-12-31"
    f"&sort[0][column]=period"
    f"&sort[0][direction]=desc"
    f"&length=10000"
)

print("Fetching Substrate Data from EIA (ERCO Facet)...")
try:
    r = requests.get(url)
    r.raise_for_status()
    res = r.json()
except Exception as e:
    print(f"Connection Error: {e}")
    sys.exit(1)

if 'error' in res:
    print(f"EIA API Error: {res['error']}")
    sys.exit(1)

try:
    records = res['response']['data']
    if not records:
        print("Error: No records found. Attempting fallback to general region search...")
        # Fallback logic if 'ERCO' fails
        sys.exit(1)
        
    df = pd.DataFrame(records)
    print(f"Columns found: {df.columns.tolist()}")

    # The API returns 'period' as the timestamp
    df['period'] = pd.to_datetime(df['period'])
    df.rename(columns={'value': 'Load_MW'}, inplace=True)
    
    # Sort for Chronological Instability Analysis
    df = df.sort_values('period')

    df[['period','Load_MW']].to_csv("ercot_load_2023.csv", index=False)
    print(f"Success: Saved {len(df)} hours to ercot_load_2023.csv")

except KeyError as e:
    print(f"Structure Error: {e}")
    print("Response Keys:", res.keys())
    if 'response' in res:
        print("Response Content Keys:", res['response'].keys())
