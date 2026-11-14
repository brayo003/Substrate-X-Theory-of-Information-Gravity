#!/usr/bin/env python3
import csv
from collections import Counter

print("🔍 ANALYZING NYC TRAFFIC DATA")
print("="*60)

with open('nyc_traffic_24h.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    speeds = []
    timestamps = []
    boroughs = Counter()
    
    for row in reader:
        try:
            speed = float(row.get('speed', 0))
            speeds.append(speed)
            
            ts = row.get('data_as_of', 'N/A')
            if ts != 'N/A' and len(timestamps) < 5:
                timestamps.append(ts)
            
            borough = row.get('borough', 'Unknown')
            boroughs[borough] += 1
        except:
            continue

import numpy as np
speeds = np.array(speeds)

print(f"\n📊 DATA OVERVIEW:")
print(f"   Total readings: {len(speeds)}")
print(f"   Sample timestamps: {timestamps[:3]}")
print(f"\n📍 BY BOROUGH:")
for borough, count in boroughs.most_common():
    print(f"   {borough}: {count}")

print(f"\n🚗 SPEED DISTRIBUTION:")
print(f"   Mean: {np.mean(speeds):.1f} mph")
print(f"   Median: {np.median(speeds):.1f} mph")
print(f"   Std Dev: {np.std(speeds):.1f}")
print(f"\n   0-1 mph (stopped): {np.sum(speeds < 1)} ({100*np.sum(speeds < 1)/len(speeds):.1f}%)")
print(f"   1-5 mph (crawling): {np.sum((speeds >= 1) & (speeds < 5))} ({100*np.sum((speeds >= 1) & (speeds < 5))/len(speeds):.1f}%)")
print(f"   5-15 mph (severe): {np.sum((speeds >= 5) & (speeds < 15))} ({100*np.sum((speeds >= 5) & (speeds < 15))/len(speeds):.1f}%)")
print(f"   15-25 mph (congested): {np.sum((speeds >= 15) & (speeds < 25))} ({100*np.sum((speeds >= 15) & (speeds < 25))/len(speeds):.1f}%)")
print(f"   25+ mph (moving): {np.sum(speeds >= 25)} ({100*np.sum(speeds >= 25)/len(speeds):.1f}%)")

print(f"\n🎯 ASSESSMENT:")
if np.sum(speeds < 1) / len(speeds) > 0.4:
    print("   ⚠️  CONFIRMED GRIDLOCK - Abnormally high stoppage")
    print("   This is NOT routine traffic. Check for:")
    print("   - Major incident/accident")
    print("   - Severe weather")
    print("   - Special event")
    print("   - Data collection issue")
elif np.mean(speeds) < 15:
    print("   🔴 SEVERE CONGESTION - Heavy but may be rush hour")
else:
    print("   🟡 MODERATE CONDITIONS - Typical urban traffic")
