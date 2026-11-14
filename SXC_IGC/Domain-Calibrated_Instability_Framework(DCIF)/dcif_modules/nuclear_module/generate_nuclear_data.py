import pandas as pd
import numpy as np

def generate():
    t = np.linspace(0, 100, 500)
    # Sample A: Steady irradiation (Classical)
    flux_a = np.ones(500) * 0.5
    # Sample B: Pulsed irradiation (Memory/Hysteresis Test)
    flux_b = np.array([1.0 if (i // 50) % 2 == 0 else 0.0 for i in range(500)])
    
    df = pd.DataFrame({
        'time': t,
        'flux_steady': flux_a,
        'flux_pulsed': flux_b
    })
    df.to_csv('nuclear_memory_test.csv', index=False)
    print("Dataset generated: nuclear_memory_test.csv")

if __name__ == "__main__":
    generate()
