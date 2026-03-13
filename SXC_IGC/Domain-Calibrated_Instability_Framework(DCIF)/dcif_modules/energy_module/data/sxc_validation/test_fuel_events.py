import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

print("="*60)
print("TESTING SXC ON FUEL SUPPLY EVENTS ONLY")
print("="*60)

# Load data
df = pd.read_csv('outage_data_with_igk.csv')
fuel = df[df['Event Type'].str.contains('Fuel', na=False)].copy()
print(f"Fuel events only: {len(fuel)} records")

# Create Failure_Event column
fuel['event_begin'] = pd.to_datetime(fuel['event_begin'])
fuel['start_time'] = pd.to_datetime(fuel['start_time'])
fuel['Failure_Event'] = 0
for event_time in fuel['event_begin'].unique():
    mask = (fuel['start_time'] >= event_time - pd.Timedelta(hours=6)) & \
           (fuel['start_time'] <= event_time)
    fuel.loc[mask, 'Failure_Event'] = 1
print(f"Positive samples (6h before events): {fuel['Failure_Event'].sum()}")

# Parameters
beta, gamma = 0.9855, 0.1857
e_mean = fuel['max_customers'].mean()
threshold = fuel['max_customers'].quantile(0.95)
tangle = threshold * 0.5  # Using best from search
cf = 1.5

print(f"\nParameters:")
print(f"  threshold: {threshold:.2f}")
print(f"  tangle: {tangle:.2f}")
print(f"  conflict: {cf}")

# Classical K
def classical_k(val):
    return ((val * beta) - (e_mean * gamma)) / (threshold * (beta - gamma))

# SXC K
def sxc_k(val):
    signal = val * cf if val > tangle else val
    return ((signal * beta) - (e_mean * gamma)) / (threshold * (beta - gamma))

# Apply both
fuel['Classical_K'] = fuel['max_customers'].apply(classical_k)
fuel['SXC_K'] = fuel['max_customers'].apply(sxc_k)
fuel['Classical_Pred'] = (fuel['Classical_K'] >= 1).astype(int)
fuel['SXC_Pred'] = (fuel['SXC_K'] >= 1).astype(int)

print("\n" + "="*60)
print("RESULTS")
print("="*60)

# Classical
print("\nClassical Model:")
print(f"  ROC-AUC:    {roc_auc_score(fuel['Failure_Event'], fuel['Classical_K']):.4f}")
print(f"  Precision:  {precision_score(fuel['Failure_Event'], fuel['Classical_Pred']):.4f}")
print(f"  Recall:     {recall_score(fuel['Failure_Event'], fuel['Classical_Pred']):.4f}")
print(f"  F1-Score:   {f1_score(fuel['Failure_Event'], fuel['Classical_Pred']):.4f}")

# SXC
print("\nSXC Model:")
print(f"  ROC-AUC:    {roc_auc_score(fuel['Failure_Event'], fuel['SXC_K']):.4f}")
print(f"  Precision:  {precision_score(fuel['Failure_Event'], fuel['SXC_Pred']):.4f}")
print(f"  Recall:     {recall_score(fuel['Failure_Event'], fuel['SXC_Pred']):.4f}")
print(f"  F1-Score:   {f1_score(fuel['Failure_Event'], fuel['SXC_Pred']):.4f}")

# False positives
classical_fp = (fuel['Classical_Pred'] & ~fuel['Failure_Event']).sum()
sxc_fp = (fuel['SXC_Pred'] & ~fuel['Failure_Event']).sum()
print(f"\nFalse Positives:")
print(f"  Classical: {classical_fp}")
print(f"  SXC:       {sxc_fp}")
