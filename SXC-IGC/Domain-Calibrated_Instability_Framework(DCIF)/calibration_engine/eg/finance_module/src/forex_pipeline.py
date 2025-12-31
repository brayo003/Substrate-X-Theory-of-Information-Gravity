#!/usr/bin/env python3
"""
DCII FOREX MODULE - EUR/USD - EXACT STRUCTURE VERSION
Matches your exact directory structure: 2024/04/12/00h_ticks.bi5
"""

import struct
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# BI5 DATA LOADER - EXACT MATCH FOR YOUR STRUCTURE
# ============================================================================

class BI5LoaderExact:
    """BI5 loader for exact directory structure: 2024/month/day/hour_ticks.bi5"""
    
    @staticmethod
    def read_bi5_file(filepath: Path) -> pd.DataFrame:
        """Read a single BI5 file."""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            if len(data) == 0:
                return pd.DataFrame()
            
            ticks = []
            # Each tick is 20 bytes
            for i in range(0, len(data), 20):
                if i + 20 > len(data):
                    break
                
                chunk = data[i:i+20]
                timestamp, ask, bid, ask_vol, bid_vol = struct.unpack('Iffff', chunk)
                
                # Convert milliseconds to datetime
                dt = datetime.fromtimestamp(timestamp / 1000.0)
                
                ticks.append({
                    'timestamp': dt,
                    'ask': ask,
                    'bid': bid,
                    'mid': (ask + bid) / 2,
                    'spread': (ask - bid) * 10000,  # Convert to pips
                    'spread_raw': ask - bid,
                    'ask_volume': ask_vol,
                    'bid_volume': bid_vol,
                    'total_volume': ask_vol + bid_vol
                })
            
            return pd.DataFrame(ticks)
        except Exception as e:
            print(f"  Error reading {filepath.name}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def load_from_structure(base_path: Path, 
                           max_files: int = 50,  # Limit for testing
                           sample_days: List[str] = None) -> pd.DataFrame:
        """
        Load BI5 files from your exact structure.
        
        Args:
            base_path: Path to 2024 directory
            max_files: Maximum number of files to load (for testing)
            sample_days: Specific days to load (e.g., ['04/12', '04/13'])
        """
        print(f"📂 Scanning directory: {base_path}")
        
        all_ticks = []
        loaded_files = 0
        
        # List all month directories
        month_dirs = sorted([d for d in base_path.iterdir() if d.is_dir()])
        print(f"Found {len(month_dirs)} month directories")
        
        for month_dir in month_dirs:
            month_name = month_dir.name
            print(f"\nMonth {month_name}:")
            
            # List all day directories in this month
            day_dirs = sorted([d for d in month_dir.iterdir() if d.is_dir()])
            print(f"  Days found: {len(day_dirs)}")
            
            for day_dir in day_dirs[:3]:  # Only process first 3 days per month for testing
                if sample_days and f"{month_name}/{day_dir.name}" not in sample_days:
                    continue
                
                # Find all BI5 files in this day
                bi5_files = sorted(day_dir.glob("*h_ticks.bi5"))
                if not bi5_files:
                    continue
                
                print(f"  Day {day_dir.name}: {len(bi5_files)} hour files")
                
                # Load first few files for testing
                for bi5_file in bi5_files[:4]:  # Only first 4 hours per day
                    if loaded_files >= max_files:
                        print(f"  Reached max files limit ({max_files})")
                        break
                    
                    df = BI5LoaderExact.read_bi5_file(bi5_file)
                    if not df.empty:
                        all_ticks.append(df)
                        loaded_files += 1
                
                if loaded_files >= max_files:
                    break
            
            if loaded_files >= max_files:
                break
        
        if all_ticks:
            result = pd.concat(all_ticks, ignore_index=True).sort_values('timestamp')
            print(f"\n✅ Successfully loaded {len(result):,} ticks from {loaded_files} files")
            print(f"   Time range: {result['timestamp'].min()} to {result['timestamp'].max()}")
            return result
        else:
            print("❌ No data loaded")
            return pd.DataFrame()

# ============================================================================
# FOREX SIGNAL PROCESSOR
# ============================================================================

