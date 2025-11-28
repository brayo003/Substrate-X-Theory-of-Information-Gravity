import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

def test_metric_propagation():
    """PROVE: Metric updates propagate correctly across domains"""
    engine = UniversalDynamicsEngine()
    
    # Add domains
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    engine.add_domain(Domain.ENERGY)
    
    print("=== METRIC PROPAGATION TEST ===")
    
    # Track metrics over steps
    metric_histories = {
        'tensions': [], 'alignments': [], 'ig_scores': []
    }
    
    for step in range(15):
        # Evolve and get metrics
        ig_score, alignment, anomalies, uri_signal = engine.integrator.coupled_pde_step()
        
        # Get domain tensions
        tensions = [state.metrics.get('Tension', 0.0) for state in engine.integrator.domain_states.values()]
        
        # Store metrics
        metric_histories['tensions'].append(tensions.copy())
        metric_histories['alignments'].append(alignment)
        metric_histories['ig_scores'].append(ig_score)
        
        if step % 5 == 0:
            print(f"Step {step:2}: IG={ig_score:.4f}, Align={alignment:.4f}, Tensions={[f'{t:.4f}' for t in tensions]}")
    
    # Analyze metric propagation
    print("\n=== METRIC PROPAGATION ANALYSIS ===")
    
    # Check IG responds to system state
    ig_changes = np.diff(metric_histories['ig_scores'])
    ig_variability = np.std(ig_changes) if len(ig_changes) > 0 else 0
    print(f"IG variability: {ig_variability:.6f}")
    assert ig_variability > 1e-6, "IG not responding to system changes"
    
    # Check alignment reflects tension coherence
    alignment_tension_correlation = []
    for i in range(len(metric_histories['alignments'])):
        tensions = metric_histories['tensions'][i]
        tension_variance = np.var(tensions) if len(tensions) > 0 else 0
        alignment = metric_histories['alignments'][i]
        
        # Higher tension variance should correlate with lower alignment
        if tension_variance > 1e-6:
            alignment_tension_correlation.append((tension_variance, alignment))
    
    if alignment_tension_correlation:
        variances, alignments = zip(*alignment_tension_correlation)
        # Simple check: when variance increases, alignment should generally decrease
        variance_changes = np.diff(variances)
        alignment_changes = np.diff(alignments)
        
        opposite_moves = sum(1 for vc, ac in zip(variance_changes, alignment_changes) 
                           if vc * ac < 0)  # Opposite signs
        total_moves = len(variance_changes)
        
        opposite_ratio = opposite_moves / total_moves if total_moves > 0 else 0
        print(f"Alignment-Tension inverse correlation: {opposite_ratio:.1%}")
        assert opposite_ratio > 0.3, "Alignment not properly reflecting tension coherence"

def test_cross_domain_effects():
    """PROVE: Changes in one domain affect cross-domain metrics"""
    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    
    print("\n=== CROSS-DOMAIN EFFECTS TEST ===")
    
    # Get baseline metrics
    ig_baseline, align_baseline, _, _ = engine.integrator.coupled_pde_step()
    
    # Artificially perturb one domain's field
    bio_state = engine.integrator.domain_states[Domain.BIO_PHYSICS]
    if hasattr(bio_state, 'concentrations') and bio_state.concentrations is not None:
        original_field = bio_state.concentrations.copy()
        bio_state.concentrations += 0.5  # Significant perturbation
        
        # Get metrics after perturbation
        ig_perturbed, align_perturbed, _, _ = engine.integrator.coupled_pde_step()
        
        print(f"Baseline: IG={ig_baseline:.4f}, Align={align_baseline:.4f}")
        print(f"Perturbed: IG={ig_perturbed:.4f}, Align={align_perturbed:.4f}")
        
        # Metrics should change due to cross-domain effects
        ig_change = abs(ig_perturbed - ig_baseline)
        align_change = abs(align_perturbed - align_baseline)
        
        assert ig_change > 1e-4 or align_change > 1e-4, "Cross-domain effects not detected"
        
        # Restore field
        bio_state.concentrations = original_field

if __name__ == "__main__":
    test_metric_propagation()
    test_cross_domain_effects()
    print("✅ Metric propagation verified!")
