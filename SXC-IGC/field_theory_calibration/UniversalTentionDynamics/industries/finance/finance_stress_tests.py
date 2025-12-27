#!/usr/bin/env python3
"""
FINANCE STRESS TESTS
Market crash scenarios and recovery patterns
"""
import numpy as np

class FinanceStressEngine:
    def __init__(self, grid_size=(32,32)):
        self.rho = np.zeros(grid_size)
        self.E = np.zeros(grid_size)
        self.F = np.zeros(grid_size)
        self.dt = 0.00005
        self.stress_history = []
        self.recovery_history = []

        # Conservative parameters for stress tests
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
            
            stress = np.mean(np.abs(self.rho))
            self.stress_history.append(stress)
            
            # Track recovery (how close to pre-shock state)
            recovery = 1.0 - stress
            self.recovery_history.append(recovery)

    def laplacian_2d(self, field):
        lap = np.zeros_like(field)
        lap[1:-1,1:-1] = (
            field[:-2,1:-1] + field[2:,1:-1] +
            field[1:-1,:-2] + field[1:-1,2:] - 4*field[1:-1,1:-1]
        )
        return lap

    def initialize_normal_market(self):
        """Initialize normal market conditions"""
        self.E = np.random.uniform(0.3, 0.7, self.rho.shape)
        self.rho = np.random.uniform(0.2, 0.5, self.rho.shape)
        self.F = np.ones(self.rho.shape) * 0.3
        return np.mean(self.rho)

print("🚨 FINANCE STRESS TESTS")
print("Market crash scenarios and recovery analysis")
print("="*50)

stress_scenarios = [
    {
        'name': 'PRICE SPIKE',
        'apply_shock': lambda engine: setattr(engine, 'rho', np.clip(engine.rho + 0.8, 0, 1)),
        'description': 'Sudden concentrated buying pressure'
    },
    {
        'name': 'MARKET CRASH', 
        'apply_shock': lambda engine: setattr(engine, 'E', engine.E * 0.2),  # 80% loss of opportunities
        'description': 'Massive loss of market confidence'
    },
    {
        'name': 'REGULATORY INTERVENTION',
        'apply_shock': lambda engine: setattr(engine, 'F', np.clip(engine.F + 0.5, 0, 1)),
        'description': 'Sudden increase in trading constraints'
    },
    {
        'name': 'FLASH CRASH',
        'apply_shock': lambda engine: setattr(engine, 'rho', engine.rho * 0.3),  # 70% price drop
        'description': 'Rapid automated selling'
    }
]

for scenario in stress_scenarios:
    print(f"\n💥 Testing: {scenario['name']}")
    print(f"   {scenario['description']}")
    
    engine = FinanceStressEngine()
    initial_density = engine.initialize_normal_market()
    
    # Run normal market for 50 steps
    engine.evolve(50)
    pre_shock_density = np.mean(engine.rho)
    
    # Apply shock
    scenario['apply_shock'](engine)
    shock_density = np.mean(engine.rho)
    
    # Run recovery for 100 steps
    engine.evolve(100)
    recovery_density = np.mean(engine.rho)
    
    # Calculate metrics
    shock_magnitude = abs(shock_density - pre_shock_density)
    recovery_rate = (recovery_density - shock_density) / (pre_shock_density - shock_density + 1e-8)
    max_stress = max(engine.stress_history)
    final_recovery = engine.recovery_history[-1]
    
    print(f"   Pre-shock density: {pre_shock_density:.3f}")
    print(f"   Shock density: {shock_density:.3f}")
    print(f"   Recovery density: {recovery_density:.3f}")
    print(f"   Shock magnitude: {shock_magnitude:.3f}")
    print(f"   Recovery rate: {recovery_rate:+.3f}")
    print(f"   Max stress: {max_stress:.3f}")
    print(f"   Final recovery: {final_recovery:.3f}")
    
    # Assessment
    if recovery_rate > 0.5 and max_stress < 0.7:
        assessment = "✅ RESILIENT"
    elif recovery_rate > 0.2:
        assessment = "⚠️  MODERATE RECOVERY"
    else:
        assessment = "❌ POOR RECOVERY"
    
    print(f"   ASSESSMENT: {assessment}")

print(f"\n📈 STRESS TESTING COMPLETE")
print("All market shock scenarios simulated and analyzed")
