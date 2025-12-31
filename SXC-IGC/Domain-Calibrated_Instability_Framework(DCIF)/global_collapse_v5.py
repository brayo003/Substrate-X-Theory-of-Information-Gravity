import json
import os

def load_coeff(module_name):
    path = f"./dcif_modules/{module_name}/coefficients.json"
    if not os.path.exists(path): path = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(path, 'r') as f: return json.load(f)['coefficients']

# 1. Setup Environment
modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0} for m in modules}

# Initial Global Shocks
state['seismic_module']['E'] = 0.4
state['viral_evolution']['E'] = 0.8

print(f"{'STEP':<5} | {'SOCIAL-T':<10} | {'FINANCE-T':<10} | {'FINANCE-F':<10} | {'STATUS'}")
print("-" * 75)

for step in range(1, 11):
    new_state = {m: state[m].copy() for m in modules}
    
    # Calculate Viral Tension for Global Erosion
    v_c = load_coeff('viral_evolution')
    state['viral_evolution']['T'] = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
    global_erosion = max(0.1, 1.0 - state['viral_evolution']['T'])

    # Calculate Tension for all modules
    for m in modules:
        if m == 'viral_evolution': continue
        c = load_coeff(m)
        effective_F = state[m]['F'] * global_erosion
        new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * effective_F)

    # 2. Catastrophic Feedback Logic (Social -> Finance)
    social_collapse_threshold = 0.9
    if state['social_module']['T'] >= social_collapse_threshold:
        collapse_severity = state['social_module']['T'] - social_collapse_threshold
        # Social collapse erodes financial damping (Trust Decay)
        new_state['finance_module']['F'] *= (1.0 - (collapse_severity * 0.3))
        # Social collapse injects panic into Finance
        new_state['finance_module']['E'] += collapse_severity * 0.2

    # 3. Standard Propagation
    new_state['urban_module']['E'] += state['seismic_module']['T'] * 0.02
    new_state['social_module']['E'] += (state['urban_module']['T'] * 0.05) + (state['finance_module']['T'] * 0.1)

    state = new_state
    
    # 4. Nuanced Status Reporting
    fin_ok = state['finance_module']['T'] < 0.6
    soc_dead = state['social_module']['T'] >= 1.0
    if soc_dead and not fin_ok: status = "💀 CASCADE FAILURE"
    elif soc_dead and fin_ok: status = "💀 PARADOXICAL COLLAPSE"
    elif not fin_ok: status = "🔥 FINANCIAL COLLAPSE"
    else: status = "⚠️ COLLAPSING"

    print(f"S{step:<4} | {state['social_module']['T']:>10.4f} | {state['finance_module']['T']:>10.4f} | {state['finance_module']['F']:>10.4f} | {status}")
