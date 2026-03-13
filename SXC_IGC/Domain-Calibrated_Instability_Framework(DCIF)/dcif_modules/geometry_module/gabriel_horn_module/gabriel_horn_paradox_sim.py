import numpy as np
import matplotlib.pyplot as plt

class GabrielHornEngine:
    def __init__(self, a=1.0, beta=0.1):
        self.a = a
        self.beta = beta
        self.dt = 0.01
        self.T = 0.01 # Initial tension
        
    def volume_capacity(self, x):
        """Volume of Gabriel's Horn from 1 to x. Bounded limit is pi."""
        return np.pi * (1.0 - 1.0/x)
        
    def surface_excitation(self, x):
        """Surface Area approximation (lower bound) from 1 to x. Unbounded."""
        return 2 * np.pi * np.log(x)
        
    def simulate(self, x_max=50):
        history_x = []
        history_T = []
        history_gamma = []
        history_E = []
        
        # x represents scale, depth, or time (must start >= 1 for the Horn)
        x = 1.0 
        
        while x < x_max:
            # Map Gabriel's Horn properties to SXC Engine parameters
            gamma = self.volume_capacity(x)
            E = self.surface_excitation(x)
            
            # SXC Dynamic Equation: dT/dx = a*T^2 - gamma*T + beta*E
            dT = (self.a * (self.T**2) - gamma * self.T + self.beta * E) * self.dt
            self.T += dT
            
            history_x.append(x)
            history_T.append(self.T)
            history_gamma.append(gamma)
            history_E.append(E)
            
            # Break condition: System shatters (blowup to infinity)
            if self.T > 50.0:
                print(f"--- SYSTEM SHATTERED ---")
                print(f"Critical Scale (x) reached: {x:.2f}")
                print(f"Max Capacity (γ) at failure: {gamma:.4f} (Approaching π = 3.1415...)")
                print(f"Excitation Load (E) at failure: {E:.4f}")
                break
                
            x += self.dt
            
        return history_x, history_T, history_gamma, history_E

# Run the simulation
print("Initiating Gabriel's Horn Substrate Mapping...")
engine = GabrielHornEngine(a=1.0, beta=0.15)
hx, hT, hGamma, hE = engine.simulate(x_max=100)

# Visualizing the paradox
plt.figure(figsize=(10, 6))

plt.plot(hx, hGamma, label="System Capacity (γ) ≈ Volume [Bounded by π]", color="blue", linewidth=2)
plt.plot(hx, hE, label="Excitation (E) ≈ Surface Area [Unbounded]", color="orange", linewidth=2)
plt.plot(hx, hT, label="System Tension (T) [Blowup]", color="red", linestyle="--", linewidth=2)

plt.axhline(np.pi, color='blue', linestyle=':', alpha=0.5, label="Max Theoretical Capacity (π)")

plt.title("The Painter's Paradox: SXC-IGC Engine Failure")
plt.xlabel("Scale / Time (x)")
plt.ylabel("Magnitude")
plt.ylim(0, 15)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("painter_paradox_sim.png")
print("Saved plot to painter_paradox_sim.png")

