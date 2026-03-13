import requests
import pandas as pd
import io

def fetch_historical_substrate():
    print("--- Substrate-X: 2024 Energy Grid Acquisition [Resilient Mode] ---")
    
    # Mirror link for PJM 2024 (CSV formatted)
    url = "https://www.eia.gov/electricity/wholesalemarkets/csv/pjm_load_act_hr_2024.csv"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # We check if it's actually a CSV or HTML junk
            content = response.text
            if "<html" in content.lower():
                print("[FAILED] Server returned HTML instead of CSV. Redirect blocked.")
                return

            # Clean the data: find the first line that looks like a header
            lines = content.splitlines()
            start_line = 0
            for i, line in enumerate(lines[:20]):
                if "Date" in line or "MW" in line:
                    start_line = i
                    break
            
            clean_content = "\n".join(lines[start_line:])
            df = pd.read_csv(io.StringIO(clean_content))
            df.to_csv("energy_load_2024.csv", index=False)
            
            # Auto-detect the Load Column
            load_col = [c for c in df.columns if 'Load' in c or 'MW' in c][0]
            
            avg_load = df[load_col].mean()
            print(f"[SUCCESS] 2024 Substrate localized.")
            print(f"Average 2024 Excitation (E_base): {avg_load:,.2f} MW")
        else:
            print(f"[FAILED] EIA Link Error: {response.status_code}")
    except Exception as e:
        print(f"[CRITICAL] Substrate Link Severed: {e}")

if __name__ == "__main__":
    fetch_historical_substrate()
