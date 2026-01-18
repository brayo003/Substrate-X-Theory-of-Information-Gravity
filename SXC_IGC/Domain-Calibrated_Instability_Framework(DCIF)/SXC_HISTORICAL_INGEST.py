import yfinance as yf
import pandas as pd
import numpy as np

def get_historical_signals():
    # Fetching VIX (Finance) and USO (Oil/Supply Chain) for 2020 Crash
    print("[INGEST] Fetching historical 2020-03-01 to 2020-05-01 data...")
    data = yf.download(["^VIX", "USO"], start="2020-03-01", end="2020-05-01", interval="1d")
    
    # Normalize
    vix = data['Close']['^VIX'].ffill()
    oil = data['Close']['USO'].ffill()
    
    # Map to Excitation (E)
    # E_fin = 1 - exp(-VIX/80)
    # E_geo = d(Oil)/dt (Volatility of supply)
    finance_E = 1 - np.exp(-vix.values / 80.0)
    geopolitical_E = np.abs(oil.pct_change().fillna(0).values) * 5.0 # Scaled vol
    
    return finance_E, geopolitical_E, vix.values

if __name__ == "__main__":
    fin, geo, raw_vix = get_historical_signals()
    print(f"Sample Fin E: {fin[:5]}")
