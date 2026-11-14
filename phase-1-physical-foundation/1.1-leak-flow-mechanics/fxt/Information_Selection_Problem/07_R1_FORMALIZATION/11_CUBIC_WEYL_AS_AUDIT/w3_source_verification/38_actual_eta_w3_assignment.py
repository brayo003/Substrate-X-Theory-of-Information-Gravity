#!/usr/bin/env python3
"""
ACTUAL η_W3 CALCULATION - USING ASSIGNMENT SYNTAX
"""

import sys
import os

sys.path.insert(0, '/tmp/cadabra2/build_local/core/packages')
sys.path.insert(0, '/tmp/cadabra2/build_local/core')

import cadabra2 as cdb

def actual_eta_w3_calculation():
    """
    Use Cadabra2 Python interface with assignment syntax
    """

    print("=" * 70)
    print("ACTUAL η_W3 CALCULATION - ASSIGNMENT SYNTAX")
    print("=" * 70)

    kernel = cdb.create_scope_from_global()

    # Define indices
    print("\nStep 1: Define indices")
    print("-" * 70)

    indices = cdb.Ex(r'{a,b,c,d,e,f,g,h,i,j}::Indices(position=independent).')
    print(indices)

    # Define metric
    print("\nStep 2: Define metric")
    print("-" * 70)

    metric = cdb.Ex(r'g_{a b}::Metric.')
    inverse_metric = cdb.Ex(r'g^{a b}::InverseMetric.')
    print(metric)
    print(inverse_metric)

    # Define derivatives
    print("\nStep 3: Define derivatives")
    print("-" * 70)

    partial = cdb.Ex(r'\partial{#}::PartialDerivative.')
    derivative = cdb.Ex(r'{\nabla{#},\Delta{#}}::Derivative.')
    print(partial)
    print(derivative)

    # Define connection with dependence
    print("\nStep 4: Define connection")
    print("-" * 70)

    gamma_depends = cdb.Ex(r'Gamma^{a}_{b c}::Depends(\partial{#}).')
    print(gamma_depends)

    # Define Riemann tensor with assignment syntax
    print("\nStep 5: Define Riemann tensor (assignment)")
    print("-" * 70)

    riemann = cdb.Ex(r'riemann := R^{d}_{e a b} = \partial_{a}{Gamma^{d}_{e b}} -\partial_{b}{Gamma^{d}_{e a}} + Gamma^{d}_{a f} Gamma^{f}_{e b} -Gamma^{d}_{b f} Gamma^{f}_{e a}')
    print(riemann)

    # Define variation symbols
    print("\nStep 6: Define variation symbols")
    print("-" * 70)

    delta_gamma = cdb.Ex(r'DeltaGamma^{a}_{b c}::TableauSymmetry(shape={2}, indices={1,2}).')
    delta_riemann = cdb.Ex(r'DeltaR^{d}_{e a b}::TableauSymmetry(shape={2,2}, indices={1,2,3,4}).')
    print(delta_gamma)
    print(delta_riemann)

    # Vary Riemann tensor
    print("\nStep 7: Vary Riemann tensor")
    print("-" * 70)

    try:
        delta_riemann_expr = cdb.vary(riemann, cdb.Ex(r'$ Gamma^{a}_{b c} -> DeltaGamma^{a}_{b c}, R^{d}_{e a b} -> DeltaR^{d}_{e a b} $'))
        print("δRiemann computed successfully")
        print(delta_riemann_expr)

        # Simplify
        print("\nStep 8: Simplify δRiemann")
        print("-" * 70)

        simplified = cdb.sort_product(delta_riemann_expr)
        print(simplified)

        return {
            'method': 'cadabra2_python',
            'delta_riemann': str(delta_riemann_expr),
            'simplified': str(simplified),
            'status': 'riemann_variation_success'
        }

    except Exception as e:
        print(f"Error with vary: {e}")
        import traceback
        traceback.print_exc()

        return {
            'method': 'cadabra2_python',
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    result = actual_eta_w3_calculation()
    print(f"\nMethod: {result['method']}")
    print(f"Status: {result['status']}")
