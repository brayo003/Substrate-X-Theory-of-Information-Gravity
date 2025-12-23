#!/usr/bin/env python3
"""
Real-time HFT analyzer with live market data integration
"""
import numpy as np
import pandas as pd
from market_microstructure import HFTMarketAnalyzer
import time

class RealTimeHFTAnalyzer(HFTMarketAnalyzer):
    """Real-time HFT analyzer with continuous signal generation"""
    
    def __init__(self, symbol='SPY', update_interval=1.0):
        super().__init__(symbol)
        self.update_interval = update_interval
        self.running = False
        self.signals_history = []
        
    def start_analysis(self, duration=3600):  # 1 hour default
        """Start real-time analysis loop"""
        self.running = True
        start_time = time.time()
        
        print(f"🔴 Starting real-time HFT analysis for {self.symbol}")
        print(f"   Duration: {duration}s | Interval: {self.update_interval}s")
        
        while self.running and (time.time() - start_time) < duration:
            try:
                # Update with new market data (mock for now)
                self.map_market_data_to_fields()
                
                # Generate signals
                signals = self.generate_trading_signals()
                signals['timestamp'] = time.time()
                self.signals_history.append(signals)
                
                # Display critical signals
                if signals['regime'] != 0 or signals['regime_confidence'] > 0.8:
                    print(f"🚨 REGIME ALERT: {signals['regime']} (conf: {signals['regime_confidence']:.1%})")
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Analysis stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in analysis loop: {e}")
                time.sleep(1)  # Wait before retry
        
        self.running = False
        print("🟢 Real-time analysis completed")
        
    def get_performance_report(self):
        """Generate performance analysis report"""
        if not self.signals_history:
            return "No signals generated"
            
        df = pd.DataFrame(self.signals_history)
        
        report = {
            'total_signals': len(df),
            'crash_regimes': len(df[df['regime'] == -1]),
            'bubble_regimes': len(df[df['regime'] == 1]),
            'avg_confidence': df['regime_confidence'].mean(),
            'market_health_trend': df['market_health'].iloc[-1] - df['market_health'].iloc[0]
        }
        
        return report

if __name__ == "__main__":
    # Demo real-time analysis (5 minutes)
    analyzer = RealTimeHFTAnalyzer(symbol='SPY', update_interval=2.0)
    analyzer.start_analysis(duration=300)  # 5 minutes
    
    # Performance report
    report = analyzer.get_performance_report()
    print("\n📊 Performance Report:")
    for key, value in report.items():
        print(f"  {key}: {value}")
