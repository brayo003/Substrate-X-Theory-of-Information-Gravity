import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier
from sklearn.metrics import f1_score
import re, warnings

warnings.filterwarnings('ignore')

def clean_col_names(df):
    new_cols = [re.sub(r'[^\w\s]', '_', str(c)).replace(' ', '_') for c in df.columns]
    df.columns = new_cols
    return df

def run_v12_recovery():
    path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
    train = pd.read_csv(path + 'Train.csv')
    test = pd.read_csv(path + 'Test.csv')
    indic = pd.read_csv('processed_indicators.csv')
    
    # 1. THE FIX: Forward-fill the Macro Data for 2024
    # Ensure every country has a row for 2024 by copying 2023
    indic_2023 = indic[indic['Year'] == 2023].copy()
    indic_2023['Year'] = 2024
    indic = pd.concat([indic, indic_2023]).drop_duplicates(subset=['Country', 'Year'])
    
    y = train['target']
    test_ids = test['ID']
    
    for df in [train, test]:
        df['disbursement_date'] = pd.to_datetime(df['disbursement_date'])
        df['Year'] = df['disbursement_date'].dt.year
        
    train = train.merge(indic, left_on=['country_id', 'Year'], right_on=['Country', 'Year'], how='left')
    test = test.merge(indic, left_on=['country_id', 'Year'], right_on=['Country', 'Year'], how='left')

    # Fill any remaining NaNs (for countries that might not be in the indicator file)
    # Use the median value for that year across other countries
    for col in indic.columns:
        if col not in ['Country', 'Year']:
            train[col] = train.groupby('Year')[col].transform(lambda x: x.fillna(x.median()))
            test[col] = test.groupby('Year')[col].transform(lambda x: x.fillna(x.median()))

    def engineer(df):
        df['Interest_Rate'] = (df['Total_Amount_to_Repay'] / (df['Total_Amount'] + 1)) - 1
        inf_col = 'Inflation__consumer_prices__annual___' # Note: sanitized name
        
        # We'll use sanitized names here to be safe
        df = clean_col_names(df)
        
        # Re-calc interactions with sanitized names
        if 'Inflation__consumer_prices__annual___' in df.columns:
            inf = 'Inflation__consumer_prices__annual___'
            df['Type1_Inf_Stress'] = (df['loan_type_Type_1'] if 'loan_type_Type_1' in df.columns else 0) * df[inf]
            df['Real_Spread'] = df['Interest_Rate'] - (df[inf] / 100)

        df['Repay_Vel'] = df['Total_Amount_to_Repay'] / (df['duration'] + 1)
        return df

    # Prep for dummy vars
    drop_cols = ['ID', 'customer_id', 'tbl_loan_id', 'target', 'disbursement_date', 'due_date', 'Country', 'country_id']
    X = pd.get_dummies(train.drop(columns=['target']), dummy_na=True)
    X_test = pd.get_dummies(test, dummy_na=True)
    
    X = clean_col_names(X)
    X_test = clean_col_names(X_test)
    
    # Feature engineering AFTER dummies to ensure loan_type is available
    X = engineer(X)
    X_test = engineer(X_test)
    
    # Keep only features we want
    features = [c for c in X.columns if c not in drop_cols]
    X, X_test = X[features], X_test[features]
    X_test = X_test.reindex(columns=X.columns, fill_value=0)

    # Training
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    test_probs = np.zeros(len(X_test))
    oof_probs = np.zeros(len(X))

    for tr_idx, val_idx in skf.split(X, y):
        model = XGBClassifier(n_estimators=1000, learning_rate=0.02, max_depth=6, scale_pos_weight=3, random_state=42)
        model.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        oof_probs[val_idx] = model.predict_proba(X.iloc[val_idx])[:, 1]
        test_probs += model.predict_proba(X_test)[:, 1] / 5

    best_f1, best_t = 0, 0.5
    for t in np.arange(0.2, 0.7, 0.01):
        score = f1_score(y, (oof_probs > t).astype(int))
        if score > best_f1:
            best_f1, best_t = score, t
            
    print(f"--- V12 RECOVERY CV F1: {best_f1:.4f} @ Threshold {best_t:.2f} ---")
    final_preds = (test_probs > best_t).astype(int)
    pd.DataFrame({'ID': test_ids, 'target': final_preds}).to_csv('V12_Recovery_Sub.csv', index=False)

if __name__ == "__main__":
    run_v12_recovery()
