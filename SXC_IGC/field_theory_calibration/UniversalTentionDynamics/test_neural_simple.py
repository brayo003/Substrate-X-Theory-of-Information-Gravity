#!/usr/bin/env python3
"""
SIMPLE NEURAL CONTROLLER TEST
Basic test to see if neural control provides any value
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
sys.path.insert(0, 'core_engine/interface') 
sys.path.insert(0, 'core_engine/neural')

from universal_dynamics_monitored import create_monitored_engine
from universal_neural_interface import UniversalNeuralInterface
from advanced_neural_controller import AdvancedNeuralController
import numpy as np

def simple_neural_test():
    """
    Simple test: Does neural control do anything at all?
    """
    print("🧠 SIMPLE NEURAL CONTROLLER TEST")
    print("Basic functionality test")
    print("=" * 50)
    
    # Create universal engine
    engine = create_monitored_engine('general', grid_size=16)
    engine.initialize_gaussian(amplitude=1.0)
    
    # Create neural controller and interface
    controller = AdvancedNeuralController(state_size=774)  # Correct size for 16x16 grid
    interface = UniversalNeuralInterface()
    
    print("✅ Systems created")
    
    # Test 1: Can neural controller generate controls?
    print("\n🔬 TEST 1: Control Generation")
    universal_state = interface.package_universal_state(engine)
    print(f"State features length: {len(controller.preprocess_state(universal_state))}")
    
    controls = controller.compute_controls(universal_state)
    
    print("Neural controls generated:")
    for control_type, params in controls.items():
        print(f"  {control_type}: {params}")
    
    # Test 2: Do controls affect the engine?
    print("\n🔬 TEST 2: Control Application")
    
    # Get initial state
    initial_rho = engine.rho.copy()
    initial_M = engine.M_factor
    
    # Apply neural controls
    interface.interface_cycle(engine, controls)
    
    # Check if anything changed
    rho_changed = not np.allclose(engine.rho, initial_rho)
    M_changed = engine.M_factor != initial_M
    
    print(f"Field changed: {rho_changed}")
    print(f"Parameters changed: {M_changed}")
    
    # Test 3: Run with and without neural control
    print("\n🔬 TEST 3: Performance Comparison")
    
    # Engine without neural control
    engine_no_control = create_monitored_engine('general', grid_size=16)
    engine_no_control.initialize_gaussian(amplitude=1.0)
    
    # Engine with neural control  
    engine_with_control = create_monitored_engine('general', grid_size=16)
    engine_with_control.initialize_gaussian(amplitude=1.0)
    
    # Run both for a few steps
    metrics_no_control = []
    metrics_with_control = []
    
    for step in range(50):
        # Engine without control
        engine_no_control.evolve(1, verbose=False)
        metrics_no_control.append({
            'complexity': calculate_complexity(engine_no_control.rho),
            'stability': 1.0 - np.mean(engine_no_control.stress_history),
            'activity': np.mean(engine_no_control.rho)
        })
        
        # Engine with neural control
        universal_state = interface.package_universal_state(engine_with_control)
        controls = controller.compute_controls(universal_state)
        interface.interface_cycle(engine_with_control, controls)
        engine_with_control.evolve(1, verbose=False)
        metrics_with_control.append({
            'complexity': calculate_complexity(engine_with_control.rho),
            'stability': 1.0 - np.mean(engine_with_control.stress_history),
            'activity': np.mean(engine_with_control.rho)
        })
        
        if step % 10 == 0:
            print(f"  Step {step}: NoControl={metrics_no_control[-1]['complexity']:.3f}, WithControl={metrics_with_control[-1]['complexity']:.3f}")
    
    # Compare final metrics
    final_no_control = {k: np.mean([m[k] for m in metrics_no_control[-10:]]) for k in metrics_no_control[0].keys()}
    final_with_control = {k: np.mean([m[k] for m in metrics_with_control[-10:]]) for k in metrics_with_control[0].keys()}
    
    print("\n📊 FINAL METRICS COMPARISON:")
    print("Metric         | No Control | With Control | Difference")
    print("-" * 50)
    for metric in final_no_control.keys():
        no_ctrl = final_no_control[metric]
        with_ctrl = final_with_control[metric]
        diff = with_ctrl - no_ctrl
        print(f"{metric:12} | {no_ctrl:10.4f} | {with_ctrl:12.4f} | {diff:+.4f}")
    
    # Overall assessment
    improvement = sum(final_with_control.values()) - sum(final_no_control.values())
    print(f"\n🎯 OVERALL IMPROVEMENT: {improvement:+.4f}")
    
    if improvement > 0:
        print("✅ Neural control provides POSITIVE value")
    else:
        print("⚠️  Neural control shows LIMITED value")
    
    return improvement > 0

def calculate_complexity(field):
    """Calculate field complexity"""
    grad_x = np.gradient(field, axis=0)
    grad_y = np.gradient(field, axis=1)
    return np.mean(grad_x**2 + grad_y**2)

if __name__ == "__main__":
    print("🎯 TESTING NEURAL CONTROLLER BASIC FUNCTIONALITY")
    print("Does it work at all? Does it provide any value?")
    print("=" * 60)
    
    success = simple_neural_test()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 CONCLUSION: Neural controller WORKS and provides value!")
        print("   Worth developing further for specific applications")
    else:
        print("🤔 CONCLUSION: Neural controller works but value is limited")
        print("   May need more sophisticated training or different approach")
    print("=" * 60)
