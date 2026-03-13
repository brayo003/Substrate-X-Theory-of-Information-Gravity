import pandas as pd
import numpy as np

def generate_dirty_data(n_events=100000):
    print("⚛️ V13 SUBSTRATE GENERATION: Creating Dirty Collision Stream...")
    
    # 1. Generate Standard Model Background (with noise)
    # Most muons are back-to-back, but detector adds a small 'jitter'
    phi1 = np.random.uniform(-np.pi, np.pi, n_events)
    # Noise floor: roughly 2-5 degrees of detector smear
    noise = np.random.normal(0, 0.05, n_events) 
    phi2 = phi1 + np.pi + noise
    # Wrap angles
    phi2 = (phi2 + np.pi) % (2 * np.pi) - np.pi
    
    pt1 = np.random.exponential(30, n_events) + 20
    pt2 = pt1 + np.random.normal(0, 2, n_events) # Energy resolution smear

    # 2. Inject 'Ghost' Anomalies (0.1% of events)
    # These are NOT back-to-back. They have high Torsion.
    n_ghosts = int(n_events * 0.001)
    ghost_indices = np.random.choice(n_events, n_ghosts, replace=False)
    # Massive torsion: muons fly off at 90-degree angles
    phi2[ghost_indices] = phi1[ghost_indices] + (np.pi / 2) 

    df = pd.DataFrame({
        'Run': [2026] * n_events,
        'Event': range(n_events),
        'pt1': pt1, 'phi1': phi1,
        'pt2': pt2, 'phi2': phi2
    })
    
    df.to_csv("v13_dirty_collisions.csv", index=False)
    print(f"✅ SUCCESS: v13_dirty_collisions.csv created with {n_ghosts} injected Ghosts.")

if __name__ == "__main__":
    generate_dirty_data()
