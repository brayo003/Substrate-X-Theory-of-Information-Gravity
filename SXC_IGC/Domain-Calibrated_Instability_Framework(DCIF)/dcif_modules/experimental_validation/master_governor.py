import json
import glob
import os

def get_tier(gamma):
    g = abs(float(gamma))
    if g >= 10:    return "TIER_0_COSMIC"
    if g >= 1:     # Finance (0.9), Social (0.8) are close to this
        return "TIER_I_HYPER" if g >= 0.6 else "TIER_II_MESO"
    if g >= 0.1:    return "TIER_II_MESO"
    if g >= 0.01:   return "TIER_III_MICRO"
    if g > 0:       return "TIER_IV_NANO"
    return "TIER_V_NULL" if g == 0 else "TIER_VI_NEGATIVE"

# 1. SCRAPE ALL 16 IDENTIFIED MODULES
constants = {
    "version": "1.2.4", 
    "global_flux": 0.01,
    "modules": {}
}

# Recursive search for all coefficient files
files = glob.glob("../**/coefficients.json", recursive=True)

for path in files:
    # Improved naming logic for non-standard folders
    folder_name = os.path.basename(os.path.dirname(path))
    module = folder_name.replace("_module", "").replace("_Module", "").lower()
    
    try:
        with open(path) as f:
            data = json.load(f)
            coeffs = data.get("coefficients", data)
            g = coeffs.get("gamma")
            b = coeffs.get("beta")
            if g is not None:
                constants["modules"][module] = {
                    "beta": float(b if b is not None else 0),
                    "gamma": float(g),
                    "tier": get_tier(g)
                }
    except: continue

# 2. SYMMETRIC INTERFERENCE (Impedance Mismatch)
shatter_points = []
mods = list(constants["modules"].keys())
phi = constants["global_flux"]

for i in range(len(mods)):
    for j in range(i + 1, len(mods)):
        s, t = mods[i], mods[j]
        gs, gt = constants["modules"][s]["gamma"], constants["modules"][t]["gamma"]
        
        # New formula: Focuses on the difference in damping behavior
        if gs == 0 or gt == 0 or (gs * gt == 0): 
            tension = 1e6 # Extreme tension for boundary-less substrates
        else:
            # The more different the gammas, the higher the tension
            tension = phi * ((gs - gt)**2) / abs(gs * gt)
        
        if tension > 0.1: # Report even moderate interference
            shatter_points.append({"pair": f"{s}<->{t}", "tension": round(tension, 6)})

constants["shatter_analysis"] = sorted(shatter_points, key=lambda x: x['tension'], reverse=True)

with open("unified_constants.json", "w") as f:
    json.dump(constants, f, indent=2)

print(f"REPORT: {len(constants['modules'])} modules synced (including Quantum & Viral).")
print(f"ANALYSIS: Generated {len(shatter_points)} interference nodes.")
