import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
import warnings

warnings.filterwarnings('ignore')

def run_v12_final_clean():
    path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
    train = pd.read_csv(path + 'Train.csv')
    test = pd.read_csv(path + 'Test.csv')
    indic = pd.read_csv('processed_indicators.csv')
    
    # Forward-fill 2024 Macro Data
    indic_2023 = indic[indic['Year'] == 2023].copy()
    indic_2023['Year'] = 2024
    indic = pd.concat([indic, indic_2023]).drop_duplicates(subset=['Country', 'Year'])
    
    y = train['target']
    test_ids = test['ID']
    
    def prep_data(df):
        df['disbursement_date'] = pd.to_datetime(df['disbursement_date'])
        df['Year'] = df['disbursement_date'].dt.year
        df = df.merge(indic, left_on=['country_id', 'Year'], right_on=['Country', 'Year'], how='left')
        
        # Numeric base features
        df['Interest_Rate'] = (df['Total_Amount_to_Repay'] / (df['Total_Amount'] + 0.01)) - 1
        df['Repay_Vel'] = df['Total_Amount_to_Repay'] / (df['duration'] + 1)
        df['is_Kenya'] = (df['country_id'] == 'Kenya').astype(int)
        df['is_Type1'] = (df['loan_type'] == 'Type 1').astype(int)

        # FIND MACRO COLS BY KEYWORD (Resilience Fix)
        macro_cols = []
        for keyword in ['Inflation', 'GDP', 'Real interest']:
            found = [c for c in df.columns if keyword.lower() in c.lower()]
            if found:
                macro_cols.append(found[0])
                # Fill missing macro data with median
                df[found[0]] = df[found[0]].fillna(df[found[0]].median())

        # Interaction: Type1 * First Macro Col (Usually Inflation)
        if macro_cols:
            df['Inf_Stress'] = df['is_Type1'] * df[macro_cols[0]]
        else:
            df['Inf_Stress'] = 0

        features = ['Total_Amount', 'Total_Amount_to_Repay', 'duration', 'Year',
                    'Interest_Rate', 'Repay_Vel', 'is_Kenya', 'is_Type1', 'Inf_Stress'] + macro_cols
        return df[features]

    X = prep_data(train)
    X_test = prep_data(test)

    print(f"Engine fired up! Training on {X.shape[1]} features...")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    test_probs = np.zeros(len(X_test))
    oof_probs = np.zeros(len(X))

    for tr_idx, val_idx in skf.split(X, y):
        model = XGBClassifier(n_estimators=1000, learning_rate=0.03, max_depth=5, scale_pos_weight=3, random_state=42)
        model.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        oof_probs[val_idx] = model.predict_proba(X.iloc[val_idx])[:, 1]
        test_probs += model.predict_proba(X_test)[:, 1] / 5

    # Optimal thresholding
    best_f1, best_t = 0, 0.5
    for t in np.arange(0.3, 0.6, 0.01):
        score = f1_score(y, (oof_probs > t).astype(int))
        if score > best_f1:
            best_f1, best_t = score, t
            
    print(f"--- V12 FINAL CV F1: {best_f1:.4f} @ Threshold {best_t:.2f} ---")
    final_preds = (test_probs > best_t).astype(int)
    pd.DataFrame({'ID': test_ids, 'target': final_preds}).to_csv('V12_Final_Clean.csv', index=False)

if __name__ == "__main__":
    run_v12_final_clean()
