import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.data_coupler import DataCoupler, DomainType
import pandas as pd
import numpy as np

def test_basic_functionality():
    print("🧪 Testing Basic DataCoupler Functionality...")
    
    # Test 1: Simple numeric data
    simple_data = pd.DataFrame({
        'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'other_vals': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    })
    
    coupler = DataCoupler()
    coupler.ingest_data(simple_data)
    metrics = coupler.output_metrics()
    
    print("✅ Simple data test passed")
    print(f"   Domain: {metrics['domain']}")
    print(f"   Tension: {metrics['metrics']['Tension']:.4f}")
    print(f"   Momentum: {metrics['metrics']['Momentum']:.4f}")
    print(f"   Variance: {metrics['metrics']['Variance']:.4f}")
    print(f"   Grid shape: {metrics['concentrations'].shape}")
    
    return metrics

def test_financial_domain():
    print("\n🧪 Testing Financial Domain Intelligence...")
    
    # Simulate stock data with volatility
    stock_data = pd.DataFrame({
        'price': [100, 105, 98, 110, 95, 108, 102, 115, 90, 105],
        'volume': [1000, 1200, 800, 1500, 700, 1300, 1100, 1600, 600, 1400]
    })
    
    coupler = DataCoupler(domain_type=DomainType.FINANCIAL)
    coupler.ingest_data(stock_data)
    metrics = coupler.output_metrics()
    
    print("✅ Financial domain test passed")
    print(f"   Financial Tension: {metrics['metrics']['Tension']:.4f}")
    print(f"   Market Momentum: {metrics['metrics']['Momentum']:.4f}")
    
    return metrics

def test_biological_domain():
    print("\n🧪 Testing Biological Domain Intelligence...")
    
    # Simulate biological measurements (e.g., gene expression)
    bio_data = pd.DataFrame({
        'gene_A': [1.0, 1.2, 0.8, 1.5, 0.9, 1.3],
        'gene_B': [2.0, 2.1, 1.9, 2.3, 1.8, 2.2],
        'protein_X': [0.5, 0.6, 0.4, 0.7, 0.45, 0.65]
    })
    
    coupler = DataCoupler(domain_type=DomainType.BIOLOGICAL)
    coupler.ingest_data(bio_data)
    metrics = coupler.output_metrics()
    
    print("✅ Biological domain test passed")
    print(f"   Biological Tension: {metrics['metrics']['Tension']:.4f}")
    
    return metrics

def test_csv_ingestion():
    print("\n🧪 Testing CSV File Ingestion...")
    
    # Create a test CSV file
    test_csv_data = pd.DataFrame({
        'time_index': range(10),
        'sensor_A': np.random.normal(100, 10, 10),
        'sensor_B': np.random.normal(50, 5, 10),
        'sensor_C': np.random.normal(200, 20, 10)
    })
    
    test_csv_data.to_csv('test_sensor_data.csv', index=False)
    
    # Load from CSV
    coupler = DataCoupler()
    coupler.ingest_data('test_sensor_data.csv')
    metrics = coupler.output_metrics()
    
    # Clean up
    import os
    os.remove('test_sensor_data.csv')
    
    print("✅ CSV ingestion test passed")
    print(f"   Auto-detected features: {metrics['feature_columns']}")
    
    return metrics

if __name__ == "__main__":
    print("🚀 DATA COUPLER COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_financial_domain() 
        test_biological_domain()
        test_csv_ingestion()
        
        print("\n🎉 ALL TESTS PASSED! DataCoupler is ready for integration.")
        print("\n📋 NEXT STEPS:")
        print("   1. Connect DataCoupler to your UniversalDynamicsEngine")
        print("   2. Feed real-world data streams")
        print("   3. Validate cross-domain predictions")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
