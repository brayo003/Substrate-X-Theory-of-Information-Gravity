import pandas as pd
import numpy as np
import os

def generate_synthetic_bulk(filename="lhc_bulk_synthetic.csv", target_size_mb=30):
    print(f"🛠️ GENERATING {target_size_mb}MB SYNTHETIC SUBSTRATE...")
    
    # Estimate rows for ~30MB (approx 50 bytes per row)
    num_rows = 600000 
    
    data = {
        'event_id': np.arange(num_rows),
        'pt1': np.random.exponential(50, num_rows), # Transverse momentum 1
        'pt2': np.random.exponential(50, num_rows), # Transverse momentum 2
        'phi1': np.random.uniform(-np.pi, np.pi, num_rows),
        'phi2': np.random.uniform(-np.pi, np.pi, num_rows),
        'met': np.random.rayleigh(20, num_rows) # Simulated Missing Transverse Energy
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    size = os.path.getsize(filename) / (1024 * 1024)
    print(f"✅ Created: {filename} ({size:.2f} MB)")

if __name__ == "__main__":
    generate_synthetic_bulk()
