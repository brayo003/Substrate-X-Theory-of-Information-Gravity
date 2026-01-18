import numpy as np
import sys
sys.path.insert(0, '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/assets/qftgrbrigbe/b')
from new_v12 import MasterBridgeV12

# Test on a large galaxy that previously failed (UGC09133, M=2.63e42)
bridge = MasterBridgeV12(2.63e42)
print(f"Mass: 2.63e42 kg")
print(f"b = {bridge.b:.2e}")

# Calculate x at a typical distance
distance = 4.7e20  # 50k ly
x = bridge.get_equilibrium_tension(distance)
print(f"x at {distance:.1e} m = {x:.2e}")

# Old formula gave x ~ 1e82, new should give ~1e-10
if x > 1e50:
    print("❌ STILL USING OLD FORMULA (cubic mass scaling)")
elif x < 1:
    print("✅ USING NEW FORMULA (mass-linear)")
else:
    print(f"⚠️ Intermediate value: {x:.2e}")
