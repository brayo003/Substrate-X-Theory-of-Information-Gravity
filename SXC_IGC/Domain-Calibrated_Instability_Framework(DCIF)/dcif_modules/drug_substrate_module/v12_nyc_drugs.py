import pandas as pd
import numpy as np

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

# ================== LOAD NYC DRUG DATA ==================
df = pd.read_csv('nyc_311_sample_10k.csv')
df['created_date'] = pd.to_datetime(df['created_date'])
df = df.sort_values('created_date').reset_index(drop=True)

print("=== NYC DRUG SUBSTRATE: FULL V12 ANALYSIS ===")
print(f"Total records: {len(df)}")
print(f"Date range: {df['created_date'].min()} to {df['created_date'].max()}")

# ================== IDENTIFY DECAY SIGNALS ==================
decay_keywords = 'drug|needle|syringe|graffiti|encampment|abandoned|vacant|noise|party|unsanitary'
df['is_decay'] = df['complaint_type'].str.contains(decay_keywords, case=False, na=False).fillna(False)

decay_signals = df[df['is_decay']]
print(f"\nDecay signals found: {len(decay_signals)} ({len(decay_signals)/len(df)*100:.1f}%)")
print("\nDecay signal types:")
print(decay_signals['complaint_type'].value_counts().head(10))

# ================== GROUP BY DAY FOR SIGNAL ==================
daily = df.groupby(df['created_date'].dt.date).agg({
    'is_decay': 'sum',
    'complaint_type': 'count'
}).rename(columns={'complaint_type': 'total_complaints'}).reset_index()
daily.columns = ['date', 'decay_count', 'total_complaints']
daily['signal'] = (daily['decay_count'] / daily['decay_count'].max()) * 100

print(f"\nDays analyzed: {len(daily)}")
print(f"Decay range: {daily['decay_count'].min()} to {daily['decay_count'].max()} per day")

# ================== RUN V12 ==================
engine = SXCOmegaEngine()
T_values = []
phase_values = []

for idx, row in daily.iterrows():
    T, phase = engine.step(row['signal'])
    T_values.append(T)
    phase_values.append(phase)

daily['T_sys'] = T_values
daily['phase'] = phase_values

print("\n=== V12 RESULTS ===")
print(f"T_sys range: {daily['T_sys'].min():.2f} to {daily['T_sys'].max():.2f}")
print(f"FIREWALL days: {(daily['phase'] == 'FIREWALL').sum()}")
print(f"FIREWALL %: {((daily['phase'] == 'FIREWALL').sum() / len(daily)) * 100:.1f}%")

# ================== FRACTURE POINTS ==================
fractures = daily[daily['T_sys'] > 1.0]
print(f"\nFracture days (T_sys > 1.0): {len(fractures)}")
if not fractures.empty:
    print("\nTop fracture days:")
    print(fractures.nlargest(5, 'T_sys')[['date', 'decay_count', 'T_sys', 'phase']])

# ================== K METRIC ==================
# K = current decay / historical max decay for that day of week? 
# Or simpler: K = decay_count / max_decay_overall
daily['K'] = daily['decay_count'] / daily['decay_count'].max()
print(f"\nK range: {daily['K'].min():.3f} to {daily['K'].max():.3f}")
print(f"Days with K > 0.5: {(daily['K'] > 0.5).sum()} ({(daily['K'] > 0.5).sum()/len(daily)*100:.1f}%)")

# ================== SAVE RESULTS ==================
daily.to_csv('nyc_drug_v12_results.csv', index=False)
print("\n✅ Saved results to nyc_drug_v12_results.csv")

# ================== QUICK SUMMARY ==================
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"Total decay signals: {len(decay_signals)}")
print(f"Peak T_sys: {daily['T_sys'].max():.2f}")
print(f"FIREWALL prevalence: {((daily['phase'] == 'FIREWALL').sum() / len(daily)) * 100:.1f}%")
print(f"K > 0.5 prevalence: {(daily['K'] > 0.5).sum() / len(daily) * 100:.1f}%")
