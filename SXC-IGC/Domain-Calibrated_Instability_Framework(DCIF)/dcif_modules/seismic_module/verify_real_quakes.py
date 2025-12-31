#!/usr/bin/env python3
import pandas as pd
from SeismicInstabilityAnalyzer import SeismicInstabilityAnalyzer

def run_real_world_test():
    # 1. Initialize the Locked Engine
    analyzer = SeismicInstabilityAnalyzer()
    
    # 2. Load the USGS Substrate
    try:
        df = pd.read_csv("global_seismic_substrate.csv")
    except Exception as e:
        print(f"❌ ERROR: Could not read substrate file: {e}")
        return

    print("="*80)
    print(f"SXC-IGC REAL-WORLD SEISMIC VALIDATION | EVENTS: {len(df)}")
    print("="*80)
    print(f"{'TIME':<25} | {'MAG':<5} | {'DEPTH':<7} | {'TENSION (T)':<12} | {'STATUS'}")
    print("-" * 80)

    for index, row in df.iterrows():
        # Mapping USGS magnitude to Excitation (E) 
        # (Scaling: Mag 7.0 approx 0.035 in engine units)
        E = row['mag'] / 200.0 
        
        # Mapping Depth to Resilience (F) 
        # (Deeper quakes = higher resistance to surface tension)
        F = 1.0 - (row['depth'] / 700.0)
        
        # 3. Process through the IGC Engine
        result = analyzer.analyze_scenario(E, F, 0.0)
        
        # Filter for high-interest events (Elevated or Crisis)
        if result['T_value'] > 0.3:
            print(f"{row['time'][:23]:<25} | {row['mag']:<5.1f} | {row['depth']:<7.1f} | "
                  f"{result['T_value']:<12.4f} | {result['status']}")

if __name__ == "__main__":
    run_real_world_test()
