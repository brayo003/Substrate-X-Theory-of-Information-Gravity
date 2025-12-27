"""
Test Functions and Examples
"""

from pathlib import Path
from datetime import datetime

def test_real_time_monitoring(module=None):
    """Test the real-time monitoring with example data."""
    print("🧪 TESTING REAL-TIME MONITORING")
    print("-"*70)
    
    # Create and calibrate a module if not provided
    if module is None:
        from finance_module import FinanceDCIIModule
        module = FinanceDCIIModule()
        module.define_domain()
        module.define_signals()
        module.normalize_signals()
        module.define_target_states()
        module.classify_stress_taxonomy()
        module.calibrate_coefficients()
    
    if not module.calibration_result or not module.calibration_result.is_valid:
        print("❌ Calibration failed, cannot test monitoring")
        return None
    
    # Test current market conditions (example values)
    current_market = {
        'vix': 35.5,           # Elevated VIX
        'equity_returns': -0.02, # Negative returns
        'volume_ratio': 1.8,   # High volume
        'bid_ask_spread': 0.05, # Wide spreads
        'put_call_ratio': 1.2   # High put/call ratio
    }
    
    result = module.monitor_real_time(current_market)
    
    print(f"📊 DCII Index: {result['dcii_index']:.3f}")
    print(f"🚨 Stress Level: {result['stress_level']}")
    print(f"🎯 Top Contributors:")
    for signal, contribution in result['contributing_factors'].items():
        print(f"    • {signal}: {contribution:.3f}")
    print(f"💡 Recommendation: {result['recommendation']}")
    print(f"⏰ Time: {result['timestamp']}")
    print("-"*70)
    
    return result

def print_quick_start_guide():
    """Print a quick start guide for using the module."""
    print("\n" + "="*70)
    print("QUICK START GUIDE")
    print("="*70)
    print("""
To use the DCII Framework with your own data:

1. Import the module:
   from finance_module import FinanceDCIIModule

2. Create your instance:
   my_module = FinanceDCIIModule(name="My_Market_DCII")

3. Load YOUR real data:
   import pandas as pd
   dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='B')
   my_module.signals = {
       'your_signal_1': pd.Series(your_data_1, index=dates),
       'your_signal_2': pd.Series(your_data_2, index=dates),
       # Add all your signals...
   }

4. Run the pipeline:
   my_module.normalize_signals()
   my_module.define_target_states()  # Adjust targets for your domain
   my_module.calibrate_coefficients()

5. Monitor real-time:
   current_data = {'signal_1': value_1, 'signal_2': value_2, ...}
   alert = my_module.monitor_real_time(current_data)
   print(f"Stress Level: {alert['stress_level']}")
   print(f"Recommendation: {alert['recommendation']}")

6. Save your calibrated module:
   results = my_module.run_full_pipeline(output_dir=Path("./my_output"))
    """)
