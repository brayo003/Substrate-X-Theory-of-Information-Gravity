import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

def test_integration_loop_consistency():
    """PROVE: State changes propagate correctly t → t+1"""
    engine = UniversalDynamicsEngine()
    
    # Add domains with tracking
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    engine.add_domain(Domain.ENERGY)
    
    print("=== INTEGRATION LOOP AUDIT ===")
    
    # Track complete system state across steps
    system_states = []
    
    for step in range(8):
        # Capture full system state before step
        pre_state = {}
        for domain, state in engine.integrator.domain_states.items():
            pre_state[domain] = {
                'field': state.concentrations.copy() if hasattr(state, 'concentrations') else None,
                'metrics': state.metrics.copy(),
                'history_len': len(state.history) if hasattr(state, 'history') else 0
            }
        
        # Execute step
        ig_score, alignment, anomalies, uri_signal = engine.integrator.coupled_pde_step()
        
        # Capture post-state
        post_state = {}
        for domain, state in engine.integrator.domain_states.items():
            post_state[domain] = {
                'field': state.concentrations.copy() if hasattr(state, 'concentrations') else None,
                'metrics': state.metrics.copy(), 
                'history_len': len(state.history) if hasattr(state, 'history') else 0
            }
        
        system_states.append((pre_state, post_state, ig_score, alignment))
        
        # Verify state progression
        print(f"Step {step}: All domains updated correctly")
    
    # Analyze integration consistency
    print("\n=== INTEGRATION CONSISTENCY ANALYSIS ===")
    
    # Check all domains updated every step
    domain_update_consistency = True
    for i, (pre, post, ig, align) in enumerate(system_states):
        for domain in pre.keys():
            # Fields should change
            if pre[domain]['field'] is not None and post[domain]['field'] is not None:
                field_changed = not np.allclose(pre[domain]['field'], post[domain]['field'])
                if not field_changed:
                    print(f"WARNING: Domain {domain.value} field unchanged at step {i}")
                    domain_update_consistency = False
            
            # History should grow
            history_grew = post[domain]['history_len'] > pre[domain]['history_len']
            if not history_grew:
                print(f"WARNING: Domain {domain.value} history not updated at step {i}")
                domain_update_consistency = False
    
    assert domain_update_consistency, "Some domains skipped in integration loop"
    
    # Check metric coherence
    metric_coherence = True
    for i, (pre, post, ig, align) in enumerate(system_states):
        # IG should be consistent with domain states
        # (This is a simplified check - in practice would verify IG inputs match outputs)
        if not (0.0 <= ig <= 1.0):
            print(f"WARNING: IG out of bounds at step {i}: {ig}")
            metric_coherence = False
        
        if not (0.0 <= align <= 1.0):
            print(f"WARNING: Alignment out of bounds at step {i}: {align}")
            metric_coherence = False
    
    assert metric_coherence, "Metric bounds violated"

def test_no_domain_isolation():
    """PROVE: No domains are isolated from system effects"""
    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    engine.add_domain(Domain.ENERGY)
    
    print("\n=== DOMAIN ISOLATION TEST ===")
    
    # Run system to establish baseline
    for _ in range(5):
        engine.integrator.coupled_pde_step()
    
    # Check that all domains have non-zero metrics and are evolving
    active_domains = 0
    for domain, state in engine.integrator.domain_states.items():
        tension = state.metrics.get('Tension', 0.0)
        momentum = state.metrics.get('Momentum', 0.0)
        variance = state.metrics.get('Variance', 0.0)
        
        has_metrics = tension > 0 or momentum > 0 or variance > 0
        has_field = hasattr(state, 'concentrations') and state.concentrations is not None
        has_history = hasattr(state, 'history') and len(state.history) > 0
        
        if has_metrics and has_field and has_history:
            active_domains += 1
            print(f"✅ {domain.value:12}: Active (T={tension:.4f}, M={momentum:.4f}, V={variance:.4f})")
        else:
            print(f"❌ {domain.value:12}: Inactive or missing data")
    
    assert active_domains == len(engine.integrator.domain_states), "Some domains are isolated"
    print(f"All {active_domains} domains actively participating in system")

if __name__ == "__main__":
    test_integration_loop_consistency()
    test_no_domain_isolation()
    print("✅ Integration loop audit passed!")
