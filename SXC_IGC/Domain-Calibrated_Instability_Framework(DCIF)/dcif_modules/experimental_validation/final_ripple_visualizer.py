import pandas as pd
import numpy as np

def simulate_ripple():
    df = pd.read_csv('domain_scales.csv')
    dt, steps = 0.05, 500
    
    # Track Tension for three key layers
    # Source (Deep Time), Bridge (Neuroscience), Sink (Social)
    p_params = df[df['domain'] == 'paleontology'].iloc[0]
    n_params = df[df['domain'] == 'neuroscience'].iloc[0]
    s_params = df[df['domain'] == 'social_module'].iloc[0]
    
    states = { 'P': [0.0, 0.0], 'N': [0.0, 0.0], 'S': [0.0, 0.0] }
    history = []

    for i in range(steps):
        # 1. The Deep Time Pulse (Paleontology)
        force = 2.0 if 10 < i < 20 else 0.0
        a_p = force - (p_params['gamma'] * states['P'][1]) - states['P'][0]
        states['P'][1] += a_p * dt; states['P'][0] += states['P'][1] * dt
        
        # 2. Propagation to Neuroscience (Protected by V12)
        v12_n = -1.5 * states['N'][1]
        a_n = (states['P'][0] * 0.7071) + v12_n - (n_params['gamma'] * states['N'][1]) - states['N'][0]
        states['N'][1] += a_n * dt; states['N'][0] += states['N'][1] * dt
        
        # 3. Propagation to Social (Double Protected)
        v12_s = -1.5 * states['S'][1]
        a_s = (states['N'][0] * 0.7071) + v12_s - (s_params['gamma'] * states['S'][1]) - states['S'][0]
        states['S'][1] += a_s * dt; states['S'][0] += states['S'][1] * dt
        
        history.append((states['P'][0], states['N'][0], states['S'][0]))

    print("=== FINAL RIPPLE AUDIT: SYSTEM SHIELDED ===")
    h = np.array(history)
    print(f"Paleontology Peak (Source): {np.max(h[:,0]):.4f}")
    print(f"Neuroscience Peak (Bridge): {np.max(h[:,1]):.4f}")
    print(f"Social Module Peak (Sink):   {np.max(h[:,2]):.4f}")
    print(f"Total Network Attenuation: {100 - (np.max(h[:,2])/np.max(h[:,0])*100):.2f}%")

simulate_ripple()
