import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

print("="*60)
print("PHASE 4: SXC VALIDATION AGAINST REAL FAILURE WINDOWS")
print("="*60)

# Load aligned data
df = pd.read_csv('aligned_for_validation.csv')
print(f"Loaded {len(df)} records with {df['Failure_Event'].sum()} positive samples")

# Define parameters (from your energy module)
beta, gamma = 0.9855, 0.1857
e_mean = df['max_customers'].mean()  # Using max_customers as load proxy
threshold = df['max_customers'].quantile(0.95)
tangle_point = threshold * 0.70
conflict_factor = 2.8

print(f"\nParameters:")
print(f"  beta: {beta}")
print(f"  gamma: {gamma}")
print(f"  threshold (95th %ile): {threshold:.2f}")
print(f"  tangle_point (70% of threshold): {tangle_point:.2f}")
print(f"  conflict_factor: {conflict_factor}")

# Classical K (linear)
def classical_k(val):
    return ((val * beta) - (e_mean * gamma)) / (threshold * (beta - gamma))

# SXC K (nonlinear gain at tangle point)
def sxc_k(val):
    signal = val * conflict_factor if val > tangle_point else val
    return ((signal * beta) - (e_mean * gamma)) / (threshold * (beta - gamma))

# Apply both
df['Classical_K'] = df['max_customers'].apply(classical_k)
df['SXC_K'] = df['max_customers'].apply(sxc_k)

# Binary predictions (K >= 1 means "failure predicted")
df['Classical_Pred'] = (df['Classical_K'] >= 1).astype(int)
df['SXC_Pred'] = (df['SXC_K'] >= 1).astype(int)

print("\n" + "="*60)
print("ROC-AUC SCORES (higher = better at ranking risk)")
print("="*60)
print(f"Classical ROC-AUC: {roc_auc_score(df['Failure_Event'], df['Classical_K']):.4f}")
print(f"SXC ROC-AUC: {roc_auc_score(df['Failure_Event'], df['SXC_K']):.4f}")

print("\n" + "="*60)
print("CLASSIFICATION METRICS (at K >= 1 threshold)")
print("="*60)

# Classical metrics
classical_precision = precision_score(df['Failure_Event'], df['Classical_Pred'])
classical_recall = recall_score(df['Failure_Event'], df['Classical_Pred'])
classical_f1 = f1_score(df['Failure_Event'], df['Classical_Pred'])

print("\nClassical Model:")
print(f"  Precision: {classical_precision:.4f} (of alarms raised, how many were real)")
print(f"  Recall:    {classical_recall:.4f} (of real failures, how many caught)")
print(f"  F1-Score:  {classical_f1:.4f} (harmonic mean)")

# SXC metrics
sxc_precision = precision_score(df['Failure_Event'], df['SXC_Pred'])
sxc_recall = recall_score(df['Failure_Event'], df['SXC_Pred'])
sxc_f1 = f1_score(df['Failure_Event'], df['SXC_Pred'])

print("\nSXC Model:")
print(f"  Precision: {sxc_precision:.4f}")
print(f"  Recall:    {sxc_recall:.4f}")
print(f"  F1-Score:  {sxc_f1:.4f}")

# Improvement
print("\n" + "="*60)
print("IMPROVEMENT")
print("="*60)
print(f"ROC-AUC Δ: +{(roc_auc_score(df['Failure_Event'], df['SXC_K']) - roc_auc_score(df['Failure_Event'], df['Classical_K'])):.4f}")
print(f"Recall Δ:  +{(sxc_recall - classical_recall):.4f}")
print(f"F1 Δ:      +{(sxc_f1 - classical_f1):.4f}")

# False positive analysis
classical_fp = len(df[(df['Classical_Pred']==1) & (df['Failure_Event']==0)])
sxc_fp = len(df[(df['SXC_Pred']==1) & (df['Failure_Event']==0)])
print(f"\nFalse Positives:")
print(f"  Classical: {classical_fp}")
print(f"  SXC:       {sxc_fp}")
print(f"  Δ:         {sxc_fp - classical_fp}")

# Save results
df[['start_time', 'event_begin', 'max_customers', 'IG_K', 'Classical_K', 'SXC_K', 
    'Classical_Pred', 'SXC_Pred', 'Failure_Event', 'Event Type']].to_csv('validation_results.csv', index=False)
print("\n✅ Saved detailed results to validation_results.csv")
