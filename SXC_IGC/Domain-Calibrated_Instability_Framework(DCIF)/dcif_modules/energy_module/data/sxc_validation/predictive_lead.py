import pandas as pd

# Load the data WITH your IG_K column
# You need to save your calculate_igc.py output first
df = pd.read_csv('outage_data_with_igk.csv')  # Save this from your previous script

df['start_time'] = pd.to_datetime(df['start_time'])
df['event_begin'] = pd.to_datetime(df['Datetime Event Began'])

# Calculate lead time
df['lead_time_mins'] = (df['event_begin'] - df['start_time']).dt.total_seconds() / 60

# Filter for fractures that happened BEFORE the event
predictive = df[(df['IG_K'] > 0.5) & (df['lead_time_mins'] > 0)]

print(f"Fractures that occurred BEFORE events: {len(predictive)}")
print(f"Average lead time: {predictive['lead_time_mins'].mean():.2f} minutes")
print(f"Max lead time: {predictive['lead_time_mins'].max():.2f} minutes")

# See if different event types have different lead times
print("\nLead time by event type:")
print(predictive.groupby('Event Type')['lead_time_mins'].describe())
