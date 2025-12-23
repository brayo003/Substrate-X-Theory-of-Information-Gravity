import numpy as np
import matplotlib.pyplot as plt

class SpontaneousStructure:
    def __init__(self, grid_size=128, box_size=20.0, m_X=0.1, temperature=0.5):
        self.grid_size = grid_size
        self.box_size = box_size
        self.m_X = m_X
        self.temperature = temperature
        
        self.x = np.linspace(-box_size/2, box_size/2, grid_size)
        self.dx = self.x[1] - self.x[0]
        self.XX, self.YY = np.meshgrid(self.x, self.x)
        
        # Start with uniform field + small fluctuations
        self.phi = np.ones((grid_size, grid_size))  # Scalar field amplitude
        self.phi += 0.1 * np.random.normal(0, 1, (grid_size, grid_size))
    
    def energy_density(self):
        """Compute Landau-Ginzburg energy density"""
        grad_x = np.gradient(self.phi, self.dx, axis=1)
        grad_y = np.gradient(self.phi, self.dx, axis=0)
        gradient_energy = 0.5 * (grad_x**2 + grad_y**2)
        
        potential = 0.5 * self.m_X**2 * (1 - self.phi**2)**2
        noise = self.temperature * np.random.normal(0, 1, self.phi.shape)
        
        return gradient_energy + potential + noise
    
    def evolve(self, n_steps=500, dt=0.1):
        """Simple gradient descent dynamics"""
        energy_history = []
        print("Testing spontaneous structure formation...")
        
        for step in range(n_steps):
            # Compute energy gradient
            energy_grad = np.gradient(self.energy_density(), self.dx)
            total_grad = np.sqrt(energy_grad[0]**2 + energy_grad[1]**2)
            
            # Update field (gradient descent)
            self.phi -= dt * total_grad
            
            # Add some noise for exploration
            self.phi += 0.01 * np.random.normal(0, 1, self.phi.shape)
            
            # Track energy
            if step % 100 == 0:
                total_energy = np.sum(self.energy_density())
                energy_history.append(total_energy)
                print(f"Step {step}: Total energy = {total_energy:.3f}")
                
                # Check for structure formation
                variance = np.var(self.phi)
                if variance > 0.1:
                    print(f"  → Structure forming! Variance = {variance:.3f}")
        
        return energy_history
    
    def analyze_structures(self):
        """Look for spontaneous vortex formation"""
        # Detect phase defects (vortices)
        phase = np.angle(self.phi)  # If complex, otherwise use gradient
        structures_detected = np.sum(np.abs(self.phi - 1.0) > 0.2)
        
        print(f"\n=== STRUCTURE ANALYSIS ===")
        print(f"Field variance: {np.var(self.phi):.4f}")
        print(f"Structures detected: {structures_detected}")
        print(f"Max deviation: {np.max(np.abs(self.phi - 1.0)):.3f}")
        
        if structures_detected > 10:
            print("🎯 SPONTANEOUS STRUCTURE FORMATION CONFIRMED!")
        else:
            print("Field remains mostly uniform")
        
        return structures_detected

def main():
    print("SPONTANEOUS STRUCTURE FORMATION TEST")
    print("=" * 50)
    print("Testing if substrate can form structures naturally...")
    
    # Test different parameters
    for temp in [0.1, 0.5, 1.0]:
        print(f"\n--- Testing temperature = {temp} ---")
        simulator = SpontaneousStructure(m_X=0.1, temperature=temp)
        energy_history = simulator.evolve(n_steps=300)
        structures = simulator.analyze_structures()
        
        # Visualization
        plt.figure(figsize=(10, 4))
        plt.subplot(121)
        plt.imshow(simulator.phi, extent=[-10,10,-10,10], cmap='viridis')
        plt.colorbar(label='Field Amplitude')
        plt.title(f'Temperature = {temp}')
        
        plt.subplot(122)
        plt.plot(energy_history)
        plt.xlabel('Time steps (x100)')
        plt.ylabel('Total Energy')
        plt.title('Energy Evolution')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'spontaneous_structures_temp_{temp}.png', dpi=120)
        plt.show()

if __name__ == "__main__":
    main()
