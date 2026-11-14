import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import f1_score
import warnings

warnings.filterwarnings('ignore')

def run_v12_truth():
    path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
    train = pd.read_csv(path + 'Train.csv')
    test = pd.read_csv(path + 'Test.csv')
    
    y = train['target']
    test_ids = test['ID']

    def prep_data(df, is_train=True):
        # Feature Engineering
        df['disbursement_date'] = pd.to_datetime(df['disbursement_date'])
        df['Month'] = df['disbursement_date'].dt.month
        df['Day'] = df['disbursement_date'].dt.day
        
        # Financial Ratios (Harder to overfit)
        df['Rate'] = df['Total_Amount_to_Repay'] / (df['Total_Amount'] + 1)
        df['Velocity'] = df['Total_Amount_to_Repay'] / (df['duration'] + 1)
        
        # Add a tiny bit of noise to training to stop memorization
        if is_train:
            df['Total_Amount'] += np.random.normal(0, df['Total_Amount'].std() * 0.01, size=len(df))
            
        features = ['Total_Amount', 'Total_Amount_to_Repay', 'duration', 'Month', 'Day', 'Rate', 'Velocity']
        return df[features]

    X = prep_data(train, is_train=True)
    X_test = prep_data(test, is_train=False)

    # Use REPEATED KFold for a much more stable CV
    rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=42)
    test_probs = np.zeros(len(X_test))
    oof_probs = np.zeros(len(X))

    print("Running Stability Test...")

    for tr_idx, val_idx in rskf.split(X, y):
        model = XGBClassifier(
            n_estimators=1000,
            max_depth=3,
            learning_rate=0.01, # Slow learning is key for finance
            subsample=0.5,      # Very aggressive subsampling
            colsample_bytree=0.5,
            scale_pos_weight=3,
            random_state=42
        )
        model.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        oof_probs[val_idx] += model.predict_proba(X.iloc[val_idx])[:, 1] / 2
        test_probs += model.predict_proba(X_test)[:, 1] / 10

    best_f1, best_t = 0, 0.5
    for t in np.arange(0.1, 0.8, 0.01):
        score = f1_score(y, (oof_probs > t).astype(int))
        if score > best_f1:
            best_f1, best_t = score, t
            
    print(f"\n--- STABLE CV F1: {best_f1:.4f} @ Threshold {best_t:.2f} ---")
    
    final_preds = (test_probs > best_t).astype(int)
    pd.DataFrame({'ID': test_ids, 'target': final_preds}).to_csv('V12_Truth.csv', index=False)

if __name__ == "__main__":
    run_v12_truth()
