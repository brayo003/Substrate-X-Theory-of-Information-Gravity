import json
import os

def load_coeff(module_name):
    path = f"./dcif_modules/{module_name}/coefficients.json"
    with open(path, 'r') as f:
        return json.load(f)['coefficients']

# 1. Setup Simulation
modules = ['seismic_module', 'urban_module', 'energy_module', 'finance_module', 'social_module']
state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0, 'prev_T': 0.0} for m in modules}

# Trigger Event
state['seismic_module']['E'] = 0.4 

print(f"{'STEP':<6} | {'SUBSTRATE':<15} | {'TENSION':<10} | {'Δ-TENSION':<10} | {'STATUS'}")
print("-" * 70)

for step in range(1, 6):
    new_state = {m: state[m].copy() for m in modules}
    
    for m in modules:
        c = load_coeff(m)
        
        # Adaptive Damping: If Tension is rising fast, inject F immediately
        dT = state[m]['T'] - state[m]['prev_T']
        if dT > 0.05:
            new_state[m]['F'] += dT * 1.5 # Dynamic response
        
        new_state[m]['prev_T'] = state[m]['T']
        new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * state[m]['F'])

    # Propagation with Social-Finance Feedback Loop
    # (Simplified coupling for clarity)
    new_state['urban_module']['E'] += new_state['seismic_module']['T'] * 0.02
    new_state['social_module']['E'] += new_state['urban_module']['T'] * 0.1
    
    state = new_state
    for m in modules:
        status = "🔥 COLLAPSE" if state[m]['T'] >= 0.6 else "🟡 STRESSED" if state[m]['T'] >= 0.4 else "OK"
        dT = state[m]['T'] - state[m]['prev_T']
        print(f"S{step:<4} | {m:<15} | {state[m]['T']:>10.4f} | {dT:>10.4f} | {status}")
    print("-" * 70)
