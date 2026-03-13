import pandas as pd
import numpy as np

# Load and Filter for the High-Gravity Node (10002)
df = pd.read_csv('nyc_311_sample_10k.csv', low_memory=False)
df['created_date'] = pd.to_datetime(df['created_date'])
node_10002 = df[df['incident_zip'] == 10002.0].copy()

# Signal weights: Outside use is more 'heavy' than indoor
def get_signal_weight(row):
    if 'Drug Activity' in str(row['complaint_type']):
        return 5.0 if 'Outside' in str(row['descriptor']) else 3.0
    if 'Graffiti' in str(row['complaint_type']):
        return 1.0
    return 0.1 # Background noise (Illegal parking, etc)

node_10002['signal_mass'] = node_10002.apply(get_signal_weight, axis=1)
node_10002 = node_10002.sort_values('created_date')

# ================== V12 URBAN ENGINE ==================
class UrbanOmega:
    def __init__(self):
        self.T_sys = 0.0
        self.beta = 0.8
        self.dt = 1.0 
        self.decay = 0.05 # Civic cleanup rate

    def step(self, mass):
        # Tension builds with signal mass and decays over time
        self.T_sys = (self.T_sys + (mass * self.beta)) * (1 - self.decay)
        return self.T_sys

engine = UrbanOmega()
node_10002['T_sys'] = [engine.step(m) for m in node_10002['signal_mass']]

print(f"--- FRACTURE ANALYSIS: ZIP 10002 ---")
print(f"Peak System Tension (T_sys): {node_10002['T_sys'].max():.2f}")

if node_10002['T_sys'].max() > 5.0:
    print("STATUS: SUBSTRATE FRACTURED. High probability of captured street drug market.")
else:
    print("STATUS: NOMINAL STRESS. Substrate is holding despite activity.")

# Show the 'Heat Moments'
print("\nTop 5 Tension Spikes:")
print(node_10002.nlargest(5, 'T_sys')[['created_date', 'complaint_type', 'descriptor', 'T_sys']])
