import pandas as pd

# UPDATED FILENAME to match your 'ls' output
file_path = 'nyc_311_sample_10k.csv'
cols = ['created_date', 'complaint_type', 'descriptor', 'incident_zip', 'street_name']

try:
    df = pd.read_csv(file_path, usecols=cols, low_memory=False)
    # Convert to datetime
    df['created_date'] = pd.to_datetime(df['created_date'])

    print("--- SUBSTRATE SIGNAL ANALYSIS ---")
    print(f"Total Records: {len(df)}")
    print("\nTop 10 Complaint Types (The Pulse):")
    print(df['complaint_type'].value_counts().head(10))

    # Filter for signals of 'Urban Decay' or 'Substrate Capture'
    # We look for Drug Activity, Homeless Encampments, or Needles
    targets = 'Drug|Needle|Encampment|Syringe|Bottle|Graffiti'
    drug_signals = df[df['complaint_type'].str.contains(targets, case=False, na=False)]

    print("\n--- DETECTED DECAY SIGNALS ---")
    if drug_signals.empty:
        print("No direct drug/decay signals found in this 10k sample.")
        print("Note: If the sample is 'Snow or Ice' heavy, the drug substrate may be shadowed.")
    else:
        print(drug_signals[['complaint_type', 'descriptor']].value_counts().head(10))

    # Identify the 'High Gravity' zip code (The epicenter of instability)
    if not drug_signals.empty:
        print("\nTop 5 High-Gravity Zip Codes:")
        print(drug_signals['incident_zip'].value_counts().head(5))

except FileNotFoundError:
    print(f"Error: Still can't find {file_path}. Check permissions or paths.")
