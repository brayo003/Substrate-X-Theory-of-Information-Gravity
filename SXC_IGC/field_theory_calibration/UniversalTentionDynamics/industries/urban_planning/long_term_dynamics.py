#!/usr/bin/env python3
"""
URBAN LONG-TERM DYNAMICS TESTS
Observe emergent patterns over extended simulation time
"""
import numpy as np
import sys
import os
sys.path.append('../../..')
from core_engine.src.universal_stable_core import UniversalStableCore

def run_long_term_test():
    print("⏳ URBAN LONG-TERM DYNAMICS TEST")
    print("Observing pattern evolution over 500+ steps")
    print("=" * 60)
    
    engine = UniversalStableCore(grid_size=(32, 32))
    engine.set_urban_parameters()
    engine.initialize_domain("urban")
    
    # Track long-term metrics
    history = {
        'step': [],
        'density_mean': [],
        'density_variance': [],
        'max_density': [],
        'stress': [],
        'development_potential': [],
        'constraints': []
    }
    
    print("🔄 Running long-term simulation...")
    convergence_detected = False
    oscillation_detected = False
    
    for step in range(500):
        if step % 50 == 0:
            print(f"  Step {step}: ρ̄={np.mean(engine.rho):.3f}, σ²={np.var(engine.rho):.4f}")
        
        if engine.evolve_system_adaptive(1):
            # Record metrics
            history['step'].append(step)
            history['density_mean'].append(np.mean(engine.rho))
            history['density_variance'].append(np.var(engine.rho))
            history['max_density'].append(np.max(engine.rho))
            history['stress'].append(engine.stress_history[-1] if engine.stress_history else 0)
            history['development_potential'].append(np.mean(engine.E))
            history['constraints'].append(np.mean(engine.F))
        
        # Check for convergence
        if step > 100 and len(history['density_mean']) > 50:
            recent_mean = history['density_mean'][-50:]
            if np.std(recent_mean) < 0.005:
                convergence_detected = True
                print(f"  🔍 Convergence detected at step {step}")
                break
        
        # Check for oscillations
        if step > 200 and len(history['density_mean']) > 100:
            recent = history['density_mean'][-100:]
            if max(recent) - min(recent) > 0.1:
                oscillation_detected = True
                print(f"  🔄 Oscillation detected at step {step}")
        
        if engine.rejected_steps > 50:
            print("  💥 Too many rejected steps - stopping")
            break
    
    # Analyze long-term behavior
    print(f"\n📊 LONG-TERM ANALYSIS:")
    print("=" * 50)
    
    final_step = history['step'][-1] if history['step'] else 0
    initial_variance = history['density_variance'][0] if history['density_variance'] else 0
    final_variance = history['density_variance'][-1] if history['density_variance'] else 0
    variance_change = final_variance - initial_variance
    
    print(f"  Total Steps: {final_step}")
    print(f"  Pattern Evolution: {variance_change:+.4f}")
    print(f"  Final Stress: {history['stress'][-1]:.3f}" if history['stress'] else "  Final Stress: N/A")
    
    # Classify long-term behavior
    if convergence_detected:
        if final_variance > 0.03:
            behavior = "✅ STABLE PATTERNS: System converged to structured state"
        else:
            behavior = "💤 HOMOGENEOUS: System converged to uniform state"
    elif oscillation_detected:
        behavior = "🔄 CYCLICAL: System shows oscillatory behavior"
    elif variance_change > 0.02:
        behavior = "📈 PATTERN GROWTH: Patterns continue developing"
    elif variance_change > -0.01:
        behavior = "⚖️  PATTERN MAINTENANCE: Patterns stable"
    else:
        behavior = "📉 PATTERN DECAY: Patterns dissolving"
    
    print(f"  Behavior: {behavior}")
    
    # Urban planning implications
    print(f"\n🏙️ URBAN PLANNING INSIGHTS:")
    print("=" * 50)
    
    avg_development = np.mean(history['development_potential']) if history['development_potential'] else 0
    avg_constraints = np.mean(history['constraints']) if history['constraints'] else 0
    development_ratio = avg_development / (avg_constraints + 1e-8)
    
    if development_ratio > 1.5:
        insight = "🚀 DEVELOPMENT-DRIVEN: Strong growth potential"
    elif development_ratio > 0.8:
        insight = "⚖️ BALANCED: Healthy development-constraint balance"
    else:
        insight = "🛑 CONSTRAINT-LIMITED: Regulations dominate"
    
    print(f"  Development/Constraint Ratio: {development_ratio:.2f}")
    print(f"  Planning Insight: {insight}")
    
    # Stability assessment
    max_stress = max(history['stress']) if history['stress'] else 0
    if max_stress < 0.3:
        stability = "🎯 EXCELLENT STABILITY"
    elif max_stress < 0.6:
        stability = "✅ GOOD STABILITY" 
    else:
        stability = "⚠️  MODERATE INSTABILITY"
    
    print(f"  Stability: {stability} (Max Stress: {max_stress:.3f})")
    
    return history, behavior

if __name__ == "__main__":
    run_long_term_test()
