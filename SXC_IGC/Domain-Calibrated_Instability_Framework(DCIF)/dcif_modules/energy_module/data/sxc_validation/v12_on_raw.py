
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score

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

# ================== LOAD RAW DATA ==================
print("="*60)
print("V12 ON RAW SUBSTRATE DATA")
print("="*60)

raw = pd.read_csv('outage_data/Outage_Dataset/eaglei_outages_2018_merged.csv')
events = pd.read_csv('outage_data/Outage_Dataset/eaglei_outages_with_events_2018.csv')

raw['start_time'] = pd.to_datetime(raw['start_time'])
events['start_time'] = pd.to_datetime(events['start_time'])

print(f"Raw records: {len(raw)}")
print(f"Event records: {len(events)}")
print(f"Raw date range: {raw['start_time'].min()} to {raw['start_time'].max()}")

# ================== CREATE FAILURE WINDOWS ==================
print("\nCreating failure windows...")
raw['Failure_Event'] = 0
event_times = events['start_time'].unique()

for et in event_times:
    mask = (raw['start_time'] >= et - pd.Timedelta(hours=6)) & \
           (raw['start_time'] <= et)
    raw.loc[mask, 'Failure_Event'] = 1

print(f"Positive samples (6h before events): {raw['Failure_Event'].sum()}")

# ================== RUN V12 ==================
print("\nRunning V12 across timeline...")

# Scale customers to V12 signal range (0-100)
max_customers = raw['max_customers'].max()
raw['signal'] = (raw['max_customers'] / max_customers) * 100

engine = SXCOmegaEngine()
T_values = []
phase_values = []

for idx, row in raw.iterrows():
    T, phase = engine.step(row['signal'])
    T_values.append(T)
    phase_values.append(phase)

raw['T_sys'] = T_values
raw['phase'] = phase_values
raw['alarm'] = (raw['T_sys'] > 0.8).astype(int)

print(f"T_sys range: {raw['T_sys'].min():.2f} to {raw['T_sys'].max():.2f}")
print(f"FIREWALL count: {(raw['phase'] == 'FIREWALL').sum()}")

# ================== EVALUATE ==================
print("\n" + "="*60)
print("RESULTS")
print("="*60)

# Classical threshold
threshold = raw['max_customers'].quantile(0.95)
raw['classical_alarm'] = (raw['max_customers'] > threshold).astype(int)

# Calculate metrics safely
classical_tp = (raw['classical_alarm'] & raw['Failure_Event']).sum()
classical_total_alarms = raw['classical_alarm'].sum()
failure_total = raw['Failure_Event'].sum()

v12_tp = (raw['alarm'] & raw['Failure_Event']).sum()
v12_total_alarms = raw['alarm'].sum()

print(f"\nClassical (max_customers > {threshold:.0f}):")
print(f"  ROC-AUC: {roc_auc_score(raw['Failure_Event'], raw['max_customers']):.4f}")
print(f"  Precision: {classical_tp/classical_total_alarms:.4f}" if classical_total_alarms > 0 else "  Precision: N/A")
print(f"  Recall: {classical_tp/failure_total:.4f}")

print(f"\nV12 (T_sys > 0.8):")
print(f"  ROC-AUC: {roc_auc_score(raw['Failure_Event'], raw['T_sys']):.4f}")
print(f"  Precision: {v12_tp/v12_total_alarms:.4f}" if v12_total_alarms > 0 else "  Precision: N/A")
print(f"  Recall: {v12_tp/failure_total:.4f}")

# Save
raw.to_csv('v12_on_raw_results.csv', index=False)
print("\n✅ Saved to v12_on_raw_results.csv")

# ================== PLOT ==================
plt.figure(figsize=(12, 6))
plt.plot(raw['start_time'][:1000], raw['max_customers'][:1000], label='Customers', alpha=0.5)
plt.plot(raw['start_time'][:1000], raw['T_sys'][:1000] * max_customers/100, label='T_sys (scaled)', alpha=0.7)
plt.legend()
plt.title('V12 on Raw Substrate (first 1000 points)')
plt.savefig('v12_raw_plot.png')
print("Plot saved to v12_raw_plot.png")
