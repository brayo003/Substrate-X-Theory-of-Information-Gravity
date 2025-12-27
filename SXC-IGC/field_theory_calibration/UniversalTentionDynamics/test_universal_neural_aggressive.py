#!/usr/bin/env python3
"""
AGGRESSIVE NEURAL NETWORK TEST
Using proven SNN parameters with our universal engine
Network-side tuning only - engine remains unchanged
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_monitored import create_monitored_engine
import numpy as np

print("🧠 AGGRESSIVE NEURAL NETWORK TEST")
print("Using proven SNN parameters with universal engine")
print("NETWORK-SIDE tuning only - engine unchanged")
print("=" * 60)

def test_aggressive_neural_response():
    """Test with aggressive SNN-like parameters"""
    print("\n🔬 TEST 1: Aggressive Neural Response")
    
    # Create engine with PROVEN SNN PARAMETERS
    engine = create_monitored_engine('general', grid_size=32,
        # AGGRESSIVE NEURAL PARAMETERS (from working SNN)
        M_factor=50000,           # Strong stiffness for sharp thresholds
        velocity_sensitivity=8.0, # High velocity sensitivity
        state_sensitivity=6.0,    # High state sensitivity  
        breaking_threshold=0.6,   # Lower breaking threshold
        broken_resistance=0.3,    # Less refractory damping
        cubic_damping=0.2,        # Much less damping
        rho_cutoff=0.8,           # Higher spike threshold
        dt=0.0002,                # Slightly larger time step
        delta1=1.5,               # Strong excitation
        delta2=1.0,               # Strong coupling
        kappa=0.4,                # Weaker inhibition
        tau_rho=0.08,             # Faster membrane dynamics
        tau_E=0.06,               # Faster excitation
        tau_F=0.12                # Slower inhibition
    )
    
    # AGGRESSIVE STIMULATION (from working SNN)
    print("  Applying aggressive stimulation...")
    center = (8, 8)
    radius = 5
    strength = 3.5  # STRONG stimulation
    duration = 25   # PERSISTENT input
    
    # Create strong Gaussian stimulus
    stimulus = np.zeros((32, 32))
    for i in range(32):
        for j in range(32):
            distance = np.sqrt((i-center[0])**2 + (j-center[1])**2)
            if distance <= radius:
                stimulus[i, j] = strength * (1 - distance/radius)
    
    # Apply persistent stimulation
    spike_counts = []
    for step in range(100):
        if step < duration:
            # Add strong persistent input to E field
            engine.E += stimulus * 0.8
        
        engine.evolve(1, verbose=False)
        
        # Check for "spikes" (regions crossing stiffness threshold)
        current_rho = engine.rho
        stiffness_active = current_rho > engine.rho_cutoff
        spike_count = np.sum(stiffness_active)
        spike_counts.append(spike_count)
        
        if step % 15 == 0 or spike_count > 0:
            rho_max = np.max(current_rho)
            broken_frac = np.mean(engine.broken_regions)
            print(f"  Step {step:3d}: Spikes: {spike_count:3d}, "
                  f"ρ_max: {rho_max:5.2f}, Broken: {broken_frac:.3f}")
    
    total_spikes = sum(spike_counts)
    sustained = any(count > 0 for count in spike_counts[50:])  # Activity after stimulus
    
    print(f"  Total spike events: {total_spikes}")
    print(f"  Sustained activity: {sustained}")
    
    return engine, spike_counts

def test_aggressive_propagation():
    """Test signal propagation with aggressive parameters"""
    print("\n🔬 TEST 2: Aggressive Signal Propagation")
    
    engine = create_monitored_engine('general', grid_size=32,
        M_factor=60000,
        velocity_sensitivity=10.0, # Very high for propagation
        state_sensitivity=5.0,
        breaking_threshold=0.5,    # Lower for easier propagation
        broken_resistance=0.25,    # Less damping
        cubic_damping=0.15,        # Minimal damping
        rho_cutoff=0.7,            # Moderate threshold
        dt=0.0002,
        delta1=1.8,                # Very strong excitation
        delta2=1.2,                # Strong coupling
        kappa=0.3,                 # Weak inhibition
        tau_rho=0.06,              # Very fast dynamics
        tau_E=0.05,
        tau_F=0.15
    )
    
    # STRONG left-side stimulation (like working SNN)
    print("  Applying strong left-side stimulation...")
    left_stimulus = np.zeros((32, 32))
    left_stimulus[:, :8] = 4.0  # VERY strong
    duration = 30
    
    propagation_data = []
    for step in range(120):
        if step < duration:
            engine.E += left_stimulus * 0.6
        
        engine.evolve(1, verbose=False)
        
        # Measure activity across layers
        current_rho = engine.rho
        layers = [
            np.sum(current_rho[:, :8] > engine.rho_cutoff),    # Left
            np.sum(current_rho[:, 8:16] > engine.rho_cutoff),  # Middle-left
            np.sum(current_rho[:, 16:24] > engine.rho_cutoff), # Middle-right  
            np.sum(current_rho[:, 24:] > engine.rho_cutoff)    # Right
        ]
        propagation_data.append(layers)
        
        if step % 25 == 0:
            print(f"  Step {step:3d}: Active neurons by layer: {layers}")
    
    # Check if signal reached right side
    reached_right = any(data[3] > 0 for data in propagation_data[80:])
    max_right_activity = max(data[3] for data in propagation_data)
    
    print(f"  Signal reached right side: {reached_right}")
    print(f"  Max right-side activity: {max_right_activity}")
    
    return engine, propagation_data

def test_aggressive_plasticity():
    """Test plasticity with aggressive activity"""
    print("\n🔬 TEST 3: Aggressive Neural Plasticity")
    
    engine = create_monitored_engine('general', grid_size=24,
        M_factor=40000,
        velocity_sensitivity=12.0, # Very high for plasticity
        state_sensitivity=8.0,
        breaking_threshold=0.4,    # Low threshold for frequent activity
        broken_resistance=0.35,    # Moderate refractory
        cubic_damping=0.25,
        rho_cutoff=0.6,            # Low threshold
        dt=0.0001,
        delta1=2.0,                # Very strong excitation
        delta2=1.5,                # Very strong coupling
        kappa=0.5,                 # Moderate inhibition
        tau_rho=0.04,              # Very fast
        tau_E=0.03,
        tau_F=0.18
    )
    
    # Track plasticity through stress history
    initial_stress = np.mean(engine.stress_history)
    
    # AGGRESSIVE training pattern
    pattern_centers = [(6, 6), (6, 18), (18, 6), (18, 18)]
    pattern_strength = 4.0
    pattern_radius = 4
    
    stress_history = []
    for step in range(200):
        # Alternate between patterns
        pattern_idx = (step // 25) % len(pattern_centers)
        center = pattern_centers[pattern_idx]
        
        # Apply strong pattern stimulation
        stimulus = np.zeros((24, 24))
        for i in range(24):
            for j in range(24):
                distance = np.sqrt((i-center[0])**2 + (j-center[1])**2)
                if distance <= pattern_radius:
                    stimulus[i, j] = pattern_strength * (1 - distance/pattern_radius)
        
        engine.E += stimulus * 0.7
        engine.evolve(1, verbose=False)
        
        stress_history.append(np.mean(engine.stress_history))
        
        if step % 40 == 0:
            current_stress = np.mean(engine.stress_history)
            active_neurons = np.sum(engine.rho > engine.rho_cutoff)
            print(f"  Step {step:3d}: Stress: {current_stress:.3f}, "
                  f"Active: {active_neurons:3d}")
    
    final_stress = np.mean(engine.stress_history)
    stress_change = final_stress - initial_stress
    
    print(f"  Initial stress: {initial_stress:.3f}")
    print(f"  Final stress: {final_stress:.3f}") 
    print(f"  Stress change: {stress_change:+.3f}")
    print(f"  Plasticity occurred: {abs(stress_change) > 0.05}")
    
    return engine, stress_history

if __name__ == "__main__":
    print("🧠 AGGRESSIVE NEURAL NETWORK TEST")
    print("Using proven SNN parameters - Engine unchanged")
    print("=" * 60)
    
    # Run all aggressive tests
    results = {}
    
    results['response'] = test_aggressive_neural_response()
    results['propagation'] = test_aggressive_propagation()  
    results['plasticity'] = test_aggressive_plasticity()
    
    print(f"\n{'='*60}")
    print("📊 AGGRESSIVE NEURAL RESULTS:")
    print("=" * 60)
    
    engine1, spikes = results['response']
    total_spikes = sum(spikes)
    sustained = any(count > 0 for count in spikes[50:])
    
    engine2, propagation = results['propagation']
    reached_right = any(data[3] > 0 for data in propagation[80:])
    
    engine3, stress_hist = results['plasticity']
    stress_change = stress_hist[-1] - stress_hist[0]
    
    print(f"  Test 1 - Total spikes: {total_spikes}")
    print(f"  Test 1 - Sustained activity: {sustained}")
    print(f"  Test 2 - Signal propagation: {reached_right}")
    print(f"  Test 3 - Plasticity measure: {stress_change:+.3f}")
    
    success_metrics = [
        total_spikes > 100,
        sustained,
        reached_right, 
        abs(stress_change) > 0.05
    ]
    
    success_count = sum(success_metrics)
    print(f"\n🎯 AGGRESSIVE PARAMETERS: {success_count}/4 tests passed")
    
    if success_count >= 3:
        print("✅ SUCCESS: Neural dynamics achieved with aggressive tuning!")
        print("   Engine CAN run neural computation with proper parameters")
    else:
        print("⚠️  PARTIAL: Some neural behaviors achieved")
        print("   May need even more aggressive tuning")
    
    print("=" * 60)
