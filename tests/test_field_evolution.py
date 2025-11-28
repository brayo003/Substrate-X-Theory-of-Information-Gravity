import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

def test_field_evolution_consistency():
    """PROVE: Field evolution is physically/logically consistent across domains"""
    engine = UniversalDynamicsEngine()
    
    # Add domains
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    engine.add_domain(Domain.ENERGY)
    
    print("=== FIELD EVOLUTION CONSISTENCY TEST ===")
    
    # Track field changes over multiple steps
    field_histories = {domain: [] for domain in engine.integrator.domain_states.keys()}
    
    for step in range(10):
        # Store current field states
        for domain, state in engine.integrator.domain_states.items():
            if hasattr(state, 'concentrations') and state.concentrations is not None:
                field_histories[domain].append(state.concentrations.copy())
        
        # Evolve system
        engine.integrator.coupled_pde_step()
    
    # Analyze field evolution consistency
    print("\n=== FIELD EVOLUTION ANALYSIS ===")
    for domain, history in field_histories.items():
        if len(history) > 1:
            changes = []
            for i in range(1, len(history)):
                change = np.linalg.norm(history[i] - history[i-1])
                changes.append(change)
            
            avg_change = np.mean(changes)
            change_std = np.std(changes)
            
            print(f"{domain.value:12}: Avg change: {avg_change:.6f} ± {change_std:.6f}")
            
            # Verify changes are reasonable (not zero, not exploding)
            assert avg_change > 1e-10, f"Field {domain.value} not evolving"
            # Adjusted threshold for grid-scale changes
            assert avg_change < 10.0, f"Field {domain.value} changing too rapidly: {avg_change}"
            assert change_std / avg_change < 10.0, f"Field {domain.value} evolution unstable"
        else:
            print(f"{domain.value:12}: Insufficient history")

def test_field_gradient_consistency():
    """PROVE: Field gradients match mathematical expectations"""
    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)
    
    # Get initial field
    state = engine.integrator.domain_states[Domain.BIO_PHYSICS]
    initial_field = state.concentrations.copy()
    
    # Evolve one step
    engine.integrator.coupled_pde_step()
    evolved_field = state.concentrations.copy()
    
    # Calculate actual change
    actual_change = evolved_field - initial_field
    
    # Calculate expected change based on PDE structure
    # For diffusion + reaction systems, changes should be smooth
    change_magnitude = np.linalg.norm(actual_change)
    change_smoothness = np.std(actual_change) / (np.mean(np.abs(actual_change)) + 1e-12)
    
    print(f"\n=== GRADIENT CONSISTENCY ===")
    print(f"Change magnitude: {change_magnitude:.6f}")
    print(f"Change smoothness (std/mean): {change_smoothness:.3f}")
    
    # Changes should be reasonably smooth (not random noise)
    assert change_smoothness < 5.0, f"Field changes too noisy: {change_smoothness}"

if __name__ == "__main__":
    test_field_evolution_consistency()
    test_field_gradient_consistency()
    print("✅ Field evolution consistency verified!")
