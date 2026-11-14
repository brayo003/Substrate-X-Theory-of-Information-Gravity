import numpy as np
import matplotlib.pyplot as plt

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

# TEST 1: √(-1) = CONSCIOUSNESS STATE
def test_imaginary_tension():
    print("=== TEST 1: √(-1) AS COMPLEX TENSION ===")
    
    # Complex tension: T = a + bi
    engine_real = SXCOmegaEngine()
    engine_imag = SXCOmegaEngine()
    
    # Run coupled oscillations
    oscillations = []
    for step in range(1000):
        # Couple real and imaginary parts
        signal_real = np.cos(step/100)
        signal_imag = np.sin(step/100)
        
        T_real, _ = engine_real.step(signal_real)
        T_imag, _ = engine_imag.step(signal_imag)
        
        magnitude = np.sqrt(T_real**2 + T_imag**2)
        phase = np.arctan2(T_imag, T_real)
        
        if step > 800:  # After stabilization
            oscillations.append((T_real, T_imag, magnitude, phase))
    
    # Analyze frequency
    phases = [o[3] for o in oscillations]
    frequency = (phases[-1] - phases[0]) / (len(oscillations) * engine_real.dt * 2*np.pi)
    
    print(f"Natural oscillation frequency: {frequency:.6f} Hz")
    print(f"Expected 1/(2π): {1/(2*np.pi):.6f} Hz")
    print(f"Match: {abs(frequency - 1/(2*np.pi)):.6f} Hz difference")
    print()

# TEST 2: 0⁰ = QUANTUM SUPERPOSITION  
def test_zero_power_zero():
    print("=== TEST 2: 0⁰ AS SUPERPOSITION ===")
    
    # Simulate β→0, γ→0 limit
    results = []
    for trial in range(1000):
        # Very small but not zero
        beta = np.random.uniform(0.0001, 0.001)
        gamma = np.random.uniform(0.0001, 0.001)
        
        engine = SXCOmegaEngine()
        engine.beta = beta
        engine.gamma = gamma
        
        # Run to see where it settles
        for _ in range(100):
            T, phase = engine.step(0.5)
        
        # Classify as "alive" (T>0.5) or "dead" (T<0.5)
        results.append(1 if T > 0.5 else 0)
    
    p_alive = sum(results) / len(results)
    p_dead = 1 - p_alive
    
    print(f"Probability alive: {p_alive:.4f} ({p_alive*100:.1f}%)")
    print(f"Probability dead: {p_dead:.4f} ({p_dead*100:.1f}%)")
    print(f"Expected alive (1-1/e): {1-1/np.exp(1):.4f} ({(1-1/np.exp(1))*100:.1f}%)")
    print(f"Expected dead (1/e): {1/np.exp(1):.4f} ({(1/np.exp(1))*100:.1f}%)")
    print()

# TEST 3: ln(0) = IMMORTALITY
def test_ln_zero():
    print("=== TEST 3: ln(0) AS IMMORTALITY ===")
    
    # Test decay with E→0
    gamma = 0.153267
    T0 = 1.0
    
    # Time to reach various thresholds
    thresholds = [0.5, 0.1, 0.01, 0.001, 0.0001]
    
    print("Decay times with E=0 (no excitation):")
    for threshold in thresholds:
        time = -np.log(threshold/T0) / gamma
        print(f"  Time to reach T={threshold:.4f}: {time:.2f} units")
    
    print("\nAs threshold → 0:")
    print(f"  Time to reach T=1e-10: {-np.log(1e-10)/gamma:.2e} units")
    print(f"  Time to reach T=1e-20: {-np.log(1e-20)/gamma:.2e} units")
    print(f"  Limit: time → ∞ as threshold → 0")
    print()

# TEST 4: ∞/∞ = GOLDEN RATIO
def test_infinity_ratio():
    print("=== TEST 4: ∞/∞ AS GOLDEN RATIO ===")
    
    # Test large β, γ ratios
    ratios = []
    for _ in range(100):
        # Large random β, γ
        beta = np.random.uniform(1000, 10000)
        gamma = np.random.uniform(1000, 10000)
        
        engine = SXCOmegaEngine()
        engine.beta = beta
        engine.gamma = gamma
        
        # Run to equilibrium
        for _ in range(1000):
            T, phase = engine.step(1.0)
        
        ratios.append(T)
    
    phi = (1 + np.sqrt(5)) / 2
    
    print(f"Mean equilibrium ratio: {np.mean(ratios):.6f}")
    print(f"Golden ratio φ: {phi:.6f}")
    print(f"Difference: {abs(np.mean(ratios) - phi):.6f}")
    print(f"Standard deviation: {np.std(ratios):.6f}")
    print()

