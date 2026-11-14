import pandas as pd
from SXC_V12_Master_Controller import SXCV12Master

def run_full_audit():
    master = SXCV12Master()
    results = []
    
    # Iterate through every allowed coupling in the Guard
    for source, targets in master.guard.adjacencies.items():
        for target in targets:
            # Check if target exists in our scale data
            if target in master.df['domain'].values:
                report = master.execute_bridge(source, target)
                results.append(report)
    
    # Sort by highest interference (The most dangerous points)
    df_audit = pd.DataFrame(results).sort_values(by='interference', ascending=False)
    
    print("\n" + "="*80)
    print("SXC GLOBAL TANGLE AUDIT: IDENTIFYING SUBSTRATE REDLINES")
    print("="*80)
    print(df_audit[['link', 'interference', 'step_down_ratio']].to_string(index=False))
    
    top_risk = df_audit.iloc[0]
    print("\n" + "!"*80)
    print(f"CRITICAL VULNERABILITY DETECTED: {top_risk['link']}")
    print(f"Requires a {top_risk['step_down_ratio']} Transformer to prevent Shatter.")
    print(f"Intervention Shield (Dashboard) will be most active here.")
    print("!"*80)

if __name__ == "__main__":
    run_full_audit()
