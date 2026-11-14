#!/usr/bin/env python3
"""
ACTUAL δ²[∫√g W₃] CALCULATION - SIMPLIFIED APPROACH
Use Cadabra2 command-line interface for actual variation calculation
"""

import subprocess
import tempfile
import os

def actual_w3_hessian_cadabra_cli():
    """
    Use Cadabra2 command-line interface to compute actual W₃ Hessian
    """
    
    print("=" * 70)
    print("ACTUAL δ²[∫√g W₃] CALCULATION USING CADABRA2 CLI")
    print("=" * 70)
    
    # Create a Cadabra2 notebook file
    cadabra_script = """
# Cadabra2 script for actual W₃ Hessian calculation
# Compute δ²[∫√g W₃] on S²×S² background

# Define indices
{\\mu,\\nu,\\rho,\\sigma,\\alpha,\\beta,\\gamma,\\delta}::Indices(position=free).

# Define metric
g_{\\mu\\nu}::Metric.
g^{\\mu\\nu}::InverseMetric.

# Define Weyl tensor
C_{\\mu\\nu\\rho\\sigma}::WeylTensor.

# Define W₃ = C·C·C
W3 := C_{\\mu\\nu\\rho\\sigma} C^{\\nu\\mu\\alpha\\beta} C^{\\sigma\\rho}{}_{\\alpha\\beta};

# Define metric perturbation
h_{\\mu\\nu}::Symmetric.

# TT conditions
tt1 := \\nabla^{\\mu} h_{\\mu\\nu} = 0;
tt2 := g^{\\mu\\nu} h_{\\mu\\nu} = 0;

# Compute first variation
# Vary W₃ with respect to metric
delta_W3 := vary(W3, g_{\\mu\\nu});

# Simplify first variation
canonicalise(_);

# Compute second variation
delta2_W3 := vary(_, g_{\\mu\\nu});

# Simplify second variation
canonicalise(_);

# Expand to see structure
expand(_);

# Extract terms with two derivatives
# Look for kinetic term structure
print("Second variation of W₃:");
_;
"""
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cnb', delete=False) as f:
        f.write(cadabra_script)
        temp_file = f.name
    
    try:
        # Run Cadabra2 CLI
        cmd = f"cd /tmp/cadabra2/build_local && PYTHONPATH=./core/packages:./core:$PYTHONPATH ./core/cadabra2-cli {temp_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        print("Cadabra2 output:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        return {
            'method': 'cadabra2_cli',
            'output': result.stdout,
            'errors': result.stderr,
            'status': 'attempted'
        }
        
    except subprocess.TimeoutExpired:
        return {
            'method': 'cadabra2_cli',
            'status': 'timeout',
            'reason': 'calculation_too_long'
        }
    except Exception as e:
        return {
            'method': 'cadabra2_cli',
            'status': 'error',
            'reason': str(e)
        }
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    result = actual_w3_hessian_cadabra_cli()
    print(f"\nMethod: {result['method']}")
    print(f"Status: {result['status']}")
