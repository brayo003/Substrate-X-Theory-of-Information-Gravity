import numpy as np

def calculate_optimal_beta():
    # Historical Data: (Estimated Intensity E, Observed Outcome T)
    # T = Outcome (1.0 = Threshold of Collapse)
    data = {
        'social': [(0.45, 1.6), (0.6, 2.1), (0.3, 0.9)],
        'finance': [(0.7, 2.5), (0.2, 0.4), (0.5, 1.8)],
        'urban': [(0.8, 2.8), (0.4, 1.2), (0.1, 0.2)]
    }
    
    calibrated_coeffs = {}
    
    for module, points in data.items():
        E = np.array([p[0] for p in points])
        T = np.array([p[1] for p in points])
        
        # Linear regression through origin: T = beta * E
        beta = np.sum(E * T) / np.sum(E**2)
        calibrated_coeffs[module] = round(beta, 3)
        
    print("CALIBRATED COEFFICIENTS (BETA):")
    for mod, b in calibrated_coeffs.items():
        print(f" - {mod:<8}: {b}")
    
    return calibrated_coeffs

if __name__ == "__main__":
    calculate_optimal_beta()
