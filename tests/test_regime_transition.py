import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

def test_regime_transition_recovery():
    """
    ULIMATE TEST: Prove the system can transition from Low Volatility → High Volatility 
    and successfully recover using Dynamic Pressure Feedback.
    """
    # Initialize engine. (Assuming the noise_std property exists)
    engine = UniversalDynamicsEngine()
    
    # Define controlled noise levels
    LOW_NOISE = 0.005
    HIGH_NOISE = 0.5 
    
    # Setup state tracking and domains
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    engine.add_domain(Domain.ENERGY)
    
    # Initialize noise to baseline level (Direct property assignment)
    engine.integrator.noise_std = LOW_NOISE

    # Helper to get metrics from a single step
    def get_metrics():
        ig, align, anomalies, uri = engine.integrator.coupled_pde_step()
        all_tensions = np.array([s.metrics.get('Tension', 0.0) for s in engine.integrator.domain_states.values()])
        avg_tension = all_tensions.mean()
        # FIX: Access Pressure via the metrics dictionary, not a direct attribute
        pressure = engine.integrator.domain_states[Domain.BIO_PHYSICS].metrics.get("Pressure", 0.0)
        return ig, align, avg_tension, pressure, anomalies
    
    # --- PHASE 1: LOW VOLATILITY BASELINE ---
    print("\n--- PHASE 1: LOW VOLATILITY BASELINE ---")
    baseline_tensions = []
    baseline_pressures = []
    for _ in range(50):
        _, _, avg_tension, pressure, _ = get_metrics()
        baseline_tensions.append(avg_tension)
        baseline_pressures.append(pressure)

    baseline_tension = np.mean(baseline_tensions[-20:])
    baseline_pressure = np.mean(baseline_pressures[-20:])
    
    print(f"Baseline Tension: {baseline_tension:.4f}, Pressure: {baseline_pressure:.4f}")
    
    # --- PHASE 2: SUSTAINED HIGH VOLATILITY STRESS INJECTION ---
    print("\n--- PHASE 2: SUSTAINED HIGH VOLATILITY STRESS INJECTION ---")
    # Inject sustained external stress by increasing noise (Direct property assignment)
    engine.integrator.noise_std = HIGH_NOISE

    stress_tensions = []
    stress_pressures = []
    
    # Run for 30 steps to force pressure mechanism to engage
    for _ in range(30):
        _, _, avg_tension, pressure, _ = get_metrics()
        stress_tensions.append(avg_tension)
        stress_pressures.append(pressure)

    peak_tension = np.max(stress_tensions)
    peak_pressure = np.max(stress_pressures)
    
    print(f"Peak Stress Tension: {peak_tension:.4f}, Peak Pressure: {peak_pressure:.4f}")

    # Assert 1: Stress successfully forced a regime change (Tension and Pressure rise)
    assert peak_tension > baseline_tension * 5.0, f"Stress failed to create High Volatility. Peak Tension: {peak_tension:.4f} (Baseline: {baseline_tension:.4f})"
    assert peak_pressure > baseline_pressure * 1.05, f"Pressure failed to rise significantly. Peak Pressure: {peak_pressure:.4f} (Baseline: {baseline_pressure:.4f})"

    # --- PHASE 3: RECOVERY VIA DYNAMIC PRESSURE FEEDBACK ---
    print("\n--- PHASE 3: RECOVERY VIA DYNAMIC PRESSURE FEEDBACK ---")
    # Remove external stress by restoring baseline noise (Direct property assignment)
    engine.integrator.noise_std = LOW_NOISE

    recovery_tensions = []
    # Run for 100 steps to allow feedback to stabilize
    for _ in range(100):
        _, _, avg_tension, _, _ = get_metrics()
        recovery_tensions.append(avg_tension)

    final_tension = np.mean(recovery_tensions[-20:])
    
    print(f"Final Recovered Tension: {final_tension:.4f}")

    # Assert 2: System successfully recovered tension to baseline
    assert final_tension < baseline_tension * 1.5, f"Recovery failed: Final tension {final_tension:.4f} is too high (Baseline: {baseline_tension:.4f})"

    print("\n✅ ULTIMATE REGIME TRANSITION VALIDATED! System is self-regulating.")
