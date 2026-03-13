import pandas as pd
import numpy as np

def calculate_nairobi_gamma():
    # Load local Nairobi CSVs generated from raw KNBS data
    # Logic: High flux in Fintech creates a specific damping signature
    try:
        fintech = pd.read_csv('fintech_tension_base.csv')
        urban = pd.read_csv('urban_tension_base.csv')
        
        # Calculate Logarithmic Decrement from the most recent flux peaks
        def get_local_gamma(data_col):
            # Normalizing and finding peak decay
            signal = data_col.values
            peaks = [signal[i] for i in range(1, len(signal)-1) 
                     if signal[i-1] < signal[i] > signal[i+1]]
            if len(peaks) < 2: return 0.5 # Default damping
            ratio = peaks[0] / peaks[1]
            return np.log(ratio) / np.pi

        g_fintech = get_local_gamma(fintech.iloc[:, 1])
        g_urban = get_local_gamma(urban.iloc[:, 1])

        print("=== NAIROBI LOCALIZATION RESULTS ===")
        print(f"Fintech Gamma: {g_fintech:.4f}")
        print(f"Urban Gamma:   {g_urban:.4f}")
        
        # Check for Golden Ratio Alignment
        if abs(g_fintech - 0.153) < 0.02:
            print("STATUS: NAIROBI FINTECH IS SELF-ORGANIZING (GOLDEN).")
        else:
            print(f"STATUS: DEVIATION DETECTED. DELTA: {abs(g_fintech - 0.153):.4f}")

    except Exception as e:
        print(f"Localization Failed: {e}")

calculate_nairobi_gamma()
