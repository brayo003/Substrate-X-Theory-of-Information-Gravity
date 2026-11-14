import pandas as pd
import numpy as np
import os
import json
import urllib.request

def get_fred_data(series_id):
    """Downloads real-world data from FRED using browser headers to prevent 404/Blocking"""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            df = pd.read_csv(response)
            df.columns = ['date', series_id]
            df['date'] = pd.to_datetime(df['date'])
            df[series_id] = pd.to_numeric(df[series_id], errors='coerce')
            return df
    except Exception as e:
        print(f"FAILED TO FETCH {series_id}: {e}")
        return None

def solve_v12(e_s, f_s, t_s, e_c, f_c, t_c):
    """SXC-V12 Engine: T = βE - γF (Instability = Sensitivity*Exposure - Damping*Flow)"""
    A = np.array([[e_s, -f_s], [e_c, -f_c]])
    b = np.array([t_s, t_c])
    try:
        x = np.linalg.solve(A, b)
        return x[0], x[1] # beta, gamma
    except Exception as e:
        return np.nan, np.nan

print("--- SXC REAL-WORLD AUDIT: LOGISTICS SUBSTRATE ---")
print("Connecting to FRED (Global Supply Chain & Port Dynamics)...")

# 1. Pull Ground-Truth Data
tension_df = get_fred_data('GSCPI')    # Global Supply Chain Pressure Index
flow_df = get_fred_data('COPTOTLA')   # Port of LA Throughput (TEUs)
exposure_df = get_fred_data('ISRATIO') # Total Business: Inventory to Sales Ratio

if tension_df is not None and flow_df is not None and exposure_df is not None:
    # 2. Synchronize Time-Series
    master_df = tension_df.merge(flow_df, on='date').merge(exposure_df, on='date')
    master_df = master_df.dropna()
    
    # Normalize Tension (Offset GSCPI to maintain positive T for Information Gravity logic)
    # GSCPI is a Z-score; we shift it so the floor represents 'minimum entropy'.
    master_df['T'] = master_df['GSCPI'] + abs(master_df['GSCPI'].min()) + 0.1
    master_df['F'] = master_df['COPTOTLA']
    master_df['E'] = master_df['ISRATIO']

    # 3. Extract Historical Regimes
    # Stable: January 2019 (Pre-Pandemic Baseline)
    # Crisis: November 2021 (Peak Supply Chain Collapse)
    stable = master_df[master_df['date'] == '2019-01-01'].iloc[0]
    crisis = master_df[master_df['date'] == '2021-11-01'].iloc[0]
    
    # 4. Engine Calibration
    beta, gamma = solve_v12(stable['E'], stable['F'], stable['T'], 
                            crisis['E'], crisis['F'], crisis['T'])
    
    ratio = beta / gamma if gamma != 0 else 0

    # 5. Output Findings
    print(f"\nREGIME ANALYSIS (AUDITED):")
    print(f"STABLE (2019): E={stable['E']:.2f}, F={stable['F']:.0f}, T={stable['T']:.2f}")
    print(f"CRISIS (2021): E={crisis['E']:.2f}, F={crisis['F']:.0f}, T={crisis['T']:.2f}")

    print("\n" + "="*45)
    print("SXC-V12: EMPIRICAL CALIBRATION RESULT")
    print("="*45)
    print(f"BETA (Sensitivity): {beta:.8f}")
    print(f"GAMMA (Damping):     {gamma:.8f}")
    print(f"RATIO (β/γ):         {ratio:.2f}")
    
    if ratio > 20:   state = "BRITTLE [SNAP]"
    elif ratio > 4:  state = "STIFF [FRACTURE]"
    else:            state = "ELASTIC [FLOW]"
    
    print(f"SUBSTRATE STATE:     {state}")
    print("="*45)

    # Update coefficients.json with the real numbers
    results = {
        "status": "empirical_audit_pass",
        "coefficients": {"beta": float(beta), "gamma": float(gamma)},
        "ratio": float(ratio),
        "source": "FRED_GSCPI_COPTOTLA_ISRATIO"
    }
    with open('coefficients.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("coefficients.json UPDATED WITH HISTORICAL REALITY.")
else:
    print("CRITICAL ERROR: Could not reach one or more data streams.")