class ForexSignalProcessor:
    """Process tick data into trading signals."""
    
    def __init__(self, tick_data: pd.DataFrame):
        self.ticks = tick_data
        self.ohlc_data = pd.DataFrame()
        self.signals = {}
        
    def create_ohlc(self, interval: str = '1min') -> pd.DataFrame:
        """Convert ticks to OHLC data."""
        if self.ticks.empty:
            return pd.DataFrame()
        
        # Set timestamp as index
        df = self.ticks.set_index('timestamp')
        
        # Resample to OHLC
        ohlc = df['mid'].resample(interval).ohlc()
        ohlc['volume'] = df['total_volume'].resample(interval).sum()
        ohlc['spread'] = df['spread'].resample(interval).mean()
        ohlc['tick_count'] = df['mid'].resample(interval).count()
        
        # Calculate returns
        ohlc['returns'] = ohlc['close'].pct_change()
        ohlc['log_returns'] = np.log(ohlc['close'] / ohlc['close'].shift(1))
        
        self.ohlc_data = ohlc.dropna()
        return self.ohlc_data
    
    def generate_basic_signals(self) -> Dict[str, pd.Series]:
        """Generate basic trading signals."""
        if self.ohlc_data.empty:
            self.create_ohlc('5min')  # Default to 5-minute bars
        
        df = self.ohlc_data
        
        # 1. Volatility (rolling std of returns)
        volatility = df['returns'].rolling(window=20, min_periods=10).std()
        
        # 2. Volume indicator (volume vs moving average)
        volume_ma = df['volume'].rolling(window=50, min_periods=25).mean()
        volume_ratio = df['volume'] / (volume_ma + 1e-8)
        
        # 3. Spread indicator
        spread_ma = df['spread'].rolling(window=50, min_periods=25).mean()
        spread_ratio = df['spread'] / (spread_ma + 1e-8)
        
        # 4. Tick frequency (market activity)
        tick_freq = df['tick_count'].rolling(window=20, min_periods=10).mean()
        
        # 5. Momentum (simple price change)
        momentum_short = df['close'].pct_change(periods=4)   # 20min momentum
        momentum_medium = df['close'].pct_change(periods=12)  # 1hr momentum
        
        self.signals = {
            'volatility': volatility,
            'volume_ratio': volume_ratio,
            'spread_ratio': spread_ratio,
            'tick_frequency': tick_freq,
            'momentum_20min': momentum_short,
            'momentum_1hr': momentum_medium
        }
        
        # Clean signals (remove NaN)
        for name in list(self.signals.keys()):
            self.signals[name] = self.signals[name].dropna()
        
        return self.signals
    
    def normalize_signals(self) -> Dict[str, pd.Series]:
        """Normalize signals to [0, 1] range."""
        normalized = {}
        
        for name, series in self.signals.items():
            if len(series) < 10:
                continue
            
            # Handle outliers by clipping at 99th percentile
            q99 = series.quantile(0.99)
            series_clipped = series.clip(upper=q99)
            
            # Z-score normalization
            mean_val = series_clipped.mean()
            std_val = series_clipped.std()
            
            if std_val > 0:
                z_scores = (series_clipped - mean_val) / std_val
                # Sigmoid to [0, 1]
                normalized[name] = 1 / (1 + np.exp(-z_scores))
            else:
                # Constant series, set to 0.5
                normalized[name] = pd.Series(0.5, index=series.index)
        
        return normalized

# ============================================================================
# SIMPLE FOREX DCII
# ============================================================================

