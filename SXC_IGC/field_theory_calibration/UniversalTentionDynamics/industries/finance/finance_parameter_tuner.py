#!/usr/bin/env python3
"""
FINANCE PARAMETER TUNER
Find optimal parameters for market dynamics
"""
import numpy as np

def test_parameter_set(delta1, delta2, dt, description):
    """Test a specific parameter set"""
    rho = np.random.uniform(0.2, 0.7, (16,16))
    E = np.random.uniform(0.3, 0.8, (16,16))
    F = np.ones((16,16)) * 0.3
    
    D_rho, D_E, D_F = 0.08, 0.15, 0.4
    price_history = []
    
    for step in range(80):
        # Basic reactions
        reaction_rho = delta1 * E * rho * (1 - rho) - delta2 * F * rho
        reaction_E = 2.0 * rho * (1 - E) - 1.5 * F * E
        reaction_F = 1.5 * rho * E - 2.0 * F * F
        
        # Update
        rho += dt * (reaction_rho + D_rho * laplacian(rho))
        E += dt * (reaction_E + D_E * laplacian(E))
        F += dt * (reaction_F + D_F * laplacian(F))
        
        rho = np.clip(rho, 0.05, 0.95)
        E = np.clip(E, 0.1, 0.9)
        F = np.clip(F, 0.1, 0.8)
        
        price_history.append(np.mean(rho))
    
    price_change = price_history[-1] - price_history[0]
    volatility = np.std(price_history)
    
    return price_change, volatility

def laplacian(field):
    lap = np.zeros_like(field)
    lap[1:-1,1:-1] = (
        field[:-2,1:-1] + field[2:,1:-1] +
        field[1:-1,:-2] + field[1:-1,2:] - 4*field[1:-1,1:-1]
    )
    return lap

print("🎯 FINANCE PARAMETER TUNING")
print("Testing different parameter combinations")
print("="*50)

# Test different parameter sets
parameter_sets = [
    (3.0, 1.5, 0.0005, "Moderate"),
    (5.0, 2.0, 0.001, "Aggressive"),
    (8.0, 3.0, 0.002, "Very Aggressive"),
    (10.0, 4.0, 0.003, "Extreme"),
    (12.0, 5.0, 0.004, "Ultra Aggressive")
]

best_score = 0
best_params = None

for delta1, delta2, dt, desc in parameter_sets:
    total_change = 0
    total_volatility = 0
    runs = 3
    
    for run in range(runs):
        change, volatility = test_parameter_set(delta1, delta2, dt, desc)
        total_change += abs(change)
        total_volatility += volatility
    
    avg_change = total_change / runs
    avg_volatility = total_volatility / runs
    
    # Score: we want both good movement and reasonable volatility
    score = avg_change * (1.0 / (avg_volatility + 0.1))
    
    print(f"\n{desc} Parameters:")
    print(f"  delta1={delta1}, delta2={delta2}, dt={dt}")
    print(f"  Avg price change: {avg_change:.4f}")
    print(f"  Avg volatility: {avg_volatility:.4f}")
    print(f"  Score: {score:.4f}")
    
    if score > best_score and avg_volatility < 0.2:
        best_score = score
        best_params = (delta1, delta2, dt, desc, avg_change, avg_volatility)

if best_params:
    delta1, delta2, dt, desc, change, vol = best_params
    print(f"\n🎯 BEST PARAMETERS: {desc}")
    print(f"   delta1={delta1}, delta2={delta2}, dt={dt}")
    print(f"   Expected change: {change:.4f}, Volatility: {vol:.4f}")
else:
    print("\n❌ No optimal parameters found - all too volatile")
