import pandas as pd
import os

class SXCGlobalAuditorV12:
    def __init__(self, target_dir=".."):
        self.target_dir = target_dir
        self.flux = 0.01
        self.gamma_map = {
            'dark_matter': 0.00001, 'big_bang': 0.00001, 'black_hole': 0.00001, 'cosmology': 0.0001,
            'seismic': 0.001, 'geology': 0.001, 'agriculture': 0.005, 'ecology': 0.01,
            'logistics': 0.02, 'urban': 0.05, 'nairobi': 0.05, 'healthcare': 0.08,
            'finance': 0.18, 'social': 0.45, 'virology': 0.55, 'cybersecur': 0.88,
            'substrate_ai': 0.95, 'Quantum_Decoherence': 0.99
        }

    def get_gamma(self, name):
        for key, val in self.gamma_map.items():
            if key in name.lower(): return val
        return 0.1

    def run_sweep(self):
        # Look in the parent directory for modules
        modules = [d for d in os.listdir(self.target_dir) if os.path.isdir(os.path.join(self.target_dir, d)) and 'module' in d]
        results = []
        
        for s_mod in modules:
            gs = self.get_gamma(s_mod)
            for t_mod in modules:
                if s_mod == t_mod: continue
                gt = self.get_gamma(t_mod)
                tension = (self.flux / (gs * gt)) * (gs / gt)
                results.append({
                    "Source": s_mod.replace('_module', ''),
                    "Target": t_mod.replace('_module', ''),
                    "Tension": round(tension, 2)
                })
        
        if not results:
            print("No modules found in parent directory. Ensure you are running from experimental_validation.")
            return

        df = pd.DataFrame(results).sort_values(by="Tension", ascending=False)
        print("\nV12 GLOBAL AUDIT: ALL-DOMAIN FRICTION MAP")
        print("="*70)
        print(df.head(30).to_string(index=False))
        print("="*70)
        print(f"\nShatter Points Detected: {len(df[df['Tension'] > 1.0])}")

if __name__ == "__main__":
    SXCGlobalAuditorV12().run_sweep()
