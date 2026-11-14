import pandas as pd
import numpy as np

def run_decoupling_test():
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
        
        # 2. TRUE DECOUPLING (Differential Damping)
        # We couple to the SOURCE tension (0.7071) but SUBTRACT the TARGET'S
        # own velocity to prevent runaway oscillation.
        coupling = 0.7071 * s_seis[0]
        v12_active_brake = -1.5 * s_fin[1] # Strong local damping
        
        # 3. Finance Evolution
        a_f = coupling + v12_active_brake - (fin['gamma'] * s_fin[1]) - s_fin[0]
        s_fin[1] += a_f * dt; s_fin[0] += s_fin[1] * dt
        
        results.append((s_seis[0], s_fin[0]))

    res_df = pd.DataFrame(results, columns=['S_T', 'F_T'])
    print(f"DECOUPLED Protection Efficiency: {(res_df['F_T'].max() / res_df['S_T'].max()) * 100:.2f}%")

run_decoupling_test()
