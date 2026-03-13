import pandas as pd
import numpy as np
import glob
import os

# ================== V12 ENGINE ==================
class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.beta = 3.5
        self.dt = 0.05
        self.decay_rate = 0.0005 
        
    def excitation_flux(self, signal):
        if signal < 45:
            return 1 - np.exp(-signal / 40.0)
        return 0.675 + ((signal - 45.0) / 20.0)

    def step(self, signal):
        self.gamma *= (1 - self.decay_rate)
        E = self.excitation_flux(signal)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt
        
        if self.T_sys > 1.0:
            self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4:
            self.phase = "NOMINAL"
            
        return self.T_sys, self.phase

# ================== SCAN ALL DATA FILES ==================
data_files = glob.glob("data/*.csv") + glob.glob("data/*.txt") + glob.glob("data/*.xlsx")
print(f"Found {len(data_files)} potential data files")

results = []

for file in data_files[:5]:  # Start with first 5 to test
    try:
        print(f"\n--- Processing: {os.path.basename(file)} ---")
        
        # Try to read the file
        if file.endswith('.xlsx'):
            df = pd.read_excel(file, nrows=1000)
        else:
            df = pd.read_csv(file, nrows=1000, on_bad_lines='skip')
        
        # Find numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            print("  No numeric columns found")
            continue
            
        # Use first numeric column as signal
        signal_col = numeric_cols[0]
        values = df[signal_col].dropna().values[:500]  # Limit to 500 points
        
        if len(values) < 10:
            print("  Not enough data points")
            continue
            
        # Normalize to 0-100
        signal = (values - values.min()) / (values.max() - values.min() + 1e-10) * 100
        
        # Run V12
        engine = SXCOmegaEngine()
        T_values = []
        phase_count = {"NOMINAL": 0, "FIREWALL": 0}
        
        for s in signal:
            T, phase = engine.step(s)
            T_values.append(T)
            phase_count[phase] = phase_count.get(phase, 0) + 1
            
        # Calculate K
        K = values / values.max()
        
        # Store results
        results.append({
            'file': os.path.basename(file),
            'records': len(values),
            'K_min': K.min(),
            'K_max': K.max(),
            'K_mean': K.mean(),
            'K_std': K.std(),
            'K_above_05': (K > 0.5).sum(),
            'K_pct_above_05': (K > 0.5).mean() * 100,
            'T_sys_min': min(T_values),
            'T_sys_max': max(T_values),
            'T_sys_mean': np.mean(T_values),
            'firewall_count': phase_count['FIREWALL'],
            'firewall_pct': phase_count['FIREWALL'] / len(T_values) * 100
        })
        
        print(f"  Records: {len(values)}")
        print(f"  K range: {K.min():.3f} to {K.max():.3f}")
        print(f"  K > 0.5: {(K > 0.5).sum()} ({(K > 0.5).mean()*100:.1f}%)")
        print(f"  T_sys range: {min(T_values):.2f} to {max(T_values):.2f}")
        print(f"  FIREWALL: {phase_count['FIREWALL']} ({phase_count['FIREWALL']/len(T_values)*100:.1f}%)")
        
    except Exception as e:
        print(f"  Error: {e}")

# ================== SAVE RESULTS ==================
results_df = pd.DataFrame(results)
results_df.to_csv('ecology_v12_scan_results.csv', index=False)
print("\n✅ Saved scan results to ecology_v12_scan_results.csv")
print(results_df[['file', 'K_above_05', 'firewall_pct']].to_string())
