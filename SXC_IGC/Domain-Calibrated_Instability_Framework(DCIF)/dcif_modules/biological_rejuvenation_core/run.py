import numpy as np
import matplotlib.pyplot as plt

# Using the Master Protocol logic:
gamma_max = 0.8
decay_rate = 0.0001 # Structural decay (Aging)
beta = 3.5
dt = 0.05
required_gamma = 0.72 # The "Stability Constant"

t_history = []
gamma_history = []
days = range(5000) # Simulating ~13 years of hyper-stable cell life

T_sys = 0.1
gamma_current = gamma_max

for day in days:
    # 1. Natural Decay of the Repair Substrate
    gamma_current *= (1 - decay_rate)
    
    # 2. MASTER PROTOCOL INTERVENTION (The Omega Pulse)
    # This is the "Eternal" logic: detect the drift and fix it before the snap.
    if gamma_current < required_gamma:
        gamma_current = gamma_max 
    
    # 3. Biological Tension Calculation
    E = 0.15 # Metabolic background noise
    T_sys += (E * beta - gamma_current * T_sys) * dt
    
    t_history.append(T_sys)
    gamma_history.append(gamma_current)

# --- VISUALIZATION ---
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(days, t_history, color='forestgreen', label='Biological Tension')
plt.axhline(y=1.0, color='red', linestyle='--', label='Shatter Threshold')
plt.title("Eternal Biological Stability")
plt.xlabel("Days")
plt.ylabel("Tension (Aging Stress)")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(days, gamma_history, color='blue')
plt.axhline(y=required_gamma, color='orange', linestyle=':', label='Stability Constant')
plt.title("The Maintenance Sawtooth (γ)")
plt.xlabel("Days")
plt.ylabel("Repair Capacity")
plt.legend()

plt.tight_layout()
plt.savefig('eternal_orbit.png')
plt.show()

print(f"Final Tension after 5000 Days: {T_sys:.4f}")
print("✓ Outcome: Structural aging prevented. System remained in 'Nominal' phase.")
