import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    from universal_dynamics_engine.data_coupler import DataCoupler, DomainType
    print("✅ SUCCESS: DataCoupler imported!")
    
    # Quick functionality test
    import pandas as pd
    data = pd.DataFrame({'test': [1,2,3,4,5]})
    coupler = DataCoupler()
    coupler.ingest_data(data)
    result = coupler.output_metrics()
    print("✅ Functionality test passed:", result.keys())
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
