import json

def load_module_data(module_name):
    with open(f"./dcif_modules/{module_name}/coefficients.json", 'r') as f:
        return json.load(f)

def calculate_stabilization(module_name, current_E):
    data = load_module_data(module_name)
    c = data['coefficients']
    beta, gamma = c['beta'], c['gamma']
    
    # Target T = 0.4 (Upper bound of Stable/Recovery)
    # 0.4 = beta*E - gamma*F -> gamma*F = beta*E - 0.4 -> F = (beta*E - 0.4)/gamma
    f_required = (beta * current_E - 0.4) / gamma
    
    return f_required, data['taxonomy']

# Scenario: Urban Module at Step 3 (E was ~0.83 based on seismic propagation)
urban_E_step3 = 0.8336 

f_needed, tax = calculate_stabilization('urban_module', urban_E_step3)

print("="*50)
print("SXC-IGC RESPONSE-ACTION MODULE (RAM) v1.0")
print("="*50)
print(f"TARGET SUBSTRATE: urban_module")
print(f"TAXONOMY:         {tax}")
print(f"CURRENT EXCITATION (E): {urban_E_step3:.4f}")
print("-" * 50)
print(f"REQUIRED DAMPING (F) TO STABILIZE: {f_needed:.4f}")
print("="*50)
