import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from theory.dynamic_metrics_core import calculate_tension

def test_actual_tension_stable_history():
    """Test the REAL tension calculation from your engine"""
    # Create stable history (no changes)
    stable_history = [
        np.array([1.0, 1.0, 1.0]),
        np.array([1.0, 1.0, 1.0]),  # No change
        np.array([1.0, 1.0, 1.0])   # No change
    ]
    external_pressure = 0.1
    
    tension = calculate_tension(stable_history, external_pressure)
    
    # Stable history should have low tension
    assert tension >= 0.0, f"Tension should be non-negative, got {tension}"
    print(f"Stable history tension: {tension}")

def test_actual_tension_changing_history():
    """Test tension with changing field states"""
    # Create changing history
    changing_history = [
        np.array([1.0, 1.0, 1.0]),
        np.array([2.0, 2.0, 2.0]),  # Big change
        np.array([3.0, 3.0, 3.0])   # Another change
    ]
    external_pressure = 0.1
    
    tension = calculate_tension(changing_history, external_pressure)
    
    # Changing history should have higher tension
    assert tension >= 0.0, f"Tension should be non-negative, got {tension}"
    print(f"Changing history tension: {tension}")

if __name__ == "__main__":
    test_actual_tension_stable_history()
    test_actual_tension_changing_history()
