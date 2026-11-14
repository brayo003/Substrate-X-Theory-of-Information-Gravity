import pandas as pd
import numpy as np

def run_stabilization_test():
    df = pd.read_csv('domain_scales.csv')
    seismic = df[df['domain'] == 'seismic_module'].iloc[0]
    finance = df[df['domain'] == 'finance_module'].iloc[0]
    dark_matter = df[df['domain'] == 'dark_matter'].iloc[0]
    
    dt, steps = 0.01, 1000
    coupling = 1 / np.sqrt(2)
    
    # States: [Tension, Velocity]
    s_seis, s_fin, s_dm = [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]
    
    results = []
    for i in range(steps):
        force = np.sin(2 * np.pi * i * dt) if i < 100 else 0.0
        
        # 1. Seismic Source
        a_s = force - (seismic['gamma'] * s_seis[1]) - s_seis[0]
        s_seis[1] += a_s * dt; s_seis[0] += s_seis[1] * dt
        
        # 2. Dark Matter (The Anchor - barely moves)
        a_dm = (s_seis[0] * coupling) - (dark_matter['gamma'] * s_dm[1]) - s_dm[0]
        s_dm[1] += a_dm * dt; s_dm[0] += s_dm[1] * dt
        
        # 3. Finance (Stabilized by DM)
        # Finance is now coupled to BOTH Seismic (Force) and Dark Matter (Brake)
        entangled_input = (s_seis[0] * coupling) + (s_dm[0] * coupling)
        a_f = entangled_input - (finance['gamma'] * s_fin[1]) - s_fin[0]
        s_fin[1] += a_f * dt; s_fin[0] += s_fin[1] * dt
        
        results.append((s_seis[0], s_fin[0]))

    res_df = pd.DataFrame(results, columns=['Seis_T', 'Fin_T'])
    print(f"STABILIZED Transmission Efficiency: {(res_df['Fin_T'].max() / res_df['Seis_T'].max()) * 100:.2f}%")

run_stabilization_test()
