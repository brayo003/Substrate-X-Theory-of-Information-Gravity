import pandas as pd
from domain_adjacency_map import DomainGuard

class SXCV12Master:
    def __init__(self, domain_file='domain_scales.csv'):
        self.df = pd.read_csv(domain_file)
        self.guard = DomainGuard()
        self.tension_registry = {row['domain']: 0.0 for _, row in self.df.iterrows()}

    def execute_bridge(self, source, target):
        if not self.guard.is_coupling_allowed(source, target):
             return {"status": "DENIED", "reason": "No causal vector"}

        src_data = self.df[self.df['domain'] == source].iloc[0]
        tgt_data = self.df[self.df['domain'] == target].iloc[0]

        # 1. Grounded Input: Flux is no longer arbitrary
        # It is anchored to the source domain's observable signal density
        input_flux = src_data['flux_anchor']

        # 2. Dimensionless Throttling (Relative Dissipation Capacity)
        # We use gamma as a recovery rate to define the transfer coefficient (tau)
        # Tau = Target recovery / (Source recovery + Target recovery)
        tau = tgt_data['gamma'] / (src_data['gamma'] + tgt_data['gamma'])
        
        # 3. Transformed Flux
        # The amount of information that actually "seats" in the target substrate
        seated_flux = input_flux * tau

        # 4. Equilibrium Tension Prediction
        # T_eq = seated_flux / target_dissipation
        t_eq = seated_flux / tgt_data['gamma']
        
        return {
            "link": f"{source} -> {target}",
            "flux_anchor": input_flux,
            "transfer_coeff": round(tau, 4),
            "t_equilibrium": round(t_eq, 4),
            "flux_type": src_data['flux_type']
        }

if __name__ == "__main__":
    master = SXCV12Master()
    # Audit the previously problematic seismic link vs the friction-zone link
    links = [("seismic_module", "atmospheric_science"), ("finance_module", "macroeconomics")]
    
    for src, tgt in links:
        res = master.execute_bridge(src, tgt)
        print(f"LINK: {res['link']} | ANCHOR: {res['flux_anchor']} | T_EQ: {res['t_equilibrium']} ({res['flux_type']})")
