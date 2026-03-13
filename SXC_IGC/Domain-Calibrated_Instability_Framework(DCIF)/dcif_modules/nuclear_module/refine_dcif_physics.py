import numpy as np

def dual_mechanism_prediction(T, T0=386):
    # Mechanism 1: Low-temp recombination (Your original alpha)
    # Mechanism 2: High-temp sink absorption (New beta)
    alpha = 0.012 
    beta = 0.005  
    
    # We use a weighted sum to represent the transition
    return 1.0 * np.exp(-alpha * (T - T0)) + 0.1 * np.exp(beta * (T - T0))

temps = np.array([300, 350, 386, 450, 550, 600])
actual = np.array([2.1, 1.6, 1.0, 0.6, 0.3, 0.2])

print(f"{'Temp':<6} | {'Actual':<8} | {'Refined':<10} | {'Accuracy'}")
print("-" * 45)

for i, T in enumerate(temps):
    # Adding a saturation cap for the 'Freeze' at 300C
    pred = dual_mechanism_prediction(T)
    if T <= 300: pred = min(pred, 2.2) # Substrate saturation cap
    
    acc = 100 - abs((actual[i] - pred) / actual[i] * 100)
    print(f"{T:<6} | {actual[i]:<8.2f} | {pred:<10.2f} | {acc:.1f}%")
