import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

def test_regime_transition_recovery_fixed():
    """
    FIXED TEST: Force high-volatility stress using repeated coupled_pde_step calls
    and correctly track metrics to validate Dynamic Pressure Feedback.
    """
    engine = UniversalDynamicsEngine()
    
    # Setup domains
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    engine.add_domain(Domain.ENERGY)
    
    # Initialize baseline noise
    engine.integrator.noise_std = 0.005
    
    # Helper function for metrics
    def get_metrics():
        ig, align, anomalies, uri = engine.integrator.coupled_pde_step()
        all_tensions = np.array([s.metrics.get('Tension', 0.0) for s in engine.integrator.domain_states.values()])
        avg_tension = all_tensions.mean()
        pressure = np.mean([s.metrics.get('Pressure', 0.0) for s in engine.integrator.domain_states.values()])
        return ig, align, avg_tension, pressure, anomalies

    # PHASE 1: LOW VOLATILITY BASELINE
    baseline_tensions = []
    for _ in range(50):
        _, _, avg_tension, _, _ = get_metrics()
        baseline_tensions.append(avg_tension)
    baseline_tension = np.mean(baseline_tensions[-20:])
    print(f"Baseline Tension: {baseline_tension:.4f}")

    # PHASE 2: FORCE HIGH VOLATILITY
    engine.integrator.noise_std = 0.5
    stress_tensions = []
    for _ in range(50):
        _, _, avg_tension, _, _ = get_metrics()
        stress_tensions.append(avg_tension)
    
    peak_tension = np.max(stress_tensions)
    print(f"Peak Stress Tension: {peak_tension:.4f}")
    assert peak_tension > baseline_tension * 1.05, "High Volatility stress failed"

    # PHASE 3: RECOVERY
    engine.integrator.noise_std = 0.005
    recovery_tensions = []
    for _ in range(30):
        _, _, avg_tension, _, _ = get_metrics()
        recovery_tensions.append(avg_tension)
    
    recovered_tension = np.mean(recovery_tensions[-10:])
    print(f"Recovered Tension: {recovered_tension:.4f}")
    assert np.abs(recovered_tension - baseline_tension) < 0.01, "Recovery failed"

    print("\n✅ REGIME TRANSITION TEST PASSED: Engine self-regulates successfully!")
