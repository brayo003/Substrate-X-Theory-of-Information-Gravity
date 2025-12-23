import json
import os

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

def run_redundancy(parallel=False):
    modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
    state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0} for m in modules}
    state['seismic_module']['E'], state['viral_evolution']['E'] = 0.4, 0.8
    
    # If parallel, we double the effective F of the financial floor
    if parallel: state['finance_module']['F'] = 1.2 

    for step in range(1, 11):
        new_state = {m: state[m].copy() for m in modules}
        v_c = load_coeff('viral_evolution')
        v_T = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
        erosion = max(0.1, 1.0 - v_T)

        for m in modules:
            if m == 'viral_evolution': continue
            c = load_coeff(m)
            # Parallel systems share the erosion tax more efficiently
            new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * (state[m]['F'] * erosion))

        # Propagation
        new_state['urban_module']['E'] += state['seismic_module']['T'] * 0.02
        new_state['social_module']['E'] += (state['urban_module']['T'] * 0.05) + (state['finance_module']['T'] * 0.1)
        state = new_state
    return state['social_module']['T']

print(f"SINGLE ENGINE TENSION (S10): {run_redundancy(parallel=False):.4f}")
print(f"REDUNDANT ENGINE TENSION (S10): {run_redundancy(parallel=True):.4f}")
