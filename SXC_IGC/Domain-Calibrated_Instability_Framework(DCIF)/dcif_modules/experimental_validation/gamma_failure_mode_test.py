import numpy as np

def predict_failure_mode(gamma):
    """Predict failure mode from gamma value"""
    if gamma < 0.05:
        return "BRITTLE SNAP (Sudden, catastrophic failure)"
    elif gamma < 0.2:
        return "STIFF FRACTURE (Cracks propagate)"
    elif gamma < 1.0:
        return "VISCOUS TANGLE (Gradual deformation)"
    else:
        return "ELASTIC FLOW (Smooth deformation, no failure)"

# Test with your data
gamma_values = {
    "seismic": 0.0403,
    "quantum": 0.0393,
    "game": 0.0402,
    "particle_physics": 0.0852,
    "viruses": 0.1000,
    "energy": 0.1857,
    "social": 0.8000,
    "dark_matter": 31.9231
}

print("GAMMA → FAILURE MODE PREDICTION")
print("="*50)
for system, gamma in gamma_values.items():
    mode = predict_failure_mode(gamma)
    print(f"{system:>20}: γ={gamma:7.4f} → {mode}")
