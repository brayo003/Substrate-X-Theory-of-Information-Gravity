#!/usr/bin/env python3
"""
FINANCE PARAMETER SWEEP
Validate engine under multiple volatility and diffusion scenarios
"""
import numpy as np

# Include minimal embedded finance engine
class FinanceEngine:
    def __init__(self, grid_size=(32,32)):
        self.rho = np.zeros(grid_size)
        self.E = np.zeros(grid_size)
        self.F = np.zeros(grid_size)
        self.dt = 0.00005
        self.stress_history = []

        # Default finance parameters
        self.delta1, self.delta2 = 2.0, 1.0
        self.tau_E, self.tau_F, self.tau_rho = 0.0002, 0.001, 0.0005
        self.D_rho, self.D_E, self.D_F = 0.05, 0.1, 0.3

    def evolve(self, steps=1):
        # Minimal evolution: simple diffusion + reaction
        for _ in range(steps):
            lap_rho = self.laplacian_2d(self.rho)
            lap_E = self.laplacian_2d(self.E)
            lap_F = self.laplacian_2d(self.F)
            
            # Reaction-diffusion for financial dynamics
            self.rho += self.dt * (
                self.delta1 * self.E * self.rho * (1 - self.rho) - 
                self.delta2 * self.F * self.rho + 
                self.D_rho * lap_rho
            )
            self.E += self.dt * (
                self.delta1 * self.rho * (1 - self.E) - 
                self.delta2 * self.F * self.E + 
                self.D_E * lap_E
            )
            self.F += self.dt * (
                self.delta2 * self.rho * self.E - 
                self.delta1 * self.F * self.F + 
                self.D_F * lap_F
            )
            
            # Clip to maintain stability
            self.rho = np.clip(self.rho, 0, 1)
            self.E = np.clip(self.E, 0, 1)
            self.F = np.clip(self.F, 0, 1)
            
            self.stress_history.append(np.mean(np.abs(self.rho)))

    def laplacian_2d(self, field):
        lap = np.zeros_like(field)
        lap[1:-1,1:-1] = (
            field[:-2,1:-1] + field[2:,1:-1] +
            field[1:-1,:-2] + field[1:-1,2:] - 4*field[1:-1,1:-1]
        )
        return lap

    def initialize_market(self):
        """Initialize with market-like conditions"""
        # Random market opportunities
        self.E = np.random.uniform(0, 0.5, self.rho.shape)
        # Some initial trading activity
        self.rho = np.random.uniform(0, 0.3, self.rho.shape)
        # Moderate constraints
        self.F = np.ones(self.rho.shape) * 0.2

print("💹 FINANCE PARAMETER SWEEP")
print("Testing volatility regimes and stability")
print("="*50)

# Run parameter sweep
param_sets = [
    {'delta1': 2.0, 'delta2': 1.0, 'desc': 'Normal Volatility'},
    {'delta1': 2.5, 'delta2': 1.2, 'desc': 'High Volatility'},
    {'delta1': 1.8, 'delta2': 0.8, 'desc': 'Low Volatility'},
    {'delta1': 3.0, 'delta2': 1.5, 'desc': 'Extreme Volatility'},
    {'delta1': 1.5, 'delta2': 0.5, 'desc': 'Calm Markets'}
]

results = []

for i, p in enumerate(param_sets):
    print(f"\n🔧 Testing {p['desc']}...")
    eng = FinanceEngine()
    eng.delta1, eng.delta2 = p['delta1'], p['delta2']
    eng.initialize_market()
    
    initial_variance = np.var(eng.rho)
    eng.evolve(steps=100)
    
    max_stress = max(eng.stress_history)
    final_variance = np.var(eng.rho)
    variance_change = final_variance - initial_variance
    
    # Stability assessment
    if max_stress < 0.3:
        stability = "✅ STABLE"
    elif max_stress < 0.6:
        stability = "⚠️  MODERATE"
    else:
        stability = "❌ UNSTABLE"
    
    results.append({
        'params': p,
        'max_stress': max_stress,
        'variance_change': variance_change,
        'stability': stability
    })
    
    print(f"   Max Stress: {max_stress:.3f} - {stability}")
    print(f"   Variance Change: {variance_change:+.4f}")

print(f"\n📊 PARAMETER SWEEP SUMMARY:")
print("="*50)
for result in results:
    p = result['params']
    print(f"   {p['desc']}: delta1={p['delta1']}, delta2={p['delta2']}")
    print(f"     → {result['stability']} (Stress: {result['max_stress']:.3f})")

# Overall assessment
stable_count = sum(1 for r in results if r['stability'] == "✅ STABLE")
total_count = len(results)
print(f"\n🎯 STABILITY SCORE: {stable_count}/{total_count} parameter sets stable")
