#!/usr/bin/env python3
"""
Analyze saved DCII data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Load your saved DCII data
dcii_file = Path("forex_dcii_results/dcii_series.csv")
if dcii_file.exists():
    dcii_data = pd.read_csv(dcii_file, index_col=0, parse_dates=True)
    print(f"✅ Loaded DCII data: {len(dcii_data)} points")
    print(f"📅 Date range: {dcii_data.index.min()} to {dcii_data.index.max()}")
    
    dcii_series = dcii_data.iloc[:, 0] if dcii_data.shape[1] > 0 else pd.Series()
    
    if not dcii_series.empty:
        # Basic statistics
        print("\n📊 DCII Distribution:")
        print(dcii_series.describe())
        
        # Check stress levels
        bins = [0, 0.3, 0.5, 0.7, 1.0]
        labels = ['Normal', 'Elevated', 'High', 'Critical']
        
        print("\n🚨 Stress Level Counts:")
        for i in range(len(bins)-1):
            low, high = bins[i], bins[i+1]
            count = ((dcii_series >= low) & (dcii_series < high)).sum()
            pct = count / len(dcii_series) * 100
            print(f"  {labels[i]:10}: {count:3d} periods ({pct:.1f}%)")
        
        # Find highest DCII periods
        print("\n🔴 Top 5 Highest Stress Periods:")
        top5 = dcii_series.nlargest(5)
        for dt, value in top5.items():
            print(f"  {dt}: DCII = {value:.3f}")
        
        # Find lowest DCII periods  
        print("\n🟢 Top 5 Lowest Stress Periods:")
        bottom5 = dcii_series.nsmallest(5)
        for dt, value in bottom5.items():
            print(f"  {dt}: DCII = {value:.3f}")
        
        # Check for consecutive high stress periods
        high_stress = dcii_series >= 0.7
        if high_stress.any():
            print(f"\n⚠️  Critical periods found: {high_stress.sum()} total")
            
            # Find longest consecutive critical period
            from itertools import groupby
            groups = [(k, sum(1 for _ in g)) for k, g in groupby(high_stress)]
            critical_groups = [(length, start) for start, (is_critical, length) in enumerate(groups) if is_critical]
            
            if critical_groups:
                max_length, start_idx = max(critical_groups, key=lambda x: x[0])
                print(f"  Longest critical streak: {max_length} periods")
else:
    print("❌ No DCII data found. Run the pipeline first.")
    print("Run: python3 dcii_forex_eurusd_final.py")
