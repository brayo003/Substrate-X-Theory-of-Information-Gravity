import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Modify new_v12 temporarily to test different b scaling
import new_v12

print("Testing different b scaling laws:")
print(f"{'Scaling':<15} {'Avg ratio':<10} {'Std dev':<10} {'Within 10%':<10}")
print("-" * 55)

original_code = open('new_v12.py').read()

for power in [2.0, 1.5, 1.0, 0.5]:
    # Create modified version with b ∝ 1/M^power
    modified = original_code.replace(
        'self.b = 1.0 / self.S_bh',
        f'self.b = 1.0 / (self.S_bh * (self.M/1.989e30)**{power-2:.1f})'
    )
    
    # Write and test
    with open('temp_new_v12.py', 'w') as f:
        f.write(modified)
    
    # Import the modified version
    import temp_new_v12 as mod
    import importlib
    importlib.reload(mod)
    
    # Test on a few galaxies
    ratios = []
    for filename in os.listdir('sparc_data')[:20]:
        if filename.endswith('_rotmod.dat'):
            filepath = os.path.join('sparc_data', filename)
            data = np.loadtxt(filepath)
            r_max_kpc = data[-1, 0]
            v_obs = data[-1, 1]
            
            r_max_m = r_max_kpc * 3.086e19
            v_obs_m_s = v_obs * 1000
            g_obs = v_obs_m_s**2 / r_max_m
            M_est = g_obs * r_max_m**2 / 6.67430e-11
            
            bridge = mod.MasterBridgeV12(M_est)
            g_v12 = bridge.calculate_gravity_acceleration(r_max_m)
            ratios.append(g_v12 / g_obs)
    
    print(f"b ∝ 1/M^{power:.1f}  {np.mean(ratios):<10.2f} {np.std(ratios):<10.2f} {sum(0.9<r<1.1 for r in ratios):<10}")
