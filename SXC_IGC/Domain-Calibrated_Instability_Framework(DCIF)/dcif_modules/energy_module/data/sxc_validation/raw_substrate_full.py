import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score

# ================== LOAD DATA ==================
print("="*60)
print("RAW SUBSTRATE FULL ANALYSIS")
print("="*60)

raw = pd.read_csv('outage_data/Outage_Dataset/eaglei_outages_2018_merged.csv')
events = pd.read_csv('outage_data/Outage_Dataset/eaglei_outages_with_events_2018.csv')

raw['start_time'] = pd.to_datetime(raw['start_time'])
events['start_time'] = pd.to_datetime(events['start_time'])

print(f"Raw records: {len(raw)}")
print(f"Event records: {len(events)}")
print(f"Raw date range: {raw['start_time'].min()} to {raw['start_time'].max()}")
print(f"Event date range: {events['start_time'].min()} to {events['start_time'].max()}")

# ================== CREATE FAILURE WINDOWS ==================
print("\nCreating failure windows...")
raw['Failure_Event'] = 0
event_times = events['start_time'].unique()

for et in event_times:
    mask = (raw['start_time'] >= et - pd.Timedelta(hours=6)) & \
           (raw['start_time'] <= et)
    raw.loc[mask, 'Failure_Event'] = 1

print(f"Positive samples (6h before events): {raw['Failure_Event'].sum()}")
print(f"Negative samples: {len(raw) - raw['Failure_Event'].sum()}")

# ================== CALCULATE K (Information Gravity) ==================
print("\nCalculating Information Gravity K...")

def calculate_k_for_county(group):
    historical_max = group['max_customers'].max()
    if historical_max == 0:
        historical_max = 1
    group['IG_K'] = group['max_customers'] / historical_max
    return group

raw = raw.groupby(['state', 'county'], group_keys=False).apply(calculate_k_for_county)

# ================== FIND PREDICTIVE WARNINGS ==================
print("\nFinding predictive warnings...")

# Merge with event times to compare
event_times_df = events[['start_time', 'event_id', 'Event Type']].drop_duplicates()
event_times_df = event_times_df.rename(columns={'start_time': 'event_time'})

# For each raw record, find closest future event in same county
predictive = []

for idx, row in raw.iterrows():
    if row['IG_K'] > 0.5:
        # Find events in same county after this time
        future_events = events[(events['county'] == row['county']) & 
                               (events['start_time'] > row['start_time'])]
        if not future_events.empty:
            first_event = future_events.iloc[0]
            lead_time = (first_event['start_time'] - row['start_time']).total_seconds() / 3600  # hours
            predictive.append({
                'raw_time': row['start_time'],
                'event_time': first_event['start_time'],
                'county': row['county'],
                'state': row['state'],
                'IG_K': row['IG_K'],
                'lead_time_hours': lead_time,
                'event_type': first_event['Event Type']
            })

predictive_df = pd.DataFrame(predictive)
print(f"Total predictive warnings (K>0.5 before event): {len(predictive_df)}")

if len(predictive_df) > 0:
    print(f"\nLead time stats (hours):")
    print(predictive_df['lead_time_hours'].describe())
    
    print(f"\nTop 10 longest lead times:")
    print(predictive_df.nlargest(10, 'lead_time_hours')[['county', 'state', 'IG_K', 'lead_time_hours', 'event_type']])
    
    print(f"\nLead time by event type:")
    print(predictive_df.groupby('event_type')['lead_time_hours'].describe())
    
    # Save predictive warnings
    predictive_df.to_csv('predictive_warnings.csv', index=False)
    print(f"\n✅ Saved {len(predictive_df)} predictive warnings to predictive_warnings.csv")

# ================== ROC ANALYSIS ==================
print("\n" + "="*60)
print("ROC ANALYSIS")
print("="*60)

# Sample for ROC (too many records, take random sample)
sample_size = min(100000, len(raw))
raw_sample = raw.sample(n=sample_size, random_state=42)

print(f"ROC on {sample_size} sampled records:")

# Classical (customers)
roc_classical = roc_auc_score(raw_sample['Failure_Event'], raw_sample['max_customers'])
print(f"  Classical (max_customers): {roc_classical:.4f}")

# IG_K
roc_igk = roc_auc_score(raw_sample['Failure_Event'], raw_sample['IG_K'])
print(f"  Information Gravity K: {roc_igk:.4f}")

# ================== PLOT LEAD TIME DISTRIBUTION ==================
if len(predictive_df) > 0:
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.hist(predictive_df['lead_time_hours'], bins=50, edgecolor='black')
    plt.xlabel('Lead Time (hours)')
    plt.ylabel('Count')
    plt.title('Distribution of Lead Times')
    
    plt.subplot(1, 2, 2)
    plt.boxplot([predictive_df[predictive_df['event_type'] == t]['lead_time_hours'] 
                 for t in predictive_df['event_type'].unique()[:5]], 
                labels=predictive_df['event_type'].unique()[:5])
    plt.xticks(rotation=45)
    plt.ylabel('Lead Time (hours)')
    plt.title('Lead Time by Event Type (top 5)')
    plt.tight_layout()
    
    plt.savefig('lead_time_analysis.png')
    print("\n✅ Plot saved to lead_time_analysis.png")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
