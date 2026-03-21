import pandas as pd
path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
test = pd.read_csv(path + 'Test.csv')
indic = pd.read_csv('processed_indicators.csv')

test['Year'] = pd.to_datetime(test['disbursement_date']).dt.year
merged = test.merge(indic, left_on=['country_id', 'Year'], right_on=['Country', 'Year'], how='left')

print("--- TEST MERGE AUDIT ---")
print(f"Test rows: {len(test)}")
print(f"Rows with missing Macro Data: {merged['Inflation, consumer prices (annual %)'].isna().sum()}")
print(f"Unique Countries in Test: {test['country_id'].unique()}")
print(f"Unique Years in Test: {test['Year'].unique()}")
