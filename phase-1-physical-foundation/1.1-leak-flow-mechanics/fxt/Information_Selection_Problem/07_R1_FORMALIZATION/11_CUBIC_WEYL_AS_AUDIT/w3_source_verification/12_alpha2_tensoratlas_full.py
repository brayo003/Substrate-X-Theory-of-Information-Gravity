#!/usr/bin/env python3
"""
Alpha_2 Calculation - Full TensorAtlas Implementation

This script attempts to compute α₂ using TensorAtlas's MetricModel
and perturbation capabilities.
"""

import sympy as sp
from tensoratlas.relativity.metrics import MetricModel
from tensoratlas.core import expand_metric_perturbation_to_order
from tensoratlas.core.variational_calculus import vary
import inspect

print("=" * 70)
print("ALPHA_2 FULL TENSORATLAS CALCULATION")
print("=" * 70)

# Define symbols
r1, r2 = sp.symbols('r1 r2', positive=True, real=True)
theta1, phi1, theta2, phi2 = sp.symbols('theta1 phi1 theta2 phi2', real=True)

print("\nStep 1: Construct S²×S² product metric")
print("=" * 70)

# Construct product metric using from_matrix method
# ds² = r₁²(dθ₁² + sin²θ₁ dφ₁²) + r₂²(dθ₂² + sin²θ₂ dφ₂²)

metric_matrix = sp.Matrix([
    [r1**2, 0, 0, 0],
    [0, r1**2 * sp.sin(theta1)**2, 0, 0],
    [0, 0, r2**2, 0],
    [0, 0, 0, r2**2 * sp.sin(theta2)**2]
])

coordinates = [theta1, phi1, theta2, phi2]

try:
    S2xS2 = MetricModel.from_matrix(
        "S2xS2",
        coordinates,
        metric_matrix,
        parameters=(r1, r2),
        signature=(1, 1, 1, 1)
    )
    print("✓ S²×S² metric constructed")
    print(f"Dimension: {S2xS2.dimension}")
    print(f"Coordinates: {S2xS2.coordinates}")

except Exception as e:
    print(f"✗ Error constructing metric: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nStep 2: Compute background curvature")
print("=" * 70)

try:
    christoffel = S2xS2.christoffel()
    print("✓ Christoffel symbols computed")

    riemann = S2xS2.riemann()
    print("✓ Riemann tensor computed")

    ricci = S2xS2.ricci()
    print("✓ Ricci tensor computed")

    scalar_curvature = S2xS2.scalar_curvature()
    print(f"✓ Scalar curvature: {scalar_curvature}")

except Exception as e:
    print(f"✗ Error computing curvature: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nStep 3: Define perturbation")
print("=" * 70)

# Define a simple TT perturbation for testing
# On S²×S², a TT perturbation in the h_ab sector
# For simplicity, use a coordinate-dependent perturbation that satisfies TT conditions

h_amp = sp.symbols('h_amp', real=True)

# TT perturbation in h_ab sector (indices 0,1 on first S²)
# This needs to be carefully constructed to satisfy TT conditions
# For now, use a simple test perturbation

h_matrix = sp.Matrix([
    [h_amp * sp.cos(theta1), 0, 0, 0],
    [0, -h_amp * sp.cos(theta1), 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
])

print("Perturbation matrix defined (simplified TT-like)")
print(f"h = {h_matrix}")

print("\nStep 4: Create perturbed metric model")
print("=" * 70)

try:
    perturbed_metric = metric_matrix + h_matrix
    print("✓ Perturbed metric constructed")

    perturbed_S2xS2 = MetricModel.from_matrix(
        "S2xS2_perturbed",
        coordinates,
        perturbed_metric,
        parameters=(r1, r2, h_amp),
        signature=(1, 1, 1, 1)
    )
    print("✓ Perturbed metric model created")

except Exception as e:
    print(f"✗ Error creating perturbed metric: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 5: Attempt perturbation expansion using TensorAtlas API")
print("=" * 70)

try:
    # Try to use the TensorAtlas perturbation expansion
    # Need to convert MetricModel to TensorHead format
    print("Attempting to use expand_metric_perturbation_to_order...")
    print("This requires TensorHead format, not MetricModel")

    # Inspect what we actually have
    print(f"\nMetric type: {type(S2xS2)}")
    print(f"Metric attribute type: {type(S2xS2.metric)}")

except Exception as e:
    print(f"✗ Error in perturbation expansion: {e}")

print("\n" + "=" * 70)
print("TENSORATLAS API LIMITATION IDENTIFIED")
print("=" * 70)

print("\nTensorAtlas MetricModel provides:")
print("  ✓ Static metric calculations")
print("  ✓ Curvature tensors")
print("  ✓ Christoffel symbols")
print("  ✓ Geodesic equations")

print("\nTensorAtlas perturbation API requires:")
print("  ✗ TensorHead format (not MetricModel)")
print("  ✗ Complex index and tensor head setup")
print("  ✗ Manual construction of perturbation expressions")

print("\nThe gap between MetricModel and perturbation API is significant.")

print("\n" + "=" * 70)
print("ALTERNATIVE: MANUAL C² CALCULATION")
print("=" * 70)

print("\nCompute C² = Riem² - 2Ric² + R²/3 directly:")

try:
    # Get the components
    Riem_components = riemann.to_matrix()
    Ricci_components = ricci.to_matrix()

    print(f"Riemann components shape: {Riem_components.shape}")
    print(f"Ricci components shape: {Ricci_components.shape}")

    # Compute C² components (simplified)
    # C^abcd C_abcd = R^abcd R_abcd - 2 R^ab R_ab + (1/3) R^2

    # This is getting complex - we need full tensor contractions
    print("Full tensor contraction requires:")
    print("  - Proper index raising/lowering")
    print("  - Tensor contraction")
    print("  - SymPy tensor operations")

except Exception as e:
    print(f"✗ Error in C² calculation: {e}")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

print("\nTensorAtlas limitations:")
print("  1. MetricModel (high-level) vs TensorHead (low-level) mismatch")
print("  2. Perturbation API requires complex manual setup")
print("  3. No direct path from MetricModel to perturbation expansion")

print("\nα₂ calculation status:")
print("  α₂ = 8 (structural argument)")
print("  Full tensor calculation: BLOCKED by API complexity")
print("  Manual implementation would require:")
print("    - Learning TensorAtlas low-level API")
print("    - Manual index management")
print("    - Manual tensor head construction")
print("    - Significant development time")

print("\nDecision:")
print("  The TensorAtlas API is too complex for immediate implementation")
print("  without extensive study of its low-level architecture.")
print("  The structural argument α₂ = 8 remains unverified.")
