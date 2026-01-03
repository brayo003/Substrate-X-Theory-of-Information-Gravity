import pandas as pd
import requests
import datetime

def fetch_grid_pulse():
    print("--- Substrate-X: Energy Grid Acquisition [Dynamic Pivot] ---")
    
    # Get today's date in CAISO format: YYYYMMDD
    today = datetime.datetime.now().strftime('%Y%m%d')
    url = f"https://www.caiso.com/outlook/SP/History/{today}/netdemand.csv"
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open("energy_load_live.csv", "wb") as f:
                f.write(response.content)
            print(f"[SUCCESS] {today} Grid Substrate localized.")
            
            # Load and verify pulse
            df = pd.read_csv("energy_load_live.csv")
            latest_val = df.iloc[-1].values[1] 
            print(f"Current Net Excitation (E): {latest_val:,.2f} MW")
        else:
            print(f"[FAILED] Link Error {response.status_code}. The Substrate is rotating.")
    except Exception as e:
        print(f"[CRITICAL] Connection Severed: {e}")

if __name__ == "__main__":
    fetch_grid_pulse()
