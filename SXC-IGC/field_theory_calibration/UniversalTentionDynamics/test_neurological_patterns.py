#!/usr/bin/env python3
"""
NEUROLOGICAL PATTERN TESTS
Testing if universal engine exhibits brain-like behaviors
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_monitored import create_monitored_engine
import numpy as np

print("🧠 NEUROLOGICAL PATTERN TESTS")
print("Testing brain-like behaviors in universal dynamics")
print("=" * 60)

def test_neural_activation_patterns():
    """Test if system exhibits neural activation patterns"""
    print("\n🔬 TEST 1: Neural Activation Patterns")
    print("Can the system exhibit firing/threshold behaviors?")
    
    # Create engine with neural-like parameters
    neural_engine = create_monitored_engine('general', grid_size=32,
                                          M_factor=50000,
                                          breaking_threshold=0.5,  # Lower threshold = more sensitive
                                          broken_resistance=0.3,   # Partial recovery
                                          cubic_damping=0.2)       # Less damping = more oscillation
    
    # Initialize with multiple "neuronal" centers
    centers = [(8,8), (8,24), (24,8), (24,24)]
    for i, (cx, cy) in enumerate(centers):
        # Create Gaussian "neurons" with different amplitudes
        x = np.linspace(-1, 1, 32)
        y = np.linspace(-1, 1, 32)
        X, Y = np.meshgrid(x, y, indexing='ij')
        
        # Each neuron has different activation threshold
        r2 = (X - (cx/16 - 1))**2 + (Y - (cy/16 - 1))**2
        neural_input = (i+1) * 0.3 * np.exp(-r2 / (2 * 0.05**2))
        neural_engine.rho += neural_input
    
    print(f"Initialized {len(centers)} neural centers")
    print(f"Initial ρ_max: {np.max(neural_engine.rho):.3f}")
    
    # Evolve and track activation patterns
    activations = []
    for step in range(200):
        neural_engine.evolve_monitored_imex()
        
        # Track which "neurons" are active (above threshold)
        active_neurons = []
        for i, (cx, cy) in enumerate(centers):
            neuron_activity = neural_engine.rho[cx-2:cx+2, cy-2:cy+2].mean()
            if neuron_activity > 0.5:  # Firing threshold
                active_neurons.append(i)
        
        activations.append(active_neurons)
        
        if step % 40 == 0:
            print(f"  Step {step}: Active neurons: {active_neurons}, ρ_max: {np.max(neural_engine.rho):.3f}")
    
    # Analyze activation patterns
    total_activations = sum(len(act) for act in activations)
    synchronous_activations = sum(1 for act in activations if len(act) > 1)
    
    print(f"\n📊 NEURAL ACTIVATION RESULTS:")
    print(f"  Total activations: {total_activations}")
    print(f"  Synchronous activations: {synchronous_activations}")
    print(f"  Sync percentage: {synchronous_activations/len(activations)*100:.1f}%")
    
    return neural_engine, activations

def test_plasticity_learning():
    """Test if system can exhibit learning-like behavior"""
    print("\n🔬 TEST 2: Synaptic Plasticity Simulation")
    print("Can constraints adapt like neural plasticity?")
    
    plastic_engine = create_monitored_engine('general', grid_size=32,
                                           M_factor=30000,
                                           breaking_threshold=0.3,  # Very sensitive
                                           recovery_rate=0.05,      # Faster learning
                                           velocity_sensitivity=8.0) # High velocity dependence
    
    # Initialize with input-output pattern
    plastic_engine.initialize_gaussian(amplitude=0.5)
    
    # Track how stiffness evolves (like synaptic weights)
    stiffness_history = []
    broken_history = []
    
    for step in range(150):
        # Store current stiffness state
        current_stiffness = plastic_engine.compute_adaptive_stiffness(plastic_engine.rho)
        stiffness_history.append(np.mean(current_stiffness))
        broken_history.append(np.mean(plastic_engine.broken_regions))
        
        plastic_engine.evolve_monitored_imex()
        
        if step % 30 == 0:
            avg_stiffness = np.mean(current_stiffness)
            broken_frac = np.mean(plastic_engine.broken_regions)
            print(f"  Step {step}: Avg stiffness: {avg_stiffness:.3f}, Broken: {broken_frac:.3f}")
    
    # Analyze plasticity
    stiffness_change = stiffness_history[-1] - stiffness_history[0]
    plasticity_measure = np.std(stiffness_history)  # Variability = learning
    
    print(f"\n📊 PLASTICITY RESULTS:")
    print(f"  Stiffness change: {stiffness_change:.3f}")
    print(f"  Plasticity measure (std): {plasticity_measure:.3f}")
    print(f"  Final broken fraction: {broken_history[-1]:.3f}")
    
    return plastic_engine, stiffness_history

def test_information_flow():
    """Test if system can propagate information like neural circuits"""
    print("\n🔬 TEST 3: Information Flow Patterns")
    print("Can the system exhibit signal propagation?")
    
    flow_engine = create_monitored_engine('general', grid_size=64,  # Larger for propagation
                                        dt=0.0002,
                                        M_factor=40000,
                                        cubic_damping=0.1)  # Low damping for propagation
    
    # Create input signal on left side
    flow_engine.rho[:, :5] = 0.8  # Input layer
    
    print(f"Initial signal strength: {np.max(flow_engine.rho):.3f}")
    
    # Track propagation through layers
    layer_strengths = []
    layers = [slice(5,15), slice(15,25), slice(25,35), slice(35,45), slice(45,55)]
    
    for step in range(100):
        flow_engine.evolve_monitored_imex()
        
        # Measure signal strength in each layer
        layer_strength = [np.mean(flow_engine.rho[layer]) for layer in layers]
        layer_strengths.append(layer_strength)
        
        if step % 20 == 0:
            print(f"  Step {step}: Layer strengths: {[f'{s:.3f}' for s in layer_strength]}")
    
    # Analyze propagation
    final_strengths = layer_strengths[-1]
    propagation_success = final_strengths[-1] > 0.1  # Signal reached end
    
    print(f"\n📊 INFORMATION FLOW RESULTS:")
    print(f"  Final layer strengths: {[f'{s:.3f}' for s in final_strengths]}")
    print(f"  Propagation successful: {propagation_success}")
    print(f"  Signal attenuation: {final_strengths[-1]/final_strengths[0]:.3f}")
    
    return flow_engine, layer_strengths

def test_memory_formation():
    """Test if system can form persistent patterns (memory)"""
    print("\n🔬 TEST 4: Memory Formation Test")
    print("Can the system maintain patterns over time?")
    
    memory_engine = create_monitored_engine('general', grid_size=32,
                                          M_factor=60000,      # Higher for stability
                                          broken_resistance=0.7, # Strong memory
                                          recovery_rate=0.02)   # Slow forgetting
    
    # Create distinct memory pattern
    x = np.linspace(-1, 1, 32)
    y = np.linspace(-1, 1, 32)
    X, Y = np.meshgrid(x, y, indexing='ij')
    
    # Create checkerboard pattern as "memory"
    memory_pattern = ((np.sin(4*np.pi*X) > 0) & (np.sin(4*np.pi*Y) > 0)).astype(float) * 0.6
    memory_engine.rho = memory_pattern.copy()
    
    initial_pattern = memory_engine.rho.copy()
    
    pattern_persistence = []
    for step in range(200):
        memory_engine.evolve_monitored_imex()
        
        # Measure pattern similarity to initial state
        correlation = np.corrcoef(initial_pattern.flatten(), 
                                memory_engine.rho.flatten())[0,1]
        pattern_persistence.append(correlation)
        
        if step % 40 == 0:
            print(f"  Step {step}: Pattern correlation: {correlation:.3f}")
    
    # Analyze memory persistence
    final_correlation = pattern_persistence[-1]
    memory_half_life = next((i for i, corr in enumerate(pattern_persistence) 
                           if corr < 0.5), len(pattern_persistence))
    
    print(f"\n📊 MEMORY RESULTS:")
    print(f"  Final pattern correlation: {final_correlation:.3f}")
    print(f"  Memory half-life (steps): {memory_half_life}")
    print(f"  Memory quality: {'GOOD' if final_correlation > 0.3 else 'POOR'}")
    
    return memory_engine, pattern_persistence

if __name__ == "__main__":
    print("🧠 COMPREHENSIVE NEUROLOGICAL TEST SUITE")
    print("Testing brain-like behaviors in universal dynamics")
    print("=" * 60)
    
    # Run all neurological tests
    results = {}
    
    results['activation'] = test_neural_activation_patterns()
    results['plasticity'] = test_plasticity_learning()  
    results['information'] = test_information_flow()
    results['memory'] = test_memory_formation()
    
    print(f"\n{'='*60}")
    print("🎯 NEUROLOGICAL TEST SUMMARY")
    print("=" * 60)
    
    # Summary insights
    neural_engine, activations = results['activation']
    sync_percentage = sum(1 for act in activations if len(act) > 1) / len(activations) * 100
    
    plastic_engine, stiffness_hist = results['plasticity']
    plasticity = np.std(stiffness_hist)
    
    flow_engine, layer_strengths = results['information']
    propagation = layer_strengths[-1][-1] > 0.1
    
    memory_engine, persistence = results['memory']
    memory_strength = persistence[-1]
    
    print(f"🧠 NEURAL BEHAVIORS DETECTED:")
    print(f"  Synchronous activation: {sync_percentage:.1f}%")
    print(f"  Plasticity measure: {plasticity:.3f}")
    print(f"  Information propagation: {'YES' if propagation else 'NO'}")
    print(f"  Memory persistence: {memory_strength:.3f}")
    
    # Overall neurological assessment
    neuro_score = (sync_percentage/100 + min(plasticity, 1.0) + 
                  (1.0 if propagation else 0.0) + memory_strength) / 4
    
    print(f"\n📊 OVERALL NEUROLOGICAL SCORE: {neuro_score:.3f}")
    
    if neuro_score > 0.6:
        print("🎉 STRONG NEURAL-LIKE BEHAVIORS DETECTED!")
        print("   The engine exhibits brain-like computation patterns")
    elif neuro_score > 0.3:
        print("✅ MODERATE NEURAL CHARACTERISTICS")
        print("   Some brain-like behaviors present")
    else:
        print("⚠️  LIMITED NEURAL BEHAVIORS")
        print("   Engine shows minimal brain-like patterns")
    
    print("=" * 60)
