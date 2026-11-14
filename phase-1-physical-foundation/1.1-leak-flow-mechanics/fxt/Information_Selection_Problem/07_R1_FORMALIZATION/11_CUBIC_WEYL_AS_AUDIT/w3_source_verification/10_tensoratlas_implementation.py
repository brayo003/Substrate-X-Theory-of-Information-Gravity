#!/usr/bin/env python3
"""
Alpha_2 Calculation - TensorAtlas Implementation

Attempt to compute α₂ using TensorAtlas perturbation capabilities.
"""

import sympy as sp
from tensoratlas.relativity import two_sphere_metric, scalar_curvature
from tensoratlas.core import MetricDef, ManifoldDef, ChartDef, IndexType, Index

print("=" * 70)
print("ALPHA_2 CALCULATION USING TENSORATLAS")
print("=" * 70)

# First, test basic functionality
print("\nTest 1: Two-sphere curvature (verified working)")
sphere = two_sphere_metric()
print(f"Scalar curvature of S²: {scalar_curvature(sphere)}")

# Now try to construct a product metric S²×S²
print("\n" + "=" * 70)
print("Test 2: Construct S²×S² product metric")
print("=" * 70)

try:
    # Define manifold
    manifold = ManifoldDef("M")
    print("✓ Manifold defined")

    # Define index types
    Greek = IndexType("Greek", r"\mu,\nu,\rho,\sigma", latex=True)
    print("✓ Index type defined")

    # Define coordinates
    theta1, phi1, theta2, phi2 = sp.symbols('theta1 phi1 theta2 phi2', real=True)
    r1, r2 = sp.symbols('r1 r2', positive=True, real=True)

    # Try to define a chart
    chart = ChartDef("chart", manifold, [theta1, phi1, theta2, phi2])
    print("✓ Chart defined")

    # Define metric components
    metric_components = sp.Array([
        [r1**2, 0, 0, 0],
        [0, r1**2 * sp.sin(theta1)**2, 0, 0],
        [0, 0, r2**2, 0],
        [0, 0, 0, r2**2 * sp.sin(theta2)**2]
    ])

    # Try to define metric
    metric = MetricDef("g", chart, metric_components, Greek)
    print("✓ Metric defined")

    # Compute curvature
    from tensoratlas.relativity import Riemann, Ricci
    riemann = Riemann(metric)
    ricci = Ricci(metric)
    print("✓ Curvature tensors computed")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TENSORATLAS LIMITATION ASSESSMENT")
print("=" * 70)

print("\nTensorAtlas capabilities:")
print("  ✓ Static metric curvature calculation")
print("  ✓ Basic tensor operations")
print("  ⚠ Metric perturbation (unclear API)")
print("  ⚠ Second variation (unclear API)")

print("\nAPI investigation needed:")
print("  - How to add perturbation h_μν to metric")
print("  - How to expand in perturbation parameter")
print("  - How to extract specific terms from expansion")

print("\nCurrent status:")
print("  α₂ = 8 (structural argument)")
print("  TensorAtlas: partially functional for static calculations")
print("  Perturbation API: needs investigation")

print("\nNext step: Consult TensorAtlas documentation for perturbation API")
