import pandas as pd

df = pd.read_csv('domain_scales.csv')
# Connectivity is inversely proportional to gamma
# High Gamma = Low Connectivity (Information gets lost)
df['Connectivity_Index'] = (1 - (df['gamma'] / df['gamma'].max())) * 100

print("=== SUBSTRATE CONNECTIVITY MAP ===")
print(df[['domain', 'Connectivity_Index']].sort_values(by='Connectivity_Index', ascending=False).head(10))
