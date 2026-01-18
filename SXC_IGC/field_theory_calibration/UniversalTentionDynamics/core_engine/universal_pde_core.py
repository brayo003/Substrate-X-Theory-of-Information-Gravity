#!/usr/bin/env python3
"""
UNIVERSAL DYNAMICS CORE - PROPER PDE STRUCTURE
With explicit mathematical definitions for E and F evolution
"""
import numpy as np
from typing import Tuple, Dict, Any

class UniversalPDECore:
    """Proper PDE-based universal dynamics with complete mathematical structure"""
    
    def __init__(self, grid_size: Tuple[int, int] = (64, 64)):
        self.GRID_X, self.GRID_Y = grid_size
        
        # ===== FIELD DECLARATIONS =====
        self.rho = np.zeros(grid_size)  # Density field
        self.E = np.zeros(grid_size)    # Excitation field (Activator)
        self.F = np.zeros(grid_size)    # Inhibition field (Inhibitor)
        
        # ===== DIFFUSION COEFFICIENTS =====
        self.D_rho = 0.01    # Density diffusion
        self.D_E = 0.1       # Activator diffusion (SLOWER for Turing patterns)
        self.D_F = 1.0       # Inhibitor diffusion (FASTER for Turing patterns)
        
        # ===== REACTION KINETICS PARAMETERS =====
        # E field reaction: f_E(ρ,E,F) = α·ρ + β·E·(1 - E) - γ·E·F - (1/τ_E)·E
        self.alpha = 1.2     # ρ → E coupling
        self.beta = 0.8      # E self-activation  
        self.gamma = 1.0     # E-F cross-inhibition
        self.tau_E = 0.5     # E decay time constant
        
        # F field reaction: f_F(ρ,E,F) = δ·ρ² + ε·E - (1/τ_F)·F
        self.delta = 0.6     # ρ² → F coupling (nonlinear)
        self.epsilon = 0.4   # E → F coupling
        self.tau_F = 0.3     # F decay time constant
        
        # ρ field reaction (existing): δ₁·E·ρ·(1 - ρ) - δ₂·F·ρ
        self.delta1 = 2.0    # E → ρ activation
        self.delta2 = 1.5    # F → ρ inhibition
        
        self.step_count = 0
        self.stress_history = []
        
        # Boundary conditions setup
        self.boundary_type = 'neumann'  # No-flux boundaries
    
    def laplacian_2d(self, field: np.ndarray) -> np.ndarray:
        """Compute 2D Laplacian with Neumann (no-flux) boundary conditions"""
        laplacian = np.zeros_like(field)
        
        # Interior points (standard 5-point stencil)
        laplacian[1:-1, 1:-1] = (
            field[:-2, 1:-1] + field[2:, 1:-1] + 
            field[1:-1, :-2] + field[1:-1, 2:] - 4 * field[1:-1, 1:-1]
        )
        
        # Neumann boundaries (zero derivative)
        # Top boundary
        laplacian[0, 1:-1] = (
            field[0, :-2] + field[0, 2:] + 2 * field[1, 1:-1] - 4 * field[0, 1:-1]
        )
        # Bottom boundary  
        laplacian[-1, 1:-1] = (
            field[-1, :-2] + field[-1, 2:] + 2 * field[-2, 1:-1] - 4 * field[-1, 1:-1]
        )
        # Left boundary
        laplacian[1:-1, 0] = (
            field[:-2, 0] + field[2:, 0] + 2 * field[1:-1, 1] - 4 * field[1:-1, 0]
        )
        # Right boundary
        laplacian[1:-1, -1] = (
            field[:-2, -1] + field[2:, -1] + 2 * field[1:-1, -2] - 4 * field[1:-1, -1]
        )
        # Corners (average of adjacent Neumann conditions)
        laplacian[0, 0] = (field[0, 1] + field[1, 0] - 2 * field[0, 0])
        laplacian[0, -1] = (field[0, -2] + field[1, -1] - 2 * field[0, -1])
        laplacian[-1, 0] = (field[-1, 1] + field[-2, 0] - 2 * field[-1, 0])
        laplacian[-1, -1] = (field[-1, -2] + field[-2, -1] - 2 * field[-1, -1])
        
        return laplacian
    
    def reaction_E(self, rho: np.ndarray, E: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Excitation field reaction kinetics: f_E(ρ,E,F)"""
        # f_E = α·ρ + β·E·(1 - E) - γ·E·F - (1/τ_E)·E
        return (
            self.alpha * rho +                    # ρ → E coupling
            self.beta * E * (1 - E) -            # E self-activation with saturation
            self.gamma * E * F -                 # E-F cross-inhibition
            (1.0 / self.tau_E) * E               # E linear decay
        )
    
    def reaction_F(self, rho: np.ndarray, E: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Inhibition field reaction kinetics: f_F(ρ,E,F)"""
        # f_F = δ·ρ² + ε·E - (1/τ_F)·F
        return (
            self.delta * rho**2 +                # ρ² → F coupling (nonlinear)
            self.epsilon * E -                   # E → F coupling
            (1.0 / self.tau_F) * F               # F linear decay
        )
    
    def reaction_rho(self, rho: np.ndarray, E: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Density field reaction kinetics"""
        # δ₁·E·ρ·(1 - ρ) - δ₂·F·ρ
        return (
            self.delta1 * E * rho * (1 - rho) -  # Logistic growth with E activation
            self.delta2 * F * rho                # Linear decay with F inhibition
        )
    
    def evolve_system(self, steps: int = 1, dt: float = 0.01) -> None:
        """Complete PDE evolution with proper mathematical structure"""
        for step in range(steps):
            self.step_count += 1
            
            # Store previous state for change detection
            rho_prev = self.rho.copy()
            
            # ===== DENSITY FIELD EVOLUTION =====
            # ∂ρ/∂t = D_ρ·∇²ρ + δ₁·E·ρ·(1 - ρ) - δ₂·F·ρ
            diffusion_rho = self.D_rho * self.laplacian_2d(self.rho)
            reaction_rho = self.reaction_rho(self.rho, self.E, self.F)
            self.rho += dt * (diffusion_rho + reaction_rho)
            
            # ===== EXCITATION FIELD EVOLUTION =====  
            # ∂E/∂t = D_E·∇²E + α·ρ + β·E·(1 - E) - γ·E·F - (1/τ_E)·E
            diffusion_E = self.D_E * self.laplacian_2d(self.E)
            reaction_E = self.reaction_E(self.rho, self.E, self.F)
            self.E += dt * (diffusion_E + reaction_E)
            
            # ===== INHIBITION FIELD EVOLUTION =====
            # ∂F/∂t = D_F·∇²F + δ·ρ² + ε·E - (1/τ_F)·F
            diffusion_F = self.D_F * self.laplacian_2d(self.F)
            reaction_F = self.reaction_F(self.rho, self.E, self.F)
            self.F += dt * (diffusion_F + reaction_F)
            
            # Enforce physical bounds
            self.enforce_bounds(self.rho, 0.0, 1.0)
            self.enforce_bounds(self.E, -1.0, 1.0)
            self.enforce_bounds(self.F, 0.0, 1.0)
            
            # Calculate system stress (gradient-based)
            stress = self.compute_stress()
            self.stress_history.append(stress)
            
            # Emergency brake for stability
            if stress > 0.9:
                self.emergency_brake()
    
    def enforce_bounds(self, A: np.ndarray, min_val: float, max_val: float) -> None:
        """Enforce physical bounds on fields"""
        np.clip(A, min_val, max_val, out=A)
    
    def compute_stress(self) -> float:
        """Compute system stress from field gradients"""
        grad_x = np.diff(self.rho, axis=0)
        grad_y = np.diff(self.rho, axis=1)
        grad_x = np.pad(grad_x, ((0,1),(0,0)), mode='edge')
        grad_y = np.pad(grad_y, ((0,0),(0,1)), mode='edge')
        return np.max(np.sqrt(grad_x**2 + grad_y**2))
    
    def emergency_brake(self) -> None:
        """Stability enforcement"""
        self.D_rho *= 0.9
        self.delta1 *= 0.8
        print("🚨 EMERGENCY BRAKE: Stability enforced")
    
    # ===== DOMAIN-SPECIFIC PARAMETER SETS =====
    def set_urban_parameters(self) -> None:
        """Urban domain: Pattern formation for city growth"""
        print("🏙️ Setting URBAN parameters...")
        # Turing pattern regime: D_F > D_E
        self.D_rho, self.D_E, self.D_F = 0.02, 0.05, 0.8
        
        # Strong development feedback
        self.alpha, self.beta, self.gamma = 1.5, 1.0, 0.8
        self.tau_E, self.tau_F = 0.6, 0.4
        self.delta, self.epsilon = 0.4, 0.3
        
        # Moderate growth dynamics
        self.delta1, self.delta2 = 2.5, 1.2
    
    def set_finance_parameters(self) -> None:
        """Finance domain: Oscillatory market dynamics"""
        print("💹 Setting FINANCE parameters...")
        # Faster dynamics for markets
        self.D_rho, self.D_E, self.D_F = 0.01, 0.1, 0.5
        
        # Strong sentiment feedback, weak regulation
        self.alpha, self.beta, self.gamma = 2.0, 1.2, 0.6
        self.tau_E, self.tau_F = 0.3, 0.2
        self.delta, self.epsilon = 0.3, 0.5
        
        # High speculation, low regulation
        self.delta1, self.delta2 = 3.0, 0.8
    
    def set_healthcare_parameters(self) -> None:
        """Healthcare domain: Epidemic wave dynamics"""
        print("🏥 Setting HEALTHCARE parameters...")
        # Moderate diffusion for disease spread
        self.D_rho, self.D_E, self.D_F = 0.03, 0.08, 0.6
        
        # Strong transmission, moderate immunity
        self.alpha, self.beta, self.gamma = 1.8, 0.9, 1.1
        self.tau_E, self.tau_F = 0.5, 0.4
        self.delta, self.epsilon = 0.5, 0.4
        
        # Balanced growth and containment
        self.delta1, self.delta2 = 2.2, 1.5
    
    def initialize_domain(self, domain: str) -> None:
        """Initialize fields for specific domain"""
        if domain == "urban":
            self.set_urban_parameters()
            # City center with development corridors
            center = (self.GRID_X//3, self.GRID_Y//3)
            x, y = np.ogrid[:self.GRID_X, :self.GRID_Y]
            dist = np.sqrt((x - center[0])**2 + (y - center[1])**2)
            self.rho = np.exp(-dist**2 / (self.GRID_X//4)**2) * 0.7
            self.E = np.random.random((self.GRID_X, self.GRID_Y)) * 0.3 + 0.2
            self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.3
            
        elif domain == "finance":
            self.set_finance_parameters()
            # Random initial prices with sentiment clusters
            self.rho = np.random.normal(0.5, 0.15, (self.GRID_X, self.GRID_Y))
            self.E = np.random.normal(0.3, 0.1, (self.GRID_X, self.GRID_Y))
            self.F = np.random.random((self.GRID_X, self.GRID_Y)) * 0.4
            
        elif domain == "healthcare":
            self.set_healthcare_parameters()
            # Infection hotspots
            self.rho = np.zeros((self.GRID_X, self.GRID_Y))
            hotspots = [(self.GRID_X//4, self.GRID_Y//4), (3*self.GRID_X//4, 3*self.GRID_Y//4)]
            for hx, hy in hotspots:
                dist = np.sqrt((np.arange(self.GRID_X)[:, None] - hx)**2 + 
                              (np.arange(self.GRID_Y) - hy)**2)
                self.rho += np.exp(-dist**2 / (self.GRID_X//8)**2) * 0.5
            self.E = np.ones((self.GRID_X, self.GRID_Y)) * 0.6
            self.F = np.random.random((self.GRID_X, self.GRID_Y)) * 0.4
    
    def run_simulation(self, domain: str, total_steps: int, report_interval: int = 50) -> None:
        """Run complete PDE-based simulation"""
        print(f"🧮 STARTING PDE SIMULATION - {domain.upper()} DOMAIN")
        print("=" * 60)
        print("PDE Structure:")
        print("  ∂ρ/∂t = D_ρ·∇²ρ + δ₁·E·ρ·(1 - ρ) - δ₂·F·ρ")
        print("  ∂E/∂t = D_E·∇²E + α·ρ + β·E·(1 - E) - γ·E·F - (1/τ_E)·E")  
        print("  ∂F/∂t = D_F·∇²F + δ·ρ² + ε·E - (1/τ_F)·F")
        print(f"Boundary Conditions: {self.boundary_type.upper()}")
        print("=" * 60)
        
        self.initialize_domain(domain)
        
        print(f"Diffusion: D_ρ={self.D_rho}, D_E={self.D_E}, D_F={self.D_F}")
        print(f"Reaction: α={self.alpha}, β={self.beta}, γ={self.gamma}")
        print(f"Initial ρ: [{self.rho.min():.3f}, {self.rho.max():.3f}]")
        
        for step in range(0, total_steps, report_interval):
            self.evolve_system(report_interval, dt=0.01)
            
            energy = np.mean(self.rho**2 + self.E**2 + self.F**2)
            stress = self.stress_history[-1] if self.stress_history else 0.0
            
            print(f"Step {self.step_count:4d}: "
                  f"Energy={energy:.3f}, "
                  f"Stress={stress:.3f}, "
                  f"ρ=[{self.rho.min():.3f},{self.rho.max():.3f}]")
            
            if stress > 0.7:
                print("  ⚠️  High stress detected")
        
        print(f"✅ {domain.upper()} PDE simulation completed")
        print(f"Final stress: {self.stress_history[-1]:.3f}")

def main():
    """Demonstrate proper PDE-based universal dynamics"""
    print("🌌 UNIVERSAL DYNAMICS - PROPER PDE STRUCTURE")
    print("With explicit mathematical definitions for all field evolutions")
    print("=" * 60)
    
    domains = ["urban", "finance", "healthcare"]
    
    for domain in domains:
        engine = UniversalPDECore(grid_size=(32, 32))
        engine.run_simulation(domain, total_steps=300, report_interval=75)
        print()

if __name__ == "__main__":
    main()
