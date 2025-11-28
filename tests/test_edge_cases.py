import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

def test_high_volatility_stress():
    """PROVE: Engine handles extreme volatility without breaking"""
    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    
    print("=== HIGH VOLATILITY STRESS TEST ===")
    
    # Artificially create high volatility by injecting noise
    for step in range(20):
        # Inject significant noise into fields
        for domain, state in engine.integrator.domain_states.items():
            if hasattr(state, 'concentrations') and state.concentrations is not None:
                noise = np.random.normal(0, 0.5, state.concentrations.shape)
                state.concentrations += noise
                state.concentrations = np.clip(state.concentrations, 0.0, 1.0)
        
        # Evolve system under stress
        ig_score, alignment, anomalies, uri_signal = engine.integrator.coupled_pde_step()
        
        # Verify no NaN or infinite values
        assert not np.isnan(ig_score), f"IG became NaN at step {step}"
        assert not np.isinf(ig_score), f"IG became infinite at step {step}"
        assert 0.0 <= ig_score <= 1.0, f"IG out of bounds at step {step}: {ig_score}"
        assert 0.0 <= alignment <= 1.0, f"Alignment out of bounds at step {step}: {alignment}"
        
        if step % 5 == 0:
            print(f"Step {step:2}: IG={ig_score:.4f}, Align={alignment:.4f}, Anomalies={len(anomalies)}")
    
    print("✅ High volatility handled without numerical issues")

def test_low_volatility_stability():
    """PROVE: Engine remains stable with near-constant inputs"""
    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    
    print("\n=== LOW VOLATILITY STABILITY TEST ===")
    
    # Force fields to be nearly constant
    for domain, state in engine.integrator.domain_states.items():
        if hasattr(state, 'concentrations') and state.concentrations is not None:
            state.concentrations = np.full_like(state.concentrations, 0.5)
    
    ig_scores = []
    alignments = []
    
    for step in range(15):
        ig_score, alignment, anomalies, uri_signal = engine.integrator.coupled_pde_step()
        
        ig_scores.append(ig_score)
        alignments.append(alignment)
        
        # Verify metrics remain bounded
        assert 0.0 <= ig_score <= 1.0, f"IG unstable with constant inputs: {ig_score}"
        assert 0.0 <= alignment <= 1.0, f"Alignment unstable with constant inputs: {alignment}"
    
    # Check stability (low variance in outputs)
    ig_std = np.std(ig_scores)
    align_std = np.std(alignments)
    
    print(f"IG stability (std): {ig_std:.6f}")
    print(f"Alignment stability (std): {align_std:.6f}")
    
    # With constant inputs, outputs should be very stable
    assert ig_std < 0.1, f"IG too variable with constant inputs: {ig_std}"
    assert align_std < 0.1, f"Alignment too variable with constant inputs: {align_std}"
    
    print("✅ Low volatility stability confirmed")

def test_boundary_conditions():
    """PROVE: Engine handles field values at boundaries (0.0 and 1.0)"""
    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)
    
    print("\n=== BOUNDARY CONDITION TEST ===")
    
    # Test minimum boundary (0.0)
    state = engine.integrator.domain_states[Domain.BIO_PHYSICS]
    state.concentrations = np.zeros_like(state.concentrations)
    
    ig_min, align_min, anomalies_min, _ = engine.integrator.coupled_pde_step()
    assert not np.isnan(ig_min), "IG became NaN at minimum boundary"
    assert not np.isinf(ig_min), "IG became infinite at minimum boundary"
    print(f"Min boundary: IG={ig_min:.4f}, Align={align_min:.4f}")
    
    # Test maximum boundary (1.0)  
    state.concentrations = np.ones_like(state.concentrations)
    
    ig_max, align_max, anomalies_max, _ = engine.integrator.coupled_pde_step()
    assert not np.isnan(ig_max), "IG became NaN at maximum boundary"
    assert not np.isinf(ig_max), "IG became infinite at maximum boundary"
    print(f"Max boundary: IG={ig_max:.4f}, Align={align_max:.4f}")
    
    print("✅ Boundary conditions handled correctly")

def test_single_domain_operation():
    """PROVE: Engine works correctly with only one domain"""
    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)  # Only one domain
    
    print("\n=== SINGLE DOMAIN OPERATION TEST ===")
    
    for step in range(10):
        ig_score, alignment, anomalies, uri_signal = engine.integrator.coupled_pde_step()
        
        # With one domain, alignment should be perfect (1.0)
        assert np.isclose(alignment, 1.0, atol=1e-6), f"Single domain alignment not 1.0: {alignment}"
        assert 0.0 <= ig_score <= 1.0, f"Single domain IG out of bounds: {ig_score}"
        
        if step % 3 == 0:
            print(f"Step {step}: IG={ig_score:.4f}, Align={alignment:.4f}")
    
    print("✅ Single domain operation verified")

if __name__ == "__main__":
    test_high_volatility_stress()
    test_low_volatility_stability()
    test_boundary_conditions()
    test_single_domain_operation()
    print("✅ All edge-case tests passed!")
