import json
import os

def load_coeff(module_name):
    paths = [f"./dcif_modules/{module_name}/coefficients.json", f"./dcif_modules/Viral_Evolution_Module/coefficients.json"]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r') as f: return json.load(f)['coefficients']
    raise FileNotFoundError(module_name)

modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']
state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0} for m in modules}

# Initial Shocks
state['seismic_module']['E'] = 0.4
state['viral_evolution']['E'] = 0.8

print(f"{'STEP':<5} | {'FINANCE-T':<10} | {'SOCIAL-T':<10} | {'STATUS'}")
print("-" * 50)

for step in range(1, 11):
    new_state = {m: state[m].copy() for m in modules}
    v_c = load_coeff('viral_evolution')
    state['viral_evolution']['T'] = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
    
    # Financial Feedback: High Tension in Finance forces E-up in Social
    f_c = load_coeff('finance_module')
    effective_F_fin = state['finance_module']['F'] * (1.0 - state['viral_evolution']['T']*0.5)
    new_state['finance_module']['T'] = (f_c['beta'] * state['finance_module']['E']) - (f_c['gamma'] * effective_F_fin)
    
    # Erosion and Propagation
    erosion = max(0.1, 1.0 - state['viral_evolution']['T'])
    for m in ['urban_module', 'social_module']:
        c = load_coeff(m)
        new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * (state[m]['F'] * erosion))
        if m == 'urban_module': new_state[m]['E'] += state['seismic_module']['T'] * 0.02
        if m == 'social_module': 
            # Social Excitation = Urban Stress + Finance Panic
            new_state[m]['E'] += (state['urban_module']['T'] * 0.05) + (state['finance_module']['T'] * 0.1)

    state = new_state
    status = "💀 TOTAL SYSTEM FAILURE" if state['social_module']['T'] > 1.0 else "⚠️ COLLAPSING"
    print(f"S{step:<4} | {state['finance_module']['T']:>10.4f} | {state['social_module']['T']:>10.4f} | {status}")
