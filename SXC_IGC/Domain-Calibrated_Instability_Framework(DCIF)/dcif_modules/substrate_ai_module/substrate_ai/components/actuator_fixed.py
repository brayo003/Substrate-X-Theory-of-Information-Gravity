#!/usr/bin/env python3
"""
ACTUATOR - FINAL WORKING VERSION
No security sandbox issues - just direct execution
"""
import sympy
import numpy as np
import math

class PythonActuator:
    def __init__(self):
        # Nothing to initialize - we'll import everything directly
        pass
    
    def execute_math(self, code: str):
        """Execute math code directly"""
        try:
            # Clean and prepare the code
            code = self._clean_code(code)
            
            # Create a clean namespace
            namespace = {}
            
            # Manually import everything we need into the namespace
            exec("import sympy", namespace)
            exec("import numpy as np", namespace)
            exec("import math", namespace)
            
            # Add common sympy functions
            exec("from sympy import symbols, integrate, diff, solve, simplify, expand, factor", namespace)
            exec("from sympy import sin, cos, tan, exp, log, pi, E, I, oo", namespace)
            
            # Add common symbols
            exec("x, y, z, t = symbols('x y z t')", namespace)
            
            # Execute the user's code
            exec(code, namespace)
            
            # Look for result
            result = None
            for var_name in ['result', 'answer', 'sol', 'solution']:
                if var_name in namespace:
                    result = namespace[var_name]
                    break
            
            # If no named result, try to find any sympy expression
            if result is None:
                for key, value in namespace.items():
                    if isinstance(value, (sympy.Basic, int, float, complex)):
                        result = value
                        break
            
            # Format output
            if result is None:
                return {
                    'success': False,
                    'output': 'No result found in code',
                    'value': None,
                    'type': 'none'
                }
            
            output = str(result)
            if hasattr(result, 'evalf'):
                try:
                    numeric = result.evalf()
                    if numeric != result:
                        output = f"{output} ≈ {numeric}"
                except:
                    pass
            
            return {
                'success': True,
                'output': output,
                'value': result,
                'type': type(result).__name__
            }
            
        except Exception as e:
            return {
                'success': False,
                'output': f"Error: {type(e).__name__}: {str(e)}",
                'value': None,
                'type': 'error'
            }
    
    def _clean_code(self, code: str) -> str:
        """Clean up code"""
        # Remove markdown
        for marker in ['```python', '```', 'PYTHON']:
            code = code.replace(marker, '')
        
        # Remove lines that might cause issues
        lines = []
        for line in code.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            # Skip dangerous lines
            if any(danger in line for danger in ['import os', 'import sys', 'subprocess', '__import__']):
                continue
            lines.append(line)
        
        # Ensure we have a result variable
        cleaned = '\n'.join(lines)
        if 'result' not in cleaned and '=' in lines[-1]:
            last_line = lines[-1]
            if not last_line.startswith('result'):
                # Add result assignment
                lines[-1] = f"result = {last_line}"
                cleaned = '\n'.join(lines)
        
        return cleaned
    
    def direct_eval(self, expression: str):
        """Direct evaluation of a math expression"""
        try:
            # Simple safe evaluation for math expressions
            import sympy
            result = sympy.sympify(expression)
            return {
                'success': True,
                'output': str(result),
                'value': result
            }
        except Exception as e:
            return {
                'success': False,
                'output': str(e),
                'value': None
            }

# Test immediately
if __name__ == "__main__":
    actuator = PythonActuator()
    
    test_cases = [
        ("import sympy\nx = sympy.symbols('x')\nresult = sympy.integrate(x**2, (x, 0, 1))"),
        ("result = integrate(x**2, (x, 0, 1))"),
        ("result = sin(pi/2)"),
        ("result = 2 + 2"),
    ]
    
    print("🧪 ACTUATOR FINAL TEST")
    print("="*60)
    
    for i, code in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Code: {code}")
        result = actuator.execute_math(code)
        
        if result['success']:
            print(f"✅ SUCCESS: {result['output']}")
            print(f"   Value: {result['value']}")
            print(f"   Type: {result['type']}")
        else:
            print(f"❌ FAILED: {result['output']}")
