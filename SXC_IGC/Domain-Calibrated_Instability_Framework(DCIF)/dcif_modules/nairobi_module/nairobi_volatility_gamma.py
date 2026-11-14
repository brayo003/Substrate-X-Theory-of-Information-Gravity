import pandas as pd
import numpy as np

def volatility_to_gamma():
    try:
        fintech = pd.read_csv('fintech_tension_base.csv')
        urban = pd.read_csv('urban_tension_base.csv')
        
        # We calculate Gamma as the ratio of Standard Deviation to Mean
        # High Volatility = High Decay/Friction
        def extract_vol_gamma(df):
            val = df.iloc[:, 1]
            return val.std() / val.mean() if val.mean() != 0 else 0.5

        g_f = extract_vol_gamma(fintech)
        g_u = extract_vol_gamma(urban)

        print("=== NAIROBI VOLATILITY-BASED GAMMA ===")
        print(f"Fintech Gamma (Vol): {g_f:.4f}")
        print(f"Urban Gamma (Vol):   {g_u:.4f}")
        
    except Exception as e:
        print(f"Analysis Failed: {e}")

volatility_to_gamma()
