import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import f1_score
import re, warnings

warnings.filterwarnings('ignore')

def clean_col_names(df):
    new_cols = [re.sub(r'[^\w\s]', '_', str(c)).replace(' ', '_') for c in df.columns]
    df.columns = new_cols
    return df

def run_v12_final_push():
    path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
    train = pd.read_csv(path + 'Train.csv')
    test = pd.read_csv(path + 'Test.csv')
    indic = pd.read_csv('processed_indicators.csv')
    
    y = train['target']
    test_ids = test['ID']
    
    # 1. Integration & Interaction
    for df in [train, test]:
        df['disbursement_date'] = pd.to_datetime(df['disbursement_date'])
        df['Year'] = df['disbursement_date'].dt.year
        
    train = train.merge(indic, left_on=['country_id', 'Year'], right_on=['Country', 'Year'], how='left')
    test = test.merge(indic, left_on=['country_id', 'Year'], right_on=['Country', 'Year'], how='left')

    def engineer(df):
        # Existing V12 Logic
        df['Interest_Rate'] = (df['Total_Amount_to_Repay'] / (df['Total_Amount'] + 1)) - 1
        inf_col = 'Inflation, consumer prices (annual %)'
        
        # THE MACRO-TYPE INTERACTION (The #1 Seeker)
        # We target Type_1 and Type_2 specifically since they are the most important
        if inf_col in df.columns:
            df['Type1_Inflation_Stress'] = (df['loan_type'] == 'Type_1').astype(int) * df[inf_col]
            df['Type2_Inflation_Stress'] = (df['loan_type'] == 'Type_2').astype(int) * df[inf_col]
            df['Real_Interest_Spread'] = df['Interest_Rate'] - (df[inf_col] / 100)

        df['Repay_Velocity'] = df['Total_Amount_to_Repay'] / (df['duration'] + 1)
        return df

    train, test = engineer(train), engineer(test)

    # 2. Strict ID Exclusion (Anti-Overfit)
    drop_cols = ['ID', 'customer_id', 'tbl_loan_id', 'target', 'disbursement_date', 'due_date', 'Country']
    features = [c for c in train.columns if c not in drop_cols]
    
    X = clean_col_names(pd.get_dummies(train[features], dummy_na=True))
    X_test = clean_col_names(pd.get_dummies(test[features], dummy_na=True))
    X_test = X_test.reindex(columns=X.columns, fill_value=0)
    
    # 3. Training the Monster
    print(f"[V12] Launching with interaction features on {len(X.columns)} signals...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    test_probs = np.zeros(len(X_test))
    oof_probs = np.zeros(len(X))

    for tr_idx, val_idx in skf.split(X, y):
        X_tr, y_tr = X.iloc[tr_idx], y.iloc[tr_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
        
        # Tuned XGB for the final push
        model = XGBClassifier(n_estimators=1200, learning_rate=0.015, max_depth=6, 
                              scale_pos_weight=3, subsample=0.8, colsample_bytree=0.8, random_state=42)
        model.fit(X_tr, y_tr)
        
        oof_probs[val_idx] = model.predict_proba(X_val)[:, 1]
        test_probs += model.predict_proba(X_test)[:, 1] / 5

    # 4. Final Score & Threshold
    best_f1, best_t = 0, 0.5
    for t in np.arange(0.2, 0.7, 0.01):
        score = f1_score(y, (oof_probs > t).astype(int))
        if score > best_f1:
            best_f1, best_t = score, t
            
    print(f"--- V12 FINAL CV F1: {best_f1:.4f} @ Threshold {best_t:.2f} ---")
    
    final_preds = (test_probs > best_t).astype(int)
    pd.DataFrame({'ID': test_ids, 'target': final_preds}).to_csv('V12_Leaderboard_Crusher.csv', index=False)

if __name__ == "__main__":
    run_v12_final_push()
