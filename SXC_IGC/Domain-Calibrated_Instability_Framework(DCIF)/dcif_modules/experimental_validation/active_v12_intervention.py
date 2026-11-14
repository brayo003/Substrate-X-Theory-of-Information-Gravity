import pandas as pd
import numpy as np

def run_active_test():
    df = pd.read_csv('domain_scales.csv')
    seis = df[df['domain'] == 'seismic_module'].iloc[0]
    fin = df[df['domain'] == 'finance_module'].iloc[0]
    
    dt, steps = 0.01, 1000
    s_seis, s_fin = [0.0, 0.0], [0.0, 0.0]
    
    results = []
    for i in range(steps):
        force = np.sin(2 * np.pi * i * dt) if i < 100 else 0.0
        
        # 1. Seismic Evolution
        a_s = force - (seis['gamma'] * s_seis[1]) - s_seis[0]
        s_seis[1] += a_s * dt; s_seis[0] += s_seis[1] * dt
        
        # 2. V12 ACTIVE COUNTER-MEASURE
        # Instead of 0.7071 coupling, we apply -0.7071 * Velocity 
        # to kill the momentum before it manifests as tension.
        v12_active_damping = -0.7071 * s_seis[1]
        
        # 3. Finance Evolution (Protected)
        a_f = (s_seis[0] * 0.7071) + v12_active_damping - (fin['gamma'] * s_fin[1]) - s_fin[0]
        s_fin[1] += a_f * dt; s_fin[0] += s_fin[1] * dt
        
        results.append((s_seis[0], s_fin[0]))

    res_df = pd.DataFrame(results, columns=['S_T', 'F_T'])
    print(f"ACTIVE V12 Protection Efficiency: {(res_df['F_T'].max() / res_df['S_T'].max()) * 100:.2f}%")

run_active_test()
