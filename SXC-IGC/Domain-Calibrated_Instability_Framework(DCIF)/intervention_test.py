import json
import os

def run_sim(intervention_type):
    def load_coeff(m):
        p = f"./dcif_modules/{m}/coefficients.json"
        if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
        with open(p, 'r') as f: return json.load(f)['coefficients']

    modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
    state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0} for m in modules}
    state['seismic_module']['E'], state['viral_evolution']['E'] = 0.4, 0.8

    if intervention_type == "BAILOUT": state['finance_module']['F'] = 1.0
    if intervention_type == "HOSPITAL": state['social_module']['E'] = 0.05

    for step in range(1, 11):
        new_state = {m: state[m].copy() for m in modules}
        v_c = load_coeff('viral_evolution')
        state['viral_evolution']['T'] = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
        erosion = max(0.1, 1.0 - state['viral_evolution']['T'])

        for m in modules:
            if m == 'viral_evolution': continue
            c = load_coeff(m)
            new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * (state[m]['F'] * erosion))

        if state['social_module']['T'] >= 0.9:
            sev = state['social_module']['T'] - 0.9
            new_state['finance_module']['F'] *= (1.0 - (sev * 0.3))
            new_state['finance_module']['E'] += sev * 0.2

        new_state['urban_module']['E'] += state['seismic_module']['T'] * 0.02
        new_state['social_module']['E'] += (state['urban_module']['T'] * 0.05) + (state['finance_module']['T'] * 0.1)
        state = new_state
    return state['social_module']['T'], state['finance_module']['T']

b_soc, b_fin = run_sim("BAILOUT")
h_soc, h_fin = run_sim("HOSPITAL")

print(f"{'STRATEGY':<15} | {'FINAL SOCIAL-T':<15} | {'FINAL FINANCE-T':<15}")
print("-" * 55)
print(f"{'BAILOUT':<15} | {b_soc:>15.4f} | {b_fin:>15.4f}")
print(f"{'FIELD HOSPITAL':<15} | {h_soc:>15.4f} | {h_fin:>15.4f}")
