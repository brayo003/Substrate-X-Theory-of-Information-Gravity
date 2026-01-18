import requests
import sys

def download_file(url, filename):
    print(f"Connecting to Substrate: {filename}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    sys.stdout.write(".")
                    sys.stdout.flush()
            print(f"\n[SUCCESS] {filename} localized.")
    except Exception as e:
        print(f"\n[ERROR] Substrate Link Severed for {filename}: {e}")

if __name__ == "__main__":
    print("--- Substrate-X: Emergency Extraction [2026.01] ---")
    
    # COVID-19 (Direct RAW mirror - Bypass Catalog)
    covid_url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv"
    
    # INFLUENZA (Verified 2025-2026 FluSight Target Data)
    flu_url = "https://raw.githubusercontent.com/cdcepi/FluSight-forecast-hub/main/target-data/target-hospital-admissions.csv"

    download_file(covid_url, "covid_data_raw.csv")
    download_file(flu_url, "flu_data_raw.csv")
