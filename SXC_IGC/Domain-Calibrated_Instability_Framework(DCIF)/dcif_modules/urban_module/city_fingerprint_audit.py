import pandas as pd
import numpy as np

def calculate_fingerprint(file_path, name):
    try:
        df = pd.read_csv(file_path)
        # Assuming traffic flow/volume is the primary tension signal
        signal = df.iloc[:, 1].values 
        
        # 1. Delta (Damping) - The recovery speed
        peaks = [signal[i] for i in range(1, len(signal)-1) 
                 if signal[i-1] < signal[i] > signal[i+1]]
        delta = np.log(peaks[0]/peaks[1])/np.pi if len(peaks) > 1 else 0.5
        
        # 2. Nu (Volatility) - The noise level
        nu = np.std(signal) / np.mean(signal) if np.mean(signal) != 0 else 0
        
        return {"City": name, "Delta (Damping)": delta, "Nu (Vol)": nu}
    except Exception as e:
        return {"City": name, "Error": str(e)}

# Running comparison
results = []
# Nairobi Data (from previous run)
results.append({"City": "Nairobi_Urban", "Delta (Damping)": 0.5, "Nu (Vol)": 0.274})

# NYC Data (Targeting your local CSV)
results.append(calculate_fingerprint('nyc_full_traffic_data.csv', "New_York_Traffic"))

print("\n=== GLOBAL CITY FINGERPRINT AUDIT ===")
print(pd.DataFrame(results))
