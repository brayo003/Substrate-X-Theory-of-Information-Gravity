# Updated run.py
import json

modules = {
    'Black Hole (Planck Anchor)': 'black_hole_module',
    'Particle Physics (X17/Muon)': 'particle_physics_module',
    'Agriculture (Nairobi Substrate)': 'agriculture_module',
    'Quantum (IBM/Google Qubit)': 'Quantum_Decoherence_Module'
}

print(f"{'DOMAIN':<30} | {'STABILITY':<10} | {'HORIZON (Units)'}")
print("-" * 65)

for label, path in modules.items():
    try:
        with open(f"{path}/coefficients.json", 'r') as f:
            d = json.load(f)
            beta, gamma = d['beta'], d['gamma']
            horizon = abs(1 / (beta * gamma)) if gamma < 0 else (beta / (gamma + 1e-9)) * 10
            status = "CRITICAL" if gamma < 0 else "STABLE"
            print(f"{label:<30} | {status:<10} | {horizon:.4f}")
    except:
        continue
