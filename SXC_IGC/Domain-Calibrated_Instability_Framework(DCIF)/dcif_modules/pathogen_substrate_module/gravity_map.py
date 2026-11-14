import pandas as pd

# Load the de-duplicated data
df = pd.read_csv("boston_311.csv")
df["open_date"] = pd.to_datetime(df["open_date"], utc=True, format="mixed")

# Focus on the 'Wild Animal' signals (The High-Mass Pulses)
wild_signals = df[df['case_topic'].str.contains('Wild', na=False)].copy()

print("=== PATHOGEN EPICENTER ANALYSIS ===")
# Identify the Top 5 High-Gravity Neighborhoods
gravity_centers = wild_signals['neighborhood'].value_counts().head(5)

print("\nTop 5 Infected Nodes (Neighborhoods):")
for neighborhood, count in gravity_centers.items():
    # Calculate the 'Local Gravity' (Reports per neighborhood)
    print(f"Node: {neighborhood: <20} | Density: {count} signals")

# Find the first 'Fracture' in time
wild_signals = wild_signals.sort_values('open_date')
patient_zero_time = wild_signals['open_date'].iloc[0]
patient_zero_loc = wild_signals['neighborhood'].iloc[0]

print(f"\nINITIAL FRACTURE DETECTED:")
print(f"Time: {patient_zero_time}")
print(f"Location: {patient_zero_loc}")
