import json
import os

def load_coeff(module_name):
    path = f"./dcif_modules/{module_name}/coefficients.json"
    with open(path, 'r') as f:
        return json.load(f)['coefficients']

# 1. Setup Simulation
with open('topology.json', 'r') as f:
    topology = json.load(f)

modules = ['seismic_module', 'urban_module', 'energy_module', 'finance_module', 'social_module']
state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0} for m in modules}

# Trigger Event
state['seismic_module']['E'] = 0.4 

print(f"{'STEP':<6} | {'SUBSTRATE':<15} | {'TENSION':<10} | {'F-LEVEL':<10} | {'STATUS'}")
print("-" * 65)

for step in range(1, 6):
    new_state = {m: state[m].copy() for m in modules}
    
    # Calculate Tension & Apply Circuit Breakers
    for m in modules:
        c = load_coeff(m)
        
        # Check for Circuit Breaker (Recommendation 4)
        for cb in topology['circuit_breakers']:
            if cb['target'] == m and state[m]['T'] > cb['threshold']:
                new_state[m]['F'] += cb['boost'] # Inject Damping
        
        new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * state[m]['F'])

    # Propagate Instability (Recommendations 1 & 2)
    for link in topology['links']:
        src, tgt = link['source'], link['target']
        
        # State-Dependent Vulnerability: More tense = more vulnerable
        vulnerability = 1.0 + (state[tgt]['T'] * 2) if state[tgt]['T'] > 0 else 1.0
        
        # Collapse Logic: Collapsed systems transmit "debris" (sustained but lower intensity)
        transfer_coeff = link['strength'] * (0.4 if state[src]['T'] >= 0.6 else 1.0)
        
        new_state[tgt]['E'] += state[src]['T'] * transfer_coeff * vulnerability

    state = new_state
    for m in modules:
        status = "🔥 COLLAPSE" if state[m]['T'] >= 0.6 else "🟡 STRESSED" if state[m]['T'] >= 0.4 else "OK"
        print(f"S{step:<4} | {m:<15} | {state[m]['T']:>10.4f} | {state[m]['F']:>10.4f} | {status}")
    print("-" * 65)
