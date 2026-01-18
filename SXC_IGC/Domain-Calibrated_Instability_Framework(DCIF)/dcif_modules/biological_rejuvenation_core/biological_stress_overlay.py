import json
import os

def load_coeff(module_name):
    # Search for both lowercase and original folder names
    paths = [
        f"./dcif_modules/{module_name}/coefficients.json",
        f"./dcif_modules/{module_name.capitalize()}_Module/coefficients.json",
        f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)['coefficients']
    raise FileNotFoundError(f"Could not locate coefficients for {module_name}")

# 1. Setup Simulation
modules = ['seismic_module', 'urban_module', 'viral_evolution', 'social_module']
state = {m: {'E': 0.1, 'F': 0.6, 'T': 0.0} for m in modules}

# Trigger 1: Seismic Event (Physical)
state['seismic_module']['E'] = 0.4 
# Trigger 2: Rapid Mutation Shift (Biological)
state['viral_evolution']['E'] = 0.8 

print(f"{'STEP':<6} | {'SUBSTRATE':<18} | {'TENSION':<10} | {'BIO-REMAINING'}")
print("-" * 75)

for step in range(1, 11):
    new_state = {m: state[m].copy() for m in modules}
    
    # Calculate Viral Tension: High Beta (0.9) vs Low Gamma (0.1)
    v_c = load_coeff('viral_evolution')
    state['viral_evolution']['T'] = (v_c['beta'] * state['viral_evolution']['E']) - (v_c['gamma'] * state['viral_evolution']['F'])
    
    # Bio-Erosion: Viral Tension directly reduces damping efficiency (F)
    # As Viral Tension rises, the system's ability to "damp" other shocks is halved
    erosion_factor = max(0.1, 1.0 - (state['viral_evolution']['T']))

    for m in modules:
        c = load_coeff(m)
        if m != 'viral_evolution':
            # Apply eroded Damping to the target substrate
            effective_F = state[m]['F'] * erosion_factor
            new_state[m]['T'] = (c['beta'] * state[m]['E']) - (c['gamma'] * effective_F)
            
            # Propagation: Seismic -> Urban -> Social
            if m == 'urban_module':
                new_state[m]['E'] += state['seismic_module']['T'] * 0.02
            if m == 'social_module':
                new_state[m]['E'] += state['urban_module']['T'] * 0.1
        else:
            # Viral evolution proceeds based on its own excitation
            new_state[m]['T'] = state[m]['T']

    state = new_state
    for m in modules:
        status = "🔥 COLLAPSE" if state[m]['T'] >= 0.6 else "OK"
        print(f"S{step:<4} | {m:<18} | {state[m]['T']:>10.4f} | {erosion_factor:>10.4f} {status}")
    print("-" * 75)
