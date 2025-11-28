import yfinance as yf
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from universal_dynamics_engine.data_coupler import DataCoupler, DomainType

def download_covid_market_data():
    """Get real COVID period data to test predictive power"""
    # Financial data during COVID
    sp500 = yf.download('^GSPC', start='2020-01-01', end='2020-06-01')
    
    # COVID case data (simulated for now, can get real data)
    covid_cases = pd.DataFrame({
        'date': pd.date_range('2020-01-01', periods=150, freq='D'),
        'cases': [100 * (1 + 0.3)**i for i in range(150)]  # Exponential growth
    })
    
    return sp500, covid_cases

# Test the data acquisition
if __name__ == "__main__":
    market_data, covid_data = download_covid_market_data()
    print(f"Market data: {len(market_data)} points")
    print(f"COVID data: {len(covid_data)} points")
