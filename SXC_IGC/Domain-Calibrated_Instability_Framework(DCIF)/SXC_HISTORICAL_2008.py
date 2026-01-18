import yfinance as yf
import pandas as pd
import numpy as np

def get_2008_signals():
    print("[INGEST] Fetching 2008-09-01 to 2008-11-01 (Lehman Collapse)...")
    # Fetching VIX and Crude Oil (WTI)
    data = yf.download(["^VIX", "CL=F"], start="2008-09-01", end="2008-11-01", interval="1d")
    vix = data['Close']['^VIX'].ffill()
    oil = data['Close']['CL=F'].ffill()
    
    # Normalizing to Excitation (E)
    finance_E = 1 - np.exp(-vix.values / 80.0)
    geopolitical_E = np.abs(oil.pct_change().fillna(0).values) * 5.0
    
    return finance_E, geopolitical_E, vix.values

if __name__ == "__main__":
    fin, geo, raw_vix = get_2008_signals()
    print(f"Initial VIX: {raw_vix[0]:.2f} | Initial Fin E: {fin[0]:.4f}")
