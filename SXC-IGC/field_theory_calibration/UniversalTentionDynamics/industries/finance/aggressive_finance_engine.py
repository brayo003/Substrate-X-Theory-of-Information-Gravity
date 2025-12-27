#!/usr/bin/env python3
"""
AGGRESSIVE FINANCE ENGINE
Strong market dynamics with active volatility
"""
import numpy as np

class AggressiveFinanceEngine:
    def __init__(self, grid_size=(32,32)):
        self.rho = np.zeros(grid_size)  # Asset prices
        self.E = np.zeros(grid_size)    # Market opportunities  
        self.F = np.zeros(grid_size)    # Regulatory constraints
        self.dt = 0.001  # Much larger time step for faster dynamics
        self.stress_history = []
        self.price_history = []
        self.recovery_count = 0

        # Very aggressive parameters for strong dynamics
        self.delta1, self.delta2 = 5.0, 2.0  # Much stronger reactions
        self.D_rho, self.D_E, self.D_F = 0.1, 0.2, 0.6  # High diffusion
        self.recovery_strength = 0.1  # Strong recovery

    def evolve(self, steps=1):
        for _ in range(steps):
            # Calculate diffusion
            lap_rho = self.laplacian_2d(self.rho)
            lap_E = self.laplacian_2d(self.E)
            lap_F = self.laplacian_2d(self.F)
            
            # Much stronger reactions with market momentum
            reaction_rho = (
                self.delta1 * self.E * self.rho * (1 - self.rho) - 
                self.delta2 * self.F * self.rho +
                0.3 * np.random.normal(0, 0.1, self.rho.shape)  # Random market noise
            )
            
            reaction_E = (
                2.0 * self.rho * (1 - self.E) - 
                1.5 * self.F * self.E +
                0.5 * (0.7 - self.E)  # Strong mean-reversion
            )
            
            reaction_F = (
                1.5 * self.rho * self.E - 
                2.0 * self.F * self.F +
                0.2 * (0.4 - self.F)  # Dynamic constraints
            )
            
            # Update fields with momentum
            self.rho += self.dt * (reaction_rho + self.D_rho * lap_rho)
            self.E += self.dt * (reaction_E + self.D_E * lap_E) 
            self.F += self.dt * (reaction_F + self.D_F * lap_F)
            
            # Enforce bounds but allow more extremes
            self.rho = np.clip(self.rho, 0.05, 0.95)
            self.E = np.clip(self.E, 0.1, 0.9)
            self.F = np.clip(self.F, 0.1, 0.8)
            
            # Track metrics
            current_price = np.mean(self.rho)
            stress = np.std(self.rho) * 2  # Amplified stress measure
            self.stress_history.append(stress)
            self.price_history.append(current_price)
            
            # Active recovery when stress is moderate
            if stress > 0.25:
                self.activate_recovery()

    def activate_recovery(self):
        """Strong recovery mechanisms"""
        self.recovery_count += 1
        # Boost market confidence
        self.E = np.clip(self.E + 0.02 * (0.7 - self.E), 0.1, 0.9)
        # Normalize constraints
        self.F = np.clip(self.F + 0.01 * (0.4 - self.F), 0.1, 0.8)
        # Gentle price stabilization
        if np.std(self.rho) > 0.2:
            self.rho = self.rho * 0.99 + np.mean(self.rho) * 0.01

    def laplacian_2d(self, field):
        lap = np.zeros_like(field)
        lap[1:-1,1:-1] = (
            field[:-2,1:-1] + field[2:,1:-1] +
            field[1:-1,:-2] + field[1:-1,2:] - 4*field[1:-1,1:-1]
        )
        return lap

    def initialize_volatile_market(self):
        """Initialize with highly dynamic market conditions"""
        # Create multiple market centers with different characteristics
        centers = [(8,8), (8,24), (24,8), (24,24), (16,16)]
        for i, (cx, cy) in enumerate(centers):
            x = np.arange(32)
            y = np.arange(32)
            X, Y = np.meshgrid(x, y, indexing='ij')
            dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
            
            if i % 2 == 0:
                # Bullish centers
                self.rho += np.exp(-dist**2 / 20) * 0.6
                self.E += np.exp(-dist**2 / 25) * 0.7
            else:
                # Bearish centers  
                self.rho += np.exp(-dist**2 / 20) * 0.3
                self.E += np.exp(-dist**2 / 25) * 0.4
        
        self.rho = np.clip(self.rho, 0.1, 0.9)
        self.E = np.clip(self.E, 0.2, 0.8)
        self.F = np.random.uniform(0.2, 0.5, self.rho.shape)

# Test the aggressive engine
print("🚀 TESTING AGGRESSIVE FINANCE ENGINE")
print("="*45)

engine = AggressiveFinanceEngine()
engine.initialize_volatile_market()

print("Initial conditions:")
print(f"  Price range: {np.min(engine.rho):.3f} - {np.max(engine.rho):.3f}")
print(f"  Opportunity range: {np.min(engine.E):.3f} - {np.max(engine.E):.3f}")
print(f"  Initial avg price: {np.mean(engine.rho):.3f}")

# Run simulation with progress tracking
print("\nSimulation progress:")
for step in range(100):
    engine.evolve(1)
    if step % 20 == 0:
        current_price = engine.price_history[-1]
        stress = engine.stress_history[-1]
        print(f"  Step {step}: Price={current_price:.3f}, Stress={stress:.3f}")

# Analysis
initial_price = engine.price_history[0]
final_price = engine.price_history[-1]
price_change = final_price - initial_price
max_stress = max(engine.stress_history)
price_volatility = np.std(engine.price_history)

print(f"\n📊 RESULTS:")
print(f"  Price change: {initial_price:.3f} → {final_price:.3f} ({price_change:+.3f})")
print(f"  Max stress: {max_stress:.3f}")
print(f"  Price volatility: {price_volatility:.4f}")
print(f"  Recovery activations: {engine.recovery_count}")

# Assessment
significant_movement = abs(price_change) > 0.05
moderate_stress = max_stress < 0.8
good_volatility = price_volatility > 0.01

if significant_movement and moderate_stress:
    print("✅ AGGRESSIVE ENGINE: EXCELLENT DYNAMICS!")
elif significant_movement:
    print("⚠️  Good dynamics but high stress")
else:
    print("❌ Still too conservative - needs more aggression")

# Show price evolution
if len(engine.price_history) > 10:
    print(f"\n📈 Price evolution sample:")
    sample_prices = engine.price_history[::20]
    for i, price in enumerate(sample_prices):
        print(f"  Step {i*20}: {price:.3f}")
