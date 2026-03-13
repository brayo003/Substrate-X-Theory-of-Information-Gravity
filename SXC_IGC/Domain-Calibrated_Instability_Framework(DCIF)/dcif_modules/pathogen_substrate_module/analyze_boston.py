import pandas as pd

df = pd.read_csv("boston_311.csv")
print("=== BOSTON SUBSTRATE ANALYSIS ===")
print(f"Total records: {len(df)}")

# Convert dates properly with mixed format
df["open_date"] = pd.to_datetime(df["open_date"], utc=True, format="mixed")
df["month"] = df["open_date"].dt.to_period("M")

print(f"Date range: {df['open_date'].min()} to {df['open_date'].max()}")
print(f"Months: {df['month'].nunique()}")

# Define decay signals for Boston context
decay_topics = [
    "Wild Animal Issue",
    "Fallen Tree or Branches", 
    "Tree or Stump Removal",
    "Pruning Request",
    "Domestic Animal Issue"
]

decay = df[df["case_topic"].isin(decay_topics)]
print(f"\nDecay signals found: {len(decay)} records")
print(decay["case_topic"].value_counts())

# Monthly decay trend
monthly = decay.groupby("month").size()
print("\nMonthly decay trend:")
print(monthly)

# Calculate K for each month
for month in monthly.index:
    month_records = df[df["month"] == month]
    month_decay = decay[decay["month"] == month]
    k = len(month_decay) / len(month_records) if len(month_records) > 0 else 0
    print(f"{month}: K={k:.3f} ({len(month_decay)}/{len(month_records)})")
