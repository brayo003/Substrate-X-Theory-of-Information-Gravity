import pandas as pd

class SXCMasterV12:
    def __init__(self, domain_file='domain_scales.csv'):
        self.df = pd.read_csv(domain_file)
        self.flux = 0.01

    def get_tension(self, source, target):
        """V12 Rigorous Asymmetric Logic: T = (Flux / (gs * gt)) * (gs / gt)"""
        src_data = self.df[self.df['domain'] == source].iloc[0]
        tgt_data = self.df[self.df['domain'] == target].iloc[0]
        
        gs, gt = src_data['gamma'], tgt_data['gamma']
        if gt == 0: return float('inf')
        
        # The logic we found: Impact Physics
        tension = (self.flux / (gs * gt)) * (gs / gt)
        return round(tension, 4)

    def audit(self):
        domains = self.df['domain'].tolist()
        print(f"\nSXC V12 RIGOROUS ENGINE: SHATTER MAP")
        print("="*50)
        for s in domains:
            for t in domains:
                if s != t:
                    t_val = self.get_tension(s, t)
                    if t_val > 1.0:
                        status = "❌ SHATTER"
                    elif t_val > 0.7:
                        status = "⚠️ TANGLE"
                    else:
                        status = "🟢 STABLE"
                    
                    if t_val > 10.0: # Filter for the high-noise zones
                        print(f"{s[:10]} -> {t[:10]} | T: {t_val:<10} | {status}")

if __name__ == "__main__":
    SXCMasterV12().audit()
