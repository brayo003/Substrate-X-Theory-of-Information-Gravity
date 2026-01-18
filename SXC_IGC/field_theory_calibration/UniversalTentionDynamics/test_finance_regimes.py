#!/usr/bin/env python3
"""
Test if engine predicts actual market regimes
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import yfinance as yf
import numpy as np

# Download real SPY data
spy = yf.download('SPY', period='6mo', interval='1d')
returns = spy['Close'].pct_change().dropna()

print("📈 REAL MARKET REGIME TEST")
print(f"Testing on SPY data: {len(returns)} trading days")

# Map real data to engine
engine = create_robust_engine('finance', grid_size=32)
engine.initialize_gaussian()

# Test if engine regime detection matches actual volatility regimes
high_vol_periods = returns.rolling(10).std() > returns.rolling(50).std()
actual_regimes = high_vol_periods.astype(int)

print("Comparing engine predictions to actual volatility regimes...")
# This would test if your regime detection matches reality
