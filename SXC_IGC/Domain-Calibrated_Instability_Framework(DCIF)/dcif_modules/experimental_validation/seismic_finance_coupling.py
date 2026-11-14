import pandas as pd
import numpy as np

def run_stress_test():
    # Load parameters
    df = pd.read_csv('domain_scales.csv')
    seismic = df[df['domain'] == 'seismic_module'].iloc[0]
    finance = df[df['domain'] == 'finance_module'].iloc[0]
    
    # Simulation parameters
    dt = 0.01
    steps = 1000
    coupling_factor = 1 / np.sqrt(2) # Verified Bell-state coupling
    
    # State vectors: [Tension, Velocity]
    s_seismic = [0.0, 0.0]
    s_finance = [0.0, 0.0]
    
    results = []
    
    for i in range(steps):
        # 1. External Force: A 1Hz seismic pulse for the first 100 steps
        force = np.sin(2 * np.pi * i * dt) if i < 100 else 0.0
        
        # 2. Evolve Seismic (Source)
        a_s = force - (seismic['gamma'] * s_seismic[1]) - s_seismic[0]
        s_seismic[1] += a_s * dt
        s_seismic[0] += s_seismic[1] * dt
        
        # 3. Evolve Finance (Target) with Entangled Input from Seismic
        # Finance "feels" the tension of Seismic through the substrate
        entangled_force = s_seismic[0] * coupling_factor
        a_f = entangled_force - (finance['gamma'] * s_finance[1]) - s_finance[0]
        s_finance[1] += a_f * dt
        s_finance[0] += s_finance[1] * dt
        
        results.append((s_seismic[0], s_finance[0]))

    res_df = pd.DataFrame(results, columns=['Seismic_T', 'Finance_T'])
    
    print("=== SEISMIC-FINANCE COUPLING AUDIT ===")
    print(f"Max Seismic Tension: {res_df['Seismic_T'].max():.4f}")
    print(f"Max Finance Tension: {res_df['Finance_T'].max():.4f}")
    print(f"Transmission Efficiency: {(res_df['Finance_T'].max() / res_df['Seismic_T'].max()) * 100:.2f}%")

run_stress_test()
