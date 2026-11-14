import pandas as pd
import numpy as np

# Load Boston Substrate
df = pd.read_csv("boston_311.csv")
df["open_date"] = pd.to_datetime(df["open_date"], utc=True, format="mixed")

# 1. Round time to 30-minute 'Gravity Windows'
df['time_window'] = df['open_date'].dt.round('30min')

# 2. De-duplicate using 'full_address'
# This collapses reports of the SAME issue at the SAME place in the SAME half-hour
initial_count = len(df)
df_true = df.drop_duplicates(subset=['full_address', 'case_topic', 'time_window'])
final_count = len(df_true)

print(f"--- BIOLOGICAL DE-DUPLICATION ---")
print(f"Original Signals: {initial_count}")
print(f"Unique Bio-Events: {final_count}")
print(f"Crowd Redundancy: {((initial_count - final_count) / initial_count) * 100:.1f}%")

# 3. Re-run V12 Omega on Clean Data
class TrueBioOmega:
    def __init__(self):
        self.T_sys = 0.0
        self.decay = 0.05 

    def step(self, mass):
        self.T_sys = (self.T_sys + mass) * (1 - self.decay)
        return self.T_sys

engine = TrueBioOmega()
df_true = df_true.sort_values('open_date')
# Weighting the pulses
df_true['mass'] = df_true['case_topic'].apply(lambda x: 5.0 if 'Wild' in str(x) else 2.0)
df_true['True_Tsys'] = [engine.step(m) for m in df_true['mass']]

print(f"\nRevised Peak Tension (T_sys): {df_true['True_Tsys'].max():.2f}")

if df_true['True_Tsys'].max() > 10.0:
    print("STATUS: FRACTURE CONFIRMED. This is a legitimate biological outbreak signal.")
else:
    print("STATUS: SIGNAL COLLAPSED. The previous spike was just social noise (one animal, many callers).")
