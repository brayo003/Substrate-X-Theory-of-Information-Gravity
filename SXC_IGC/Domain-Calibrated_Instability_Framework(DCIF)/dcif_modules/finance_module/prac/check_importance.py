import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import re

def clean_col_names(df):
    new_cols = [re.sub(r'[^\w\s]', '_', str(c)).replace(' ', '_') for c in df.columns]
    df.columns = new_cols
    return df

path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
train = pd.read_csv(path + 'Train.csv')
y = train['target']

# Exclude the "Memorization" columns
drop_cols = ['ID', 'customer_id', 'tbl_loan_id', 'target', 'disbursement_date', 'due_date']
features = [c for c in train.columns if c not in drop_cols]

X = clean_col_names(pd.get_dummies(train[features], dummy_na=True))

model = XGBClassifier(n_estimators=100)
model.fit(X, y)

importances = pd.Series(model.feature_importances_, index=X.columns)
print("\n--- TOP 10 V12 ELITE SIGNALS ---")
print(importances.sort_values(ascending=False).head(10))
