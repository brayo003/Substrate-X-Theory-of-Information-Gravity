import pandas as pd

# Load your enriched data
df = pd.read_csv('outage_data_with_igk.csv')
df['event_begin'] = pd.to_datetime(df['event_begin'])
df['start_time'] = pd.to_datetime(df['start_time'])

# Create Failure_Event column (6-hour window before each event)
df['Failure_Event'] = 0
for event_time in df['event_begin'].unique():
    mask = (df['start_time'] >= event_time - pd.Timedelta(hours=6)) & \
           (df['start_time'] <= event_time)
    df.loc[mask, 'Failure_Event'] = 1

# Save for Phase 4
df.to_csv('aligned_for_validation.csv', index=False)
print(f"Created validation file with {df['Failure_Event'].sum()} positive samples")
