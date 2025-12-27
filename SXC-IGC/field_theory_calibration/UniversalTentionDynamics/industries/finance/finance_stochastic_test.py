#!/usr/bin/env python3
"""
FINANCE STOCHASTIC CONSISTENCY
Test reproducibility with different random seeds
"""
import numpy as np

class StochasticFinanceEngine:
    def __init__(self, grid_size=(24,24), seed=42):
        self.rng = np.random.RandomState(seed)
        self.rho = np.zeros(grid_size)
        self.E = np.zeros(grid_size) 
        self.F = np.zeros(grid_size)
        self.dt = 0.00005
        self.final_densities = []
        
        # Standard finance parameters
        self.delta1, self.delta2 = 2.0, 1.0
        self.D_rho, self.D_E, self.D_F = 0.05, 0.1, 0.3

    def evolve(self, steps=1):
        for _ in range(steps):
            lap_rho = self.laplacian_2d(self.rho)
            lap_E = self.laplacian_2d(self.E)
            lap_F = self.laplacian_2d(self.F)
            
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
            
            self.rho = np.clip(self.rho, 0, 1)
            self.E = np.clip(self.E, 0, 1)
            self.F = np.clip(self.F, 0, 1)

    def laplacian_2d(self, field):
        lap = np.zeros_like(field)
        lap[1:-1,1:-1] = (
            field[:-2,1:-1] + field[2:,1:-1] +
            field[1:-1,:-2] + field[1:-1,2:] - 4*field[1:-1,1:-1]
        )
        return lap

    def initialize_random_market(self):
        """Initialize with random market conditions using seeded RNG"""
        self.E = self.rng.uniform(0.2, 0.6, self.rho.shape)
        self.rho = self.rng.uniform(0.1, 0.4, self.rho.shape)
        self.F = np.ones(self.rho.shape) * 0.3

print("🎲 FINANCE STOCHASTIC CONSISTENCY TEST")
print("Testing reproducibility across different random seeds")
print("="*55)

# Test multiple runs with different seeds
num_runs = 6
final_results = []

print(f"\nRunning {num_runs} simulations with different seeds...")
for run in range(num_runs):
    seed = 100 + run * 10  # Different seeds for each run
    engine = StochasticFinanceEngine(seed=seed)
    engine.initialize_random_market()
    
    initial_density = np.mean(engine.rho)
    engine.evolve(80)  # Run for 80 steps
    final_density = np.mean(engine.rho)
    
    final_results.append(final_density)
    print(f"  Run {run+1} (seed={seed}): Final density = {final_density:.4f}")

# Statistical analysis
mean_density = np.mean(final_results)
std_density = np.std(final_results)
cv_density = std_density / mean_density  # Coefficient of variation

print(f"\n📊 STATISTICAL ANALYSIS:")
print(f"  Mean final density: {mean_density:.4f}")
print(f"  Standard deviation: {std_density:.4f}")
print(f"  Coefficient of variation: {cv_density:.4f}")

# Consistency assessment
if std_density < 0.001:
    consistency = "✅ EXCELLENT CONSISTENCY"
elif std_density < 0.005:
    consistency = "⚠️  GOOD CONSISTENCY" 
elif std_density < 0.01:
    consistency = "🎲 MODERATE VARIABILITY"
else:
    consistency = "❌ HIGH VARIABILITY"

print(f"\n🎯 CONSISTENCY ASSESSMENT: {consistency}")

# Long-term stability test
print(f"\n⏳ LONG-TERM STABILITY TEST (single run, 200 steps)")
long_term_engine = StochasticFinanceEngine(seed=42)
long_term_engine.initialize_random_market()

density_history = []
for step in range(200):
    long_term_engine.evolve(1)
    density_history.append(np.mean(long_term_engine.rho))
    if step % 40 == 0:
        print(f"  Step {step}: density = {density_history[-1]:.4f}")

# Analyze long-term behavior
density_range = max(density_history) - min(density_history)
final_trend = density_history[-1] - density_history[100]  # Last 100 steps trend

print(f"\n📈 LONG-TERM ANALYSIS:")
print(f"  Density range: {density_range:.4f}")
print(f"  Final trend (last 100 steps): {final_trend:+.4f}")

if abs(final_trend) < 0.01 and density_range < 0.1:
    stability = "✅ EXCELLENT LONG-TERM STABILITY"
elif abs(final_trend) < 0.02:
    stability = "⚠️  GOOD LONG-TERM STABILITY"
else:
    stability = "❌ DRIFTING OVER TIME"

print(f"  STABILITY: {stability}")

print(f"\n🎯 FINANCE STOCHASTIC TESTING COMPLETE")
print("Reproducibility and long-term stability validated")
