import os
import json

def audit_fragility():
    modules_dir = '.' 
    modules = [d for d in os.listdir(modules_dir) if os.path.isdir(os.path.join(modules_dir, d)) and not d.startswith('.')]
    
    print(f"{'DOMAIN':<30} | {'RATIO (β/γ)':<12} | {'SENSITIVITY'}")
    print("-" * 65)
    
    results = []
    for mod in modules:
        path = os.path.join(mod, 'coefficients.json')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    # Extract from the nested 'coefficients' key
                    c = data.get('coefficients', {})
                    b = c.get('beta', 0)
                    g = c.get('gamma', 0)
                    
                    ratio = b / g if g != 0 else float('inf')
                    results.append((mod, ratio))
            except Exception:
                continue
    
    for name, ratio in sorted(results, key=lambda x: x[1], reverse=True):
        if ratio > 20: status = "BRITTLE [QUANTUM SNAP]"
        elif ratio > 4: status = "STIFF [CRUSTAL FRACTURE]"
        elif ratio > 2: status = "VISCOUS [URBAN TANGLE]"
        else: status = "ELASTIC [COSMIC FLOW]"
        print(f"{name:<30} | {ratio:>12.2f} | {status}")

if __name__ == "__main__":
    audit_fragility()
