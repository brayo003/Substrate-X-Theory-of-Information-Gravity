#!/usr/bin/env python3
"""
Exploratory reaction–diffusion simulation with domain-themed presets
"""
import numpy as np
from typing import Tuple, Dict, Any

class UniversalCoreLanguage:
    """Core mathematical language for universal dynamics"""
    
    def __init__(self, grid_size: Tuple[int, int] = (64, 64)):
        self.GRID_X, self.GRID_Y = grid_size
        
        # ===== FIELD DECLARATIONS =====
        self.rho = np.zeros(grid_size)  # Density field (primary state)
        self.E = np.zeros(grid_size)    # Excitation field  
        self.F = np.zeros(grid_size)    # Inhibition field
        
        # ===== UNIVERSAL PARAMETERS =====
        self.tau_rho = 0.1    # Density time constant
        self.tau_E = 0.08     # Excitation time constant  
        self.tau_F = 0.12     # Inhibition time constant
        self.M = 5000         # Stiffness factor
        self.delta1 = 2.0     # Excitation coupling
        self.delta2 = 1.5     # Inhibition coupling
        self.kappa = 1.0      # Field coupling constant
        
        self.step_count = 0
        self.stress_history = []
    
    # ===== PHYSICS KERNELS =====
    def diffusion(self, A: np.ndarray, tau: float) -> None:
        """∇²A diffusion operator - Universal spatial spread"""
        laplacian = np.zeros_like(A)
        laplacian[1:-1, 1:-1] = (A[:-2, 1:-1] + A[2:, 1:-1] + 
                                A[1:-1, :-2] + A[1:-1, 2:] - 4*A[1:-1, 1:-1])
        A += tau * laplacian
    
    def reaction(self, rho: np.ndarray, E: np.ndarray, F: np.ndarray) -> None:
        """G(rho,E) - L(rho,F) reaction terms - Universal local interactions"""
        growth = self.delta1 * E * rho * (1 - rho)  # Logistic growth with excitation
        loss = self.delta2 * F * rho                # Linear loss with inhibition
        rho += growth - loss
    
    def field_coupling(self, A: np.ndarray, B: np.ndarray, coupling: float) -> None:
        """Field interaction: A influences B - Universal field coupling"""
        B += coupling * A * (1 - B)
    
    def apply_damping(self, A: np.ndarray, M: float, dt: float) -> None:
        """Universal damping: prevents numerical explosions"""
        damping = M * A * (A - 1) * (A - 1)  # Cubic damping term
        A -= dt * damping
    
    def enforce_bounds(self, A: np.ndarray, min_val: float, max_val: float) -> None:
        """Hard physics constraints - Universal bounds enforcement"""
        np.clip(A, min_val, max_val, out=A)
    
    def compute_stress(self) -> float:
        """System stress metric - Universal stability measure"""
        grad_x = np.diff(self.rho, axis=0)
        grad_y = np.diff(self.rho, axis=1)
        # Pad gradients to original shape
        grad_x = np.pad(grad_x, ((0,1),(0,0)), mode='edge')
        grad_y = np.pad(grad_y, ((0,0),(0,1)), mode='edge')
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        return np.max(gradient_magnitude)
    
    def emergency_brake(self) -> None:
        """Universal stability enforcement"""
        self.M *= 1.5     # Increase stiffness
        self.delta1 *= 0.7    # Reduce excitation  
        self.tau_rho *= 0.8   # Slow down dynamics
        print("🚨 EMERGENCY BRAKE: Stability enforced")
    
    # ===== CORE EVOLUTION EQUATION =====
    def evolve_system(self, steps: int = 1, dt: float = 0.001) -> None:
        """Main universal equation: ∂rho/∂t = D∇²rho + G(rho,E) - L(rho,F)"""
        for step in range(steps):
            self.step_count += 1
            
            # Step 1: Diffusion term (spatial spread)
            self.diffusion(self.rho, self.tau_rho * dt)
            
            # Step 2: Reaction terms (local interactions)  
            self.reaction(self.rho, self.E, self.F)
            
            # Step 3: Field coupling (E and F evolution)
            self.field_coupling(self.rho, self.E, self.tau_E * dt)
            self.field_coupling(self.rho, self.F, self.tau_F * dt)
            
            # Step 4: Nonlinear damping (universal stability)
            self.apply_damping(self.rho, self.M, dt)
            self.apply_damping(self.E, self.M, dt) 
            self.apply_damping(self.F, self.M, dt)
            
            # Step 5: Enforce bounds (physics constraints)
            self.enforce_bounds(self.rho, 0.0, 1.0)
            self.enforce_bounds(self.E, -1.0, 1.0)
            self.enforce_bounds(self.F, 0.0, 1.0)
            
            # Step 6: Calculate system stress
            stress = self.compute_stress()
            self.stress_history.append(stress)
            
            if stress > 0.8:
                self.emergency_brake()
    
    # ===== DOMAIN-SPECIFIC IMPLEMENTATIONS =====
    def initialize_urban(self) -> None:
        """Urban domain: rho=population, E=development, F=constraints"""
        print("🏙️ Initializing URBAN domain...")
        self.tau_rho = 0.05    # Fast population dynamics
        self.M = 3000          # Soft urban constraints
        self.delta1 = 2.5      # Strong development drive
        
        # City center population
        x, y = np.ogrid[:self.GRID_X, :self.GRID_Y]
        center_x, center_y = self.GRID_X // 4, self.GRID_Y // 4
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        self.rho = np.exp(-dist**2 / (2 * (self.GRID_X // 10)**2)) * 0.6
        
        # Development corridors
        self.E = np.zeros((self.GRID_X, self.GRID_Y))
        self.E[self.GRID_X//2, :] = 0.4  # Horizontal corridor
        self.E[:, self.GRID_Y//2] = 0.4  # Vertical corridor
        
        # Zoning constraints
        self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.3
    
    def initialize_finance(self) -> None:
        """Finance domain: rho=prices, E=sentiment, F=regulation"""
        print("💹 Initializing FINANCE domain...")
        self.tau_rho = 0.01    # Very fast price changes
        self.M = 10000         # Stiff market mechanisms
        self.delta1 = 1.8      # Moderate speculation
        
        # Random initial prices
        self.rho = np.random.normal(0.5, 0.1, (self.GRID_X, self.GRID_Y))
        
        # Sentiment clusters
        self.E = np.random.random((self.GRID_X, self.GRID_Y)) * 0.3
        
        # Regulatory pressure
        self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.6
    
    def initialize_healthcare(self) -> None:
        """Healthcare domain: rho=infection, E=transmission, F=immunity"""
        print("🏥 Initializing HEALTHCARE domain...")
        self.tau_rho = 0.02    # Moderate infection spread
        self.M = 8000          # Medium containment stiffness
        self.delta1 = 2.2      # Strong transmission
        
        # Initial infection hotspots
        self.rho = np.zeros((self.GRID_X, self.GRID_Y))
        hotspots = [(self.GRID_X//3, self.GRID_Y//3), 
                   (2*self.GRID_X//3, 2*self.GRID_Y//3)]
        for hx, hy in hotspots:
            dist = np.sqrt((np.arange(self.GRID_X)[:, None] - hx)**2 + 
                          (np.arange(self.GRID_Y) - hy)**2)
            self.rho += np.exp(-dist**2 / (2 * (self.GRID_X//15)**2)) * 0.4
        
        # Transmission potential
        self.E = np.ones((self.GRID_X, self.GRID_Y)) * 0.5
        
        # Immunity/resistance
        self.F = np.random.random((self.GRID_X, self.GRID_Y)) * 0.3
    
    # ===== UNIVERSAL ENGINE EXECUTION =====
    def run_universal_engine(self, domain: str, total_steps: int, report_interval: int = 100) -> None:
        """Main universal engine execution"""
        print(f"🚀 STARTING UNIVERSAL ENGINE - {domain.upper()} DOMAIN")
        print("=" * 60)
        
        # Domain initialization
        if domain == "urban":
            self.initialize_urban()
        elif domain == "finance":
            self.initialize_finance()
        elif domain == "healthcare":
            self.initialize_healthcare()
        else:
            raise ValueError(f"Unknown domain: {domain}")
        
        print(f"Parameters: tau_rho={self.tau_rho}, M={self.M}, delta1={self.delta1}")
        print(f"Initial state - rho: [{self.rho.min():.3f}, {self.rho.max():.3f}]")
        
        # Main evolution loop
        for step in range(0, total_steps, report_interval):
            self.evolve_system(report_interval)
            
            # Domain monitoring
            energy = np.mean(self.rho**2 + self.E**2 + self.F**2)
            stress = self.stress_history[-1] if self.stress_history else 0.0
            
            print(f"Step {self.step_count:4d}: "
                  f"Energy={energy:.3f}, "
                  f"Stress={stress:.3f}, "
                  f"rho=[{self.rho.min():.3f},{self.rho.max():.3f}]")
            
            # Adaptive stabilization
            if stress > 0.6:
                print("  ⚠️  High stress - adaptive stabilization active")
        
        print(f"✅ {domain.upper()} simulation completed: {self.step_count} total steps")
        print(f"Final stress: {self.stress_history[-1]:.3f}")

def main():
    """Demonstrate the Universal Core Language"""
    print("🌌 UNIVERSAL DYNAMICS CORE LANGUAGE DEMO")
    print("Fundamental mathematical primitives for SXC-IGC engine")
    print("=" * 60)
    
    # Test all domains
    domains = ["urban", "finance", "healthcare"]
    
    for domain in domains:
        engine = UniversalCoreLanguage(grid_size=(32, 32))
        engine.run_universal_engine(domain, total_steps=500, report_interval=100)
        print()

if __name__ == "__main__":
    main()
