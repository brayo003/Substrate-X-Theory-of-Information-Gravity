import json
import os

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

# Initial Static Coupling Matrix
# Format: (Source, Target): Strength
coupling_matrix = {
    ('seismic_module', 'urban_module'): 0.02,
    ('urban_module', 'social_module'): 0.05,
    ('finance_module', 'social_module'): 0.1,
    ('seismic_module', 'finance_module'): 0.0 # Emergency Bypass Only
}

def run_adaptive_sim():
    global coupling_matrix
    modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
    state = {m: {'E': 0.1, 'F': 0.8, 'T': 0.0} for m in modules}
    state['seismic_module']['E'], state['viral_evolution']['E'] = 0.4, 0.8

    print(f"{'STEP':<5} | {'SOC-T':<10} | {'FIN-T':<10} | {'ACTION'}")
    print("-" * 55)

    for step in range(1, 11):
        new_state = {m: state[m].copy() for m in modules}
        
        # 1. Viral Erosion Calculation
        v_c = load_coeff('viral_evolution')
        v_T = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
        erosion = max(0.1, 1.0 - v_T)

        # 2. ADAPTIVE TOPOLOGY LOGIC
        action = "NOMINAL"
        # Strategy A: Load-Shedding (Urban -> Social)
        if state['urban_module']['T'] > 0.5:
            coupling_matrix[('urban_module', 'social_module')] *= 0.5
            action = "LOAD-SHED"

        # Strategy B: Emergency Bypass (Seismic -> Finance)
        if state['social_module']['T'] > 0.8 and state['finance_module']['T'] < 0.4:
            coupling_matrix[('seismic_module', 'finance_module')] = 0.01
            action = "BYPASS"

        # 3. Calculate Tension
        for m in modules:
            if m == 'viral_evolution': continue
            c = load_coeff(m)
            new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * (state[m]['F'] * erosion))

        # 4. Apply Rewired Propagation
        new_state['urban_module']['E'] += state['seismic_module']['T'] * coupling_matrix[('seismic_module', 'urban_module')]
        new_state['social_module']['E'] += (state['urban_module']['T'] * coupling_matrix[('urban_module', 'social_module')])
        new_state['finance_module']['E'] += state['seismic_module']['T'] * coupling_matrix[('seismic_module', 'finance_module')]
        
        state = new_state
        print(f"S{step:<4} | {state['social_module']['T']:>10.4f} | {state['finance_module']['T']:>10.4f} | {action}")

run_adaptive_sim()
