#!/usr/bin/env python3
"""
DCII FOREX MODULE - EUR/USD
Uses real BI5 tick data from current directory
"""

import struct
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# BI5 DATA LOADER
# ============================================================================

class BI5Loader:
    """Loads and processes BI5 tick data files."""
    
    @staticmethod
    def read_bi5_file(filepath: Path) -> pd.DataFrame:
        """
        Read a BI5 file and return DataFrame with ticks.
        
        BI5 Format (binary):
        - Each tick: 5 fields (20 bytes total)
        - timestamp (uint32): milliseconds since epoch
        - ask (float32): ask price
        - bid (float32): bid price
        - ask_volume (float32)
        - bid_volume (float32)
        """
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            if len(data) % 20 != 0:
                print(f"Warning: File {filepath} has unexpected size")
                return pd.DataFrame()
            
            ticks = []
            for i in range(0, len(data), 20):
                chunk = data[i:i+20]
                if len(chunk) < 20:
                    break
                
                # Unpack binary data
                timestamp, ask, bid, ask_vol, bid_vol = struct.unpack('Iffff', chunk)
                
                # Convert timestamp to datetime
                dt = datetime.fromtimestamp(timestamp / 1000.0)
                
                ticks.append({
                    'timestamp': dt,
                    'ask': ask,
                    'bid': bid,
                    'mid': (ask + bid) / 2,  # Mid price
                    'spread': ask - bid,     # Spread in pips
                    'ask_volume': ask_vol,
                    'bid_volume': bid_vol,
                    'total_volume': ask_vol + bid_vol
                })
            
            return pd.DataFrame(ticks)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def load_all_bi5_data(base_path: Path, year: int = 2024, 
                         months: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Load all BI5 files from directory structure.
        
        Structure: year/month/day/hour_ticks.bi5
        Example: 2024/1/1/00h_ticks.bi5
        """
        all_ticks = []
        
        if months is None:
            months = list(range(1, 13))  # All months
        
        for month in months:
            month_dir = base_path / str(month)
            if not month_dir.exists():
                continue
            
            print(f"  Loading month {month}...")
            
            # Find all day directories
            day_dirs = [d for d in month_dir.iterdir() if d.is_dir()]
            for day_dir in day_dirs:
                # Find all BI5 files
                bi5_files = list(day_dir.glob("*h_ticks.bi5"))
                
                for bi5_file in bi5_files:
                    df = BI5Loader.read_bi5_file(bi5_file)
                    if not df.empty:
                        all_ticks.append(df)
                
                if len(bi5_files) > 0:
                    print(f"    Day {day_dir.name}: {len(bi5_files)} files")
        
        if all_ticks:
            result = pd.concat(all_ticks, ignore_index=True).sort_values('timestamp')
            print(f"  Total ticks loaded: {len(result):,}")
            return result
        else:
            print("  No data loaded")
            return pd.DataFrame()

# ============================================================================
# FOREX SIGNAL GENERATOR
# ============================================================================

class ForexSignalGenerator:
    """Generates market signals from tick data."""
    
    def __init__(self, tick_data: pd.DataFrame):
        self.ticks = tick_data
        self.signals = {}
    
    def resample_to_interval(self, interval: str = '5min') -> pd.DataFrame:
        """Resample tick data to regular intervals."""
        if self.ticks.empty:
            return pd.DataFrame()
        
        # Set timestamp as index
        df = self.ticks.set_index('timestamp')
        
        # Resample to desired interval
        resampled = df['mid'].resample(interval).ohlc()
        resampled['volume'] = df['total_volume'].resample(interval).sum()
        resampled['spread'] = df['spread'].resample(interval).mean()
        resampled['tick_count'] = df['mid'].resample(interval).count()
        
        # Calculate returns
        resampled['returns'] = resampled['close'].pct_change()
        
        return resampled.dropna()
    
    def generate_signals(self, interval: str = '5min') -> Dict[str, pd.Series]:
        """Generate multiple market signals from tick data."""
        df = self.resample_to_interval(interval)
        
        if df.empty:
            return {}
        
        # 1. Volatility (Rolling standard deviation of returns)
        returns_vol = df['returns'].rolling(window=20).std()
        
        # 2. Volume surge (Volume relative to moving average)
        volume_ma = df['volume'].rolling(window=50).mean()
        volume_surge = df['volume'] / (volume_ma + 1e-8)
        
        # 3. Spread widening (Spread relative to average)
        spread_ma = df['spread'].rolling(window=50).mean()
        spread_widening = df['spread'] / (spread_ma + 1e-8)
        
        # 4. Price momentum
        momentum_1h = df['close'].pct_change(12)  # 1 hour momentum (12 * 5min)
        momentum_4h = df['close'].pct_change(48)  # 4 hour momentum
        
        # 5. Tick frequency (Market activity)
        tick_freq = df['tick_count'].rolling(window=20).mean()
        
        # 6. Absolute returns (magnitude of price changes)
        abs_returns = df['returns'].abs()
        
        self.signals = {
            'volatility': returns_vol,
            'volume_surge': volume_surge,
            'spread_widening': spread_widening,
            'momentum_1h': momentum_1h,
            'momentum_4h': momentum_4h,
            'tick_frequency': tick_freq,
            'abs_returns': abs_returns
        }
        
        return self.signals

# ============================================================================
# FOREX DCII MODULE
# ============================================================================

class ForexDCIIModule:
    """DCII Module for EUR/USD Forex Market."""
    
    def __init__(self, data_path: Path, name: str = "EURUSD_Forex_DCII"):
        self.name = name
        self.data_path = data_path
        self.tick_data = pd.DataFrame()
        self.signals = {}
        self.normalized_signals = {}
        self.normalization_params = {}
        
        # DCII parameters (will be calibrated)
        self.beta = 1.0  # Pressure coefficient
        self.gamma = 1.0  # Resilience coefficient
        
    def load_data(self, months: List[int] = None) -> 'ForexDCIIModule':
        """Load BI5 tick data from current directory structure."""
        print(f"📂 Loading EUR/USD tick data from {self.data_path}...")
        
        if months is None:
            months = [1]  # Default: load January data for quick testing
        
        self.tick_data = BI5Loader.load_all_bi5_data(self.data_path, months=months)
        
        if self.tick_data.empty:
            print("❌ No data loaded! Check directory structure.")
            print(f"   Expected: {self.data_path}/month/day/*h_ticks.bi5")
        else:
            print(f"✅ Loaded {len(self.tick_data):,} ticks")
            print(f"   Date range: {self.tick_data['timestamp'].min()} to {self.tick_data['timestamp'].max()}")
        
        return self
    
    def generate_and_normalize_signals(self, interval: str = '15min') -> 'ForexDCIIModule':
        """Generate and normalize market signals."""
        if self.tick_data.empty:
            print("❌ No tick data available. Load data first.")
            return self
        
        # Generate signals
        generator = ForexSignalGenerator(self.tick_data)
        raw_signals = generator.generate_signals(interval)
        
        if not raw_signals:
            print("❌ Failed to generate signals")
            return self
        
        # Remove NaN values and align indices
        for name, series in raw_signals.items():
            raw_signals[name] = series.dropna()
        
        # Find common index (where all signals have values)
        common_idx = None
        for series in raw_signals.values():
            if common_idx is None:
                common_idx = series.index
            else:
                common_idx = common_idx.intersection(series.index)
        
        # Align all signals to common index
        self.signals = {}
        for name, series in raw_signals.items():
            self.signals[name] = series.loc[common_idx]
        
        # Normalize signals to [0, 1] range
        self.normalized_signals = {}
        self.normalization_params = {}
        
        print("\n📊 Signal Statistics:")
        for name, series in self.signals.items():
            # Winsorize outliers (cap at 99th percentile)
            q99 = series.quantile(0.99)
            series_clean = series.clip(upper=q99)
            
            # Z-score normalization then sigmoid
            mean_val = series_clean.mean()
            std_val = series_clean.std()
            z_scores = (series_clean - mean_val) / (std_val + 1e-8)
            normalized = 1 / (1 + np.exp(-z_scores))
            
            self.normalized_signals[name] = normalized
            self.normalization_params[name] = {
                'mean': float(mean_val),
                'std': float(std_val),
                'q99': float(q99)
            }
            
            print(f"  {name:20} | Mean: {mean_val:8.6f} | Std: {std_val:8.6f} | Norm range: [{normalized.min():.3f}, {normalized.max():.3f}]")
        
        print(f"\n✅ Generated {len(self.signals)} signals with {len(common_idx)} data points")
        return self
    
    def compute_dcii(self, signal_values: Dict[str, float]) -> float:
        """
        Compute DCII index for given signal values.
        
        DCII = β * mean(signals) - γ * std(signals)
        """
        if not signal_values:
            return 0.0
        
        values = list(signal_values.values())
        pressure = self.beta * np.mean(values)
        resilience = self.gamma * np.std(values) if len(values) > 1 else 0.0
        
        dcii = pressure - resilience
        return np.clip(dcii, 0.0, 1.0)
    
    def calibrate_simple(self) -> 'ForexDCIIModule':
        """
        Simple calibration using predefined scenarios.
        In production, you'd use historical stress periods.
        """
        print("\n🔧 Calibrating DCII parameters for Forex...")
        
        # Define calibration scenarios based on normalized signal levels
        scenarios = [
            {
                'name': 'normal',
                'signals': {name: 0.3 for name in self.normalized_signals.keys()},
                'target': 0.3,
                'weight': 1.0
            },
            {
                'name': 'stress',
                'signals': {name: 0.7 for name in self.normalized_signals.keys()},
                'target': 0.7,
                'weight': 2.0  # Higher weight for stress scenarios
            },
            {
                'name': 'crisis',
                'signals': {name: 0.9 for name in self.normalized_signals.keys()},
                'target': 0.9,
                'weight': 3.0  # Highest weight for crisis
            }
        ]
        
        # For forex markets, typical values might be:
        # Higher beta (more sensitive to pressure) 
        # Moderate gamma (some resilience from diversification)
        self.beta = 1.3
        self.gamma = 0.7
        
        print(f"✅ Calibrated: β={self.beta:.3f}, γ={self.gamma:.3f}")
        print("   (Note: Using preset values for forex. For production, optimize with historical crises.)")
        
        return self
    
    def compute_historical_dcii(self) -> pd.Series:
        """Compute DCII for all historical data points."""
        if not self.normalized_signals:
            print("❌ No normalized signals available")
            return pd.Series()
        
        # Align all signals
        signals_df = pd.DataFrame(self.normalized_signals)
        
        # Compute DCII for each time point
        dcii_values = []
        for idx, row in signals_df.iterrows():
            signal_dict = row.to_dict()
            dcii = self.compute_dcii(signal_dict)
            dcii_values.append(dcii)
        
        return pd.Series(dcii_values, index=signals_df.index)
    
    def monitor_current(self, current_signals_raw: Dict[str, float]) -> Dict:
        """
        Monitor current market conditions.
        
        Args:
            current_signals_raw: Raw signal values (not normalized)
        """
        # Normalize current signals
        normalized = {}
        for name, value in current_signals_raw.items():
            if name in self.normalization_params:
                params = self.normalization_params[name]
                # Cap at 99th percentile
                value_capped = min(value, params['q99'])
                # Z-score then sigmoid
                z = (value_capped - params['mean']) / (params['std'] + 1e-8)
                normalized[name] = 1 / (1 + np.exp(-z))
            else:
                print(f"⚠️  No normalization params for {name}")
                normalized[name] = value
        
        # Compute DCII
        dcii = self.compute_dcii(normalized)
        
        # Classify stress level
        if dcii < 0.3:
            level = "Normal"
            color = "green"
            action = "Normal trading"
        elif dcii < 0.5:
            level = "Elevated"
            color = "yellow"
            action = "Increase monitoring"
        elif dcii < 0.7:
            level = "High Stress"
            color = "orange"
            action = "Reduce position sizes"
        else:
            level = "Crisis"
            color = "red"
            action = "Close non-essential positions"
        
        # Identify top contributors
        sorted_signals = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'dcii': float(dcii),
            'level': level,
            'color': color,
            'action': action,
            'top_contributors': dict(sorted_signals[:3]),
            'all_signals': normalized
        }
    
    def run_pipeline(self) -> Dict:
        """Run complete DCII pipeline for Forex."""
        print("="*70)
        print("FOREX DCII PIPELINE: EUR/USD")
        print("="*70)
        
        try:
            # Step 1-2: Load data and generate signals
            print("\n📥 STEP 1-2: DATA LOADING & SIGNAL GENERATION")
            print("-"*40)
            
            # Load data from current directory
            self.load_data(months=[1, 2])  # Load Jan-Feb for better statistics
            
            if self.tick_data.empty:
                print("❌ No data loaded. Check if BI5 files exist in current directory.")
                print("   Current directory structure should be: month/day/*h_ticks.bi5")
                return {}
            
            # Generate signals
            self.generate_and_normalize_signals(interval='15min')  # 15-minute intervals
            
            if not self.signals:
                print("❌ Failed to generate signals. Pipeline stopped.")
                return {}
            
            # Step 3: Calibration
            print("\n🔧 STEP 3: CALIBRATION")
            print("-"*40)
            self.calibrate_simple()
            
            # Step 4: Historical analysis
            print("\n📈 STEP 4: HISTORICAL ANALYSIS")
            print("-"*40)
            historical_dcii = self.compute_historical_dcii()
            
            if not historical_dcii.empty:
                print(f"Historical DCII Statistics:")
                print(f"  Mean: {historical_dcii.mean():.3f}")
                print(f"  Std: {historical_dcii.std():.3f}")
                print(f"  Min: {historical_dcii.min():.3f}")
                print(f"  Max: {historical_dcii.max():.3f}")
                
                # Count stress levels
                normal_pct = (historical_dcii < 0.3).mean() * 100
                elevated_pct = ((historical_dcii >= 0.3) & (historical_dcii < 0.5)).mean() * 100
                high_pct = ((historical_dcii >= 0.5) & (historical_dcii < 0.7)).mean() * 100
                crisis_pct = (historical_dcii >= 0.7).mean() * 100
                
                print(f"\nStress Level Distribution:")
                print(f"  Normal: {normal_pct:.1f}%")
                print(f"  Elevated: {elevated_pct:.1f}%")
                print(f"  High Stress: {high_pct:.1f}%")
                print(f"  Crisis: {crisis_pct:.1f}%")
            
            # Step 5: Test monitoring
            print("\n🎯 STEP 5: TEST MONITORING")
            print("-"*40)
            
            # Create realistic test signals based on signal statistics
            test_signals = {}
            for name, params in self.normalization_params.items():
                # Use mean + 2 std as test value (elevated/stress scenario)
                test_value = params['mean'] + 2 * params['std']
                test_signals[name] = test_value
            
            alert = self.monitor_current(test_signals)
            
            print(f"Test Alert (Elevated Scenario):")
            print(f"  DCII Index: {alert['dcii']:.3f}")
            print(f"  Stress Level: {alert['level']} ({alert['color']})")
            print(f"  Recommended Action: {alert['action']}")
            print(f"  Top 3 Contributors: {alert['top_contributors']}")
            
            print("\n" + "="*70)
            print("✅ FOREX DCII PIPELINE COMPLETE!")
            print("="*70)
            
            return {
                'module': self,
                'historical_dcii': historical_dcii,
                'test_alert': alert,
                'signal_count': len(self.signals),
                'data_points': len(historical_dcii) if not historical_dcii.empty else 0
            }
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to run the Forex DCII module."""
    
    # Use current directory as data path
    current_dir = Path.cwd() / "2024"  # Your data is in "2024" subdirectory
    
    if not current_dir.exists():
        print(f"❌ Data directory not found: {current_dir}")
        print("Please make sure you have a '2024' directory with BI5 data in the current directory.")
        print("Current directory contents:")
        import os
        print(os.listdir('.'))
        return
    
    print(f"📁 Using BI5 data from: {current_dir}")
    
    # Create and run the Forex DCII module
    forex_module = ForexDCIIModule(current_dir, name="EURUSD_Forex_DCII")
    results = forex_module.run_pipeline()
    
    if results:
        print(f"\n📋 Summary:")
        print(f"  Signals generated: {results['signal_count']}")
        print(f"  Data points analyzed: {results['data_points']}")
        
        print("\n💡 Example usage for real-time monitoring:")
        print("""
# After running the pipeline, you can monitor current conditions:
current_market = {
    'volatility': 0.00015,      # 1.5 pips volatility
    'volume_surge': 2.5,        # 2.5x normal volume
    'spread_widening': 1.8,     # 1.8x normal spread
    'momentum_1h': -0.001,      # -0.1% over 1 hour
    'momentum_4h': -0.002,      # -0.2% over 4 hours
    'tick_frequency': 1200,     # 1200 ticks/interval
    'abs_returns': 0.0001       # 0.01% average absolute return
}

alert = forex_module.monitor_current(current_market)
print(f"DCII Index: {alert['dcii']:.3f}")
print(f"Stress Level: {alert['level']} ({alert['color']})")
print(f"Action: {alert['action']}")
print(f"Top Contributors: {alert['top_contributors']}")
        """)

if __name__ == "__main__":
    main()
