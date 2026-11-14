import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load Boston Substrate
df = pd.read_csv("boston_311.csv")
df["open_date"] = pd.to_datetime(df["open_date"], utc=True, format="mixed")
df = df.sort_values("open_date")

# Define Weights for the Biological Substrate
# Wild Animal issues are 'heavier' than domestic as they represent untracked entropy
def get_bio_mass(row):
    topic = str(row['case_topic'])
    if 'Wild Animal' in topic: return 5.0
    if 'Domestic Animal' in topic: return 3.0
    if 'Tree' in topic or 'Pruning' in topic: return 1.0
    return 0.1

df['signal_mass'] = df.apply(get_bio_mass, axis=1)

# ================== V12 OMEGA ENGINE ==================
class BostonBioOmega:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.beta = 0.5  # Sensitivity to bio-pulses
        self.decay = 0.03 # Natural 'healing' rate of the urban ecosystem
        
    def step(self, mass):
        # Tension builds with signal mass and decays naturally
        self.T_sys = (self.T_sys + (mass * self.beta)) * (1 - self.decay)
        
        if self.T_sys > 1.5:
            self.phase = "FIREWALL" # Biological Saturation
        elif self.T_sys < 0.5:
            self.phase = "NOMINAL"
        return self.T_sys, self.phase

engine = BostonBioOmega()
results = [engine.step(m) for m in df['signal_mass']]
df['T_sys'], df['phase'] = zip(*results)

print("\n=== BOSTON BIOLOGICAL SUBSTRATE ANALYSIS ===")
print(f"Peak System Tension (T_sys): {df['T_sys'].max():.2f}")
print(f"Hours in FIREWALL Phase: {len(df[df['phase'] == 'FIREWALL'])}")

# Identify High-Gravity Moments
print("\nTop 5 Biological Fracture Points:")
print(df.nlargest(5, 'T_sys')[['open_date', 'case_topic', 'T_sys']])

# Plotting the Tension
plt.figure(figsize=(12, 6))
plt.plot(df['open_date'], df['T_sys'], color='red', label='System Tension (T_sys)')
plt.axhline(y=1.5, color='black', linestyle='--', label='Fracture Threshold')
plt.title('Boston Substrate X: Biological Instability (2025-2026)')
plt.ylabel('T_sys (Information Gravity)')
plt.legend()
plt.savefig('boston_bio_tension.png')
print("\n✅ Analysis complete. Tension plot saved to boston_bio_tension.png")
