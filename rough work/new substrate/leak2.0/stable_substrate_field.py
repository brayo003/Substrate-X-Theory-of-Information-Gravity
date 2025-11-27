import numpy as np
import matplotlib.pyplot as plt

class StableSubstrateField:
    def __init__(self, grid_size=128, box_size=20.0, m_X=0.5, lambda_param=1.0):
        self.grid_size = grid_size
        self.box_size = box_size
        self.m_X = m_X  # Field mass
        self.lambda_param = lambda_param  # Self-coupling
        
        self.x = np.linspace(-box_size/2, box_size/2, grid_size)
        self.dx = self.x[1] - self.x[0]
        self.XX, self.YY = np.meshgrid(self.x, self.x)
        
        # Complex field (amplitude + phase)
        self.phi = np.ones((grid_size, grid_size), dtype=complex)
        # Small initial fluctuations
        noise = 0.05 * (np.random.normal(0,1, (grid_size, grid_size)) + 
                       1j * np.random.normal(0,1, (grid_size, grid_size)))
        self.phi += noise
    
    def potential_energy(self, phi):
        """STABLE potential: V(φ) = m²|φ|² + λ|φ|⁴"""
        # This potential is bounded below and has stable vacuum
        return 0.5 * self.m_X**2 * np.abs(phi)**2 + 0.25 * self.lambda_param * np.abs(phi)**4
    
    def gradient_energy(self):
        """Energy from field gradients"""
        grad_x = np.gradient(np.real(self.phi), self.dx, axis=1)
        grad_y = np.gradient(np.real(self.phi), self.dx, axis=0)
        grad_energy = 0.5 * (grad_x**2 + grad_y**2)
        return grad_energy
    
    def total_energy_density(self):
        """Total energy density - guaranteed positive"""
        return self.gradient_energy() + self.potential_energy(self.phi)
    
    def evolve_stable(self, n_steps=200, dt=0.01):
        """Stable time evolution using gradient flow"""
        energy_history = []
        print("Evolving stable substrate field...")
        
        for step in range(n_steps):
            # Compute force from potential: F = -∇V
            # For complex field, we evolve real and imaginary parts separately
            phi_real = np.real(self.phi)
            phi_imag = np.imag(self.phi)
            
            # Gradient descent on energy
            energy_grad_real = np.gradient(self.total_energy_density(), self.dx, axis=1)
            energy_grad_imag = np.gradient(self.total_energy_density(), self.dx, axis=0)
            
            # Update field (simplified dynamics)
            phi_real -= dt * energy_grad_real
            phi_imag -= dt * energy_grad_imag
            
            self.phi = phi_real + 1j * phi_imag
            
            # Track stability
            total_energy = np.sum(self.total_energy_density())
            energy_history.append(total_energy)
            
            if step % 40 == 0:
                max_amplitude = np.max(np.abs(self.phi))
                print(f"Step {step}: Energy = {total_energy:.3f}, Max |φ| = {max_amplitude:.3f}")
                
                # Check for vortex formation
                vortices = self.detect_vortices()
                if vortices > 0:
                    print(f"  → {vortices} vortices detected!")
        
        return energy_history
    
    def detect_vortices(self):
        """Detect topological defects (vortices) in the phase"""
        phase = np.angle(self.phi)
        vortex_count = 0
        
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # Check phase winding around plaquette
                phase_diff = (phase[i+1,j] - phase[i,j] + 
                             phase[i+1,j+1] - phase[i+1,j] +
                             phase[i,j+1] - phase[i+1,j+1] +
                             phase[i,j] - phase[i,j+1])
                if np.abs(phase_diff) > 3.0:
                    vortex_count += 1
        
        return vortex_count
    
    def analyze_field(self):
        """Comprehensive field analysis"""
        print(f"\n=== SUBSTRATE FIELD ANALYSIS ===")
        print(f"Average amplitude: {np.mean(np.abs(self.phi)):.3f}")
        print(f"Amplitude variance: {np.var(np.abs(self.phi)):.4f}")
        print(f"Phase coherence: {np.abs(np.mean(np.exp(1j * np.angle(self.phi)))):.3f}")
        
        vortices = self.detect_vortices()
        print(f"Vortices detected: {vortices}")
        
        if vortices > 0:
            print("🎯 TOPOLOGICAL STRUCTURES FORMING!")
            print("→ Substrate can support stable vortices")
        else:
            print("Field remains mostly uniform")
            print("→ May need different parameters for structure formation")

def main():
    print("STABLE SUBSTRATE FIELD SIMULATION")
    print("=" * 45)
    print("Testing if substrate has stable vacuum and can form structures...")
    
    # Test with stable parameters
    substrate = StableSubstrateField(m_X=0.5, lambda_param=1.0)
    
    # Initial state
    plt.figure(figsize=(12, 4))
    
    plt.subplot(131)
    plt.imshow(np.abs(substrate.phi), extent=[-10,10,-10,10], cmap='viridis')
    plt.colorbar(label='|φ|')
    plt.title('Initial Field Amplitude')
    
    plt.subplot(132)
    plt.imshow(np.angle(substrate.phi), extent=[-10,10,-10,10], cmap='hsv')
    plt.colorbar(label='Phase')
    plt.title('Initial Field Phase')
    
    # Evolve
    energy_history = substrate.evolve_stable(n_steps=200, dt=0.01)
    substrate.analyze_field()
    
    # Final state
    plt.subplot(133)
    plt.imshow(np.abs(substrate.phi), extent=[-10,10,-10,10], cmap='viridis')
    plt.colorbar(label='|φ|')
    plt.title('Final Field Amplitude')
    
    plt.tight_layout()
    plt.savefig('stable_substrate_field.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Energy evolution
    plt.figure(figsize=(8, 4))
    plt.plot(energy_history)
    plt.xlabel('Time Step')
    plt.ylabel('Total Energy')
    plt.title('Energy Evolution - Stable System')
    plt.grid(True, alpha=0.3)
    plt.savefig('stable_energy_evolution.png', dpi=120, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
