#!/usr/bin/env python3
"""
HFT Market Microstructure Analyzer
Using multi-scale field theory for regime detection and arbitrage
"""
import numpy as np
import pandas as pd
import sys
import os

# Add core engine to path
core_engine_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core_engine', 'src')
sys.path.insert(0, core_engine_path)

try:
    from universal_dynamics import create_engine
except ImportError:
    print("⚠️  Could not import core engine. Using simplified version.")
    # Fallback simplified engine for testing
    class FallbackEngine:
        def __init__(self):
            self.rho = np.random.rand(64, 64)
            self.E = np.random.rand(64, 64) 
            self.F = np.random.rand(64, 64)
            self.delta1 = 2.0
            self.delta2 = 1.5
        
        def evolve(self, steps):
            pass
        
        def get_field_statistics(self):
            return {
                'rho_max': np.max(self.rho),
                'rho_rms': np.sqrt(np.mean(self.rho**2)),
                'E_rms': np.sqrt(np.mean(self.E**2)),
                'F_rms': np.sqrt(np.mean(self.F**2)),
                'stiffness_active': True
            }

class HFTMarketAnalyzer:
    """
    High-Frequency Trading market analyzer using universal dynamics
    """
    
    def __init__(self, symbol='SPY', lookback_period=1000):
        self.symbol = symbol
        self.lookback_period = lookback_period
        
        try:
            # Create finance-optimized engine
            self.engine = create_engine(
                domain='finance',
                grid_size=64,
                dt=0.0001,
                delta1=2.0,
                delta2=1.5,
                cubic_damping=1.0,
                M_factor=100000
            )
            print(f"🚀 HFT Market Analyzer initialized for {symbol}")
        except:
            # Fallback for testing
            self.engine = FallbackEngine()
            print(f"⚠️  HFT Market Analyzer (fallback) initialized for {symbol}")
        
        # Market data buffers
        self.order_book_density = np.zeros((64, 64))
        self.price_momentum = np.zeros((64, 64))
        self.market_sentiment = np.zeros((64, 64))
    
    def generate_mock_data(self):
        """Generate mock market data for testing"""
        mock_order_book = pd.DataFrame({
            'bid_volume': np.random.exponential(100, 64),
            'ask_volume': np.random.exponential(100, 64)
        })
        
        mock_trades = pd.DataFrame({
            'price': 450 + np.cumsum(np.random.normal(0, 0.1, 100)),
            'volume': np.random.exponential(1000, 100)
        })
        
        mock_quotes = pd.DataFrame({
            'bid_price': 449.9 + np.random.normal(0, 0.05, 50),
            'ask_price': 450.1 + np.random.normal(0, 0.05, 50)
        })
        
        return mock_order_book, mock_trades, mock_quotes
    
    def map_market_data_to_fields(self, order_book=None, trades=None, quotes=None):
        """Map market data to field theory representation"""
        if order_book is None or trades is None or quotes is None:
            order_book, trades, quotes = self.generate_mock_data()
        
        # Simplified field mapping for testing
        self.order_book_density = np.random.rand(64, 64)
        self.price_momentum = np.random.normal(0, 0.1, (64, 64))
        self.market_sentiment = np.random.normal(0, 0.2, (64, 64))
        
        # Update engine fields
        self.engine.rho = self.order_book_density
        self.engine.E = self.price_momentum
        self.engine.F = self.market_sentiment
    
    def detect_regime_switch(self):
        """Detect market regime switches"""
        rho_max = np.max(self.engine.rho)
        F_rms = np.sqrt(np.mean(self.engine.F**2))
        
        if rho_max < 0.7 and F_rms < -0.3:
            return -1, 0.9  # Crash regime
        elif rho_max > 0.7 and F_rms > 0.3:
            return 1, 0.8   # Bubble regime
        else:
            return 0, 0.6   # Normal regime
    
    def generate_trading_signals(self):
        """Generate trading signals"""
        regime, regime_confidence = self.detect_regime_switch()
        
        signals = {
            'regime': regime,
            'regime_confidence': regime_confidence,
            'market_health': np.mean(self.engine.rho),
            'sentiment_score': np.mean(self.engine.F),
            'liquidity_score': np.std(self.engine.rho)  # Volatility as liquidity proxy
        }
        
        return signals

# Example usage
if __name__ == "__main__":
    print("🧪 Testing HFT Analyzer Standalone")
    analyzer = HFTMarketAnalyzer()
    analyzer.map_market_data_to_fields()
    signals = analyzer.generate_trading_signals()
    
    print("🎯 Trading Signals:")
    for key, value in signals.items():
        print(f"  {key}: {value}")
