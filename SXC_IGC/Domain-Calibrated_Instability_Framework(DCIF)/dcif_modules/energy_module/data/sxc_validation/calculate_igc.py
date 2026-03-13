import pandas as pd
import numpy as np
import os

# Load the verified Substrate
file_path = 'outage_data/Outage_Dataset/eaglei_outages_with_events_2018.csv'
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit()

df = pd.read_csv(file_path)
df['start_time'] = pd.to_datetime(df['start_time'])
df = df.sort_values(['state', 'county', 'start_time'])

def calculate_gravity_k(group):
    # m = Local Substrate Mass (Max customers ever impacted in this county)
    # Using max() as the local 'carrying capacity' of the information substrate
    m = group['max_customers'].max()
    if m == 0: m = 1  # Avoid division by zero
    
    # e = Realized Entropy (Current outages)
    e = group['mean_customers']
    
    # K = e / m (Information Gravity Metric)
    group['IG_K'] = e / m
    
    # Rate of change (Temporal Flux)
    group['dK_dt'] = group['IG_K'].diff().fillna(0)
    return group

print("--- PHASE 3: CALCULATING INFORMATION GRAVITY (K) ---")
results = df.groupby(['state', 'county'], group_keys=False).apply(calculate_gravity_k)

# Threshold for 'Structural Fracture'
critical_zones = results[results['IG_K'] > 0.5].copy()

print(f"Total Substrate Records: {len(results)}")
print(f"Fractures (K > 0.5) Found: {len(critical_zones)}")

if not critical_zones.empty:
    print("\nTop 15 High-Gravity Fractures vs. Real-World Events:")
    print(critical_zones[['start_time', 'county', 'IG_K', 'Event Type']].head(15))
else:
    print("\nNo K > 0.5 fractures found. Lowering threshold for analysis...")
    print(results[['start_time', 'county', 'IG_K', 'Event Type']].sort_values('IG_K', ascending=False).head(10))
