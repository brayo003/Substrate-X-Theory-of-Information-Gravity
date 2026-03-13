import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

# ================== THE ACTUAL V12 ENGINE ==================
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

    def apply_intervention(self, type="MICRO"):
        if type == "DEEP":
            self.gamma = min(self.gamma_max, self.gamma * 1.15)
            self.T_sys *= 0.60
        else:
            self.gamma = min(self.gamma_max, self.gamma * 1.05)

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

# ================== LOAD DATA ==================
print("="*60)
print("V12 ENGINE TEST ON GRID DATA")
print("="*60)

df = pd.read_csv('outage_data_with_igk.csv')
print(f"Loaded {len(df)} records")

# Sort by time (important for dynamics!)
df['start_time'] = pd.to_datetime(df['start_time'])
df = df.sort_values('start_time').reset_index(drop=True)

# Create Failure_Event (6h window before each event)
df['event_begin'] = pd.to_datetime(df['event_begin'])
df['Failure_Event'] = 0
for event_time in df['event_begin'].unique():
    mask = (df['start_time'] >= event_time - pd.Timedelta(hours=6)) & \
           (df['start_time'] <= event_time)
    df.loc[mask, 'Failure_Event'] = 1
print(f"Positive samples (6h before events): {df['Failure_Event'].sum()}")

# ================== RUN V12 OVER TIME ==================
print("\nRunning V12 engine across timeline...")

# Scale max_customers to match V12's expected signal range
# V12 excitation expects signal ~0-100 range
max_val = df['max_customers'].max()
df['scaled_signal'] = (df['max_customers'] / max_val) * 100

# Initialize engine and storage
engine = SXCOmegaEngine()
T_values = []
phase_values = []

# Run through each timepoint IN ORDER
for idx, row in df.iterrows():
    T, phase = engine.step(row['scaled_signal'])
    T_values.append(T)
    phase_values.append(phase)

df['V12_T'] = T_values
df['V12_phase'] = phase_values
df['V12_alarm'] = (df['V12_T'] > 0.8).astype(int)  # Alarm before FIREWALL

print(f"Done. T_sys range: {df['V12_T'].min():.2f} to {df['V12_T'].max():.2f}")
print(f"FIREWALL phases: {(df['V12_phase'] == 'FIREWALL').sum()}")

# ================== EVALUATE ==================
print("\n" + "="*60)
print("PREDICTIVE PERFORMANCE")
print("="*60)

# Classical threshold (simple load > 95th %ile)
threshold = df['max_customers'].quantile(0.95)
df['classical_alarm'] = (df['max_customers'] > threshold).astype(int)

# ROC-AUC scores
print("\nROC-AUC (ranking ability):")
print(f"  Classical (load > threshold): {roc_auc_score(df['Failure_Event'], df['max_customers']):.4f}")
print(f"  V12 (T_sys):                  {roc_auc_score(df['Failure_Event'], df['V12_T']):.4f}")

# Binary metrics
print("\nBinary predictions (alarm vs no alarm):")
print(f"\nClassical (load > {threshold:.0f}):")
print(f"  Precision: {precision_score(df['Failure_Event'], df['classical_alarm']):.4f}")
print(f"  Recall:    {recall_score(df['Failure_Event'], df['classical_alarm']):.4f}")
print(f"  F1-Score:  {f1_score(df['Failure_Event'], df['classical_alarm']):.4f}")

print(f"\nV12 (T_sys > 0.8):")
print(f"  Precision: {precision_score(df['Failure_Event'], df['V12_alarm']):.4f}")
print(f"  Recall:    {recall_score(df['Failure_Event'], df['V12_alarm']):.4f}")
print(f"  F1-Score:  {f1_score(df['Failure_Event'], df['V12_alarm']):.4f}")

# False positives
classical_fp = (df['classical_alarm'] & ~df['Failure_Event']).sum()
v12_fp = (df['V12_alarm'] & ~df['Failure_Event']).sum()
print(f"\nFalse Positives:")
print(f"  Classical: {classical_fp}")
print(f"  V12:       {v12_fp}")
print(f"  Δ:         {v12_fp - classical_fp}")

# Save results
df.to_csv('v12_grid_results.csv', index=False)
print("\n✅ Saved results to v12_grid_results.csv")
