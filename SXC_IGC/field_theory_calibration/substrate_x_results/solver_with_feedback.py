#!/usr/bin/env python3
"""
Solver with substrate-gravity feedback
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver_fixed_gamma import SubstrateXSolver

class SubstrateXWithFeedback(SubstrateXSolver):
    """
    Extended solver with substrate → gravity feedback
    """
    
    def step(self):
        """Extended step with feedback from s to E,F"""
        # Store old fields for feedback
        E_old = self.E.copy()
        F_old = self.F.copy()
        s_old = self.s.copy()
        
        # 1. First evolve substrate field (original physics)
        super().step()
        
        # 2. Apply feedback: substrate modifies gravity
        # Simple feedback model: s field creates additional gravitational sources
        feedback_strength = 1e-10  # Tune this for k_eff calibration
        
        # E feedback: s creates additional potential
        # ∂E/∂t ∝ -s (substrate density creates gravitational potential)
        self.E += feedback_strength * self.s * self.dt
        
        # F feedback: gradient of s creates additional acceleration  
        # ∂F/∂t ∝ -∇s (substrate gradient creates gravitational acceleration)
        grad_s_x, grad_s_y = np.gradient(self.s, self.dx, axis=0), np.gradient(self.s, self.dx, axis=1)
        self.F[:,:,0] += feedback_strength * grad_s_x * self.dt
        self.F[:,:,1] += feedback_strength * grad_s_y * self.dt
        
        # Print feedback magnitude for debugging
        E_feedback = np.max(np.abs(self.E - E_old))
        F_feedback = np.max(np.sqrt((self.F[:,:,0] - F_old[:,:,0])**2 + 
                                   (self.F[:,:,1] - F_old[:,:,1])**2))
        if E_feedback > 1e-10 or F_feedback > 1e-10:
            print(f"Feedback: ΔE={E_feedback:.2e}, ΔF={F_feedback:.2e}")

def test_with_feedback():
    """Test if feedback enables gravity modification"""
    print("🎯 TESTING WITH FEEDBACK LOOP")
    print("=" * 60)
    
    solver = SubstrateXWithFeedback(
        grid_size=16,
        domain_size=2e11,
        alpha=1e5, beta=1e5, gamma=1e5,  # Strong coupling
        chi=1.0, tau=1e6
    )
    
    mass = 2e30
    solver.add_point_mass(mass, (0,0))
    
    # Add initial substrate perturbation
    solver.s += 1e-5
    
    print("Initial state:")
    E_initial = solver.E.copy()
    F_initial = solver.F.copy()
    s_initial = solver.s.copy()
    
    char_distance = 2e10
    distances = np.sqrt(solver.X**2 + solver.Y**2)
    char_idx = np.unravel_index(np.argmin(np.abs(distances - char_distance)), distances.shape)
    
    F_initial_char = np.sqrt(F_initial[:,:,0]**2 + F_initial[:,:,1]**2)[char_idx]
    g_newton = solver.G * mass / (distances[char_idx] + solver.r_min)**2
    
    print(f"  Newtonian g: {g_newton:.6e} m/s²")
    print(f"  Initial F: {F_initial_char:.6e} m/s²")
    print(f"  Initial k_eff: {(F_initial_char - g_newton)/g_newton:.6f}")
    
    # Evolve with feedback
    print("Evolving with feedback...")
    for i in range(50):
        solver.step()
    
    E_final = solver.E.copy()
    F_final = solver.F.copy()
    s_final = solver.s.copy()
    
    F_final_char = np.sqrt(F_final[:,:,0]**2 + F_final[:,:,1]**2)[char_idx]
    k_eff_final = (F_final_char - g_newton) / g_newton
    
    print("\nFinal state:")
    print(f"  Final F: {F_final_char:.6e} m/s²")
    print(f"  Final k_eff: {k_eff_final:.6f}")
    print(f"  Target k_eff: 0.000200")
    
    E_change = np.max(np.abs(E_final - E_initial))
    F_change = np.max(np.sqrt((F_final[:,:,0] - F_initial[:,:,0])**2 + 
                             (F_final[:,:,1] - F_initial[:,:,1])**2))
    
    print(f"  E field change: {E_change:.2e}")
    print(f"  F field change: {F_change:.2e}")
    
    if abs(k_eff_final) > 1e-6:
        print("  ✅ GRAVITY MODIFICATION ACHIEVED!")
    else:
        print("  ❌ Still no gravity modification")

def explain_feedback_physics():
    """Explain the needed feedback physics"""
    print(f"\n🔬 FEEDBACK PHYSICS EXPLANATION")
    print("=" * 60)
    print("For k_eff > 0 (enhanced gravity), you need:")
    print("")
    print("1. Mass creates gravity (E,F fields)")
    print("2. Gravity excites substrate (s field evolves)") 
    print("3. Substrate creates ADDITIONAL gravity (feedback)")
    print("4. Total gravity = Newtonian + Substrate contribution")
    print("")
    print("Mathematically:")
    print("  g_total = g_newton × (1 + k_eff)")
    print("  k_eff = (g_substrate_contribution) / g_newton")
    print("")
    print("Without step 3 (feedback), k_eff = 0 always!")
    print("Your original theory was missing the feedback equations.")

if __name__ == "__main__":
    test_with_feedback()
    explain_feedback_physics()
