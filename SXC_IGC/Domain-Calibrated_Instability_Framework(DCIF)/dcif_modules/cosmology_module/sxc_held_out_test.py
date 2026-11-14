import numpy as np
import glob
import os
import random
import sys

# Import the logic from your local file
try:
    from SXC_Dynamic_Sink import SXCGovernor
except ImportError:
    print("Error: SXC_Dynamic_Sink.py not found in current directory.")
    sys.exit(1)

# 1. Get all local SPARC data
files = glob.glob("data/sparc/*.dat")
if not files:
    print("Error: No data found in data/sparc/")
    sys.exit(1)

random.shuffle(files)

# 2. Split: 50% for the "Death Test"
split_idx = len(files) // 2
test_files = files[split_idx:]

print(f"--- SXC HELD-OUT VALIDATION ---")
print(f"Testing on {len(test_files)} unseen galaxies.")

results = []
tensions = []

for f in test_files:
    try:
        data = np.genfromtxt(f)
        if data.ndim < 2 or data.shape[1] < 5: continue
        r, v_obs = data[:, 0], data[:, 1]
        v_bar = np.sqrt(np.nan_to_num(data[:, 3:6]**2).sum(axis=1))
        
        gov = SXCGovernor()
        
        for i in range(len(r)):
            if r[i] <= 0: continue
            sig = v_bar[i]**2 / r[i]
            gov.step(sig, v_obs[i], v_bar[i])
            tensions.append(gov.T_sys)
            
        # Evaluation
        v_pred = []
        for i in range(len(r)):
            if r[i] <= 0: continue
            step_val = gov.step(v_bar[i]**2 / r[i], v_obs[i], v_bar[i])
            v_pred.append(np.sqrt(max(0, v_bar[i]**2 * (1 + gov.K * step_val))))
        
        if v_pred:
            v_pred = np.array(v_pred)
            error = np.mean(abs(v_pred - v_obs[:len(v_pred)]) / v_obs[:len(v_pred)] * 100)
            results.append(error)
    except Exception as e:
        continue

if results:
    print(f"Final Tension (Last Seen): {tensions[-1]:.4f}")
    print(f"Median Error on UNSEEN data: {np.median(results):.2f}%")
    
    if np.median(results) < 20.0 and max(tensions) < 5.0:
        print("\nVERDICT: GENERALIZED. The 1.254 scaling holds on unseen data.")
    else:
        print("\nVERDICT: OVERFITTED. The logic failed the out-of-sample test.")
else:
    print("Validation failed: No results generated.")
