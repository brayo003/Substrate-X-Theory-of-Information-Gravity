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

# ================== LOAD DATA ==================
df = pd.read_csv("nyc_311_sample_10k.csv")
print(f"Loaded {len(df)} records")

# Convert created_date to datetime
df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
df = df.dropna(subset=["created_date"])
df = df.sort_values("created_date").reset_index(drop=True)

# Group by day
daily = df.groupby(df["created_date"].dt.date).size().reset_index()
daily.columns = ["date", "complaints"]
daily["signal"] = (daily["complaints"] / daily["complaints"].max()) * 100

# Run V12 engine
engine = SXCOmegaEngine()
T_values = []
phase_values = []

for idx, row in daily.iterrows():
    T, phase = engine.step(row["signal"])
    T_values.append(T)
    phase_values.append(phase)

daily["T_sys"] = T_values
daily["phase"] = phase_values

# Results
print("\n=== URBAN SUBSTRATE RESULTS ===")
print(f"Days analyzed: {len(daily)}")
print(f"T_sys range: {daily['T_sys'].min():.2f} to {daily['T_sys'].max():.2f}")
print(f"FIREWALL days: {(daily['phase'] == 'FIREWALL').sum()}")
firewall_pct = (daily['phase'] == 'FIREWALL').sum() / len(daily) * 100
print(f"FIREWALL %: {firewall_pct:.1f}%")

# Show last few days
print("\nLast 5 days:")
print(daily[["date", "complaints", "T_sys", "phase"]].tail())
