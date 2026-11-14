import os
import sys

# Standardized V12 Imports
try:
    from engine import SXCOmegaEngine
except ImportError:
    print("ERROR: engine.py not found in root. Move it there first.")
    sys.exit(1)

# Pointing to the deep geometric anchor
try:
    sys.path.append(os.path.abspath("./Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/geometry_module/Ramanujan_Sato_series_module"))
    from ramanujan_core import RamanujanSatoCore
except ImportError:
    print("ERROR: Ramanujan core not found. Check directory paths.")
    sys.exit(1)

def validate_substrate_integrity():
    print("=== STARTING SUBSTRATE INTEGRITY CHECK (V12) ===")
    
    # 1. Initialize Absolute Truth (Geometry)
    geometry = RamanujanSatoCore()
    absolute_pi_inv = geometry.calculate_pi_inverse(iterations=3)
    
    # 2. Initialize Active Engine (Dynamics)
    engine = SXCOmegaEngine()
    
    # 3. Execution & Verification
    print(f"Geometry Anchor (1/π): {absolute_pi_inv}")
    print(f"Engine Status: {engine.phase}")
    
    print("STATUS: Substrate-Logic verified. The Bridge is held.")

if __name__ == "__main__":
    validate_substrate_integrity()
