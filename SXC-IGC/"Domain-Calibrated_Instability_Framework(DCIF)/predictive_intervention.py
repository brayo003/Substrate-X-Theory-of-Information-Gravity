import json
import os

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

def run_simulation(mode="reactive"):
    # Initial Setup
    coupling = {
        ('seismic_module', 'urban_module'): 0.02,
        ('urban_module', 'social_module'): 0.05,
        ('finance_module', 'social_module'): 0.1
    }
    modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
    state = {m: {'E': 0.1, 'F': 0.8, 'T': 0.0} for m in modules}
    state['seismic_module']['E'], state['viral_evolution']['E'] = 0.4, 0.8

    for step in range(1, 11):
        new_state = {m: state[m].copy() for m in modules}
        v_c = load_coeff('viral_evolution')
        erosion = max(0.1, 1.0 - ((v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])))

        # INTERVENTION LOGIC
        if mode == "reactive":
            if state['urban_module']['T'] > 0.7:
                coupling[('urban_module', 'social_module')] *= 0.5
        
        elif mode == "predictive":
            # Lookahead: Projected Target T = Current T + (Source T * link * 3 steps)
            projected_social_T = state['social_module']['T'] + (state['urban_module']['T'] * coupling[('urban_module', 'social_module')] * 3)
            if projected_social_T > 0.6 and state['social_module']['T'] < 0.4:
                coupling[('urban_module', 'social_module')] *= 0.3

        # Physics Step
        for m in modules:
            if m == 'viral_evolution': continue
            c = load_coeff(m)
            new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * (state[m]['F'] * erosion))

        new_state['urban_module']['E'] += state['seismic_module']['T'] * coupling[('seismic_module', 'urban_module')]
        new_state['social_module']['E'] += (state['urban_module']['T'] * coupling[('urban_module', 'social_module')])
        state = new_state
    
    return state['social_module']['T']

print(f"REACTIVE FINAL T: {run_simulation('reactive'):.4f}")
print(f"PREDICTIVE FINAL T: {run_simulation('predictive'):.4f}")
