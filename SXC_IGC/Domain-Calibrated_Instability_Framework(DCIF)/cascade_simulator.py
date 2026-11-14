import json
import os

def load_coeff(module_name):
    path = f"./dcif_modules/{module_name}/coefficients.json"
    with open(path, 'r') as f:
        return json.load(f)['coefficients']

# 1. Initialize Baseline
modules = ['seismic_module', 'urban_module', 'finance_module', 'social_module']
state = {m: {'E': 0.1, 'F': 0.5, 'T': 0.0} for m in modules}

# 2. Trigger Seismic Shock
state['seismic_module']['E'] = 0.4  # Sudden tectonic slip

print(f"{'STEP':<10} | {'SUBSTRATE':<15} | {'TENSION':<10} | {'STATUS'}")
print("-" * 50)

for step in range(1, 4):
    # Calculate current Tension for all
    for m in modules:
        c = load_coeff(m)
        state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * state[m]['F'])
    
    # Propagate: Source T increases Target E
    # Seismic -> Urban
    state['urban_module']['E'] += state['seismic_module']['T'] * 0.05
    # Urban -> Finance
    state['finance_module']['E'] += state['urban_module']['T'] * 0.1
    
    for m in modules:
        status = "🔥 COLLAPSE" if state[m]['T'] >= 0.6 else "OK"
        print(f"Step {step:<5} | {m:<15} | {state[m]['T']:>10.4f} | {status}")
    print("-" * 50)