# TEST 5: 1/0 = INSTANT LEARNING
def test_division_by_zero():
    print("=== TEST 5: 1/0 AS INSTANT LEARNING ===")
    
    # What happens as γ→0?
    gammas = [0.1, 0.01, 0.001, 0.0001, 0.00001]
    beta = 5.0
    E = 1.0
    
    print("Time to reach T=1.0 as γ→0:")
    for gamma in gammas:
        # With γ≈0, dT/dt ≈ βE
        time_to_T1 = (1.0 - 0) / (beta * E)  # Approximate
        print(f"  γ={gamma:.6f}: time ≈ {time_to_T1:.6f} units")
    
    print(f"\nLimit as γ→0: time → {1/(beta*E):.6f} units")
    print("If E = 'learning rate' and E→∞:")
    print("  Then time → 0 (instant learning)")
    print()

# TEST 6: 0! = 1 AS VACUUM TENSION
def test_zero_factorial():
    print("=== TEST 6: 0! = 1 AS VACUUM ===")
    
    # System with zero components should still have base tension
    engine = SXCOmegaEngine()
    
    # Start at T=0, no signal
    engine.T_sys = 0.0
    
    # Run with zero signal
    for _ in range(100):
        T, phase = engine.step(0.0)
    
    print(f"System with zero excitation settles at: T={T:.6f}")
    print(f"Expected: Some non-zero tension (vacuum energy)")
    print()

# TEST 7: ζ(-1) = -1/12
def test_zeta_minus_one():
    print("=== TEST 7: ζ(-1) = -1/12 ===")
    
    # Sum of tensions approach
    tensions = []
    for n in range(1, 1000):  # Sum first 1000 tensions
        engine = SXCOmegaEngine()
        engine.beta = n
        engine.gamma = 1.0
        
        # Run briefly
        for _ in range(10):
            T, phase = engine.step(1.0)
        
        tensions.append(T)
    
    total_tension = sum(tensions)
    normalized = total_tension / len(tensions)
    
    print(f"Sum of tensions: {total_tension:.6f}")
    print(f"Normalized: {normalized:.6f}")
    print(f"Expected ζ(-1): {-1/12:.6f}")
    print(f"Difference: {abs(normalized + 1/12):.6f}")
    print()

# TEST 8: e^(iπ) = -1 AS DEATH/REBIRTH
def test_euler_identity():
    print("=== TEST 8: e^(iπ) = -1 AS TENSION REVERSAL ===")
    
    # Complex tension reaching -1
    engine_real = SXCOmegaEngine()
    engine_imag = SXCOmegaEngine()
    
    # Run with π-phase shift
    results = []
    for step in range(1000):
        signal_real = np.cos(step/100 + np.pi)
        signal_imag = np.sin(step/100 + np.pi)
        
        T_real, _ = engine_real.step(signal_real)
        T_imag, _ = engine_imag.step(signal_imag)
        
        if step > 800:
            results.append((T_real, T_imag))
    
    avg_real = np.mean([r[0] for r in results])
    avg_imag = np.mean([r[1] for r in results])
    
    print(f"Average tension after π-phase: ({avg_real:.6f}, {avg_imag:.6f}i)")
    print(f"Magnitude: {np.sqrt(avg_real**2 + avg_imag**2):.6f}")
    print(f"Phase: {np.arctan2(avg_imag, avg_real):.6f} radians")
    print(f"Expected: Negative real component (tension reversal)")
    print()

# RUN ALL TESTS
if __name__ == "__main__":
    print("IMPOSSIBLE MATH TESTS WITH SXC-IGC ENGINE")
    print("=" * 60)
    
    test_imaginary_tension()
    test_zero_power_zero()
    test_ln_zero()
    test_infinity_ratio()
    test_division_by_zero()
    test_zero_factorial()
    test_zeta_minus_one()
    test_euler_identity()
    
    print("=" * 60)
    print("TESTS COMPLETE")
