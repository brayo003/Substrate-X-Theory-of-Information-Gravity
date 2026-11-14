# v12_master_final.py
import pandas as pd

class SXCMasterV12:
    def __init__(self, domain_file='domain_scales.csv'):
        self.df = pd.read_csv(domain_file)
        self.f_base = 0.01      # Current information flux
        self.t_target = 0.7     # Target tension (safe operational limit)
    
    def calculate_tension(self, source, target):
        """V12 Physics: T = (Flux / (γs·γt)) × (γs/γt) = Flux / (γt²)"""
        src_data = self.df[self.df['domain'] == source].iloc[0]
        tgt_data = self.df[self.df['domain'] == target].iloc[0]
        
        gs, gt = src_data['gamma'], tgt_data['gamma']
        if gt == 0:
            return float('inf'), 0, float('inf')
        
        # The revolutionary simplification
        tension = self.f_base / (gt ** 2)
        
        # Safe flux for this target: T_target × γt²
        safe_flux = self.t_target * (gt ** 2)
        
        # Buffer requirement: how much to reduce current flux
        if safe_flux > 0:
            buffer_req = self.f_base / safe_flux
        else:
            buffer_req = float('inf')
        
        return tension, safe_flux, buffer_req
    
    def generate_reality_map(self):
        """Generate complete operational reality map"""
        domains = self.df['domain'].tolist()
        results = []
        
        for source in domains:
            src_gamma = self.df[self.df['domain'] == source].iloc[0]['gamma']
            for target in domains:
                if source == target:
                    continue
                
                tgt_gamma = self.df[self.df['domain'] == target].iloc[0]['gamma']
                if tgt_gamma <= 0:
                    continue
                
                tension, safe_flux, buffer_req = self.calculate_tension(source, target)
                
                results.append({
                    'Source': source,
                    'Target': target,
                    'γ_source': src_gamma,
                    'γ_target': tgt_gamma,
                    'Tension': tension,
                    'Safe_Flux': safe_flux,
                    'Buffer_Req': buffer_req,
                    'Category': self.categorize_link(tension)
                })
        
        return pd.DataFrame(results)
    
    def categorize_link(self, tension):
        """Categorize by physical reality"""
        if tension >= 1000:
            return "🚫 PHYSICALLY IMPOSSIBLE"
        elif tension >= 100:
            return "💥 HIGH RISK - FRAGMENTATION"
        elif tension >= 10:
            return "⚠️  MEDIUM RISK - UNSTABLE"
        elif tension >= 1:
            return "🔸 LOW RISK - MANAGEABLE"
        else:
            return "✅ SAFE - OPERATIONAL"
    
    def print_summary_statistics(self, df):
        """Print key insights"""
        print("\n" + "="*80)
        print("V12 FINAL SYNTHESIS: KEY INSIGHTS")
        print("="*80)
        
        total_links = len(df)
        impossible = len(df[df['Tension'] >= 1000])
        high_risk = len(df[df['Tension'] >= 100])
        medium_risk = len(df[df['Tension'] >= 10])
        
        print(f"\nTotal Domain Links Analyzed: {total_links}")
        print(f"Physically Impossible Links: {impossible} ({impossible/total_links*100:.1f}%)")
        print(f"High Risk Links (Fragmentation): {high_risk} ({high_risk/total_links*100:.1f}%)")
        print(f"Medium Risk Links: {medium_risk} ({medium_risk/total_links*100:.1f}%)")
        
        # Show most problematic targets
        print(f"\nMOST VULNERABLE TARGETS:")
        vulnerable_targets = df.groupby('Target')['Tension'].max().sort_values(ascending=False)
        for target, tension in vulnerable_targets.head(5).items():
            print(f"  {target}: max tension = {tension:.0f}")
        
        # Show critical findings
        print(f"\nCRITICAL FINDINGS:")
        print(f"1. Dark Matter (γ=0.0001) cannot receive ANY information flow")
        print(f"2. Telecom (γ=0.002) requires 3,571x flux reduction")
        print(f"3. Seismic/Cosmology (γ≈0.01) requires 143x flux reduction")
        print(f"4. Fast→Fast domains (γ>0.1) are generally safe")

if __name__ == "__main__":
    # Initialize and run
    engine = SXCMasterV12()
    
    print("V12 MASTER SYNTHESIS: OPERATIONAL REALITY")
    print("="*80)
    
    # Generate reality map
    reality_df = engine.generate_reality_map()
    
    # Sort by tension (highest first)
    reality_df = reality_df.sort_values('Tension', ascending=False)
    
    # Print top 50 most critical links
    print(f"\n{'Source → Target':<25} {'Tension':<10} {'Safe_Flux':<12} {'Buffer':<12} {'Category':<25}")
    print("-"*80)
    
    for _, row in reality_df.head(50).iterrows():
        source_short = row['Source'][:12]
        target_short = row['Target'][:12]
        pair = f"{source_short}→{target_short}"
        
        print(f"{pair:<25} {row['Tension']:<10.1f} {row['Safe_Flux']:<12.7f} {row['Buffer_Req']:<12.1f}x {row['Category']:<25}")
    
    # Print summary statistics
    engine.print_summary_statistics(reality_df)
