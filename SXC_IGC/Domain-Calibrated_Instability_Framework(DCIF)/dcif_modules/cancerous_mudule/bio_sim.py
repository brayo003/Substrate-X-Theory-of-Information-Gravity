import numpy as np
import matplotlib.pyplot as plt
from v12_engine import SXCOmegaEngine

def run_homeostatic_simulation():
    # Initialize V12 Engine
    engine = SXCOmegaEngine(beta=3.5, gamma=0.8)
    
    steps = 200
    t_sys_history = []
    signal_history = []
    phase_history = []
    
    # Simulation Parameters
    homeostasis_strength = 0.9  # Initial ability to pull signal back to 0
    stress_intensity = 5.0      # Magnitude of external noise
    
    print(f"STARTING SIMULATION: Homeostatic Stress Test")
    print("-" * 50)
    
    current_signal = 0.0
    for i in range(steps):
        # 1. Stochastic Pressure (External Stress)
        noise = np.random.normal(0, stress_intensity)
        current_signal += noise
        
        # 2. Homeostatic Correction (Regulation)
        # As simulation progresses, regulation weakens (fatigue)
        current_regulation = homeostasis_strength * (1 - (i / (steps * 1.2)))
        current_signal *= (1 - current_regulation)
        
        # 3. DCIF Observation
        # Use absolute value of fluctuation as the 'Tension' signal
        abs_signal = abs(current_signal)
        t_sys, phase = engine.step(abs_signal)
        
        # Record
        signal_history.append(abs_signal)
        t_sys_history.append(t_sys)
        phase_history.append(1 if phase == "FIREWALL" else 0)
        
        if i % 20 == 0:
            print(f"Step {i:03d} | Signal: {abs_signal:6.2f} | T_SYS: {t_sys:6.4f} | Phase: {phase}")

    return signal_history, t_sys_history, phase_history

if __name__ == "__main__":
    s, t, p = run_homeostatic_simulation()
    
    # Logic Check: Did FIREWALL happen only when the signal became unrecoverable?
    firewall_start = next((i for i, val in enumerate(p) if val == 1), None)
    if firewall_start:
        print(f"\n[INVARIANT CHECK]: FIREWALL detected at Step {firewall_start}")
    else:
        print("\n[INVARIANT CHECK]: System remained NOMINAL.")
