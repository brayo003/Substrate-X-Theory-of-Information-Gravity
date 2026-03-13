import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

print("="*60)
print("TESTING BEST PARAMETERS ON HELD-OUT DATA")
print("="*60)

# Load test data
test = pd.read_csv('test_data.csv')
print(f"Testing on {len(test)} records")

# Load best parameters from search
best_params = pd.read_csv('parameter_search_results.csv')
best = best_params.loc[best_params['roc_auc'].idxmax()]
tp = best['tangle_point']
cf = best['conflict_factor']

print(f"\nBest parameters from training:")
print(f"  tangle_point = {tp}")
print(f"  conflict_factor = {cf}")

# Fixed parameters
beta, gamma = 0.9855, 0.1857
e_mean = test['max_customers'].mean()
threshold = test['max_customers'].quantile(0.95)
tangle = threshold * tp

print(f"\nTest set statistics:")
print(f"  threshold: {threshold:.2f}")
print(f"  tangle: {tangle:.2f}")

# Create Failure_Event column
test['event_begin'] = pd.to_datetime(test['event_begin'])
test['start_time'] = pd.to_datetime(test['start_time'])
test['Failure_Event'] = 0
for event_time in test['event_begin'].unique():
    mask = (test['start_time'] >= event_time - pd.Timedelta(hours=6)) & \
           (test['start_time'] <= event_time)
    test.loc[mask, 'Failure_Event'] = 1

# Classical K
def classical_k(val):
    return ((val * beta) - (e_mean * gamma)) / (threshold * (beta - gamma))

# SXC K with best params
def sxc_k(val):
    signal = val * cf if val > tangle else val
    return ((signal * beta) - (e_mean * gamma)) / (threshold * (beta - gamma))

# Apply both
test['Classical_K'] = test['max_customers'].apply(classical_k)
test['SXC_K'] = test['max_customers'].apply(sxc_k)
test['Classical_Pred'] = (test['Classical_K'] >= 1).astype(int)
test['SXC_Pred'] = (test['SXC_K'] >= 1).astype(int)

print("\n" + "="*60)
print("TEST SET RESULTS")
print("="*60)

# Classical metrics
classical_roc = roc_auc_score(test['Failure_Event'], test['Classical_K'])
classical_prec = precision_score(test['Failure_Event'], test['Classical_Pred'])
classical_rec = recall_score(test['Failure_Event'], test['Classical_Pred'])
classical_f1 = f1_score(test['Failure_Event'], test['Classical_Pred'])

print("\nClassical Model:")
print(f"  ROC-AUC:    {classical_roc:.4f}")
print(f"  Precision:  {classical_prec:.4f}")
print(f"  Recall:     {classical_rec:.4f}")
print(f"  F1-Score:   {classical_f1:.4f}")

# SXC metrics
sxc_roc = roc_auc_score(test['Failure_Event'], test['SXC_K'])
sxc_prec = precision_score(test['Failure_Event'], test['SXC_Pred'])
sxc_rec = recall_score(test['Failure_Event'], test['SXC_Pred'])
sxc_f1 = f1_score(test['Failure_Event'], test['SXC_Pred'])

print("\nSXC Model (best params):")
print(f"  ROC-AUC:    {sxc_roc:.4f}")
print(f"  Precision:  {sxc_prec:.4f}")
print(f"  Recall:     {sxc_rec:.4f}")
print(f"  F1-Score:   {sxc_f1:.4f}")

print("\n" + "="*60)
print("IMPROVEMENT")
print("="*60)
print(f"ROC-AUC Δ:  {sxc_roc - classical_roc:+.4f}")
print(f"Recall Δ:   {sxc_rec - classical_rec:+.4f}")
print(f"F1 Δ:       {sxc_f1 - classical_f1:+.4f}")

# False positives
classical_fp = (test['Classical_Pred'] & ~test['Failure_Event']).sum()
sxc_fp = (test['SXC_Pred'] & ~test['Failure_Event']).sum()
print(f"\nFalse Positives:")
print(f"  Classical: {classical_fp}")
print(f"  SXC:       {sxc_fp}")
print(f"  Δ:         {sxc_fp - classical_fp}")
