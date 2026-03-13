#!/usr/bin/env python3
"""
STANDALONE PARAMETER SWEEP TESTS
Includes engine code to avoid import issues
"""
import numpy as np
import os
import sys

# ============================================================================
# INCLUDED UNIVERSAL ENGINE CORE (to avoid import issues)
# ============================================================================
class UniversalStableCore:
    def __init__(self, grid_size=(32, 32)):
        self.GRID_X, self.GRID_Y = grid_size
        self.rho = np.zeros(grid_size)
        self.E = np.zeros(grid_size)  
        self.F = np.zeros(grid_size)
        self.dt = 0.001
        self.step_count = 0
        self.stress_history = []
        self.rejected_steps = 0
        self.max_changes = []
        
        # Urban default parameters
        self.D_rho, self.D_E, self.D_F = 0.02, 0.05, 0.5
        self.delta1, self.delta2 = 1.5, 1.0
        self.alpha, self.beta, self.gamma = 1.0, 0.6, 0.8
        self.tau_E, self.tau_F = 0.8, 0.6
        self.delta, self.epsilon = 0.3, 0.2
    
    def set_urban_parameters(self):
        self.D_rho, self.D_E, self.D_F = 0.02, 0.05, 0.5
        self.delta1, self.delta2 = 1.5, 1.0
    
    def laplacian_2d(self, field):
        laplacian = np.zeros_like(field)
        laplacian[1:-1, 1:-1] = (
            field[:-2, 1:-1] + field[2:, 1:-1] + 
            field[1:-1, :-2] + field[1:-1, 2:] - 4*field[1:-1, 1:-1]
        )
        return laplacian
    
    def reaction_rho(self, rho, E, F):
        return self.delta1 * E * rho * (1 - rho) - self.delta2 * F * rho
    
    def reaction_E(self, rho, E, F):
        return (self.alpha * rho + self.beta * E * (1 - E) - 
                self.gamma * E * F - (1/self.tau_E) * E)
    
    def reaction_F(self, rho, E, F):
        return self.delta * rho**2 + self.epsilon * E - (1/self.tau_F) * F
    
    def evolve_system_adaptive(self, steps):
        successful = 0
        for _ in range(steps):
            try:
                # Simple evolution without complex adaptive stepping for testing
                drho_dt = self.D_rho * self.laplacian_2d(self.rho) + self.reaction_rho(self.rho, self.E, self.F)
                dE_dt = self.D_E * self.laplacian_2d(self.E) + self.reaction_E(self.rho, self.E, self.F)
                dF_dt = self.D_F * self.laplacian_2d(self.F) + self.reaction_F(self.rho, self.E, self.F)
                
                self.rho += self.dt * drho_dt
                self.E += self.dt * dE_dt
                self.F += self.dt * dF_dt
                
                # Basic bounds
                self.rho = np.clip(self.rho, 0, 1)
                self.E = np.clip(self.E, -1, 1)
                self.F = np.clip(self.F, 0, 1)
                
                self.step_count += 1
                successful += 1
                
                # Simple stress calculation
                stress = np.max(np.abs(drho_dt))
                self.stress_history.append(stress)
                
            except Exception:
                self.rejected_steps += 1
                break
        
        return successful
    
    def initialize_domain(self, domain):
        if domain == "urban":
            self.set_urban_parameters()
            center = (self.GRID_X//3, self.GRID_Y//3)
            x, y = np.ogrid[:self.GRID_X, :self.GRID_Y]
            dist = np.sqrt((x - center[0])**2 + (y - center[1])**2)
            self.rho = np.exp(-dist**2 / (self.GRID_X//6)**2) * 0.5
            self.E = np.ones((self.GRID_X, self.GRID_Y)) * 0.3
            self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.4

# ============================================================================
# PARAMETER SWEEP TEST
# ============================================================================
def run_parameter_sweep():
    print("🎯 STANDALONE URBAN PARAMETER SWEEP TESTS")
    print("=" * 60)
    
    test_cases = [
        (0.01, 0.05, 0.8, 2.5, 1.2, "Turing Pattern Regime"),
        (0.02, 0.1, 0.5, 1.8, 0.8, "Fast Development"),
        (0.03, 0.08, 0.6, 2.2, 1.5, "Balanced Growth"),
    ]
    
    results = []
    
    for D_rho, D_E, D_F, delta1, delta2, desc in test_cases:
        print(f"\n🔬 Testing: {desc}")
        
        engine = UniversalStableCore(grid_size=(16, 16))  # Smaller for speed
        engine.D_rho, engine.D_E, engine.D_F = D_rho, D_E, D_F
        engine.delta1, engine.delta2 = delta1, delta2
        
        engine.initialize_domain("urban")
        
        stable_steps = 0
        for step in range(100):
            if engine.evolve_system_adaptive(1):
                stable_steps += 1
        
        final_variance = np.var(engine.rho)
        pattern_formed = final_variance > 0.01
        
        status = "✅ PATTERNS" if pattern_formed else "💤 NO PATTERNS"
        print(f"  {status} - Steps: {stable_steps}, Variance: {final_variance:.4f}")
        
        results.append({
            'description': desc,
            'stable_steps': stable_steps,
            'pattern_formed': pattern_formed,
            'variance': final_variance
        })
    
    # Summary
    print(f"\n📊 SUMMARY: {sum(1 for r in results if r['pattern_formed'])}/{len(results)} formed patterns")
    return results

if __name__ == "__main__":
    run_parameter_sweep()
