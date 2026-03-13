import pandas as pd

# Check 2018 matched events
df_2018 = pd.read_csv('outage_data/Outage_Dataset/eaglei_outages_with_events_2018.csv')
print(f"2018 matched events: {len(df_2018)}")
print("\nColumns:", df_2018.columns.tolist())
print("\nSample:")
print(df_2018.head())

# Check time-lagged versions
df_2018_8h = pd.read_csv('outage_data/Outage_Dataset/eaglei_outages_with_events_2018_8_hours_lag.csv')
df_2018_24h = pd.read_csv('outage_data/Outage_Dataset/eaglei_outages_with_events_2018_24_hours_lag.csv')
print(f"\n8-hour lag records: {len(df_2018_8h)}")
print(f"24-hour lag records: {len(df_2018_24h)}")
