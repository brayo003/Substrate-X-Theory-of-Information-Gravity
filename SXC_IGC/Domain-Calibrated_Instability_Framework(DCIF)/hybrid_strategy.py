import json
import os

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

def run_hybrid():
    coupling = {('urban_module', 'social_module'): 0.05}
    base_coupling = 0.05
    modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
    state = {m: {'E': 0.1, 'F': 0.8, 'T': 0.0} for m in modules}
    state['seismic_module']['E'], state['viral_evolution']['E'] = 0.4, 0.8

    print(f"{'STEP':<5} | {'SOC-T':<10} | {'LINK-%':<10} | {'PHASE'}")
    print("-" * 45)

    for step in range(1, 11):
        new_state = {m: state[m].copy() for m in modules}
        v_c = load_coeff('viral_evolution')
        erosion = max(0.1, 1.0 - ((v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])))

        # HYBRID LOGIC
        phase = "RECOVERY" if step > 1 and state['social_module']['T'] < new_state['social_module']['T'] else "NOMINAL"
        
        # Phase 1: Predictive (Mild)
        if 0.4 < state['urban_module']['T'] <= 0.7:
            coupling[('urban_module', 'social_module')] = base_coupling * 0.9
            phase = "PREDICTIVE"
        
        # Phase 2: Reactive (Aggressive)
        if state['urban_module']['T'] > 0.7:
            coupling[('urban_module', 'social_module')] = base_coupling * 0.5
            phase = "FIREWALL"

        # Physics Step
        for m in modules:
            if m == 'viral_evolution': continue
            c = load_coeff(m)
            new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * (state[m]['F'] * erosion))

        new_state['urban_module']['E'] += state['seismic_module']['T'] * 0.02
        new_state['social_module']['E'] += (state['urban_module']['T'] * coupling[('urban_module', 'social_module')])
        
        link_pct = (coupling[('urban_module', 'social_module')] / base_coupling) * 100
        state = new_state
        print(f"S{step:<4} | {state['social_module']['T']:>10.4f} | {link_pct:>9.0f}% | {phase}")

run_hybrid()
