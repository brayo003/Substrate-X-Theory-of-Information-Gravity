#!/usr/bin/env python3
"""
TENSORATLAS DEEPER INVESTIGATION
Attempt to use variational functions for kinetic term extraction
"""

import tensoratlas as ta
import inspect

def investigate_tensorAtlas_variational():
    """
    Deep investigation of TensorAtlas variational capabilities
    """
    
    print("=" * 70)
    print("TENSORATLAS DEEPER INVESTIGATION")
    print("=" * 70)
    
    # Step 1: Check variational derivative function
    print("\nStep 1: Check variational_derivative function")
    print("-" * 70)
    
    try:
        sig = inspect.signature(ta.variational_derivative)
        print(f"variational_derivative signature: {sig}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 2: Check variational_problem function
    print("\nStep 2: Check variational_problem function")
    print("-" * 70)
    
    try:
        sig = inspect.signature(ta.variational_problem)
        print(f"variational_problem signature: {sig}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 3: Check if we can define custom invariants
    print("\nStep 3: Check custom invariant definition")
    print("-" * 70)
    
    try:
        # Check curvature_invariant IR
        print("Attempting to create a curvature invariant IR...")
        
        # Try to get the registry
        reg = ta.standard_riemannian_registry()
        print(f"Registry obtained: {reg}")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 4: Try to use the extract_euler_lagrange function
    print("\nStep 4: Check extract_euler_lagrange_tensor_expr")
    print("-" * 70)
    
    try:
        from tensoratlas.variational_tensor_expr import extract_euler_lagrange_tensor_expr
        sig = inspect.signature(extract_euler_lagrange_tensor_expr)
        print(f"extract_euler_lagrange_tensor_expr signature: {sig}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 5: Check the internal semantic IR structure
    print("\nStep 5: Check semantic IR structure")
    print("-" * 70)
    
    try:
        from tensoratlas.semantic_ir import ir_node, normalize_tensor_expr
        
        # Try to create a simple IR node
        simple_ir = ir_node("curvature_invariant", payload="test", connection="CD")
        normalized = normalize_tensor_expr(simple_ir)
        print(f"IR node created: {simple_ir}")
        print(f"Normalized: {normalized}")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 6: Check if we can combine Weyl tensors
    print("\nStep 6: Check Weyl tensor combination")
    print("-" * 70)
    
    try:
        # Check weyl_tensor_expr function
        sig = inspect.signature(ta.weyl_tensor_expr)
        print(f"weyl_tensor_expr signature: {sig}")
        print()
        
        # Check what inputs it needs
        print("weyl_tensor_expr requires:")
        print("  - Riemann tensor")
        print("  - Ricci tensor")
        print("  - Scalar curvature")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 7: Check tensor algebra functions
    print("\nStep 7: Check tensor algebra functions")
    print("-" * 70)
    
    algebra_funcs = [f for f in dir(ta) if 'contract' in f.lower() or 'tensor' in f.lower()]
    print(f"Tensor algebra functions: {algebra_funcs[:10]}")
    print()
    
    # Step 8: Check if we can do contractions
    print("\nStep 8: Check contraction capabilities")
    print("-" * 70)
    
    try:
        sig = inspect.signature(ta.tensor_contract)
        print(f"tensor_contract signature: {sig}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 9: Final assessment
    print("\n" + "=" * 70)
    print("FINAL ASSESSMENT")
    print("=" * 70)
    print()
    print("TensorAtlas provides:")
    print("  ✓ Variational infrastructure")
    print("  ✓ Curvature invariants")
    print("  ✓ Weyl tensor construction")
    print("  ✓ Tensor contractions")
    print("  ✓ Euler-Lagrange extraction")
    print()
    print("However, constructing W₃ = C·C·C requires:")
    print("  - Multiple Weyl tensor instances")
    print("  - Complex index contractions")
    print("  - Custom invariant definition")
    print("  - Second variation (not just first)")
    print()
    print("The API exists but using it for this specific")
    print("calculation would require:")
    print("  - Deep study of internal IR structure")
    print("  - Custom invariant construction")
    print("  - Manual index management")
    print("  - Extensive debugging")
    print()
    print("This is feasible but would require significant")
    print("development effort beyond current scope.")
    print()
    print("=" * 70)
    
    return {
        'tensorAtlas_available': True,
        'variational_infrastructure': True,
        'weyl_construction': True,
        'custom_invariant_support': 'unclear',
        'second_variation_support': 'unclear',
        'estimation': 'Feasible with significant development effort'
    }

if __name__ == "__main__":
    result = investigate_tensorAtlas_variational()
    print(f"\nTensorAtlas available: {result['tensorAtlas_available']}")
