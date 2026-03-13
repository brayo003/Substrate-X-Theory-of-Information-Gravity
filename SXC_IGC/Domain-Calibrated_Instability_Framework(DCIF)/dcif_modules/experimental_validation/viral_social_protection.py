import pandas as pd
import numpy as np

def run_viral_test():
    df = pd.read_csv('domain_scales.csv')
    viral = df[df['domain'] == 'Viral_Evolution'].iloc[0]
    social = df[df['domain'] == 'social_module'].iloc[0]
    
    dt, steps = 0.01, 2000
    s_viral, s_social = [0.0, 0.0], [0.0, 0.0]
    
    results = []
    for i in range(steps):
        # A sharp "Outbreak" pulse (Delta function approximation)
        outbreak = 5.0 if 100 < i < 110 else 0.0
        
        # 1. Viral Evolution Dynamics
        a_v = outbreak - (viral['gamma'] * s_viral[1]) - s_viral[0]
        s_viral[1] += a_v * dt; s_viral[0] += s_viral[1] * dt
        
        # 2. V12 Decoupling (The Safety Valve)
        entangled_load = 0.7071 * s_viral[0]
        v12_brake = -2.0 * s_social[1] # Increased braking for social stability
        
        # 3. Social Module Dynamics
        a_soc = entangled_load + v12_brake - (social['gamma'] * s_social[1]) - s_social[0]
        s_social[1] += a_soc * dt; s_social[0] += s_social[1] * dt
        
        results.append((s_viral[0], s_social[0]))

    res_df = pd.DataFrame(results, columns=['Viral_T', 'Social_T'])
    print(f"=== VIRAL-SOCIAL OUTBREAK AUDIT ===")
    print(f"Viral Peak Tension: {res_df['Viral_T'].max():.4f}")
    print(f"Social Peak Tension (Protected): {res_df['Social_T'].max():.4f}")
    print(f"Containment Efficiency: {100 - (res_df['Social_T'].max() / res_df['Viral_T'].max() * 100):.2f}%")

run_viral_test()
