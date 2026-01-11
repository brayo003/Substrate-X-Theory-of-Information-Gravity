import numpy as np

class CosmologyV12:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma = 0.0548  # Cosmology calibration
        self.beta = 0.8183   # Cosmology calibration
        self.dt = 0.05
        self.decay_rate = 0.0005
        
    def excitation_flux(self, signal):
        signal = min(signal, 1000)
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

# Test NGC 2403
engine = CosmologyV12()
radii = [0.30, 0.61, 0.91, 1.22, 1.52, 1.83, 2.13, 2.44, 2.74, 3.05, 4.00, 5.00, 7.00, 10.00, 15.00, 20.00]
v_bar = [12.4, 25.6, 38.5, 48.5, 55.9, 61.9, 66.7, 70.7, 73.8, 76.6, 83.2, 87.8, 94.8, 102.7, 109.5, 113.8]
v_obs = [45.2, 68.4, 85.1, 92.5, 98.7, 103.2, 107.5, 110.8, 114.1, 117.2, 125.4, 128.9, 131.2, 133.5, 134.1, 134.5]

print("Radius | V_bar | Tension | V_SXC | V_obs")
print("----------------------------------------")
for i in range(len(radii)):
    accel_signal = v_bar[i]**2 / max(radii[i], 0.1)
    tension, phase = engine.step(accel_signal)
    
    # Velocity conversion: K optimized from earlier
    K = 12.5
    v_sxc = np.sqrt(v_bar[i]**2 * (1 + K * tension))
    
    print(f"{radii[i]:6.2f} | {v_bar[i]:6.1f} | {tension:8.4f} | {v_sxc:6.1f} | {v_obs[i]:6.1f}")
