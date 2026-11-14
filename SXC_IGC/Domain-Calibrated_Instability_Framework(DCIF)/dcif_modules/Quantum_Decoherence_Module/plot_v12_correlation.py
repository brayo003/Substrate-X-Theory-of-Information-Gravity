import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

df = pd.read_csv('ibmq_v12_performance_map.csv')
# Filter out the 'Negative Gravity' anomalies for clean physics
df = df[df['Tension'] > 0] 

plt.figure(figsize=(10, 7))
sns.regplot(data=df, x='Tension', y='gate_error', 
            scatter_kws={'s': 100, 'alpha': 0.6, 'color': '#440154'}, 
            line_kws={'color': '#fde725'})

corr, p_val = pearsonr(df['Tension'], df['gate_error'])

plt.title(f'DCIF V12 Validation: Tension vs. Gate Error\nCorrelation: {corr:.3f} | p-value: {p_val:.4f}')
plt.xlabel('Information Gravity (Tension)')
plt.ylabel('Measured Gate Error Rate')
plt.grid(True, alpha=0.3)
plt.savefig('v12_correlation_proof.png')
print(f"Correlation Analysis Complete. R = {corr:.3f}")
