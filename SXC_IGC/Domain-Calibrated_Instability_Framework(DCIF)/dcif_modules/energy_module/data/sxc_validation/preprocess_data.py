import pandas as pd

# Load failure and load datasets
load = pd.read_csv("EIA930_BALANCE_2023.csv")
failures = pd.read_excel("oe417_DisturbanceReports_2023.xlsx")

# Normalize timestamps to UTC for consistency
load['UTC'] = pd.to_datetime(load['UTC Time'])
failures['Start'] = pd.to_datetime(failures['Event Start Time'])

# Save cleaned versions for Phase 3
load.to_csv("load_clean.csv", index=False)
failures.to_csv("failures_clean.csv", index=False)
