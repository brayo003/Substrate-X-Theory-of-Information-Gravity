import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
import warnings

warnings.filterwarnings('ignore')

def run_v12_gen():
    path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
    train = pd.read_csv(path + 'Train.csv')
    test = pd.read_csv(path + 'Test.csv')
    indic = pd.read_csv('processed_indicators.csv')
    
    y = train['target']
    test_ids = test['ID']

    def prep_data(df):
        # 1. Bucket the Amounts (Stop memorization)
        df['Amt_Bin'] = pd.qcut(df['Total_Amount'], 10, labels=False, duplicates='drop')
        
        # 2. Ratio features are harder to memorize
        df['Risk_Ratio'] = df['Total_Amount_to_Repay'] / (df['Total_Amount'] + 1)
        df['Time_Pressure'] = df['Total_Amount_to_Repay'] / (df['duration'] + 1)
        
        # 3. Simplify categories
        df['is_Type1'] = (df['loan_type'] == 'Type 1').astype(int)
        
        # 4. Extract simple time cycles
        df['disbursement_date'] = pd.to_datetime(df['disbursement_date'])
        df['Month'] = df['disbursement_date'].dt.month
        
        features = ['Amt_Bin', 'Risk_Ratio', 'Time_Pressure', 'duration', 'is_Type1', 'Month']
        return df[features]

    X = prep_data(train)
    X_test = prep_data(test)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    test_probs = np.zeros(len(X_test))
    oof_probs = np.zeros(len(X))

    print(f"Training on {X.shape[1]} RUTHLESS features...")

    for tr_idx, val_idx in skf.split(X, y):
        # High regularization to force generalization
        model = XGBClassifier(
            n_estimators=500,
            max_depth=3, # Shallower trees = less overfitting
            learning_rate=0.05,
            subsample=0.6,
            colsample_bytree=0.6,
            random_state=42
        )
        model.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        oof_probs[val_idx] = model.predict_proba(X.iloc[val_idx])[:, 1]
        test_probs += model.predict_proba(X_test)[:, 1] / 5

    best_f1, best_t = 0, 0.5
    for t in np.arange(0.2, 0.7, 0.01):
        score = f1_score(y, (oof_probs > t).astype(int))
        if score > best_f1:
            best_f1, best_t = score, t
            
    print(f"\n--- GENERALIZED CV F1: {best_f1:.4f} @ Threshold {best_t:.2f} ---")
    
    final_preds = (test_probs > best_t).astype(int)
    pd.DataFrame({'ID': test_ids, 'target': final_preds}).to_csv('V12_General.csv', index=False)

if __name__ == "__main__":
    run_v12_gen()
