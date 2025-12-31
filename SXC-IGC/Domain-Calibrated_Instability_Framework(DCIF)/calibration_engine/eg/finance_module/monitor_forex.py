#!/usr/bin/env python3
"""
Simple Forex Market Monitor using DCII
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path

class SimpleForexMonitor:
    """Simple monitor for forex market conditions."""
    
    def __init__(self, params_file="forex_dcii_results/parameters.json"):
        self.params_file = Path(params_file)
        self.load_parameters()
    
    def load_parameters(self):
        """Load calibration parameters."""
        if self.params_file.exists():
            try:
                with open(self.params_file, 'r') as f:
                    self.params = json.load(f)
                
                self.beta = self.params.get('beta', 1.3)
                self.gamma = self.params.get('gamma', 0.8)
                self.signals = self.params.get('signals', [])
                
                print(f"✅ Loaded DCII parameters from {self.params_file}")
                print(f"   β = {self.beta:.2f}, γ = {self.gamma:.2f}")
                print(f"   Signals: {', '.join(self.signals)}")
                print(f"   Calibrated: {self.params.get('calibration_date', 'Unknown')}")
                
            except Exception as e:
                print(f"⚠️  Could not load parameters: {e}")
                self.use_defaults()
        else:
            print(f"⚠️  Parameters file not found: {self.params_file}")
            print("Using default parameters...")
            self.use_defaults()
    
    def use_defaults(self):
        """Use default parameters."""
        self.beta = 1.3
        self.gamma = 0.8
        self.signals = ['volatility', 'volume_stress', 'spread_stress', 
                       'liquidity', 'momentum_short', 'momentum_medium']
        self.params = {'beta': self.beta, 'gamma': self.gamma, 'signals': self.signals}
    
    def compute_dcii(self, signal_values):
        """Compute DCII from signal values."""
        values = list(signal_values.values())
        if not values:
            return 0.5
        
        pressure = self.beta * np.mean(values)
        resilience = self.gamma * np.std(values) if len(values) > 1 else 0
        dcii = pressure - resilience
        
        return max(0.0, min(1.0, dcii))
    
    def classify(self, dcii):
        """Classify DCII value."""
        if dcii < 0.3:
            return "Normal 🟢", "Continue normal trading"
        elif dcii < 0.5:
            return "Elevated 🟡", "Increase monitoring, watch for changes"
        elif dcii < 0.7:
            return "High Stress 🟠", "Reduce position sizes, set tight stops"
        else:
            return "Critical 🔴", "Consider closing positions, avoid new trades"
    
    def analyze_contributors(self, signal_values):
        """Analyze which signals are contributing most to stress."""
        sorted_sigs = sorted(signal_values.items(), 
                           key=lambda x: x[1], 
                           reverse=True)
        
        return sorted_sigs[:3]  # Top 3 contributors
    
    def get_signal_status(self, value):
        """Get human-readable status for signal value."""
        if value > 0.7:
            return "Very High"
        elif value > 0.5:
            return "High"
        elif value > 0.3:
            return "Normal"
        else:
            return "Low"
    
    def monitor(self, market_data):
        """
        Monitor current market conditions.
        
        market_data should be a dict with keys matching your signals.
        Example values (normalized 0-1):
          volatility: 0.3 (low) to 0.9 (high)
          volume_stress: 0.4 (normal) to 1.0 (high)
          spread_stress: 0.2 (tight) to 0.8 (wide)
          liquidity: 0.5 (normal) to 0.1 (low) or 0.9 (high)
          momentum_short: 0.3 (negative) to 0.7 (positive)
          momentum_medium: 0.4 (negative) to 0.6 (positive)
        """
        print("\n" + "="*60)
        print("FOREX MARKET MONITOR - EUR/USD")
        print("="*60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Validate signals
        valid_signals = {}
        for signal in self.signals:
            if signal in market_data:
                valid_signals[signal] = market_data[signal]
            else:
                print(f"⚠️  Missing signal: {signal}, using default 0.5")
                valid_signals[signal] = 0.5
        
        # Compute DCII
        dcii = self.compute_dcii(valid_signals)
        level, action = self.classify(dcii)
        
        print(f"\n📊 DCII Index: {dcii:.3f}")
        print(f"🚨 Stress Level: {level}")
        print(f"💡 Recommended Action: {action}")
        
        # Show contributors
        top_contributors = self.analyze_contributors(valid_signals)
        print(f"\n🔍 Top 3 Contributors:")
        for signal, value in top_contributors:
            status = self.get_signal_status(value)
            print(f"  {signal:20}: {value:.3f} ({status})")
        
        print("\n📈 All Signals:")
        for signal, value in valid_signals.items():
            status = self.get_signal_status(value)
            print(f"  {signal:20}: {value:.3f} ({status})")
        
        print("\n" + "-"*60)
        return {
            'dcii': float(dcii),
            'level': level,
            'action': action,
            'contributors': dict(top_contributors),
            'all_signals': valid_signals,
            'timestamp': datetime.now().isoformat(),
            'parameters': {'beta': self.beta, 'gamma': self.gamma}
        }

def main():
    """Main function with examples."""
    monitor = SimpleForexMonitor()
    
    print("\n" + "="*60)
    print("DCII FOREX MONITOR - DEMONSTRATION")
    print("="*60)
    
    # Example 1: Normal market
    print("\n📈 Example 1: Normal Trading Hours (London/NY Overlap)")
    normal_market = {
        'volatility': 0.3,
        'volume_stress': 0.4,
        'spread_stress': 0.3,
        'liquidity': 0.6,
        'momentum_short': 0.5,
        'momentum_medium': 0.52
    }
    result1 = monitor.monitor(normal_market)
    
    # Example 2: Economic news release
    print("\n📰 Example 2: NFP News Release (High Impact)")
    news_market = {
        'volatility': 0.8,
        'volume_stress': 0.9,
        'spread_stress': 0.7,
        'liquidity': 0.8,
        'momentum_short': 0.6,
        'momentum_medium': 0.55
    }
    result2 = monitor.monitor(news_market)
    
    # Example 3: Asian session (low liquidity)
    print("\n🌏 Example 3: Asian Session (Low Liquidity)")
    asian_market = {
        'volatility': 0.4,
        'volume_stress': 0.3,
        'spread_stress': 0.5,
        'liquidity': 0.2,  # Low liquidity
        'momentum_short': 0.45,
        'momentum_medium': 0.48
    }
    result3 = monitor.monitor(asian_market)
    
    # Example 4: Risk-off sentiment
    print("\n⚠️  Example 4: Risk-Off Sentiment (Flight to Safety)")
    riskoff_market = {
        'volatility': 0.7,
        'volume_stress': 0.8,
        'spread_stress': 0.6,
        'liquidity': 0.7,
        'momentum_short': 0.35,  # Negative momentum
        'momentum_medium': 0.38   # Negative momentum
    }
    result4 = monitor.monitor(riskoff_market)
    
    print("\n" + "="*60)
    print("💡 HOW TO USE THIS MONITOR")
    print("="*60)
    print("""
