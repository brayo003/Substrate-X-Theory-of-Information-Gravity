import pandas as pd

print("=== DIAGNOSING BOSTON DATA ===")
df = pd.read_csv("boston_311.csv")
print(f"Total records: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Check date column sample
print("\nFirst 5 raw dates:")
print(df["open_date"].head())

print("\nLast 5 raw dates:")
print(df["open_date"].tail())

# Check unique date formats
print("\nUnique date patterns (first 20):")
date_patterns = df["open_date"].astype(str).str[:19].value_counts().head(20)
print(date_patterns)

# Check case topics
print("\nCase topics distribution:")
print(df["case_topic"].value_counts().head(20))

# Save this info
df.info()
