import pandas as pd
from domain_adjacency_map import DomainGuard

class SXCV12RigorousMaster:
    def __init__(self, domain_file='domain_scales.csv'):
        self.df = pd.read_csv(domain_file)
        self.guard = DomainGuard()

    def execute_bridge(self, source, target):
        if source not in self.df['domain'].values or target not in self.df['domain'].values:
            return {"status": "DENIED", "reason": "Missing Data"}
        
        if not self.guard.is_coupling_allowed(source, target):
            return {"status": "DENIED", "reason": "Causal Barrier"}

        src_data = self.df[self.df['domain'] == source].iloc[0]
        tgt_data = self.df[self.df['domain'] == target].iloc[0]

        # V12.5 Rigorous Product Logic
        flux = src_data['flux_anchor']
        gamma_s = src_data['gamma']
        gamma_t = tgt_data['gamma']
        
        # Tension = Load / (Source_Recovery * Target_Recovery)
        tension = flux / (gamma_s * gamma_t)
        
        return {
            "link": f"{source} -> {target}",
            "tension": round(tension, 4),
            "product": round(gamma_s * gamma_t, 6)
        }

def run_audit():
    master = SXCV12RigorousMaster()
    results = []
    for src, targets in master.guard.adjacencies.items():
        for tgt in targets:
            res = master.execute_bridge(src, tgt)
            if res.get("status") != "DENIED":
                results.append(res)
    
    df = pd.DataFrame(results).sort_values(by="tension", ascending=False)
    print("\n" + "="*60)
    print("SXC RIGOROUS STABILITY AUDIT (V12.5 PRODUCT LOGIC)")
    print("="*60)
    print(df.to_string(index=False))

if __name__ == "__main__":
    run_audit()
