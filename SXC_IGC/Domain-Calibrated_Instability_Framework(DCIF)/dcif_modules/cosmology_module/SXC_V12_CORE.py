import pandas as pd
import numpy as np
import glob

def run_cosmology_scan():
    print("--- Substrate-X: Galactic Rotation Scan [SPARC Dataset] ---")
    files = glob.glob("data/sparc/*.dat")
    
    # Global Conflict Factor (Consistent with Nairobi & Energy)
    conflict_factor = 2.8
    beta = 1.0  # Scale of Information Gravity

    for file in files[:5]: # Testing first 5 galaxies
        df = pd.read_table(file, sep='\s+', skiprows=3, names=['Rad', 'Vobs', 'Vgas', 'Vdisk', 'Vbulge'])
        
        # Calculate Classical Predicted Velocity (Newtonian)
        # V_newton = sqrt(Vgas^2 + Vdisk^2 + Vbulge^2)
        df['V_classical'] = np.sqrt(df['Vgas']**2 + df['Vdisk']**2 + df['Vbulge']**2)
        
        # Calculate Substrate-X Tangle Point
        # Tangle occurs where Disk and Gas substrates interfere significantly
        tangle_threshold = df['V_classical'].median()
        
        def calculate_sxc_v(row):
            v_base = row['V_classical']
            # If the base signal is in the 'Tangle Zone', apply the 2.8x Tension
            if v_base > tangle_threshold:
                return v_base * np.sqrt(conflict_factor) # Square root because V^2 proportional to Force
            return v_base

        df['V_SXC'] = df.apply(calculate_sxc_v, axis=1)
        
        error_classical = np.mean(np.abs(df['Vobs'] - df['V_classical']))
        error_sxc = np.mean(np.abs(df['Vobs'] - df['V_SXC']))
        
        print(f"Galaxy: {file.split('/')[-1]}")
        print(f"  Classical Error: {error_classical:.2f}")
        print(f"  Substrate-X Error: {error_sxc:.2f}")
        print(f"  Improvement: {((error_classical - error_sxc) / error_classical) * 100:.1f}%")
        print("-" * 30)

if __name__ == "__main__":
    run_cosmology_scan()
