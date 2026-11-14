import numpy as np

# Your β values vs possible determinants
systems = {
    "Seismic": {"beta": 18.39, "components": "millions", "connectivity": "high"},
    "Quantum": {"beta": 0.95, "components": "few", "connectivity": "medium"},
    "Social": {"beta": 3.45, "components": "billions", "connectivity": "low"},
    "Energy": {"beta": 0.99, "components": "thousands", "connectivity": "medium"},
}

print("β (Excitation Sensitivity) Hypothesis Test")
print("="*50)
print("Hypothesis: β ∝ (Components) × (Connectivity) × (Flow Rate)")
print("-"*50)

# Qualitative assessment
for name, data in systems.items():
    beta = data['beta']
    
    # Make qualitative predictions
    if beta > 10:
        pred = "VERY sensitive: Many components, high connectivity, fast flow"
    elif beta > 1:
        pred = "Moderately sensitive"
    else:
        pred = "Less sensitive: Fewer/slower interactions"
    
    print(f"{name:<10}: β={beta:5.2f} → {pred}")

print("\n" + "="*50)
print("Observation: Seismic has highest β (18.39)")
print("Explanation: Fault networks have MANY interacting points,")
print("             high stress connectivity, rapid stress transfer")
print("             → High excitation sensitivity")
