import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

print("="*60)
print("SPLITTING DATA FOR PARAMETER SEARCH")
print("="*60)

# Load your enriched data
df = pd.read_csv('outage_data_with_igk.csv')
print(f"Total records: {len(df)}")

# Create a year column if not present
df['start_time'] = pd.to_datetime(df['start_time'])
df['year'] = pd.DatetimeIndex(df['start_time']).year

# Option 1: Split by year (recommended - tests generalization across time)
if 2018 in df['year'].values and 2019 in df['year'].values:
    train = df[df['year'] == 2018].copy()
    test = df[df['year'] == 2019].copy()
    print(f"\nSplit by year:")
    print(f"  Train (2018): {len(train)} records")
    print(f"  Test (2019): {len(test)} records")
else:
    # Option 2: Random split if only one year
    train, test = train_test_split(df, test_size=0.3, random_state=42)
    print(f"\nRandom split (70/30):")
    print(f"  Train: {len(train)} records")
    print(f"  Test: {len(test)} records")

# Save splits
train.to_csv('train_data.csv', index=False)
test.to_csv('test_data.csv', index=False)
print(f"\n✅ Saved train_data.csv and test_data.csv")
