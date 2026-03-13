import numpy as np

# SXC-V12 Parameters
alpha = 0.5  # Gradient weight
beta = 0.8   # Excitation (The Kick/Log Drum energy)
gamma = 0.3  # Damping (The Dancers/Stability)
b = 0.1      # Cubic Saturation constant

def calculate_tension(t):
    # Simulating a buildup over time
    excitation = np.sin(t * 0.1) + (t * 0.05) 
    # The Core V12 Equation: rx + ax^2 - bx^3
    T = (alpha * 1.0) + (beta * excitation) - (b * (excitation**3))
    return np.clip(T, 0, 1.2) # Threshold at 1.2 for 'Firewall'

# Generate 500 points of data for a 4-bar build
curve = [calculate_tension(i) for i in range(500)]

with open("v12_automation.txt", "w") as f:
    for value in curve:
        f.write(f"{value}\n")

print("V12 Tension Curve generated. Import v12_automation.txt into FL Studio.")
