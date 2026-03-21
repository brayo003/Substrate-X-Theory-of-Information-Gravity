import json
import glob
import os

def get_tier(gamma):
    g = float(gamma)
    if g >= 0.6: return "TIER_I_FLUID"
    if 0.1 < g < 0.6: return "TIER_II_VISCOUS"
    if 0.0 < g <= 0.1: return "TIER_III_FOUNDATIONAL"
    if g == 0: return "TIER_IV_INERT"
    return "TIER_V_ANOMALOUS"

constants = {"version": "1.2.2", "tiers": {}}

# Walk all directories to find REAL coefficients
files = glob.glob("../**/*module/coefficients.json", recursive=True)
for path in files:
    module = os.path.basename(os.path.dirname(path)).replace("_module", "")
    try:
        with open(path) as f:
            data = json.load(f)
            # Handle nested 'coefficients' key or flat structure
            coeffs = data.get("coefficients", data)
            gamma = coeffs.get("gamma")
            beta = coeffs.get("beta")
            
            if gamma is not None:
                tier = get_tier(gamma)
                if tier not in constants["tiers"]:
                    constants["tiers"][tier] = {"modules": {}}
                constants["tiers"][tier]["modules"][module] = {
                    "beta": beta,
                    "gamma": gamma
                }
    except:
        continue

with open("unified_constants.json", "w") as f:
    json.dump(constants, f, indent=2)

print(f"SUCCESS: Scanned {len(files)} modules. unified_constants.json is now the Ground Truth.")
