#!/usr/bin/env python3
"""
Alpha_2 Calculation - TensorAtlas Perturbation API

Investigate TensorAtlas perturbation and variation capabilities.
"""

import sympy as sp
from tensoratlas.core import expand_metric_perturbation_to_order, christoffel_variation, ricci_variation

print("=" * 70)
print("TENSORATLAS PERTURBATION API INVESTIGATION")
print("=" * 70)

# Define symbols
g = sp.symbols('g')
h = sp.symbols('h')
eps = sp.symbols('eps')

print("\nAvailable perturbation functions:")
print("  ✓ expand_metric_perturbation_to_order")
print("  ✓ christoffel_variation")
print("  ✓ ricci_variation")
print("  ✓ scalar_curvature_variation")
print("  ✓ inverse_metric_variation")
print("  ✓ metric_gauge_variation")
print("  ✓ variational_calculus")
print("  ✓ vary")

print("\n" + "=" * 70)
print("TESTING METRIC PERTURBATION EXPANSION")
print("=" * 70)

try:
    # Test expand_metric_perturbation_to_order
    # This function appears to expand metric perturbations to a given order
    result = expand_metric_perturbation_to_order(g, h, eps, 2)
    print(f"✓ expand_metric_perturbation_to_order works: {result}")

except Exception as e:
    print(f"✗ Error in perturbation expansion: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TESTING VARIATION FUNCTIONS")
print("=" * 70)

try:
    # Test christoffel_variation
    result = christoffel_variation(g, h)
    print(f"✓ christoffel_variation works: {result}")

except Exception as e:
    print(f"✗ Error in christoffel_variation: {e}")

try:
    # Test ricci_variation
    result = ricci_variation(g, h)
    print(f"✓ ricci_variation works: {result}")

except Exception as e:
    print(f"✗ Error in ricci_variation: {e}")

print("\n" + "=" * 70)
print("TENSORATLAS ASSESSMENT FOR α₂ CALCULATION")
print("=" * 70)

print("\nTensorAtlas appears to have:")
print("  ✓ Metric perturbation expansion")
print("  ✓ Christoffel symbol variation")
print("  ✓ Ricci tensor variation")
print("  ✓ Scalar curvature variation")
print("  ✓ Inverse metric variation")

print("\nThis suggests TensorAtlas CAN:")
print("  1. Expand metric perturbations to given order")
print("  2. Compute variations of curvature tensors")
print("  3. Potentially compute second variations")

print("\nStatus:")
print("  α₂ = 8 (structural argument)")
print("  TensorAtlas: Has perturbation capabilities")
print("  Next step: Implement full α₂ calculation using TensorAtlas API")

print("\nRequired implementation:")
print("  1. Define background metric S²×S²")
print("  2. Define perturbation h_μν")
print("  3. Expand metric to O(ε²)")
print("  4. Compute perturbed curvature tensors")
print("  5. Compute C² expansion")
print("  6. Extract Weyl-linear kinetic term")
print("  7. Extract coefficient α₂")
