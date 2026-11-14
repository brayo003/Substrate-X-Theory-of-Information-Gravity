import pandas as pd
import numpy as np

def test_nairobi_correlation():
    print("--- Nairobi: Classical vs Substrate-X Failure Prediction ---")
    
    agri = pd.read_csv('agricultural_entropy_base.csv')
    urban = pd.read_csv('urban_tension_base.csv')
    
    e_col = agri.columns[1]
    u_col = urban.columns[1]
    
    E_series = pd.to_numeric(agri[e_col], errors='coerce').fillna(0)
    U_series = pd.to_numeric(urban[u_col], errors='coerce').fillna(0)
    
    # Parameters from your calibrated engine
    beta = 0.5922
    gamma = 0.6698
    conflict_factor = 2.8
    finance_drain = 2.5
    social_excite = 1.8
    
    # Calculate NET E series
    net_E = (E_series * social_excite) + (U_series * 1.2)
    tangle_point = net_E.quantile(0.70)
    
    def calculate_tension(net_val, use_conflict=True):
        effective = net_val * conflict_factor if (use_conflict and net_val > tangle_point) else net_val
        raw_T = (effective * beta) - (finance_drain * gamma)
        return np.tanh(raw_T / 10.0)
    
    # Calculate both classical and SXC tensions
    classical_t = [calculate_tension(val, use_conflict=False) for val in net_E]
    sxc_t = [calculate_tension(val, use_conflict=True) for val in net_E]
    
    # Failure thresholds
    tangle_threshold = 0.6
    ghost_snap_threshold = 0.9
    
    # Count predictions
    classical_tangles = sum(1 for t in classical_t if t >= tangle_threshold)
    classical_snaps = sum(1 for t in classical_t if t >= ghost_snap_threshold)
    
    sxc_tangles = sum(1 for t in sxc_t if t >= tangle_threshold)
    sxc_snaps = sum(1 for t in sxc_t if t >= ghost_snap_threshold)
    
    # Early warnings (SXC detects before classical)
    early_warnings = 0
    for i in range(len(net_E)-1):
        if (sxc_t[i] >= ghost_snap_threshold and 
            classical_t[i] < ghost_snap_threshold and
            classical_t[i+1] >= ghost_snap_threshold):
            early_warnings += 1
    
    print(f"\nClassical Analysis:")
    print(f"  Tangle warnings: {classical_tangles}")
    print(f"  Ghost snaps: {classical_snaps}")
    
    print(f"\nSubstrate-X Analysis:")
    print(f"  Tangle warnings: {sxc_tangles}")
    print(f"  Ghost snaps: {sxc_snaps}")
    
    if classical_snaps > 0:
        ratio = sxc_snaps / classical_snaps
        print(f"\nHidden Failure Ratio: {ratio:.2f}x")
        
        if 6.0 <= ratio <= 7.5:
            print("✅ MATCHES ENERGY MODULE (6.7x pattern)")
        else:
            print("⚠️  Ratio differs from energy module")
    
    print(f"\nEarly warnings (SXC detects first): {early_warnings}")
    
    if early_warnings > 0:
        avg_lead = len(net_E) / early_warnings
        print(f"Average warning lead: ~{avg_lead:.1f} time steps")

if __name__ == "__main__":
    test_nairobi_correlation()