class SimpleForexDCII:
    """Simple DCII implementation for Forex."""
    
    def __init__(self, name: str = "EURUSD_DCII"):
        self.name = name
        self.beta = 1.0  # Pressure coefficient
        self.gamma = 1.0  # Resilience coefficient
        self.signals = {}
        self.normalized_signals = {}
        
    def load_and_process(self, data_path: Path) -> bool:
        """Load data and generate signals."""
        print("="*60)
        print(f"DCII FOREX MODULE: {self.name}")
        print("="*60)
        
        # Load data
        print("\n1. LOADING DATA")
        print("-"*40)
        tick_data = BI5LoaderExact.load_from_structure(data_path, max_files=20)
        
        if tick_data.empty:
            print("❌ Failed to load data")
            return False
        
        # Process data
        print("\n2. PROCESSING DATA")
        print("-"*40)
        processor = ForexSignalProcessor(tick_data)
        processor.create_ohlc('5min')  # 5-minute bars
        
        print(f"OHLC Data: {len(processor.ohlc_data)} bars")
        print(f"Date range: {processor.ohlc_data.index.min()} to {processor.ohlc_data.index.max()}")
        
        # Generate signals
        raw_signals = processor.generate_basic_signals()
        self.normalized_signals = processor.normalize_signals()
        
        print(f"\nGenerated {len(self.normalized_signals)} signals:")
        for name, series in self.normalized_signals.items():
            print(f"  {name:20} | Length: {len(series):6} | Range: [{series.min():.3f}, {series.max():.3f}]")
        
        return True
    
    def compute_dcii_point(self, signal_values: Dict[str, float]) -> float:
        """Compute DCII for a single point in time."""
        if not signal_values:
            return 0.5  # Neutral
        
        values = list(signal_values.values())
        pressure = self.beta * np.mean(values)
        resilience = self.gamma * np.std(values) if len(values) > 1 else 0
        
        dcii = pressure - resilience
        return np.clip(dcii, 0.0, 1.0)
    
    def compute_historical_dcii(self) -> pd.Series:
        """Compute DCII over all historical data."""
        if not self.normalized_signals:
            print("❌ No signals available")
            return pd.Series()
        
        # Align all signals to common timestamps
        signal_dfs = []
        for name, series in self.normalized_signals.items():
            signal_dfs.append(pd.DataFrame({name: series}))
        
        if not signal_dfs:
            return pd.Series()
        
        # Merge all signals
        all_signals = pd.concat(signal_dfs, axis=1).dropna()
        
        print(f"\n3. COMPUTING HISTORICAL DCII")
        print("-"*40)
        print(f"Aligned data points: {len(all_signals)}")
        
        # Compute DCII for each time point
        dcii_values = []
        timestamps = []
        
        for idx, row in all_signals.iterrows():
            signal_dict = row.to_dict()
            dcii = self.compute_dcii_point(signal_dict)
            dcii_values.append(dcii)
            timestamps.append(idx)
        
        dcii_series = pd.Series(dcii_values, index=timestamps)
        
        # Print statistics
        print(f"DCII Statistics:")
        print(f"  Mean: {dcii_series.mean():.3f}")
        print(f"  Std:  {dcii_series.std():.3f}")
        print(f"  Min:  {dcii_series.min():.3f}")
        print(f"  Max:  {dcii_series.max():.3f}")
        
        # Distribution
        bins = [(0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.0)]
        labels = ['Normal', 'Elevated', 'High', 'Critical']
        
        print(f"\nStress Level Distribution:")
        for (low, high), label in zip(bins, labels):
            count = ((dcii_series >= low) & (dcii_series < high)).sum()
            percentage = count / len(dcii_series) * 100
            print(f"  {label:10}: {percentage:5.1f}% ({count} periods)")
        
        return dcii_series
    
    def calibrate_forex(self):
        """Simple calibration for forex."""
        print("\n4. CALIBRATION")
        print("-"*40)
        
        # Forex markets typically:
        # - Higher sensitivity to pressure (volatility, volume spikes)
        # - Moderate resilience (liquidity provides some stability)
        self.beta = 1.3
        self.gamma = 0.7
        
        print(f"Calibrated parameters:")
        print(f"  β (pressure): {self.beta:.2f} - Higher sensitivity for forex")
        print(f"  γ (resilience): {self.gamma:.2f} - Moderate resilience")
        print(f"  Ratio (γ/β): {self.gamma/self.beta:.2f}")
        
        if self.gamma/self.beta < 0.6:
            print("  System: Fragile (low resilience relative to pressure sensitivity)")
        elif self.gamma/self.beta < 0.9:
            print("  System: Balanced")
        else:
            print("  System: Resilient")
    
    def monitor_example(self):
        """Show example monitoring scenario."""
        print("\n5. EXAMPLE MONITORING")
        print("-"*40)
        
        # Example 1: Normal market conditions
        normal_market = {
            'volatility': 0.3,      # Low volatility
            'volume_ratio': 0.4,    # Normal volume
            'spread_ratio': 0.3,    # Tight spreads
            'tick_frequency': 0.5,  # Normal activity
            'momentum_20min': 0.4,  # Slight positive momentum
            'momentum_1hr': 0.45    # Neutral longer-term
        }
        
        dcii_normal = self.compute_dcii_point(normal_market)
        level_normal = self.classify_dcii(dcii_normal)
        
        # Example 2: Stress market conditions
        stress_market = {
            'volatility': 0.8,      # High volatility
            'volume_ratio': 0.9,    # High volume
            'spread_ratio': 0.85,   # Widening spreads
            'tick_frequency': 0.9,  # High activity
            'momentum_20min': 0.1,  # Negative momentum
            'momentum_1hr': 0.15    # Negative longer-term
        }
        
        dcii_stress = self.compute_dcii_point(stress_market)
        level_stress = self.classify_dcii(dcii_stress)
        
        print("Example Scenarios:")
        print(f"  Normal Market:   DCII = {dcii_normal:.3f} - {level_normal}")
        print(f"  Stress Market:   DCII = {dcii_stress:.3f} - {level_stress}")
        
        print("\nTop contributors in stress scenario:")
        sorted_signals = sorted(stress_market.items(), key=lambda x: x[1], reverse=True)
        for signal, value in sorted_signals[:3]:
            print(f"  {signal:20}: {value:.3f}")
    
    def classify_dcii(self, dcii: float) -> str:
        """Classify DCII value into stress level."""
        if dcii < 0.3:
            return "Normal"
        elif dcii < 0.5:
            return "Elevated"
        elif dcii < 0.7:
            return "High Stress"
        else:
            return "Critical"
    
    def run_complete(self, data_path: Path):
        """Run complete pipeline."""
        success = self.load_and_process(data_path)
        
        if not success:
            print("\n❌ Pipeline failed at data loading stage")
            return
        
        self.calibrate_forex()
        historical_dcii = self.compute_historical_dcii()
        self.monitor_example()
        
        print("\n" + "="*60)
        print("✅ DCII FOREX PIPELINE COMPLETE")
        print("="*60)
        
        # Save results if you want
        if not historical_dcii.empty:
            output_dir = Path("forex_dcii_output")
            output_dir.mkdir(exist_ok=True)
            
            # Save DCII series
            historical_dcii.to_csv(output_dir / "historical_dcii.csv")
            
            # Save parameters
            params = {
                'beta': self.beta,
                'gamma': self.gamma,
                'signals': list(self.normalized_signals.keys()),
                'timestamp': datetime.now().isoformat()
            }
            
            import json
            with open(output_dir / "parameters.json", 'w') as f:
                json.dump(params, f, indent=2)
            
            print(f"\n💾 Results saved to: {output_dir}/")
            print("  - historical_dcii.csv: DCII values over time")
            print("  - parameters.json: Calibrated parameters")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function."""
    
    # Your data is in the "2024" directory in current folder
    data_path = Path.cwd() / "2024"
    
    if not data_path.exists():
        print(f"❌ Data directory not found: {data_path}")
        print("Make sure you have a '2024' directory with BI5 data in current folder.")
        print(f"Current directory: {Path.cwd()}")
        print(f"Contents: {list(Path.cwd().iterdir())}")
        return
    
    print(f"🔍 Data path: {data_path}")
    
    # Run the DCII pipeline
    dcii_module = SimpleForexDCII(name="EURUSD_Forex_DCII")
    dcii_module.run_complete(data_path)
    
    print("\n📋 QUICK USAGE:")
    print("-"*40)
    print("""
# Monitor current market:
current = {
    'volatility': 0.6,      # Moderate volatility
    'volume_ratio': 0.7,    # Elevated volume
    'spread_ratio': 0.4,    # Normal spread
    'tick_frequency': 0.8,  # High activity
    'momentum_20min': 0.3,  # Slight negative
    'momentum_1hr': 0.35    # Neutral
}

dcii = dcii_module.compute_dcii_point(current)
level = dcii_module.classify_dcii(dcii)
print(f"DCII: {dcii:.3f} - {level}")
    """)

if __name__ == "__main__":
    main()
