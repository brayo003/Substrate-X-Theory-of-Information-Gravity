import numpy as np
import matplotlib.pyplot as plt

class SXCOmegaEngine:
    def __init__(self):
        self.alpha = 1.254
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.beta = 0.4
        self.dt = 0.05
        self.decay_rate = 0.05 
        
    def excitation_flux(self, signal):
        # Sigmoid squash to prevent input-driven divergence
        return 1 / (1 + np.exp(-(signal - 45) / 10))

    def step(self, signal):
        self.gamma *= (1 - self.decay_rate)
        E = self.excitation_flux(signal)
        
        # Alpha scaling applied to outflow resistance
        gamma_eff = (5.5 * self.alpha) if self.phase == "FIREWALL" else self.alpha
        
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        
        # The Delta-T calculation
        self.T_sys += (inflow - outflow) * self.dt
        
        # Hard Physical Limit (The Substrate Bound)
        self.T_sys = np.clip(self.T_sys, 0, 1.5)
        
        if self.T_sys > 1.0:
            self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4:
            self.phase = "NOMINAL"
            
        return self.T_sys, self.phase

def test_shear_behavior():
    """Test engine response to different shear rates"""
    print("=== Testing Non-Newtonian Fluid Behavior ===")
    
    shear_rates = np.linspace(0.1, 100, 50)  # Range of shear rates (s⁻¹)
    viscosity_values = []
    phases = []
    
    for shear_rate in shear_rates:
        engine = SXCOmegaEngine()
        signal = shear_rate * 10  # Scale appropriately
        
        # Let system stabilize for 100 steps
        for _ in range(100):
            T_sys, phase = engine.step(signal)
        
        viscosity = T_sys  # Effective viscosity ≈ T_sys
        viscosity_values.append(viscosity)
        phases.append(phase)
        
        print(f"Shear rate: {shear_rate:.1f} s⁻¹ → Viscosity: {viscosity:.3f}, Phase: {phase}")
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(shear_rates, viscosity_values, 'b-', linewidth=2)
    plt.xlabel('Shear Rate (s⁻¹)', fontsize=12)
    plt.ylabel('Apparent Viscosity', fontsize=12)
    plt.title('Non-Newtonian Flow Curve from SXC-IGC Engine', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    plt.xscale('log')
    
    # Mark phase transitions
    for i, phase in enumerate(phases):
        if phase == "FIREWALL" and (i == 0 or phases[i-1] == "NOMINAL"):
            plt.axvline(x=shear_rates[i], color='r', linestyle='--', alpha=0.5, label='Phase Transition')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig('non_newtonian_curve.png', dpi=150)
    plt.show()
    
    print(f"\n=== Results Summary ===")
    print(f"At low shear (0.1 s⁻¹): viscosity = {viscosity_values[0]:.3f}")
    print(f"At high shear (100 s⁻¹): viscosity = {viscosity_values[-1]:.3f}")
    print(f"Viscosity ratio (low/high): {viscosity_values[0]/viscosity_values[-1]:.1f}x")
    
    # Classify the fluid type
    if viscosity_values[-1] < viscosity_values[0]:
        print("→ Fluid shows SHEAR-THINNING behavior (pseudoplastic)")
    elif viscosity_values[-1] > viscosity_values[0]:
        print("→ Fluid shows SHEAR-THICKENING behavior (dilatant)")
    else:
        print("→ Fluid shows NEWTONIAN behavior")

if __name__ == "__main__":
    test_shear_behavior()
