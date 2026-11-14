import sys
import os
# Force the path to include the Core
sys.path.append(os.path.abspath('../../'))

try:
    from SXC_V12_CORE import SXCOmegaEngine
    print("✓ CORE ENGINE LINKED: Substrate-X V12 found.")
except ImportError:
    print("! ERROR: Core not found. Check directory structure.")
    sys.exit()

# Initialize the Engine with your 0.1199 Stability Logic
engine = SXCOmegaEngine()
print(f"Operationalizing Stability Constant: {0.1199}")

# Test the 'Biological Orbit' on the Core Engine
tension, integrity = engine.step(15.0) # Simulate moderate metabolic signal
print(f"Audit Result -> Tension: {tension:.4f} | Substrate Integrity: {integrity:.4f}")
