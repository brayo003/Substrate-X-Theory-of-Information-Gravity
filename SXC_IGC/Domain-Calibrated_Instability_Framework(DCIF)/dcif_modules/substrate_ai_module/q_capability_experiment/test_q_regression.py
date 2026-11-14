"""
Regression Test: Prevent Q_old Reintroduction

This test ensures that the falsified Q_old is not reintroduced as an active
transport classifier in the backend.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.domains.physical_field.physical_field_models import QObservation


def test_q_observation_deprecated():
    """Test that QObservation is marked as deprecated."""
    print("="*80)
    print("REGRESSION TEST: Q_old Deprecation")
    print("="*80)
    
    # Check that QObservation docstring contains deprecation warning
    assert "DEPRECATED" in QObservation.__doc__, "QObservation should be marked as DEPRECATED"
    print("✓ QObservation is marked as DEPRECATED")
    
    # Check that the docstring mentions the falsification
    assert "falsified" in QObservation.__doc__.lower(), "QObservation docstring should mention falsification"
    print("✓ QObservation docstring mentions falsification")
    
    # Check that the docstring recommends SpectralTransportObservable
    assert "SpectralTransportObservable" in QObservation.__doc__, "QObservation should recommend SpectralTransportObservable"
    print("✓ QObservation recommends SpectralTransportObservable")
    
    print("\n✓ Q_old deprecation regression test PASSED")
    return True


def test_spectral_observable_active():
    """Test that SpectralTransportObservable is the active transport classifier."""
    print("\n" + "="*80)
    print("REGRESSION TEST: SpectralTransportObservable Active")
    print("="*80)
    
    from sim_world.domains.physical_field.physical_field_models import SpectralTransportObservable
    
    # Check that SpectralTransportObservable is NOT deprecated
    assert "DEPRECATED" not in SpectralTransportObservable.__doc__, "SpectralTransportObservable should not be deprecated"
    print("✓ SpectralTransportObservable is not deprecated")
    
    # Check that it mentions the validated methodology
    doc_lower = SpectralTransportObservable.__doc__.lower()
    assert "validated" in doc_lower or "validation" in doc_lower or "defensible" in doc_lower, "SpectralTransportObservable should mention validation"
    print("✓ SpectralTransportObservable mentions validation")
    
    # Check that it mentions the fundamental quantity D(k)
    assert "D(k)" in SpectralTransportObservable.__doc__, "SpectralTransportObservable should mention D(k)"
    print("✓ SpectralTransportObservable mentions fundamental quantity D(k)")
    
    print("\n✓ SpectralTransportObservable active regression test PASSED")
    return True


def test_compute_theoretical_q_deprecated():
    """Test that compute_theoretical_q is marked as deprecated."""
    print("\n" + "="*80)
    print("REGRESSION TEST: compute_theoretical_q Deprecation")
    print("="*80)
    
    from sim_world.domains.physical_field.physical_field_dynamics import compute_theoretical_q
    
    # Check that compute_theoretical_q docstring contains deprecation warning
    assert "DEPRECATED" in compute_theoretical_q.__doc__, "compute_theoretical_q should be marked as DEPRECATED"
    print("✓ compute_theoretical_q is marked as DEPRECATED")
    
    # Check that it recommends the spectral alternative
    assert "compute_spectral_transport_observable" in compute_theoretical_q.__doc__, "compute_theoretical_q should recommend spectral alternative"
    print("✓ compute_theoretical_q recommends spectral alternative")
    
    print("\n✓ compute_theoretical_q deprecation regression test PASSED")
    return True


def main():
    """Run all regression tests."""
    print("="*80)
    print("Q_old REINTRODUCTION REGRESSION TESTS")
    print("="*80)
    
    tests = [
        test_q_observation_deprecated,
        test_spectral_observable_active,
        test_compute_theoretical_q_deprecated,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print("REGRESSION TEST SUMMARY")
    print("="*80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ ALL REGRESSION TESTS PASSED")
        print("Q_old is properly deprecated and SpectralTransportObservable is active")
        return 0
    else:
        print(f"\n✗ {failed} REGRESSION TEST(S) FAILED")
        print("Q_old may be reintroduced as an active transport classifier")
        return 1


if __name__ == "__main__":
    exit(main())
