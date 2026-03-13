import pandas as pd

class SXCSynthesisV12:
    def __init__(self, domain_file='domain_scales.csv'):
        self.df = pd.read_csv(domain_file)
        self.f_base = 0.01
        self.t_target = 0.7

    def generate_final_map(self):
        results = []
        domains = self.df['domain'].tolist()
        for s in domains:
            src = self.df[self.df['domain'] == s].iloc[0]
            for t in domains:
                if s == t: continue
                tgt = self.df[self.df['domain'] == t].iloc[0]
                gs, gt = src['gamma'], tgt['gamma']
                if gt <= 0: continue

                t_curr = (self.f_base / (gs * gt)) * (gs / gt)
                f_safe = self.t_target * (gt ** 2)
                l_buffer = t_curr / self.t_target

                results.append({
                    "Link": f"{s[:10]}->{t[:10]}",
                    "Tension": round(t_curr, 1),
                    "Safe_Flux": f"{f_safe:.7f}",
                    "Buffer_Req": f"{l_buffer:.1f}x"
                })
        
        df = pd.DataFrame(results).sort_values(by="Tension", ascending=False)
        print("\nV12 MASTER SYNTHESIS: OPERATIONAL REALITY")
        print("="*75)
        print(df.to_string(index=False))
        print("="*75)

if __name__ == "__main__":
    SXCSynthesisV12().generate_final_map()
