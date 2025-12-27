#!/usr/bin/env python3
"""
OPTIMIZED FINANCE ENGINE
Enhanced market dynamics with better shock recovery
"""
import numpy as np

class OptimizedFinanceEngine:
    def __init__(self, grid_size=(32,32)):
        self.rho = np.zeros(grid_size)  # Asset prices
        self.E = np.zeros(grid_size)    # Market opportunities  
        self.F = np.zeros(grid_size)    # Regulatory constraints
        self.dt = 0.0001  # Slightly larger time step
        self.stress_history = []
        self.recovery_active = False

        # Enhanced parameters for better dynamics
        self.delta1, self.delta2 = 3.0, 1.5  # Stronger reactions
        self.D_rho, self.D_E, self.D_F = 0.08, 0.15, 0.4  # More diffusion
        self.recovery_rate = 0.05  # Active recovery mechanism

    def evolve(self, steps=1):
        for _ in range(steps):
            # Calculate diffusion
            lap_rho = self.laplacian_2d(self.rho)
            lap_E = self.laplacian_2d(self.E)
            lap_F = self.laplacian_2d(self.F)
            
            # Enhanced reactions with recovery mechanisms
            reaction_rho = (
                self.delta1 * self.E * self.rho * (1 - self.rho) - 
                self.delta2 * self.F * self.rho
            )
            
            reaction_E = (
                self.delta1 * self.rho * (1 - self.E) - 
                self.delta2 * self.F * self.E +
                self.recovery_rate * (0.5 - self.E)  # Mean-reversion
            )
            
            reaction_F = (
                self.delta2 * self.rho * self.E - 
                self.delta1 * self.F * self.F +
                0.1 * (0.3 - self.F)  # Regulatory normalization
            )
            
            # Update fields
            self.rho += self.dt * (reaction_rho + self.D_rho * lap_rho)
            self.E += self.dt * (reaction_E + self.D_E * lap_E) 
            self.F += self.dt * (reaction_F + self.D_F * lap_F)
            
            # Enforce bounds with smooth clipping
            self.rho = np.clip(self.rho, 0.01, 0.99)  # Avoid extremes
            self.E = np.clip(self.E, 0.05, 0.95)
            self.F = np.clip(self.F, 0.05, 0.95)
            
            # Track stress (price volatility)
            stress = np.std(self.rho)
            self.stress_history.append(stress)
            
            # Activate recovery if stress is high
            if stress > 0.3:
                self.recovery_active = True
                self.enhance_recovery()
            elif stress < 0.1:
                self.recovery_active = False

    def enhance_recovery(self):
        """Active recovery mechanisms during high stress"""
        # Gradually restore market confidence
        self.E = np.clip(self.E + 0.01 * (0.6 - self.E), 0.05, 0.95)
        # Normalize constraints after shocks
        self.F = np.clip(self.F + 0.005 * (0.3 - self.F), 0.05, 0.95)

    def laplacian_2d(self, field):
        lap = np.zeros_like(field)
        lap[1:-1,1:-1] = (
            field[:-2,1:-1] + field[2:,1:-1] +
            field[1:-1,:-2] + field[1:-1,2:] - 4*field[1:-1,1:-1]
        )
        return lap

    def initialize_volatile_market(self):
        """Initialize with more dynamic market conditions"""
        self.E = np.random.uniform(0.3, 0.8, self.rho.shape)
        self.rho = np.random.uniform(0.2, 0.7, self.rho.shape)
        self.F = np.ones(self.rho.shape) * 0.3

# Test the optimized engine
print("🚀 TESTING OPTIMIZED FINANCE ENGINE")
print("="*40)

engine = OptimizedFinanceEngine()
engine.initialize_volatile_market()

print("Initial conditions:")
print(f"  Price range: {np.min(engine.rho):.3f} - {np.max(engine.rho):.3f}")
print(f"  Opportunity range: {np.min(engine.E):.3f} - {np.max(engine.E):.3f}")

# Run simulation
price_history = []
for step in range(100):
    engine.evolve(1)
    avg_price = np.mean(engine.rho)
    price_history.append(avg_price)
    if step % 25 == 0:
        stress = engine.stress_history[-1] if engine.stress_history else 0
        print(f"Step {step}: Price={avg_price:.3f}, Stress={stress:.3f}")

price_change = price_history[-1] - price_history[0]
max_stress = max(engine.stress_history) if engine.stress_history else 0

print(f"\nResults:")
print(f"  Price change: {price_change:+.3f}")
print(f"  Max stress: {max_stress:.3f}")
print(f"  Recovery active: {engine.recovery_active}")

if abs(price_change) > 0.02 and max_stress < 0.5:
    print("✅ OPTIMIZED ENGINE: GOOD DYNAMICS!")
else:
    print("⚠️  Further tuning needed")
