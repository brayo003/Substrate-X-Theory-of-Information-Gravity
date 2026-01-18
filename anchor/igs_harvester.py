#!/usr/bin/env python3
import os

def init_harvester():
    print("="*80)
    print("SUBSTRATE X: IGS CLOCK RESIDUAL HARVESTER")
    print("="*80)
    print("TARGET SCALE: A ≈ 10^-16, α = 0.016")
    print("\n[STEP 1] Directory check...")
    
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"[*] Created {data_dir}")
    else:
        print("[*] Data directory ready.")

    print("\n[STEP 2] Analysis Protocol:")
    print("1. Target: IGS .clk and .sp3 files (GNSS Atomic Clock Logs).")
    print("2. Objective: Isolate the Flicker Floor (10^-16).")
    print("3. Correlation: Map 'Clock Stutter' vs. Orbital Matter Density.")
    print("-" * 80)
    print("READY FOR DATA INGESTION.")

if __name__ == "__main__":
    init_harvester()
