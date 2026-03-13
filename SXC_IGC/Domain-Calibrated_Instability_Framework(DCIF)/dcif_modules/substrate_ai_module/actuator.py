# V12_SYNC_VERIFIED: 2026-03-13
import subprocess
import os

class PythonActuator:
    def execute_math(self, code_payload):
        print(f"🛠️  ACTUATOR: Offloading to Python...")
        full_code = f"import sympy\nfrom sympy import *\n{code_payload}"
        
        with open("temp_solve.py", "w") as f:
            f.write(full_code)
            
        try:
            result = subprocess.check_output(
                ["python3", "temp_solve.py"], 
                stderr=subprocess.STDOUT, 
                timeout=5
            )
            return {"success": True, "output": result.decode().strip()}
        except subprocess.CalledProcessError as e:
            return {"success": False, "output": e.output.decode().strip()}
        except Exception as e:
            return {"success": False, "output": str(e)}
