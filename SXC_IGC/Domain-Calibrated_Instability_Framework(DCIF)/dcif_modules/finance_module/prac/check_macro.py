import pandas as pd

# Load data
path = "the-ai4eac-finance-practice-challenge20260306-12254-19b0z5g/"
train = pd.read_csv(path + 'Train.csv')
indic = pd.read_csv(path + 'economic_indicators.csv')

# 1. Pivot Economic Indicators
# Convert YR2001, YR2002... into a 'Year' and 'Value' column
id_vars = ['Country', 'Indicator']
indic_long = indic.melt(id_vars=id_vars, var_name='Year', value_name='Value')
indic_long['Year'] = indic_long['Year'].str.replace('YR', '').astype(int)

# 2. Extract Year from Train
train['Year'] = pd.to_datetime(train['disbursement_date']).dt.year

print(f"Loan Years range: {train['Year'].min()} to {train['Year'].max()}")
print("Indicators available for these countries:", indic['Country'].unique())

# 3. Pivot again to have Indicators as COLUMNS (Inflation, Exchange Rate)
indic_pivoted = indic_long.pivot_table(index=['Country', 'Year'], columns='Indicator', values='Value').reset_index()
print("\nSample of Pivoted Macro Data:")
print(indic_pivoted.head())

# Save for the main script
indic_pivoted.to_csv('processed_indicators.csv', index=False)
