import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
import warnings

warnings.filterwarnings('ignore')

def run_v12_pro_strat():
    path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
    train = pd.read_csv(path + 'Train.csv')
    test = pd.read_csv(path + 'Test.csv')
    indic = pd.read_csv('processed_indicators.csv')
    
    # Macro Data Prep
    indic_2023 = indic[indic['Year'] == 2023].copy()
    indic_2023['Year'] = 2024
    indic = pd.concat([indic, indic_2023]).drop_duplicates(subset=['Country', 'Year'])
    
    y = train['target']
    test_ids = test['ID']

    def prep_data(df):
        # Convert dates
        df['disbursement_date'] = pd.to_datetime(df['disbursement_date'])
        df['Year'] = df['disbursement_date'].dt.year
        df['Month'] = df['disbursement_date'].dt.month
        
        # Merge Macro
        df = df.merge(indic, left_on=['country_id', 'Year'], right_on=['Country', 'Year'], how='left')
        
        # Financial Engineering
        df['Interest_Rate'] = (df['Total_Amount_to_Repay'] / (df['Total_Amount'] + 1)) - 1
        df['Repay_Vel'] = df['Total_Amount_to_Repay'] / (df['duration'] + 1)
        
        # Categorical
        df['loan_type_code'] = pd.factorize(df['loan_type'])[0]

        # Macro Keywords
        macro_cols = []
        for kw in ['Inflation', 'GDP', 'Real interest']:
            found = [c for c in df.columns if kw.lower() in c.lower()]
            if found:
                macro_cols.append(found[0])
                df[found[0]] = df[found[0]].fillna(df[found[0]].median())

        features = ['Total_Amount', 'Total_Amount_to_Repay', 'duration', 'Year', 'Month',
                    'Interest_Rate', 'Repay_Vel', 'loan_type_code'] + macro_cols
        return df[features]

    X = prep_data(train)
    X_test = prep_data(test)

    # Stratified KFold with Shuffling
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    test_probs = np.zeros(len(X_test))
    oof_probs = np.zeros(len(X))

    print(f"Training on {X.shape[1]} features...")

    for tr_idx, val_idx in skf.split(X, y):
        # Increased regularization (colsample, subsample) to fight overfitting
        model = XGBClassifier(
            n_estimators=1000, 
            learning_rate=0.015, 
            max_depth=4, 
            scale_pos_weight=3, 
            subsample=0.7, 
            colsample_bytree=0.7,
            reg_alpha=0.1,
            reg_lambda=1.0,
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
            
    print(f"\n--- CV F1: {best_f1:.4f} @ Threshold {best_t:.2f} ---")
    
    final_preds = (test_probs > best_t).astype(int)
    pd.DataFrame({'ID': test_ids, 'target': final_preds}).to_csv('V12_Regularized.csv', index=False)
    print("Saved: V12_Regularized.csv")

if __name__ == "__main__":
    run_v12_pro_strat()
