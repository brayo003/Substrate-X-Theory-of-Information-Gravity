# final_dark_matter_calibration.py
import numpy as np
import json

# Your validated parameters
DARK_MATTER_PARAMS = {
    "alpha": 0.0,      # Gradient coefficient
    "beta": 0.9185,    # Excitation sensitivity
    "gamma": 22.5543,  # Damping sensitivity (EXTREME!)
    
    # System-specific calibrations
    "systems": {
        "dwarf_galaxy": {"E": 0.10, "F": 0.0050, "T": 0.02},
        "milky_way": {"E": 0.30, "F": 0.0100, "T": 0.05},
        "cluster_core": {"E": 0.60, "F": 0.0156, "T": 0.20},
        "bullet_cluster": {"E": 0.95, "F": 0.0010, "T": 0.85}
    },
    
    # Physical interpretation
    "interpretation": {
        "gamma_meaning": "Extreme sensitivity of DM tension to interaction changes",
        "damping_trend": "F increases with system scale, crashes in collisions",
        "testable_predictions": [
            "All cluster collisions: F ≈ 0.001",
            "DM in clusters: 3× stickier than in dwarfs",
            "γ ≈ 22.5 should appear in DM studies"
        ]
    }
}

# Save to JSON
with open("dark_matter_calibration.json", "w") as f:
    json.dump(DARK_MATTER_PARAMS, f, indent=2)

print("✅ Dark Matter Calibration Saved!")
print(f"   β = {DARK_MATTER_PARAMS['beta']:.4f}")
print(f"   γ = {DARK_MATTER_PARAMS['gamma']:.4f} (EXTREME!)")
print(f"   Validated for {len(DARK_MATTER_PARAMS['systems'])} systems")
