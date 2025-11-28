"""
Planetary Dynamics N-Body Simulation
Tests UDE stability and conservation using the RK4 Integrator for Gravity.
CORRECTION: Adjusted initial velocity for stable circular orbit (E_Total = -0.5).
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

# Gravitational Constant (Canonical Units)
G = 1.0

class Body:
    def __init__(self, mass: float, position: np.ndarray, velocity: np.ndarray):
        self.mass = mass
        self.r = position  # Position vector (x, y)
        self.v = velocity  # Velocity vector (vx, vy)
        
    def __repr__(selfself):
        return f"Body(m={self.mass:.2f}, r={self.r}, v={self.v})"

class NBodySystem:
    def __init__(self, bodies: List[Body]):
        self.bodies = bodies

    def calculate_accelerations(self, r_list: List[np.ndarray]) -> List[np.ndarray]:
        """Calculates the acceleration vector for every body due to mutual gravity."""
        
        N = len(self.bodies)
        a_list = [np.zeros(2) for _ in range(N)]
        masses = [body.mass for body in self.bodies]
        
        for i in range(N):
            for j in range(i + 1, N):
                # Vector distance from i to j
                r_vec = r_list[j] - r_list[i]
                r_mag = np.linalg.norm(r_vec)

                # Use softening parameter for calculation, though distance is 1.0 initially
                r_mag_cubed = (r_mag**2 + 1e-6**2)**1.5 # Use slight softening in force calculation
                
                if r_mag < 1e-6: 
                    continue
                
                # Acceleration magnitude is G * m_j / r^2
                accel_mag_i = G * masses[j] / r_mag_cubed 
                accel_mag_j = G * masses[i] / r_mag_cubed 
                
                a_i_vec = accel_mag_i * r_vec
                a_j_vec = -accel_mag_j * r_vec
                
                a_list[i] += a_i_vec
                a_list[j] += a_j_vec
                
        return a_list

    def rhs(self, state: np.ndarray) -> np.ndarray:
        """Right-Hand Side function for the RK4 Integrator."""
        N = len(self.bodies)
        r_list = [state[i*4 : i*4+2] for i in range(N)]
        v_list = [state[i*4+2 : i*4+4] for i in range(N)]
        
        a_list = self.calculate_accelerations(r_list)
        
        dydt = np.empty_like(state)
        for i in range(N):
            dydt[i*4 : i*4+2] = v_list[i]
            dydt[i*4+2 : i*4+4] = a_list[i]
            
        return dydt

    def rk4_step(self, dt: float):
        """Performs one step of the 4th order Runge-Kutta integration."""
        
        current_state = np.concatenate([np.concatenate([b.r, b.v]) for b in self.bodies])
        
        k1 = self.rhs(current_state)
        k2 = self.rhs(current_state + 0.5 * dt * k1)
        k3 = self.rhs(current_state + 0.5 * dt * k2)
        k4 = self.rhs(current_state + dt * k3)
        
        new_state = current_state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        N = len(self.bodies)
        for i in range(N):
            self.bodies[i].r = new_state[i*4 : i*4+2]
            self.bodies[i].v = new_state[i*4+2 : i*4+4]

    def total_energy(self) -> float:
        """Calculates the total energy (Kinetic + Potential) of the system."""
        
        # 1. Kinetic Energy
        KE = 0.0
        for body in self.bodies:
            KE += 0.5 * body.mass * np.linalg.norm(body.v)**2
            
        # 2. Potential Energy
        PE = 0.0
        N = len(self.bodies)
        for i in range(N):
            for j in range(i + 1, N):
                r_vec = self.bodies[j].r - self.bodies[i].r
                r_mag = np.linalg.norm(r_vec)
                
                # No softening in Potential Energy check for bound orbit analysis
                PE -= G * self.bodies[i].mass * self.bodies[j].mass / r_mag 
                
        return KE + PE

    def total_angular_momentum(self) -> float:
        """Calculates the total angular momentum (r x p) of the system (z-component)."""
        Lz = 0.0
        for body in self.bodies:
            Lz += body.mass * (body.r[0] * body.v[1] - body.r[1] * body.v[0])
        return Lz


def run_n_body_simulation(total_time: float = 100.0, dt: float = 0.01):
    """
    Sets up and runs a stable test case (binary star system).
    """
    print("🛰️ DEMONSTRATING PLANETARY DYNAMICS STABILITY (RK4 Integration)")
    print("==========================================================")
    
    # --- 1. Setup Binary System ---
    m1, m2 = 1.0, 1.0
    r_separation = 1.0
    
    # CORRECTED VELOCITY for E_Total = -0.5: v = sqrt(0.5)
    v_mag = np.sqrt(0.5) 
    
    body1 = Body(m1, np.array([-0.5 * r_separation, 0.0]), np.array([0.0, -v_mag]))
    body2 = Body(m2, np.array([0.5 * r_separation, 0.0]), np.array([0.0, v_mag]))
    
    system = NBodySystem([body1, body2])
    
    # --- 2. Initial State Analysis ---
    initial_energy = system.total_energy()
    initial_momentum = system.total_angular_momentum()
    
    print(f"🧬 SYSTEM INITIALIZED: Binary Star (Masses 1.0, 1.0)")
    print(f"   Initial Energy (E): {initial_energy:.8f} (Expected -0.5)")
    print(f"   Initial Momentum (L): {initial_momentum:.8f}")
    
    num_steps = int(total_time / dt)
    history = []
    
    # --- 3. Evolution and Conservation Check ---
    print(f"⏳ Evolving system for {num_steps} steps (T={total_time})...")
    
    for step in range(num_steps):
        system.rk4_step(dt)
        history.append([b.r.copy() for b in system.bodies])
        
        if step % (num_steps // 10) == 0:
            current_energy = system.total_energy()
            current_momentum = system.total_angular_momentum()
            
            # Use absolute difference for comparison against the initial values
            E_error = abs(current_energy - initial_energy) / abs(initial_energy) if abs(initial_energy) > 1e-10 else 0
            L_error = abs(current_momentum - initial_momentum) / abs(initial_momentum) if abs(initial_momentum) > 1e-10 else 0
            
            print(f"Step {step}: E_Error={E_error*1e6:.2f} ppm, L_Error={L_error*1e6:.2f} ppm")

    # --- 4. Final Analysis and Visualization ---
    final_energy = system.total_energy()
    final_momentum = system.total_angular_momentum()
    
    final_E_error = abs(final_energy - initial_energy) / abs(initial_energy) if abs(initial_energy) > 1e-10 else 0
    final_L_error = abs(final_momentum - initial_momentum) / abs(initial_momentum) if abs(initial_momentum) > 1e-10 else 0
    
    print("\n📊 CONSERVATION ANALYSIS (TEST PASSED IF ERRORS ARE LOW):")
    print(f"   Final Energy Error: {final_E_error*1e6:.2f} ppm (Parts Per Million)")
    print(f"   Final Momentum Error: {final_L_error*1e6:.2f} ppm")
    
    visualize_orbits(history)


def visualize_orbits(history):
    """Visualizes the orbits of the bodies."""
    history = np.array(history)
    
    plt.figure(figsize=(8, 8))
    
    plt.plot(history[:, 0, 0], history[:, 0, 1], label='Body 1 (Star 1)', linestyle='-')
    plt.plot(history[:, 1, 0], history[:, 1, 1], label='Body 2 (Star 2)', linestyle='--')
    
    plt.scatter(history[0, 0, 0], history[0, 0, 1], color='red', marker='o', s=50, label='Start')
    plt.scatter(history[0, 1, 0], history[0, 1, 1], color='red', marker='o', s=50)

    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.title('Binary Star System Orbit (RK4 Integrator)')
    plt.legend()
    plt.axis('equal')
    plt.grid(True)
    plt.savefig('binary_star_orbit_stable.png')
    plt.close()
    print("\n🖼️ Orbit visualization saved to 'binary_star_orbit_stable.png'")

if __name__ == '__main__':
    run_n_body_simulation()
