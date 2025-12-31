import json
import os

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

# --- v7 Integrated Logic ---
# 1. Proactive mutual support (F-sharing)
# 2. Dynamic Firewall (Decoupling at T > 0.6)
# 3. Excitation Sink (Sacrificial Finance to save Social)

modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
state = {m: {'E': 0.1, 'F': 0.8, 'T': 0.0} for m in modules}
state['seismic_module']['E'], state['viral_evolution']['E'] = 0.4, 0.8

print(f"{'STEP':<5} | {'SOC-T':<10} | {'URBAN-T':<10} | {'MODE'}")
print("-" * 45)

for step in range(1, 11):
    new_state = {m: state[m].copy() for m in modules}
    v_c = load_coeff('viral_evolution')
    v_T = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
    erosion = max(0.1, 1.0 - v_T)

    mode = "INTEGRATED"
    for m in modules:
        if m == 'viral_evolution': continue
        c = load_coeff(m)
        new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * (state[m]['F'] * erosion))

    # RAM DECISION: If Urban is collapsing, decouple it to save Social
    urban_coupling = 0.05
    if state['urban_module']['T'] > 0.6:
        urban_coupling = 0.0 # FIREWALL ACTIVE
        mode = "DECOUPLED"

    new_state['urban_module']['E'] += state['seismic_module']['T'] * 0.02
    new_state['social_module']['E'] += (state['urban_module']['T'] * urban_coupling) + (state['finance_module']['T'] * 0.1)
    state = new_state
    print(f"S{step:<4} | {state['social_module']['T']:>10.4f} | {state['urban_module']['T']:>10.4f} | {mode}")
