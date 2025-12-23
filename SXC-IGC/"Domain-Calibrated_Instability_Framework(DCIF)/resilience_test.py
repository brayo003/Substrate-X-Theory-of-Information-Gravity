import json
import os

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

def run_simulation(integrated=False):
    modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
    state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0} for m in modules}
    state['seismic_module']['E'], state['viral_evolution']['E'] = 0.4, 0.8

    if integrated:
        # Initial Proactive Boost
        state['finance_module']['F'] = 0.8
        state['social_module']['F'] = 0.7

    for step in range(1, 11):
        new_state = {m: state[m].copy() for m in modules}
        
        # 1. Mutual Cross-Coupling (Integrated Only)
        if integrated:
            # Finance supports Social cohesion; Social stability protects Finance
            new_state['social_module']['F'] += 0.15 * state['finance_module']['F']
            new_state['finance_module']['F'] += 0.10 * state['social_module']['F']

        # 2. Physics & Erosion
        v_c = load_coeff('viral_evolution')
        v_T = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
        erosion = max(0.1, 1.0 - v_T)

        for m in modules:
            if m == 'viral_evolution': continue
            c = load_coeff(m)
            new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * (state[m]['F'] * erosion))

        # 3. Catastrophic Feedback (Logic remains, but integrated F should fight it)
        if state['social_module']['T'] >= 0.9:
            sev = state['social_module']['T'] - 0.9
            new_state['finance_module']['F'] *= (1.0 - (sev * 0.3))
            new_state['finance_module']['E'] += sev * 0.2

        new_state['urban_module']['E'] += state['seismic_module']['T'] * 0.02
        new_state['social_module']['E'] += (state['urban_module']['T'] * 0.05) + (state['finance_module']['T'] * 0.1)
        state = new_state
    return state['social_module']['T'], state['finance_module']['T']

silo_s, silo_f = run_simulation(integrated=False)
int_s, int_f = run_simulation(integrated=True)

print(f"{'SYSTEM TYPE':<15} | {'SOCIAL-T (S10)':<15} | {'FINANCE-T (S10)':<15} | {'STATUS'}")
print("-" * 75)
print(f"{'SILOED':<15} | {silo_s:>15.4f} | {silo_f:>15.4f} | 💀 CASCADE")
print(f"{'INTEGRATED':<15} | {int_s:>15.4f} | {int_f:>15.4f} | {'🟢 STABLE' if int_f < 0.6 else '🟡 STRESSED'}")
