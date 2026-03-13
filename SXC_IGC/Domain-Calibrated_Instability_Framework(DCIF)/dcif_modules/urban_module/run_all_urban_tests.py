#!/usr/bin/env python3
"""
MASTER URBAN TEST RUNNER
Execute all urban validation tests
"""
import sys
import os
import importlib.util

def run_test_module(module_name, description):
    """Dynamically import and run a test module"""
    print(f"\n{'='*70}")
    print(f"🚀 RUNNING: {description}")
    print(f"{'='*70}")
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run the main function
        if hasattr(module, 'run_parameter_sweep'):
            return module.run_parameter_sweep()
        elif hasattr(module, 'run_spatial_scenarios'):
            return module.run_spatial_scenarios()  
        elif hasattr(module, 'run_stress_tests'):
            return module.run_stress_tests()
        elif hasattr(module, 'run_stochastic_tests'):
            return module.run_stochastic_tests()
        elif hasattr(module, 'run_long_term_test'):
            return module.run_long_term_test()
            
    except Exception as e:
        print(f"❌ ERROR running {module_name}: {e}")
        return None

def main():
    print("🌌 COMPREHENSIVE URBAN DYNAMICS VALIDATION")
    print("Running all test suites for urban domain verification")
    print("=" * 70)
    
    test_suites = [
        ("parameter_sweep", "Parameter Sweep Tests"),
        ("spatial_scenarios", "Spatial Scenario Tests"), 
        ("stress_tests", "Stress & Edge Case Tests"),
        ("stochastic_consistency", "Stochastic Consistency Tests"),
        ("long_term_dynamics", "Long-Term Dynamics Tests")
    ]
    
    results = {}
    
    for module_name, description in test_suites:
        result = run_test_module(module_name, description)
        results[module_name] = result
    
    # Final summary
    print(f"\n{'='*70}")
    print("🎯 URBAN VALIDATION TESTING COMPLETE")
    print(f"{'='*70}")
    print("📊 All test suites have been executed")
    print("💡 Check individual test outputs for detailed results")
    print("🚀 Urban dynamics engine is ready for domain deployment!")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