1. CREATE your market data dictionary:
   current_market = {
       'volatility': calculate_volatility(),      # 0-1 scale
       'volume_stress': calculate_volume_ratio(), # 0-1 scale
       'spread_stress': calculate_spread_ratio(), # 0-1 scale
       'liquidity': calculate_liquidity(),        # 0-1 scale
       'momentum_short': short_term_momentum(),   # 0-1 scale
       'momentum_medium': medium_term_momentum()  # 0-1 scale
   }

2. MONITOR current conditions:
   from monitor_forex import SimpleForexMonitor
   monitor = SimpleForexMonitor()
   alert = monitor.monitor(current_market)
   
   print(f"Alert Level: {alert['level']}")
   print(f"Action: {alert['action']}")
   print(f"Top Risk Factors: {alert['contributors']}")

3. INTEGRATE with trading system:
   - Use DCII < 0.3 for aggressive trading
   - Use 0.3 < DCII < 0.5 for normal trading
   - Use 0.5 < DCII < 0.7 for reduced size
   - Use DCII > 0.7 for no new trades

4. VALUES GUIDE (normalized 0-1):
   - 0.0-0.2: Very Low
   - 0.2-0.4: Low/Normal
   - 0.4-0.6: Elevated
   - 0.6-0.8: High
   - 0.8-1.0: Extreme
    """)
    
    print("\n" + "="*60)
    print("✅ DCII FOREX MONITOR READY FOR USE")
    print("="*60)
    
    return {
        'normal': result1,
        'news': result2,
        'asian': result3,
        'riskoff': result4,
        'monitor': monitor
    }

if __name__ == "__main__":
    main()
