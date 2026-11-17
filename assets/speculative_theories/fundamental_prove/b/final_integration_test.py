"""
FINAL INTEGRATION TEST: Run all phases and check binary outcome
"""

import subprocess
import sys
import os

def run_phase_test(phase_dir, test_file):
    """Run a phase test and capture output"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {phase_dir}/{test_file}")
    print('='*60)
    
    try:
        # Run the test
        result = subprocess.run(
            [sys.executable, f"{phase_dir}/{test_file}"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Check for success indicators in output
        success_indicators = ['✓ SUCCESS', 'UNIVERSALITY CONFIRMED', 'FALSIFIABLE PREDICTIONS CONFIRMED']
        failure_indicators = ['✗ FAILURE', 'UNIVERSALITY VIOLATED']
        
        success = False
        for indicator in success_indicators:
            if indicator in result.stdout:
                success = True
                break
        
        # Also check return code
        if result.returncode == 0 and success:
            return True, result.stdout
        else:
            return False, result.stdout
            
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {phase_dir}/{test_file}")
        return False, "Timeout"
    except Exception as e:
        print(f"ERROR running {phase_dir}/{test_file}: {str(e)}")
        return False, str(e)

def main():
    """Run all phase tests and determine final status"""
    print("FINAL INTEGRATION TEST: SXC-IGC GRADUATION CHECK")
    print("="*60)
    
    phase_tests = [
        ('phase_I', 'test_uniqueness.py'),
        ('phase_II', 'test_geometry_alpha.py'),
        ('phase_III', 'test_spectral_lock.py'),
        ('phase_IV', 'test_solver_invariance.py'),
        ('phase_V', 'test_falsifiable_prediction.py'),
    ]
    
    results = {}
    all_passed = True
    
    # Create directories if they don't exist
    for phase_dir, _ in phase_tests:
        os.makedirs(phase_dir, exist_ok=True)
    
    # Run each test
    for phase_dir, test_file in phase_tests:
        passed, output = run_phase_test(phase_dir, test_file)
        results[f"{phase_dir}/{test_file}"] = {
            'passed': passed,
            'output': output[:1000]  # Store first 1000 chars
        }
        
        if not passed:
            all_passed = False
    
    # Final assessment
    print("\n" + "="*60)
    print("FINAL STATUS CHECK (BINARY)")
    print("="*60)
    
    passed_count = sum(1 for r in results.values() if r['passed'])
    total_count = len(results)
    
    print(f"\nTests passed: {passed_count}/{total_count}")
    
    # Check binary conditions from the framework
    print("\nBINARY CONDITIONS FOR GRADUATION:")
    
    conditions = {
        "1. Cubic V(I) is unique": results.get('phase_I/test_uniqueness.py', {}).get('passed', False),
        "2. α emerges from minimal bit-cost geometry": results.get('phase_II/test_geometry_alpha.py', {}).get('passed', False),
        "3. Same α controls entropy and correlations": results.get('phase_III/test_spectral_lock.py', {}).get('passed', False),
        "4. Fixed point is solver-independent": results.get('phase_IV/test_solver_invariance.py', {}).get('passed', False),
        "5. A new hard prediction exists": results.get('phase_V/test_falsifiable_prediction.py', {}).get('passed', False),
    }
    
    all_conditions_met = True
    for condition, met in conditions.items():
        status = "✓" if met else "✗"
        print(f"  {status} {condition}")
        if not met:
            all_conditions_met = False
    
    print("\n" + "="*60)
    
    if all_conditions_met:
        print("🎉 SXC-IGC GRADUATES TO FUNDAMENTAL THEORY")
        print("\nAll five binary conditions are satisfied:")
        print("1. Action is uniquely determined by physical principles")
        print("2. α=1.254 emerges from geometry without tuning")
        print("3. Spectral lock confirms fractal/information/field unity")
        print("4. Solver invariance proves dynamics are physical")
        print("5. Novel falsifiable predictions exist")
        print("\nThe theory is now a candidate for fundamental physics.")
        return True
    else:
        print("❌ SXC-IGC REMAINS A PHENOMENOLOGICAL MODEL")
        print("\nNot all binary conditions are satisfied.")
        print("The framework is useful but not yet fundamental.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
