#!/usr/bin/env python3
"""
Alpha_2 Calculation - EinsteinPy Implementation

This script attempts to compute α₂ using EinsteinPy tensor modules.
The goal is to compute δ²(∫√g C²)/δgδg and extract the Weyl-linear kinetic term.
"""

import sympy as sp
from einsteinpy.symbolic import ChristoffelSymbols, RiemannCurvatureTensor, RicciTensor, RicciScalar, MetricTensor
from einsteinpy.symbolic import WeylTensor

print("=" * 70)
print("ALPHA_2 CALCULATION USING EINSTEINPY")
print("=" * 70)

# First, test if we can construct a simple metric and compute curvature
print("\nTest 1: Construct S² metric")
theta, phi, r = sp.symbols('theta phi r', positive=True, real=True)

# S² metric in coordinates (theta, phi)
# ds² = r²(dθ² + sin²θ dφ²)
S2_metric = sp.Array([
    [r**2, 0],
    [0, r**2 * sp.sin(theta)**2]
])

S2_coords = [theta, phi]

print(f"S² metric: {S2_metric}")
print(f"Coordinates: {S2_coords}")

try:
    # Create MetricTensor object
    S2 = MetricTensor(S2_metric, S2_coords)
    print("✓ MetricTensor object created successfully")

    # Compute Christoffel symbols
    S2_christoffel = ChristoffelSymbols.from_metric(S2)
    print("✓ Christoffel symbols computed")

    # Compute Riemann tensor
    S2_riemann = RiemannCurvatureTensor.from_metric(S2)
    print("✓ Riemann tensor computed")

    # Compute Ricci tensor
    S2_ricci = RicciTensor.from_metric(S2)
    print("✓ Ricci tensor computed")

    # Compute Ricci scalar
    S2_ricci_scalar = RicciScalar.from_metric(S2)
    print(f"✓ Ricci scalar computed: {S2_ricci_scalar.expr}")

    # Compute Weyl tensor (should be zero for 2D)
    try:
        S2_weyl = WeylTensor.from_metric(S2)
        print("✓ Weyl tensor computed (should be zero in 2D)")
    except Exception as e:
        print(f"Weyl tensor computation: {e}")

except Exception as e:
    print(f"✗ Error in test 1: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test 2: Construct S²×S² product metric")
print("=" * 70)

# Product metric S²(r₁) × S²(r₂)
theta1, phi1, theta2, phi2 = sp.symbols('theta1 phi1 theta2 phi2', positive=True, real=True)
r1, r2 = sp.symbols('r1 r2', positive=True, real=True)

# Metric for S²(r₁) × S²(r₂)
# ds² = r₁²(dθ₁² + sin²θ₁ dφ₁²) + r₂²(dθ₂² + sin²θ₂ dφ₂²)
S2xS2_metric = sp.Array([
    [r1**2, 0, 0, 0],
    [0, r1**2 * sp.sin(theta1)**2, 0, 0],
    [0, 0, r2**2, 0],
    [0, 0, 0, r2**2 * sp.sin(theta2)**2]
])

S2xS2_coords = [theta1, phi1, theta2, phi2]

print(f"S²×S² metric constructed")
print(f"Coordinates: {S2xS2_coords}")

try:
    # Create MetricTensor object
    S2xS2 = MetricTensor(S2xS2_metric, S2xS2_coords)
    print("✓ Product MetricTensor object created successfully")

    # Compute Christoffel symbols
    S2xS2_christoffel = ChristoffelSymbols.from_metric(S2xS2)
    print("✓ Christoffel symbols computed")

    # Compute Riemann tensor
    S2xS2_riemann = RiemannCurvatureTensor.from_metric(S2xS2)
    print("✓ Riemann tensor computed")

    # Compute Ricci tensor
    S2xS2_ricci = RicciTensor.from_metric(S2xS2)
    print("✓ Ricci tensor computed")

    # Compute Ricci scalar
    S2xS2_ricci_scalar = RicciScalar.from_metric(S2xS2)
    print(f"✓ Ricci scalar computed: {sp.simplify(S2xS2_ricci_scalar.expr)}")

    # Compute Weyl tensor
    try:
        S2xS2_weyl = WeylTensor.from_metric(S2xS2)
        print("✓ Weyl tensor computed")

        # Check if Weyl is zero for equal radii
        S2xS2_weyl_equal = S2xS2_weyl.tensor().subs({r1: r, r2: r})
        print(f"Weyl tensor for equal radii: {S2xS2_weyl_equal}")

    except Exception as e:
        print(f"Weyl tensor computation: {e}")

except Exception as e:
    print(f"✗ Error in test 2: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test 3: Metric perturbation capability")
print("=" * 70)

print("Testing whether EinsteinPy supports metric perturbations...")

# EinsteinPy limitation: it's designed for static metric calculations
# It may not support dynamic metric perturbations with parameters
print("EinsteinPy limitation: primarily designed for static metric calculations")
print("May not support parameterized metric perturbations for second variation")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("EinsteinPy available but may not support:")
print("  - Parameterized metric perturbations g → g + εh")
print("  - Second variation calculations")
print("  - Automatic extraction of kinetic terms")
print("\nAlternative: Manual tensor calculation using SymPy")
print("  - Define background metric")
print("  - Define perturbation h_μν")
print("  - Compute perturbed Christoffel symbols")
print("  - Compute perturbed curvature tensors")
print("  - Expand C² to O(ε²)")
print("  - Extract Weyl-linear kinetic term")
