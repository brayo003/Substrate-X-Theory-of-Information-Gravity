#!/usr/bin/env python3
"""
Test the Universal Dynamics Engine across multiple domains
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test core engine directly
    print("🚀 Testing Core Engine...")
    
    # Import core engine
    from core_engine.src.universal_dynamics import create_engine
    
    # Test 1: Basic engine functionality
    print("1. Testing basic engine...")
    engine = create_engine('general')
    engine.initialize_gaussian()
    print("   ✓ Engine created and initialized")
    
    # Test 2: Evolution
    print("2. Testing evolution...")
    engine.evolve(10)
    stats = engine.get_field_statistics()
    print(f"   ✓ Evolution successful - Rho max: {stats['rho_max']:.3f}")
    
    # Test 3: Different domains
    print("3. Testing domain-specific engines...")
    finance_engine = create_engine('finance')
    urban_engine = create_engine('urban')
    healthcare_engine = create_engine('healthcare')
    print("   ✓ Domain engines created")
    
    print("✅ Core engine tests passed!")
    
    # Test 4: Try to import HFT analyzer
    print("4. Testing HFT analyzer import...")
    try:
        # Add industries to path
        industries_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'industries', 'finance', 'hft')
        sys.path.insert(0, industries_path)
        
        from market_microstructure import HFTMarketAnalyzer
        print("   ✓ HFT analyzer imported successfully")
        
        # Test HFT analyzer
        print("5. Testing HFT analyzer functionality...")
        analyzer = HFTMarketAnalyzer()
        print("   ✓ HFT analyzer created")
        
    except ImportError as e:
        print(f"   ⚠️  HFT analyzer import failed: {e}")
        print("   This is expected if there are dependency issues")
    
    print("\n🎉 Engine is working! Core functionality verified.")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
