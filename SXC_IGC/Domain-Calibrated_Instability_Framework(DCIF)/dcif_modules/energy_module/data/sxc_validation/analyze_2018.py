import pandas as pd
import numpy as np

# Load the main file
print("Loading 2018 outage data...")
df = pd.read_csv('outage_data/Outage_Dataset/eaglei_outages_with_events_2018.csv')

# Basic stats
print(f"\n{'='*50}")
print("BASIC STATISTICS")
print(f"{'='*50}")
print(f"Total records: {len(df)}")
print(f"Unique event_ids: {df['event_id'].nunique()}")
print(f"States covered: {df['state_event'].nunique()}")
print(f"\nOutage magnitude stats (max_customers):")
print(df['max_customers'].describe())

# Duration analysis (convert minutes to hours)
print(f"\n{'='*50}")
print("DURATION ANALYSIS")
print(f"{'='*50}")
df['duration_hours'] = df['duration'] / 60
print(f"\nDuration stats (hours):")
print(df['duration_hours'].describe())

# Group by event to see multi-county events
print(f"\n{'='*50}")
print("EVENT SUMMARY (by event_id)")
print(f"{'='*50}")
event_summary = df.groupby('event_id').agg({
    'max_customers': 'sum',
    'duration': 'mean',
    'fips': 'nunique'
}).rename(columns={'fips': 'counties_affected'})

print(f"\nEvent summary stats:")
print(event_summary.describe())

# Additional useful stats
print(f"\n{'='*50}")
print("TOP 10 LARGEST EVENTS (by total customers affected)")
print(f"{'='*50}")
top_events = event_summary.nlargest(10, 'max_customers')[['max_customers', 'counties_affected']]
print(top_events)

print(f"\n{'='*50}")
print("DURATION DISTRIBUTION")
print(f"{'='*50}")
print(f"Events shorter than 1 hour: {len(df[df['duration_hours'] < 1])}")
print(f"Events 1-6 hours: {len(df[(df['duration_hours'] >= 1) & (df['duration_hours'] < 6)])}")
print(f"Events 6-24 hours: {len(df[(df['duration_hours'] >= 6) & (df['duration_hours'] < 24)])}")
print(f"Events longer than 24 hours: {len(df[df['duration_hours'] >= 24])}")

print(f"\nAnalysis complete!")
