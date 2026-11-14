import pandas as pd
import os

filepath = 'raw_data/normal_lung_control.txt'

if not os.path.exists(filepath):
    print("CRITICAL: File does not exist.")
    exit()

print(f"AUDITING SUBSTRATE: {filepath}")
print("-" * 40)

# Load the first 5 lines to check headers
try:
    df = pd.read_csv(filepath, sep='\t')
    print(f"COLUMNS FOUND: {list(df.columns)}")
    
    # Check for expected miRNA identifiers
    if 'miRNA_ID' in df.columns or 'miRNA_id' in df.columns:
        print("VERDICT: HEADER INTEGRITY VALIDATED (miRNA Format detected)")
    else:
        print("VERDICT: HEADER MISMATCH. This might be a different data type.")

    # Check Signal Density
    row_count = len(df)
    print(f"SIGNAL UNITS: {row_count}")
    if row_count > 500:
        print("VERDICT: SIGNAL DENSITY VALIDATED (Sufficient for V12 Engine)")
    else:
        print("VERDICT: DENSITY WARNING. File may be truncated.")

except Exception as e:
    print(f"CRITICAL: Failed to parse file. {e}")
