import numpy as np
import sys
sys.path.append('.')
from sxc_igc_core import SXC_IGC_Core

print("\n=== TEST 3: LONG-RUN CONVERGENCE/BOUNDEDNESS ===\n")

# Simulate your claimed 17,547-step run
np.random.seed(42)  # For reproducibility
config = {
    "initial_state": np.array([0.0]),
    "observables": {
        "norm_volume": np.random.randn(20000),
        "norm_volatility": np.random.randn(20000)
    },
    "coefficients": {"alpha": 0.1, "beta": -0.05},  # Mix of signs
    "time_step": 0.001
}

engine = SXC_IGC_Core(config)
steps = 17547

try:
    engine.run(steps=steps)
    history = engine.get_history()
    final_state = history[-1]
    max_abs = np.max(np.abs(history))
    
    print(f"Ran {steps} steps successfully.")
    print(f"Final state: {final_state[0]:.6e}")
    print(f"Max absolute value during run: {max_abs:.6e}")
    
    # A key stability indicator: does the state drift to astronomical values?
    if max_abs > 1e6:
        print("⚠️  CAUTION: Large state drift observed. Engine may be numerically unstable.")
    else:
        print("✅ PASS: Engine completed long run without catastrophic drift.")
        
except Exception as e:
    print(f"❌ FAIL: Engine crashed at step {len(engine.history)}: {e}")
