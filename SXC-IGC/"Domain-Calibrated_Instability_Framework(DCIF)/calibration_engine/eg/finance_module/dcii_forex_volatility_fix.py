#!/usr/bin/env python3
"""
Quick fix for volatility calculation issue
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Load your saved DCII data
dcii_file = Path("forex_dcii_results/dcii_series.csv")
if dcii_file.exists():
    dcii_data = pd.read_csv(dcii_file, index_col=0, parse_dates=True)
    print(f"Loaded DCII data: {len(dcii_data)} points")
    print(f"Date range: {dcii_data.index.min()} to {dcii_data.index.max()}")
    
    # Plot distribution
    print("\nDCII Distribution:")
    print(dcii_data.describe())
    
    # Check stress levels
    bins = [0, 0.3, 0.5, 0.7, 1.0]
    labels = ['Normal', 'Elevated', 'High', 'Critical']
    
    dcii_series = dcii_data.iloc[:, 0] if dcii_data.shape[1] > 0 else pd.Series()
    
    if not dcii_series.empty:
        print("\nStress Level Counts:")
        for i in range(len(bins)-1):
            low, high = bins[i], bins[i+1]
            count = ((dcii_series >= low) & (dcii_series < high)).sum()
            pct = count / len(dcii_series) * 100
            print(f"  {labels[i]:10}: {count:3d} periods ({pct:.1f}%)")
        
        # Find highest DCII periods
        print("\nTop 5 Highest Stress Periods:")
        top5 = dcii_series.nlargest(5)
        for dt, value in top5.items():
            print(f"  {dt}: DCII = {value:.3f}")
        
        # Find lowest DCII periods  
        print("\nTop 5 Lowest Stress Periods:")
        bottom5 = dcii_series.nsmallest(5)
        for dt, value in bottom5.items():
            print(f"  {dt}: DCII = {value:.3f}")

# Create a simple monitoring script
cat > monitor_forex.py << 'EOF2'
#!/usr/bin/env python3
"""
Simple Forex Market Monitor using DCII
"""

import json
import numpy as np
from datetime import datetime

class SimpleForexMonitor:
    """Simple monitor for forex market conditions."""
    
    def __init__(self, params_file="forex_dcii_results/parameters.json"):
        try:
            with open(params_file, 'r') as f:
                self.params = json.load(f)
            
            self.beta = self.params.get('beta', 1.3)
            self.gamma = self.params.get('gamma', 0.8)
            self.signals = self.params.get('signals', [])
            
            print(f"✅ Loaded DCII parameters:")
            print(f"   β = {self.beta:.2f}, γ = {self.gamma:.2f}")
            print(f"   Signals: {', '.join(self.signals)}")
            
        except Exception as e:
            print(f"⚠️  Could not load parameters: {e}")
            print("Using default parameters...")
            self.beta = 1.3
            self.gamma = 0.8
            self.signals = ['volatility', 'volume_stress', 'spread_stress', 
                           'liquidity', 'momentum_short', 'momentum_medium']
    
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
            return "Elevated 🟡", "Increase monitoring"
        elif dcii < 0.7:
            return "High Stress 🟠", "Reduce position sizes"
        else:
            return "Critical 🔴", "Consider closing positions"
    
    def analyze_contributors(self, signal_values):
        """Analyze which signals are contributing most to stress."""
        sorted_sigs = sorted(signal_values.items(), 
                           key=lambda x: x[1], 
                           reverse=True)
        
        return sorted_sigs[:3]  # Top 3 contributors
    
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
        print("FOREX MARKET MONITOR")
        print("="*60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Compute DCII
        dcii = self.compute_dcii(market_data)
        level, action = self.classify(dcii)
        
        print(f"\n📊 DCII Index: {dcii:.3f}")
        print(f"🚨 Stress Level: {level}")
        print(f"💡 Action: {action}")
        
        # Show contributors
        top_contributors = self.analyze_contributors(market_data)
        print(f"\n🔍 Top Contributors:")
        for signal, value in top_contributors:
            status = "High" if value > 0.7 else "Elevated" if value > 0.5 else "Normal" if value > 0.3 else "Low"
            print(f"  {signal:20}: {value:.3f} ({status})")
        
        print("\n" + "-"*60)
        return {
            'dcii': dcii,
            'level': level,
            'action': action,
            'contributors': dict(top_contributors),
            'timestamp': datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    monitor = SimpleForexMonitor()
    
    # Example 1: Normal market
    print("\nExample 1: Normal Trading Hours")
    normal_market = {
        'volatility': 0.3,
        'volume_stress': 0.4,
        'spread_stress': 0.3,
        'liquidity': 0.6,
        'momentum_short': 0.5,
        'momentum_medium': 0.52
    }
    monitor.monitor(normal_market)
    
    # Example 2: Economic news release
    print("\nExample 2: NFP News Release")
    news_market = {
        'volatility': 0.8,
        'volume_stress': 0.9,
        'spread_stress': 0.7,
        'liquidity': 0.8,
        'momentum_short': 0.6,
        'momentum_medium': 0.55
    }
    monitor.monitor(news_market)
    
    # Example 3: Asian session (low liquidity)
    print("\nExample 3: Asian Session (Low Liquidity)")
    asian_market = {
        'volatility': 0.4,
        'volume_stress': 0.3,
        'spread_stress': 0.5,
        'liquidity': 0.2,  # Low liquidity
        'momentum_short': 0.45,
        'momentum_medium': 0.48
    }
    monitor.monitor(asian_market)
    
    print("\n" + "="*60)
    print("💡 How to use:")
    print("="*60)
    print("""
1. Create your own market data dict:
   market = {
       'volatility': your_volatility_value,      # 0-1
       'volume_stress': your_volume_value,       # 0-1  
       'spread_stress': your_spread_value,       # 0-1
       'liquidity': your_liquidity_value,        # 0-1
       'momentum_short': your_short_momentum,    # 0-1
       'momentum_medium': your_medium_momentum   # 0-1
   }

2. Monitor:
   result = monitor.monitor(market)
   print(f"DCII: {result['dcii']:.3f}")
   print(f"Action: {result['action']}")

3. Values guide:
   - 0.0-0.3: Very low/normal
   - 0.3-0.5: Elevated  
   - 0.5-0.7: High
   - 0.7-1.0: Extreme
    """)
EOF2

chmod +x monitor_forex.py
python3 monitor_forex.py
