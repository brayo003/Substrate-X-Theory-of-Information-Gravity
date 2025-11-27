#!/usr/bin/env python3
"""
UNIVERSAL DYNAMICS CORE - NUMERICALLY STABLE
With proper stability analysis and adaptive time stepping
"""
import numpy as np
from typing import Tuple, Dict, Any

class UniversalStableCore:
    """Numerically stable universal dynamics with adaptive time stepping"""
    
    def __init__(self, grid_size: Tuple[int, int] = (64, 64)):
        self.GRID_X, self.GRID_Y = grid_size
        
        # ===== FIELD DECLARATIONS =====
        self.rho = np.zeros(grid_size)  # Density field
        self.E = np.zeros(grid_size)    # Excitation field
        self.F = np.zeros(grid_size)    # Inhibition field
        
        # ===== ADAPTIVE TIME STEPPING =====
        self.dt = 0.001                # Start with small time step
        self.dt_min = 1e-6
        self.dt_max = 0.01
        self.cfl_safety = 0.1          # CFL safety factor
        
        # ===== STABILITY MONITORING =====
        self.step_count = 0
        self.stress_history = []
        self.rejected_steps = 0
        self.max_changes = []
        
        # ===== DIFFUSION COEFFICIENTS =====
        self.D_rho = 0.01
        self.D_E = 0.1  
        self.D_F = 1.0
        
        # ===== REACTION PARAMETERS =====
        self.alpha, self.beta, self.gamma = 1.2, 0.8, 1.0
        self.tau_E, self.tau_F = 0.5, 0.3
        self.delta, self.epsilon = 0.6, 0.4
        self.delta1, self.delta2 = 2.0, 1.5
        
        self.boundary_type = 'neumann'
    
    def compute_max_change_per_step(self, dt: float) -> Tuple[float, float, float]:
        """Compute maximum predicted change in any field for given time step"""
        # Compute time derivatives
        drho_dt = self.D_rho * self.laplacian_2d(self.rho) + self.reaction_rho(self.rho, self.E, self.F)
        dE_dt = self.D_E * self.laplacian_2d(self.E) + self.reaction_E(self.rho, self.E, self.F)
        dF_dt = self.D_F * self.laplacian_2d(self.F) + self.reaction_F(self.rho, self.E, self.F)
        
        # Maximum absolute changes
        max_drho = np.max(np.abs(drho_dt)) * dt
        max_dE = np.max(np.abs(dE_dt)) * dt  
        max_dF = np.max(np.abs(dF_dt)) * dt
        
        return max_drho, max_dE, max_dF
    
    def check_stability_criteria(self, dt: float) -> Tuple[bool, str]:
        """Check multiple stability criteria for given time step"""
        max_drho, max_dE, max_dF = self.compute_max_change_per_step(dt)
        
        # Criterion 1: Maximum change per step < 20% of field range
        if max_drho > 0.2 or max_dE > 0.2 or max_dF > 0.2:
            return False, f"Change too large: Δρ={max_drho:.3f}, ΔE={max_dE:.3f}, ΔF={max_dF:.3f}"
        
        # Criterion 2: Diffusion stability (CFL condition)
        dx = 1.0 / self.GRID_X
        max_D = max(self.D_rho, self.D_E, self.D_F)
        cfl_limit = self.cfl_safety * dx**2 / (2 * max_D)
        if dt > cfl_limit:
            return False, f"CFL violation: dt={dt:.6f} > limit={cfl_limit:.6f}"
        
        # Criterion 3: Reaction vs damping balance
        reaction_terms = np.array([
            np.max(np.abs(self.reaction_rho(self.rho, self.E, self.F))),
            np.max(np.abs(self.reaction_E(self.rho, self.E, self.F))),
            np.max(np.abs(self.reaction_F(self.rho, self.E, self.F)))
        ])
        
        # If any reaction term dominates without sufficient damping
        if np.any(reaction_terms > 10.0):  # Arbitrary threshold for now
            return False, f"Reaction dominance: max_reaction={np.max(reaction_terms):.3f}"
        
        return True, "Stable"
    
    def adaptive_time_step(self) -> float:
        """Compute adaptive time step based on stability criteria"""
        # Start with current dt
        test_dt = self.dt
        
        # Binary search for maximum stable dt
        for attempt in range(10):
            stable, reason = self.check_stability_criteria(test_dt)
            if stable:
                # Try increasing dt
                test_dt = min(test_dt * 1.5, self.dt_max)
            else:
                # Reduce dt
                test_dt = max(test_dt * 0.5, self.dt_min)
                if test_dt == self.dt_min:
                    break
        
        self.dt = test_dt
        return self.dt
    
    def laplacian_2d(self, field: np.ndarray) -> np.ndarray:
        """Compute 2D Laplacian with Neumann boundaries"""
        laplacian = np.zeros_like(field)
        laplacian[1:-1, 1:-1] = (
            field[:-2, 1:-1] + field[2:, 1:-1] + 
            field[1:-1, :-2] + field[1:-1, 2:] - 4 * field[1:-1, 1:-1]
        )
        return laplacian
    
    def reaction_E(self, rho: np.ndarray, E: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Excitation field reaction kinetics"""
        return (
            self.alpha * rho +
            self.beta * E * (1 - E) -
            self.gamma * E * F -
            (1.0 / self.tau_E) * E
        )
    
    def reaction_F(self, rho: np.ndarray, E: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Inhibition field reaction kinetics"""
        return (
            self.delta * rho**2 +
            self.epsilon * E -
            (1.0 / self.tau_F) * F
        )
    
    def reaction_rho(self, rho: np.ndarray, E: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Density field reaction kinetics"""
        return (
            self.delta1 * E * rho * (1 - rho) -
            self.delta2 * F * rho
        )
    
    def evolve_system_adaptive(self, target_steps: int) -> int:
        """Evolve system with adaptive time stepping"""
        actual_steps = 0
        
        for attempt in range(target_steps * 10):  # Allow many attempts due to rejected steps
            if actual_steps >= target_steps:
                break
            
            # Compute adaptive time step
            dt = self.adaptive_time_step()
            
            # Store previous state for rollback
            rho_prev = self.rho.copy()
            E_prev = self.E.copy()
            F_prev = self.F.copy()
            
            try:
                # Tentative evolution step
                diffusion_rho = self.D_rho * self.laplacian_2d(self.rho)
                reaction_rho = self.reaction_rho(self.rho, self.E, self.F)
                self.rho += dt * (diffusion_rho + reaction_rho)
                
                diffusion_E = self.D_E * self.laplacian_2d(self.E)
                reaction_E = self.reaction_E(self.rho, self.E, self.F)
                self.E += dt * (diffusion_E + reaction_E)
                
                diffusion_F = self.D_F * self.laplacian_2d(self.F)
                reaction_F = self.reaction_F(self.rho, self.E, self.F)
                self.F += dt * (diffusion_F + reaction_F)
                
                # Check for numerical issues
                if (np.any(np.isnan(self.rho)) or np.any(np.isnan(self.E)) or 
                    np.any(np.isnan(self.F)) or np.any(self.rho > 1e6)):
                    raise ValueError("Numerical explosion detected")
                
                # Enforce bounds
                self.enforce_bounds(self.rho, 0.0, 1.0)
                self.enforce_bounds(self.E, -1.0, 1.0)
                self.enforce_bounds(self.F, 0.0, 1.0)
                
                # Compute changes for monitoring
                max_drho = np.max(np.abs(self.rho - rho_prev))
                max_dE = np.max(np.abs(self.E - E_prev))
                max_dF = np.max(np.abs(self.F - F_prev))
                max_change = max(max_drho, max_dE, max_dF)
                self.max_changes.append(max_change)
                
                # Success - increment step count
                self.step_count += 1
                actual_steps += 1
                
                # Compute stress
                stress = self.compute_stress()
                self.stress_history.append(stress)
                
            except (ValueError, FloatingPointError):
                # Rollback and reduce time step
                self.rho, self.E, self.F = rho_prev, E_prev, F_prev
                self.dt = max(self.dt * 0.1, self.dt_min)
                self.rejected_steps += 1
                if self.rejected_steps > 100:
                    print("  💥 Too many rejected steps - stopping")
                    break
        
        return actual_steps
    
    def enforce_bounds(self, A: np.ndarray, min_val: float, max_val: float) -> None:
        """Enforce physical bounds"""
        np.clip(A, min_val, max_val, out=A)
    
    def compute_stress(self) -> float:
        """Compute system stress"""
        grad_x = np.diff(self.rho, axis=0)
        grad_y = np.diff(self.rho, axis=1)
        grad_x = np.pad(grad_x, ((0,1),(0,0)), mode='edge')
        grad_y = np.pad(grad_y, ((0,0),(0,1)), mode='edge')
        return np.max(np.sqrt(grad_x**2 + grad_y**2))
    
    def set_urban_parameters(self) -> None:
        """Stable urban parameters"""
        print("🏙️ Setting STABLE URBAN parameters...")
        self.D_rho, self.D_E, self.D_F = 0.02, 0.05, 0.5  # Reduced D_F
        self.alpha, self.beta, self.gamma = 1.0, 0.6, 0.8
        self.tau_E, self.tau_F = 0.8, 0.6  # Slower decay
        self.delta, self.epsilon = 0.3, 0.2
        self.delta1, self.delta2 = 1.5, 1.0  # Reduced growth
    
    def set_finance_parameters(self) -> None:
        """Stable finance parameters"""
        print("💹 Setting STABLE FINANCE parameters...")
        self.D_rho, self.D_E, self.D_F = 0.01, 0.08, 0.3  # Much reduced D_F
        self.alpha, self.beta, self.gamma = 1.2, 0.8, 1.2  # More inhibition
        self.tau_E, self.tau_F = 0.4, 0.3
        self.delta, self.epsilon = 0.2, 0.3
        self.delta1, self.delta2 = 1.8, 1.2  # Balanced growth
    
    def set_healthcare_parameters(self) -> None:
        """Stable healthcare parameters"""
        print("🏥 Setting STABLE HEALTHCARE parameters...")
        self.D_rho, self.D_E, self.D_F = 0.03, 0.06, 0.4
        self.alpha, self.beta, self.gamma = 0.9, 0.5, 1.0
        self.tau_E, self.tau_F = 0.7, 0.5
        self.delta, self.epsilon = 0.4, 0.3
        self.delta1, self.delta2 = 1.2, 1.3  # More inhibition
    
    def initialize_domain(self, domain: str) -> None:
        """Initialize with smoother initial conditions"""
        if domain == "urban":
            self.set_urban_parameters()
            center = (self.GRID_X//3, self.GRID_Y//3)
            x, y = np.ogrid[:self.GRID_X, :self.GRID_Y]
            dist = np.sqrt((x - center[0])**2 + (y - center[1])**2)
            self.rho = np.exp(-dist**2 / (self.GRID_X//6)**2) * 0.5  # Smoother
            self.E = np.ones((self.GRID_X, self.GRID_Y)) * 0.3
            self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.4
            
        elif domain == "finance":
            self.set_finance_parameters()
            # Smoother initial conditions
            self.rho = np.random.normal(0.5, 0.08, (self.GRID_X, self.GRID_Y))  # Less variance
            self.E = np.random.normal(0.3, 0.05, (self.GRID_X, self.GRID_Y))
            self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.5
            
        elif domain == "healthcare":
            self.set_healthcare_parameters()
            self.rho = np.zeros((self.GRID_X, self.GRID_Y))
            hotspots = [(self.GRID_X//4, self.GRID_Y//4), (3*self.GRID_X//4, 3*self.GRID_Y//4)]
            for hx, hy in hotspots:
                dist = np.sqrt((np.arange(self.GRID_X)[:, None] - hx)**2 + 
                              (np.arange(self.GRID_Y) - hy)**2)
                self.rho += np.exp(-dist**2 / (self.GRID_X//10)**2) * 0.3  # Weaker hotspots
            self.E = np.ones((self.GRID_X, self.GRID_Y)) * 0.4
            self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.4
    
    def run_stable_simulation(self, domain: str, target_time: float = 3.0) -> None:
        """Run simulation with adaptive time stepping"""
        print(f"🎯 STABLE SIMULATION - {domain.upper()} DOMAIN")
        print("=" * 60)
        print("Features:")
        print("  • Adaptive time stepping (CFL + reaction limits)")
        print("  • Stability checking before each step")  
        print("  • Automatic rollback on instability")
        print("  • Smoother initial conditions")
        print("=" * 60)
        
        self.initialize_domain(domain)
        
        print(f"Parameters: D_ρ={self.D_rho}, D_E={self.D_E}, D_F={self.D_F}")
        print(f"Reaction: α={self.alpha}, β={self.beta}, γ={self.gamma}")
        print(f"Initial ρ: [{self.rho.min():.3f}, {self.rho.max():.3f}]")
        
        elapsed_time = 0.0
        report_interval = target_time / 6
        
        while elapsed_time < target_time:
            # Evolve for next time interval
            steps = self.evolve_system_adaptive(int(report_interval / self.dt_min))
            
            if steps == 0:
                print("  💥 No progress possible - stopping")
                break
            
            elapsed_time = self.step_count * self.dt  # Approximate
            
            energy = np.mean(self.rho**2 + self.E**2 + self.F**2)
            stress = self.stress_history[-1] if self.stress_history else 0.0
            avg_change = np.mean(self.max_changes[-steps:]) if self.max_changes else 0.0
            
            print(f"Time {elapsed_time:.2f}: "
                  f"Steps={self.step_count}, "
                  f"dt={self.dt:.6f}, "
                  f"Energy={energy:.3f}, "
                  f"Stress={stress:.3f}, "
                  f"Δ_avg={avg_change:.4f}")
            
            if self.rejected_steps > 0:
                print(f"  ⚠️  Rejected steps: {self.rejected_steps}")
            
            if stress > 0.8:
                print("  🚨 High stress - consider parameter adjustment")
        
        print(f"✅ {domain.upper()} completed: {self.step_count} steps")
        print(f"Final dt: {self.dt:.6f}, Final stress: {self.stress_history[-1]:.3f}")
        print(f"Total rejected steps: {self.rejected_steps}")

def main():
    """Demonstrate numerically stable universal dynamics"""
    print("🌌 UNIVERSAL DYNAMICS - NUMERICALLY STABLE")
    print("With adaptive time stepping and stability analysis")
    print("=" * 60)
    
    domains = ["urban", "finance", "healthcare"]
    
    for domain in domains:
        engine = UniversalStableCore(grid_size=(32, 32))
        engine.run_stable_simulation(domain, target_time=2.0)
        print()

if __name__ == "__main__":
    main()
