import numpy as np

def calculate_conflict_scaling(ratios):
    # The V12 Constant for 3-way interference
    K_conflict = 2.8 
    base_tension = np.mean(ratios)
    return base_tension * K_conflict

# Example: Finance (Ratio 400), Urban (Ratio 300), Social (Ratio 250)
ratios = [400, 300, 250]
result = calculate_conflict_scaling(ratios)
print(f"SXC-V12 Conflict Test: Interacting Tensions scale to {result:.2f}")
