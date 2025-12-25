#!/usr/bin/env python3
"""
DCII FOREX MODULE - FINAL VERSION
Fixed timestamp issue and improved calibration
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
# BI5 LOADER WITH FIXED TIMESTAMPS
# ============================================================================

class BI5LoaderFixed:
    """BI5 loader with proper timestamp handling."""
    
    @staticmethod
    def parse_timestamp(timestamp_ms: int, filepath: Path) -> datetime:
        """
        Parse timestamp from BI5 file.
        BI5 timestamps might be in milliseconds since a different epoch.
        """
        try:
            # Try standard Unix epoch (seconds since 1970-01-01)
            dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
            
            # If date is 1970, try alternative: milliseconds since 2001-01-01
            if dt.year == 1970:
                # Try: milliseconds since 2001-01-01
                epoch_2001 = datetime(2001, 1, 1)
                dt = epoch_2001 + timedelta(milliseconds=timestamp_ms)
            
            # Extract date from filename as fallback
            # Filename format: YYYY/MM/DD/HHh_ticks.bi5
            parts = filepath.parts
            if len(parts) >= 4:
                try:
                    year = int(parts[-4])
                    month = int(parts[-3])
                    day = int(parts[-2])
                    hour = int(filepath.stem.split('h_')[0])
                    
                    # Create datetime from filename
                    dt_from_file = datetime(year, month, day, hour)
                    
                    # Keep the time from timestamp but date from filename
                    dt = dt.replace(year=dt_from_file.year, 
                                   month=dt_from_file.month, 
                                   day=dt_from_file.day)
                except:
                    pass
            
            return dt
        except:
            # Fallback: use current time
            return datetime.now()
    
    @staticmethod
    def read_bi5_file(filepath: Path) -> pd.DataFrame:
        """Read a single BI5 file with corrected timestamps."""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            if len(data) == 0:
                return pd.DataFrame()
            
            ticks = []
            # Extract hour from filename for timestamp correction
            hour_from_file = 0
            try:
                hour_from_file = int(filepath.stem.split('h_')[0])
            except:
                pass
            
            for i in range(0, len(data), 20):
                if i + 20 > len(data):
                    break
                
                chunk = data[i:i+20]
                timestamp, ask, bid, ask_vol, bid_vol = struct.unpack('Iffff', chunk)
                
                # Parse timestamp with correction
                dt = BI5LoaderFixed.parse_timestamp(timestamp, filepath)
                
                # Calculate mid price and spread in pips
                mid_price = (ask + bid) / 2
                spread_pips = (ask - bid) * 10000  # For EUR/USD, 1 pip = 0.0001
                
                ticks.append({
                    'timestamp': dt,
                    'ask': ask,
                    'bid': bid,
                    'mid': mid_price,
                    'spread_pips': spread_pips,
                    'spread_raw': ask - bid,
                    'ask_volume': ask_vol,
                    'bid_volume': bid_vol,
                    'total_volume': ask_vol + bid_vol,
                    'file_hour': hour_from_file
                })
            
            return pd.DataFrame(ticks)
        except Exception as e:
            print(f"  Error reading {filepath.name}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def load_sample_data(data_path: Path, 
                        sample_size: int = 10,
                        specific_month: Optional[int] = None) -> pd.DataFrame:
        """
        Load sample data for testing.
        
        Args:
            sample_size: Number of BI5 files to load
            specific_month: Load only from this month (e.g., 4 for April)
        """
        print(f"📂 Loading data from: {data_path}")
        
        all_ticks = []
        loaded_files = 0
        
        # Get month directories
        month_dirs = []
        for item in data_path.iterdir():
            if item.is_dir():
                try:
                    month_num = int(item.name)
                    month_dirs.append((month_num, item))
                except:
                    # Skip non-numeric directories
                    pass
        
        # Sort by month
        month_dirs.sort(key=lambda x: x[0])
        
        # Filter by specific month if requested
        if specific_month is not None:
            month_dirs = [(m, p) for m, p in month_dirs if m == specific_month]
        
        print(f"Found {len(month_dirs)} month directories")
        
        for month_num, month_dir in month_dirs:
            print(f"\nMonth {month_num:02d}:")
            
            # Get day directories
            day_dirs = []
            for item in month_dir.iterdir():
                if item.is_dir():
                    try:
                        day_num = int(item.name)
                        day_dirs.append((day_num, item))
                    except:
                        pass
            
            day_dirs.sort(key=lambda x: x[0])
            
            for day_num, day_dir in day_dirs[:3]:  # First 3 days only
                bi5_files = sorted(day_dir.glob("*h_ticks.bi5"))
                
                if bi5_files:
                    print(f"  Day {day_num:02d}: {len(bi5_files)} hours")
                    
                    # Load first few files from this day
                    for bi5_file in bi5_files[:2]:  # First 2 hours
                        if loaded_files >= sample_size:
                            break
                        
                        df = BI5LoaderFixed.read_bi5_file(bi5_file)
                        if not df.empty:
                            all_ticks.append(df)
                            loaded_files += 1
                            print(f"    Loaded: {bi5_file.name} ({len(df)} ticks)")
                
                if loaded_files >= sample_size:
                    break
            
            if loaded_files >= sample_size:
                break
        
        if all_ticks:
            result = pd.concat(all_ticks, ignore_index=True).sort_values('timestamp')
            print(f"\n✅ Loaded {len(result):,} ticks from {loaded_files} files")
            
            # Verify dates
            print(f"\n📅 Date verification:")
            print(f"   Start: {result['timestamp'].min()}")
            print(f"   End:   {result['timestamp'].max()}")
            print(f"   Unique days: {result['timestamp'].dt.date.nunique()}")
            
            # Check for 1970 dates
            old_dates = (result['timestamp'].dt.year == 1970).sum()
            if old_dates > 0:
                print(f"   ⚠️  Found {old_dates} ticks with 1970 dates")
            
            return result
        else:
            print("❌ No data loaded")
            return pd.DataFrame()

# ============================================================================
# IMPROVED FOREX DCII ENGINE
# ============================================================================

class ForexDCIICore:
    """Core DCII engine for forex markets."""
    
    def __init__(self):
        self.beta = 1.0  # Pressure sensitivity
        self.gamma = 1.0  # Resilience
        self.signals = {}
        self.normalized_signals = {}
        self.normalization_params = {}
        
        # Forex market characteristics
        self.market_info = {
            'instrument': 'EUR/USD',
            'typical_spread': 0.0001,  # 1 pip
            'typical_volatility': 0.0005,  # 5 pips per period
            'trading_hours': '24/5'
        }
    
    def process_tick_data(self, tick_data: pd.DataFrame, 
                         interval: str = '10min') -> bool:
        """Process tick data into signals."""
        if tick_data.empty:
            return False
        
        print(f"\n📊 Processing {len(tick_data):,} ticks into {interval} bars...")
        
        # Resample to OHLC
        df = tick_data.set_index('timestamp')
        ohlc = df['mid'].resample(interval).ohlc()
        ohlc['volume'] = df['total_volume'].resample(interval).sum()
        ohlc['spread'] = df['spread_pips'].resample(interval).mean()
        ohlc['tick_count'] = df['mid'].resample(interval).count()
        
        # Calculate returns and volatility
        ohlc['returns'] = ohlc['close'].pct_change()
        ohlc['abs_returns'] = ohlc['returns'].abs()
        
        # Generate signals
        signals = {}
        
        # 1. Normalized volatility (z-score of absolute returns)
        vol_window = min(20, len(ohlc) // 4)
        if vol_window > 5:
            signals['volatility'] = ohlc['abs_returns'].rolling(vol_window).std()
        
        # 2. Volume stress (volume vs MA)
        volume_window = min(50, len(ohlc) // 2)
        if volume_window > 10:
            volume_ma = ohlc['volume'].rolling(volume_window).mean()
            signals['volume_stress'] = ohlc['volume'] / (volume_ma + 1e-8)
        
        # 3. Spread stress
        spread_window = min(50, len(ohlc) // 2)
        if spread_window > 10:
            spread_ma = ohlc['spread'].rolling(spread_window).mean()
            signals['spread_stress'] = ohlc['spread'] / (spread_ma + 1e-8)
        
        # 4. Liquidity (tick frequency)
        tick_window = min(20, len(ohlc) // 4)
        if tick_window > 5:
            tick_ma = ohlc['tick_count'].rolling(tick_window).mean()
            signals['liquidity'] = ohlc['tick_count'] / (tick_ma + 1e-8)
        
        # 5. Momentum
        signals['momentum_short'] = ohlc['close'].pct_change(periods=6)   # 1 hour
        signals['momentum_medium'] = ohlc['close'].pct_change(periods=24)  # 4 hours
        
        # Remove NaN
        for name in list(signals.keys()):
            signals[name] = signals[name].dropna()
        
        self.signals = signals
        return len(signals) > 0
    
    def normalize_signals_robust(self):
        """Robust signal normalization."""
        if not self.signals:
            return
        
        self.normalized_signals = {}
        self.normalization_params = {}
        
        print("\n🔢 Normalizing signals...")
        
        for name, series in self.signals.items():
            if len(series) < 10:
                continue
            
            # Handle outliers using IQR method
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            
            if iqr > 0:
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                series_clipped = series.clip(lower_bound, upper_bound)
            else:
                series_clipped = series
            
            # Robust statistics (median and MAD)
            median_val = series_clipped.median()
            mad = (series_clipped - median_val).abs().median()
            
            if mad > 0:
                # Modified z-score
                modified_z = 0.6745 * (series_clipped - median_val) / mad
                # Sigmoid to [0, 1]
                normalized = 1 / (1 + np.exp(-modified_z))
            else:
                # Constant series
                normalized = pd.Series(0.5, index=series.index)
            
            self.normalized_signals[name] = normalized
            self.normalization_params[name] = {
                'median': float(median_val),
                'mad': float(mad),
                'q1': float(q1),
                'q3': float(q3),
                'min_raw': float(series.min()),
                'max_raw': float(series.max())
            }
            
            print(f"  {name:20} | Median: {median_val:8.4f} | MAD: {mad:8.4f} | Norm: [{normalized.min():.3f}, {normalized.max():.3f}]")
    
    def calibrate_using_quartiles(self):
        """Calibrate using data quartiles."""
        if not self.normalized_signals:
            print("❌ No signals for calibration")
            return
        
        # Collect all normalized values
        all_values = []
        for series in self.normalized_signals.values():
            all_values.extend(series.values)
        
        all_values = np.array(all_values)
        
        # Calculate pressure (mean) and resilience (dispersion) at different quartiles
        q25, q50, q75 = np.percentile(all_values, [25, 50, 75])
        
        # For forex: higher beta (more reactive), moderate gamma
        # Beta = 1.3 means 30% more sensitive than baseline
        # Gamma = 0.8 means 20% less resilience than baseline
        self.beta = 1.3
        self.gamma = 0.8
        
        print(f"\n🎯 Calibration Results:")
        print(f"   Data quartiles: Q1={q25:.3f}, Median={q50:.3f}, Q3={q75:.3f}")
        print(f"   β (pressure coefficient): {self.beta:.2f}")
        print(f"   γ (resilience coefficient): {self.gamma:.2f}")
        print(f"   System type: {'Fragile' if self.gamma/self.beta < 0.6 else 'Balanced' if self.gamma/self.beta < 0.9 else 'Resilient'}")
    
    def compute_dcii_series(self) -> pd.Series:
        """Compute DCII time series."""
        if not self.normalized_signals:
            return pd.Series()
        
        # Align all signals
        signal_frames = []
        for name, series in self.normalized_signals.items():
            signal_frames.append(pd.DataFrame({name: series}))
        
        aligned = pd.concat(signal_frames, axis=1).dropna()
        
        print(f"\n📈 Computing DCII for {len(aligned)} time points...")
        
        # Compute DCII for each row
        dcii_values = []
        for _, row in aligned.iterrows():
            signal_dict = row.to_dict()
            values = list(signal_dict.values())
            
            pressure = self.beta * np.mean(values)
            resilience = self.gamma * np.std(values) if len(values) > 1 else 0
            
            dcii = pressure - resilience
            dcii_values.append(max(0, min(1, dcii)))
        
        return pd.Series(dcii_values, index=aligned.index)
    
    def analyze_stress_levels(self, dcii_series: pd.Series):
        """Analyze stress level distribution."""
        if dcii_series.empty:
            return
        
        print(f"\n🚨 Stress Level Analysis:")
        print("-"*40)
        
        # Define stress levels
        levels = [
            (0.0, 0.3, "Normal", "🟢"),
            (0.3, 0.5, "Elevated", "🟡"),
            (0.5, 0.7, "High", "🟠"),
            (0.7, 1.0, "Critical", "🔴")
        ]
        
        total = len(dcii_series)
        for low, high, name, emoji in levels:
            mask = (dcii_series >= low) & (dcii_series < high)
            count = mask.sum()
            percentage = count / total * 100
            
            # Get average DCII in this range
            avg_in_range = dcii_series[mask].mean() if count > 0 else 0
            
            print(f"{emoji} {name:10}: {percentage:5.1f}% ({count:4d} periods)")
            if count > 0:
                print(f"      Avg DCII: {avg_in_range:.3f}, Range: [{dcii_series[mask].min():.3f}, {dcii_series[mask].max():.3f}]")
        
        # Overall statistics
        print(f"\n📊 Overall Statistics:")
        print(f"   Mean DCII: {dcii_series.mean():.3f}")
        print(f"   Std Dev:   {dcii_series.std():.3f}")
        print(f"   Skewness:  {dcii_series.skew():.3f}")
        print(f"   Kurtosis:  {dcii_series.kurtosis():.3f}")
    
    def monitor_example_scenarios(self):
        """Show example monitoring scenarios."""
        print(f"\n🎭 Example Monitoring Scenarios:")
        print("-"*40)
        
        scenarios = [
            ("Normal Trading", {
                'volatility': 0.3,
                'volume_stress': 0.4,
                'spread_stress': 0.2,
                'liquidity': 0.5,
                'momentum_short': 0.4,
                'momentum_medium': 0.45
            }),
            ("News Volatility", {
                'volatility': 0.8,
                'volume_stress': 0.9,
                'spread_stress': 0.7,
                'liquidity': 0.9,
                'momentum_short': 0.6,
                'momentum_medium': 0.55
            }),
            ("Liquidity Crisis", {
                'volatility': 0.9,
                'volume_stress': 1.0,
                'spread_stress': 0.9,
                'liquidity': 0.1,  # Low liquidity
                'momentum_short': 0.1,
                'momentum_medium': 0.2
            })
        ]
        
        for name, signals in scenarios:
            # Filter to only signals we have
            available_signals = {k: v for k, v in signals.items() 
                               if k in self.normalization_params}
            
            if not available_signals:
                continue
            
            dcii = self.compute_dcii_point(available_signals)
            level = self.classify_dcii(dcii)
            
            # Get top 2 contributors
            sorted_sigs = sorted(available_signals.items(), 
                               key=lambda x: x[1], reverse=True)[:2]
            
            print(f"\n{name}:")
            print(f"  DCII: {dcii:.3f} - {level}")
            print(f"  Top contributors: {', '.join([f'{k}={v:.2f}' for k, v in sorted_sigs])}")
    
    def compute_dcii_point(self, signal_values: Dict[str, float]) -> float:
        """Compute DCII for a single point."""
        if not signal_values:
            return 0.5
        
        values = list(signal_values.values())
        pressure = self.beta * np.mean(values)
        resilience = self.gamma * np.std(values) if len(values) > 1 else 0
        
        return max(0, min(1, pressure - resilience))
    
    def classify_dcii(self, dcii: float) -> str:
        """Classify DCII value."""
        if dcii < 0.3:
            return "Normal 🟢"
        elif dcii < 0.5:
            return "Elevated 🟡"
        elif dcii < 0.7:
            return "High Stress 🟠"
        else:
            return "Critical 🔴"

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Run complete DCII pipeline."""
    
    print("="*70)
    print("FOREX DCII PIPELINE - FINAL VERSION")
    print("="*70)
    
    # Data path
    data_path = Path.cwd() / "2024"
    
    if not data_path.exists():
        print(f"❌ Data directory not found: {data_path}")
        return
    
    print(f"Data source: {data_path}")
    
    # Step 1: Load data
    print("\n" + "="*70)
    print("STEP 1: DATA LOADING")
    print("="*70)
    
    tick_data = BI5LoaderFixed.load_sample_data(
        data_path, 
        sample_size=15,
        specific_month=4  # Load April data
    )
    
    if tick_data.empty:
        print("❌ Failed to load data")
        return
    
    # Step 2: Process data
    print("\n" + "="*70)
    print("STEP 2: SIGNAL PROCESSING")
    print("="*70)
    
    dcii_engine = ForexDCIICore()
    success = dcii_engine.process_tick_data(tick_data, interval='15min')
    
    if not success:
        print("❌ Failed to process signals")
        return
    
    dcii_engine.normalize_signals_robust()
    
    # Step 3: Calibration
    print("\n" + "="*70)
    print("STEP 3: CALIBRATION")
    print("="*70)
    
    dcii_engine.calibrate_using_quartiles()
    
    # Step 4: Historical analysis
    print("\n" + "="*70)
    print("STEP 4: HISTORICAL ANALYSIS")
    print("="*70)
    
    historical_dcii = dcii_engine.compute_dcii_series()
    dcii_engine.analyze_stress_levels(historical_dcii)
    
    # Step 5: Example monitoring
    print("\n" + "="*70)
    print("STEP 5: MONITORING EXAMPLES")
    print("="*70)
    
    dcii_engine.monitor_example_scenarios()
    
    # Save results
    print("\n" + "="*70)
    print("STEP 6: SAVING RESULTS")
    print("="*70)
    
    output_dir = Path("forex_dcii_results")
    output_dir.mkdir(exist_ok=True)
    
    # Save DCII series
    historical_dcii.to_csv(output_dir / "dcii_series.csv")
    
    # Save parameters
    import json
    params = {
        'beta': dcii_engine.beta,
        'gamma': dcii_engine.gamma,
        'calibration_date': datetime.now().isoformat(),
        'signals': list(dcii_engine.normalized_signals.keys()),
        'data_points': len(historical_dcii),
        'market': 'EUR/USD'
    }
    
    with open(output_dir / "parameters.json", 'w') as f:
        json.dump(params, f, indent=2)
    
    print(f"💾 Results saved to: {output_dir}/")
    print("   - dcii_series.csv: Historical DCII values")
    print("   - parameters.json: Calibration parameters")
    
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE")
    print("="*70)
    
    print(f"\n📋 Quick Usage:")
    print("-"*40)
    print("""
# Monitor current market:
current = {
    'volatility': 0.6,
    'volume_stress': 0.7,
    'spread_stress': 0.5,
    'liquidity': 0.8,
    'momentum_short': 0.4,
    'momentum_medium': 0.45
}

dcii = dcii_engine.compute_dcii_point(current)
level = dcii_engine.classify_dcii(dcii)
print(f"Market Condition: {level}")
print(f"DCII Index: {dcii:.3f}")
    """)

if __name__ == "__main__":
    main()
