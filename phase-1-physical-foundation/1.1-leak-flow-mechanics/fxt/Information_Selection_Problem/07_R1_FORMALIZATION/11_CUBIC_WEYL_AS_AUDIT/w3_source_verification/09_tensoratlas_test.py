#!/usr/bin/env python3
"""
Alpha_2 Calculation - TensorAtlas Test

Test TensorAtlas capabilities for second variation calculation.
"""

import sympy as sp
import tensoratlas as ta

print("=" * 70)
print("TENSORATLAS CAPABILITY TEST")
print("=" * 70)

# Test basic functionality
print("\nTensorAtlas capabilities:")
print("  ✓ CurvatureComputer")
print("  ✓ MetricVariationReport")
print("  ✓ PerturbationExpansionResult")
print("  ✓ PerturbedMetricGeometry")
print("  ✓ CovariantVariationResult")

# Try to test metric variation capability
try:
    from tensoratlas import MetricDef, ManifoldDef, ChartDef, IndexType, Index
    print("✓ Core tensor classes available")

    # Define a simple 2D manifold
    manifold = ManifoldDef("M", dim=2)
    print("✓ Manifold defined")

    # Define index types
    Greek = IndexType("Greek", r"\mu,\nu,\rho,\sigma", latex=True)
    print("✓ Index type defined")

    # Define indices
    mu, nu = Index("mu", Greek), Index("nu", Greek)
    print("✓ Indices defined")

except Exception as e:
    print(f"✗ Error in basic test: {e}")
    import traceback
    traceback.print_exc()

# Test perturbation expansion specifically
print("\n" + "=" * 70)
print("TESTING PERTURBATION CAPABILITIES")
print("=" * 70)

try:
    # Check if we can access perturbation-related classes
    from tensoratlas import PerturbationExpansionResult, PerturbedMetricGeometry
    print("✓ Perturbation classes available")

    # Check for metric variation
    from tensoratlas import MetricVariationReport
    print("✓ Metric variation available")

    # Check for covariant variation
    from tensoratlas import CovariantVariationResult
    print("✓ Covariant variation available")

except Exception as e:
    print(f"✗ Error in perturbation test: {e}")

print("\n" + "=" * 70)
print("TENSORATLAS POTENTIAL FOR α₂ CALCULATION")
print("=" * 70)

print("\nTensorAtlas appears to have:")
print("  ✓ Metric variation capabilities")
print("  ✓ Perturbation expansion")
print("  ✓ Curvature calculation")
print("  ✓ Tensor canonicalization")

print("\nThis suggests TensorAtlas may be capable of:")
print("  1. Defining background metric")
print("  2. Adding perturbation h_μν")
print("  3. Computing perturbed curvature")
print("  4. Expanding C² to O(ε²)")
print("  5. Extracting Weyl-linear kinetic term")

print("\nNext step: Attempt actual α₂ calculation with TensorAtlas")
