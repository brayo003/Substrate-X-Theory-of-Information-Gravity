import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('ibmq_toronto_substrate_map.csv')

plt.figure(figsize=(12, 6))
sns.barplot(data=df, x='qubit', y='Tension', palette='viridis')
plt.axhline(0.5, color='red', linestyle='--', label='High Gravity Threshold')
plt.title('DCIF Substrate Tension: IBMQ Toronto')
plt.ylabel('Information Gravity (Tension)')
plt.xlabel('Qubit Index')
plt.legend()
plt.savefig('toronto_tension_map.png')
print("Heatmap saved to toronto_tension_map.png")
