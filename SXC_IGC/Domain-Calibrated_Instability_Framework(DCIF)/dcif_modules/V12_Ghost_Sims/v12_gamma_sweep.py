import pandas as pd
import numpy as np

df = pd.read_csv("lhc_real_data.csv", on_bad_lines='skip')
df.columns = df.columns.str.strip()
df['flux'] = pd.to_numeric(df['pt1'], errors='coerce') + pd.to_numeric(df['pt2'], errors='coerce')
df = df.dropna(subset=['flux'])

gammas = [0.0001, 0.001, 0.01, 0.1]
print(f"{'Gamma':<10} | {'Shatter Events':<15} | {'Notes'}")
print("-" * 45)

for g in gammas:
    limit = 10**8 # Fixed limit to see how Gamma affects tension
    tension = (df['flux'] / g**2)
    shatters = len(df[tension > limit])
    
    note = "Extreme" if g == 0.0001 else "Hidden Sector" if g == 0.01 else "Quantum Gravity"
    print(f"{g:<10} | {shatters:<15} | {note}")

