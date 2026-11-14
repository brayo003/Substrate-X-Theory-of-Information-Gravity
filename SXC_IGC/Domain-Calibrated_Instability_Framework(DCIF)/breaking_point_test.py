import json
import os

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

def run_core(f_fin, f_soc, dynamic=False):
    modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
    state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0} for m in modules}
    state['seismic_module']['E'], state['viral_evolution']['E'] = 0.4, 0.8
    state['finance_module']['F'], state['social_module']['F'] = f_fin, f_soc

    for step in range(1, 11):
        new_state = {m: state[m].copy() for m in modules}
        
        # Experiment 3: Dynamic Reallocation (Agile Sharing)
        if dynamic and state['social_module']['T'] > 0.5:
            transfer = state['finance_module']['F'] * 0.1
            new_state['finance_module']['F'] -= transfer
            new_state['social_module']['F'] += transfer

        v_c = load_coeff('viral_evolution')
        v_T = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
        erosion = max(0.1, 1.0 - v_T)

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

print(f"{'EXPERIMENT':<25} | {'SOC-T':<10} | {'FIN-T':<10} | {'RESULT'}")
print("-" * 65)

# Exp 1: Graduated Integration
for boost in [0.0, 0.2, 0.4]:
    s, f = run_core(0.6 + boost, 0.6 + boost)
    res = "FAIL" if s > 1.0 else "HOLD"
    print(f"GRADUATED (F+{boost:<3})      | {s:>10.4f} | {f:>10.4f} | {res}")

# Exp 2: Asymmetric
for name, f_vals in [("FIN-FIRST", (0.9, 0.6)), ("SOC-FIRST", (0.6, 0.9)), ("BALANCED", (0.75, 0.75))]:
    s, f = run_core(f_vals[0], f_vals[1])
    res = "FAIL" if s > 1.0 else "HOLD"
    print(f"ASYM: {name:<15} | {s:>10.4f} | {f:>10.4f} | {res}")

# Exp 3: Dynamic
s, f = run_core(0.75, 0.75, dynamic=True)
res = "FAIL" if s > 1.0 else "HOLD"
print(f"DYNAMIC REALLOCATION      | {s:>10.4f} | {f:>10.4f} | {res}")
