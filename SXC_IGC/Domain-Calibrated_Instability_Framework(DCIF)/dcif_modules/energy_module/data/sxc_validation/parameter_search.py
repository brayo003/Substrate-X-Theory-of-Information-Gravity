import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
import itertools

print("="*60)
print("PARAMETER SEARCH FOR SXC")
print("="*60)

# Load training data
train = pd.read_csv('train_data.csv')
print(f"Training on {len(train)} records")

# Define parameter grid
tangle_points = [0.5, 0.6, 0.7, 0.8]
conflict_factors = [1.5, 2.0, 2.5, 3.0, 4.0]

# Fixed parameters
beta, gamma = 0.9855, 0.1857
e_mean = train['max_customers'].mean()
threshold = train['max_customers'].quantile(0.95)

print(f"\nParameters being tested:")
print(f"  tangle_point: {tangle_points}")
print(f"  conflict_factor: {conflict_factors}")
print(f"  threshold (95th %ile): {threshold:.2f}")

# Create Failure_Event column (6-hour window before each event)
train['event_begin'] = pd.to_datetime(train['event_begin'])
train['start_time'] = pd.to_datetime(train['start_time'])
train['Failure_Event'] = 0
for event_time in train['event_begin'].unique():
    mask = (train['start_time'] >= event_time - pd.Timedelta(hours=6)) & \
           (train['start_time'] <= event_time)
    train.loc[mask, 'Failure_Event'] = 1

results = []

print("\n" + "="*60)
print("SEARCHING...")
print("="*60)

for tp in tangle_points:
    for cf in conflict_factors:
        tangle = threshold * tp
        
        def sxc_k(val):
            signal = val * cf if val > tangle else val
            return ((signal * beta) - (e_mean * gamma)) / (threshold * (beta - gamma))
        
        train['SXC_K'] = train['max_customers'].apply(sxc_k)
        train['SXC_Pred'] = (train['SXC_K'] >= 1).astype(int)
        
        # Skip if no predictions
        if train['SXC_Pred'].sum() == 0:
            continue
            
        roc = roc_auc_score(train['Failure_Event'], train['SXC_K'])
        prec = precision_score(train['Failure_Event'], train['SXC_Pred'])
        rec = recall_score(train['Failure_Event'], train['SXC_Pred'])
        f1 = f1_score(train['Failure_Event'], train['SXC_Pred'])
        
        results.append({
            'tangle_point': tp,
            'conflict_factor': cf,
            'tangle_value': tangle,
            'roc_auc': roc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'true_pos': (train['SXC_Pred'] & train['Failure_Event']).sum(),
            'false_pos': (train['SXC_Pred'] & ~train['Failure_Event']).sum()
        })
        
        print(f"tp={tp}, cf={cf:3.1f} → ROC={roc:.4f}, F1={f1:.4f}")

# Show best results
results_df = pd.DataFrame(results)
print("\n" + "="*60)
print("TOP 5 BY ROC-AUC")
print("="*60)
print(results_df.nlargest(5, 'roc_auc')[['tangle_point', 'conflict_factor', 'roc_auc', 'f1_score']])

print("\n" + "="*60)
print("TOP 5 BY F1-SCORE")
print("="*60)
print(results_df.nlargest(5, 'f1_score')[['tangle_point', 'conflict_factor', 'roc_auc', 'f1_score']])

# Save all results
results_df.to_csv('parameter_search_results.csv', index=False)
print("\n✅ Saved full results to parameter_search_results.csv")

# Save best params
best_roc = results_df.loc[results_df['roc_auc'].idxmax()]
print(f"\nBest ROC-AUC: {best_roc['roc_auc']:.4f} at tp={best_roc['tangle_point']}, cf={best_roc['conflict_factor']}")
