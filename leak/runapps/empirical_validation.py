#!/usr/bin/env python3
from parameter_refinement import *
from solar_system_tests import *
from galactic_tests import *

def run_empirical_validation():
    """Run all empirical tests against your theory"""
    print("🔬 COMPREHENSIVE EMPIRICAL VALIDATION")
    print("=" * 60)
    
    tests = {
        "G Constant Calibration": calibrate_gravitational_constant,
        "Pioneer Anomaly": pioneer_anomaly_prediction,
        "Mercury Precession": mercury_precession_test,
        "Planetary Orbits": planetary_orbits_validation,
        "Galactic Rotation": galactic_rotation_curve,
        "Dark Matter Replacement": dark_matter_replacement_test,
    }
    
    results = {}
    for test_name, test_func in tests.items():
        print(f"\n▶️ RUNNING: {test_name}")
        results[test_name] = test_func()
    
    print("\n" + "=" * 60)
    print("📊 EMPIRICAL VALIDATION SUMMARY:")
    for test, result in results.items():
        print(f"   {test}: {type(result).__name__}")
    
    print("\n🎯 NEXT: Calibrate parameters to match these observations")
    return results

if __name__ == "__main__":
    run_empirical_validation()
