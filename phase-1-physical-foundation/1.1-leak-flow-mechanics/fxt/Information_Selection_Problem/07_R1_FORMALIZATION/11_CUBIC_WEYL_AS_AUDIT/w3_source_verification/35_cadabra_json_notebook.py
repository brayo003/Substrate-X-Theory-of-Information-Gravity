#!/usr/bin/env python3
"""
Use Cadabra2 to compute actual W₃ Hessian
Based on the variational_derivatives.cnb example
"""

import subprocess
import json

def create_cadabra_notebook():
    """
    Create a Cadabra2 notebook for W₃ Hessian calculation
    """
    
    notebook = {
        "cells": [
            {
                "cell_origin": "client",
                "cell_type": "latex",
                "cells": [
                    {
                        "cell_origin": "client",
                        "cell_type": "latex_view",
                        "source": r"\section*{W₃ Hessian Calculation}\n\nCalculate δ²[∫√g W₃] to extract kinetic term coefficient for η_W3"
                    }
                ],
                "hidden": True,
                "source": r"\section*{W₃ Hessian Calculation}\n\nCalculate δ²[∫√g W₃] to extract kinetic term coefficient for η_W3"
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\text{Attached property Indices to~}\{\mu,\nu,\rho,\sigma,\alpha,\beta\}.\end{dmath*}"
                    },
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\text{Attached property Metric to~}g_{\mu\nu}.\end{dmath*}"
                    },
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\text{Attached property WeylTensor to~}C_{\mu\nu\rho\sigma}.\end{dmath*}"
                    }
                ],
                "source": r"{\mu,\nu,\rho,\sigma,\alpha,\beta}::Indices(position=free).\ng_{\mu\nu}::Metric.\nC_{\mu\nu\rho\sigma}::WeylTensor."
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}C_{\mu\nu\rho\sigma} C^{\nu\mu\alpha\beta} C^{\sigma\rho}{}_{\alpha\beta}\end{dmath*}"
                    }
                ],
                "source": r"W3 := C_{\mu\nu\rho\sigma} C^{\nu\mu\alpha\beta} C^{\sigma\rho}{}_{\alpha\beta};"
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\text{Attached property Symmetric to~}h_{\mu\nu}.\end{dmath*}"
                    },
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\text{Attached property Accent to~}\delta{#}.\end{dmath*}"
                    }
                ],
                "source": r"h_{\mu\nu}::Symmetric.\n\delta{#}::Accent."
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\int{} \sqrt{-g} W_{3}\, {\rm d}x\end{dmath*}"
                    }
                ],
                "source": r"S := \int{ \sqrt{-g} W3 }{x};"
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\frac{1}{2}\int{} \sqrt{-g} \delta{g_{\mu\nu}} \partial_{\rho\sigma}{W_{3}} \delta{g_{\mu\nu}}\, {\rm d}x\end{dmath*}"
                    }
                ],
                "source": r"vary(S, $g_{\mu\nu} -> \delta{g_{\mu\nu}}$);"
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\frac{1}{2}\int{} \sqrt{-g} \delta{g_{\mu\nu}} \partial_{\rho\sigma}{W_{3}} \delta{g_{\mu\nu}}\, {\rm d}x\end{dmath*}"
                    }
                ],
                "source": r"canonicalise(_);"
            },
            {
                "cell_origin": "client",
                "cell_type": "latex",
                "cells": [
                    {
                        "cell_origin": "client",
                        "cell_type": "latex_view",
                        "source": "This gives the first variation. Now compute second variation by varying again."
                    }
                ],
                "hidden": True,
                "source": "This gives the first variation. Now compute second variation by varying again."
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\frac{1}{4}\int{} \sqrt{-g} \delta{g_{\mu\nu}} \partial_{\rho\sigma\alpha\beta}{W_{3}} \delta{g_{\alpha\beta}}\, {\rm d}x\end{dmath*}"
                    }
                ],
                "source": r"vary(_, $g_{\mu\nu} -> \delta{g_{\mu\nu}}$);"
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\frac{1}{4}\int{} \sqrt{-g} \delta{g_{\mu\nu}} \partial_{\rho\sigma\alpha\beta}{W_{3}} \delta{g_{\alpha\beta}}\, {\rm d}x\end{dmath*}"
                    }
                ],
                "source": r"canonicalise(_);"
            },
            {
                "cell_origin": "client",
                "cell_type": "input",
                "cells": [
                    {
                        "cell_origin": "server",
                        "cell_type": "latex_view",
                        "source": r"\begin{dmath*}{}\frac{1}{4}\int{} \sqrt{-g} \delta{g_{\mu\nu}} \partial_{\rho\sigma\alpha\beta}{W_{3}} \delta{g_{\alpha\beta}}\, {\rm d}x\end{dmath*}"
                    }
                ],
                "source": r"expand(_);"
            },
            {
                "cell_origin": "client",
                "cell_type": "latex",
                "cells": [
                    {
                        "cell_origin": "client",
                        "cell_type": "latex_view",
                        "source": "The result shows the second variation structure. Now we need to extract the kinetic term coefficient."
                    }
                ],
                "hidden": True,
                "source": "The result shows the second variation structure. Now we need to extract the kinetic term coefficient."
            }
        ],
        "description": "W₃ Hessian calculation for η_W3",
        "version": 1
    }
    
    with open('/tmp/w3_hessian_proper.cnb', 'w') as f:
        json.dump(notebook, f, indent=2)
    
    return '/tmp/w3_hessian_proper.cnb'

def run_cadabra_calculation():
    """
    Run Cadabra2 with the proper notebook
    """
    
    notebook_file = create_cadabra_notebook()
    
    cmd = f"cd /tmp/cadabra2/build_local && PYTHONPATH=./core/packages:./core:$PYTHONPATH ./core/cadabra2-cli {notebook_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    
    print("Cadabra2 output:")
    print(result.stdout)
    
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result

if __name__ == "__main__":
    result = run_cadabra_calculation()
