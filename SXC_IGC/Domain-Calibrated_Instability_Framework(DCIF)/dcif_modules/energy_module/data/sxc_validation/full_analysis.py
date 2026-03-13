import pandas as pd
import numpy as np
import os

print("="*60)
print("SXC-IGC VALIDATION: FULL ANALYSIS PIPELINE")
print("="*60)

# Load data
file_path = 'outage_data/Outage_Dataset/eaglei_outages_with_events_2018.csv'
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit()

df = pd.read_csv(file_path)
print(f"Loaded {len(df)} records")

# Convert timestamps
df['start_time'] = pd.to_datetime(df['start_time'])
df['event_begin'] = pd.to_datetime(df['Datetime Event Began'])
df = df.sort_values(['state', 'county', 'start_time'])

# Calculate Information Gravity K
print("\n--- CALCULATING INFORMATION GRAVITY (K) ---")

def calculate_k_for_county(group):
    """Calculate K = current / historical_max for each outage"""
    historical_max = group['max_customers'].max()
    if historical_max == 0:
        historical_max = 1
    group['IG_K'] = group['max_customers'] / historical_max
    return group

# Apply the calculation
df = df.groupby(['state', 'county'], group_keys=False).apply(calculate_k_for_county)

# Calculate lead time (NOW before filtering)
df['lead_time_mins'] = (df['event_begin'] - df['start_time']).dt.total_seconds() / 60

# Count fractures
fractures = df[df['IG_K'] > 0.5]
print(f"Total records: {len(df)}")
print(f"Fractures (K > 0.5): {len(fractures)}")

# Predictive fractures (K > 0.5 BEFORE event)
predictive = fractures[fractures['lead_time_mins'] > 0]
print(f"Predictive fractures (K>0.5 before event): {len(predictive)}")

if len(predictive) > 0:
    print(f"Average lead time: {predictive['lead_time_mins'].mean():.2f} minutes")
    print(f"Max lead time: {predictive['lead_time_mins'].max():.2f} minutes")
    print(f"Min lead time: {predictive['lead_time_mins'].min():.2f} minutes")
    
    print("\n--- LEAD TIME BY EVENT TYPE ---")
    print(predictive.groupby('Event Type')['lead_time_mins'].describe())
else:
    print("\n⚠️ No predictive fractures found with positive lead time.")
    print("Checking for near-simultaneous events (lead_time ≈ 0)...")
    near_simultaneous = fractures[abs(fractures['lead_time_mins']) < 5]
    print(f"Fractures within ±5 minutes of event: {len(near_simultaneous)}")

# Save enriched data
output_file = 'outage_data_with_igk.csv'
df.to_csv(output_file, index=False)
print(f"\n✅ Saved enriched data to {output_file}")

# Show top fractures (highest K values)
print("\n--- TOP 10 FRACTURES (Highest K) ---")
top_fractures = fractures.nlargest(10, 'IG_K')[['start_time', 'county', 'state', 'IG_K', 'lead_time_mins', 'Event Type']]
print(top_fractures.to_string())

# Show top predictive events if they exist
if len(predictive) > 0:
    print("\n--- TOP PREDICTIVE EVENTS (Highest Lead Time) ---")
    top_predictive = predictive.nlargest(10, 'lead_time_mins')[['start_time', 'county', 'state', 'IG_K', 'lead_time_mins', 'Event Type']]
    print(top_predictive.to_string())
