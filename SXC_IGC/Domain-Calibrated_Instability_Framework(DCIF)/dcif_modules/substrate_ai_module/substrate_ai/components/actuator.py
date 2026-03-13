# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
ACTUATOR - Fixed version with proper imports
"""
import sympy
import numpy as np
import math
import ast

class PythonActuator:
    def __init__(self):
        # Pre-import all safe modules
        self.safe_builtins = {
            'abs': abs, 'min': min, 'max': max, 'sum': sum,
            'len': len, 'range': range, 'round': round, 'pow': pow,
            'str': str, 'int': int, 'float': float, 'bool': bool,
            'list': list, 'dict': dict, 'set': set, 'tuple': tuple,
            'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter,
            'sorted': sorted, 'reversed': reversed,
        }
        
        self.safe_modules = {
            'sympy': sympy,
            'sp': sympy,  # Common alias
            'np': np,
            'numpy': np,
            'math': math,
            '__builtins__': self.safe_builtins
        }
    
    def execute_math(self, code: str):
        """Execute math code safely"""
        try:
            # Clean the code
            code = self._clean_code(code)
            
            # Create execution environment with ALL needed imports
            exec_env = {}
            
            # Add all safe modules and builtins
            exec_env.update(self.safe_modules)
            exec_env.update(self.safe_builtins)
            
            # Add sympy common functions
            exec_env.update({
                'symbols': sympy.symbols,
                'integrate': sympy.integrate,
                'diff': sympy.diff,
                'solve': sympy.solve,
                'simplify': sympy.simplify,
                'expand': sympy.expand,
                'factor': sympy.factor,
                'sin': sympy.sin,
                'cos': sympy.cos,
                'tan': sympy.tan,
                'exp': sympy.exp,
                'log': sympy.log,
                'pi': sympy.pi,
                'E': sympy.E,
                'I': sympy.I,
                'oo': sympy.oo,  # infinity
                'x': sympy.symbols('x'),
                'y': sympy.symbols('y'),
                'z': sympy.symbols('z'),
                't': sympy.symbols('t'),
            })
            
            # Execute the code
            exec(code, exec_env)
            
            # Look for result in various possible variables
            result = None
            possible_result_vars = ['result', 'answer', 'sol', 'solution', 'res']
            
            for var in possible_result_vars:
                if var in exec_env:
                    result = exec_env[var]
                    break
            
            # If no result variable found, try to get last expression
            if result is None:
                # Parse code and evaluate last expression
                tree = ast.parse(code)
                if tree.body and isinstance(tree.body[-1], ast.Expr):
                    last_expr = tree.body[-1]
                    result_code = compile(ast.Expression(last_expr.value), '<string>', 'eval')
                    result = eval(result_code, exec_env)
            
            # Format the result nicely
            if hasattr(result, '__str__'):
                output = str(result)
                if hasattr(result, 'evalf'):  # Sympy objects
                    try:
                        numeric = result.evalf()
                        if numeric != result:
                            output = f"{output} ≈ {numeric}"
                    except:
                        pass
            else:
                output = str(result)
            
            return {
                'success': True,
                'output': output,
                'value': result,
                'type': type(result).__name__ if result is not None else 'None'
            }
            
        except Exception as e:
            return {
                'success': False,
                'output': f"Error: {type(e).__name__}: {str(e)}",
                'value': None,
                'type': 'error'
            }
    
    def _clean_code(self, code: str) -> str:
        """Clean and fix common code issues"""
        # Remove markdown
        code = code.replace('```python', '').replace('```', '').strip()
        
        # Fix common import patterns
        import_fixes = [
            ('import sympy as sp', 'import sympy\nsp = sympy'),
            ('import numpy as np', 'import numpy\nnp = numpy'),
            ('from sympy import *', 'import sympy\nfrom sympy import symbols, integrate, diff, solve, simplify'),
            ('import math as m', 'import math\nm = math'),
        ]
        
        for old, new in import_fixes:
            if old in code:
                code = code.replace(old, new)
        
        # Ensure result variable exists
        if 'result' not in code and '=' in code:
            # Add result variable assignment for last line
            lines = code.strip().split('\n')
            last_line = lines[-1].strip()
            if not last_line.startswith('result') and '=' in last_line:
                lines[-1] = f"result = {last_line}"
                code = '\n'.join(lines)
        
        return code
    
    def safe_execute(self, expression: str, variables: dict = None):
        """Safe execution of a single expression"""
        try:
            exec_env = self.safe_modules.copy()
            if variables:
                exec_env.update(variables)
            
            result = eval(expression, exec_env)
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

# Test the actuator immediately
if __name__ == "__main__":
    actuator = PythonActuator()
    
    test_cases = [
        ("import sympy\nx = sympy.symbols('x')\nresult = sympy.integrate(x**2, (x, 0, 1))"),
        ("import numpy as np\nresult = np.array([1, 2, 3]).sum()"),
        ("import math\nresult = math.pi * 2"),
        ("x = symbols('x')\nresult = integrate(x**2, (x, 0, 1))"),
    ]
    
    print("🧪 Testing Actuator Fix")
    print("="*60)
    
    for i, code in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Code: {code[:50]}...")
        result = actuator.execute_math(code)
        
        if result['success']:
            print(f"✅ Success: {result['output']}")
        else:
            print(f"❌ Failed: {result['output']}")
