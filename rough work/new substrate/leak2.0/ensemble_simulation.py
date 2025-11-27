import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.fft import fftn, ifftn, fftfreq

class SubstrateEnsemble:
    def __init__(self, grid_size=64, box_size=10.0, m_X=0.1, n_fields=3):
        self.grid_size = grid_size
        self.box_size = box_size
        self.m_X = m_X
        self.n_fields = n_fields
        
        # Spatial grid
        self.x = np.linspace(-box_size/2, box_size/2, grid_size)
        self.dx = self.x[1] - self.x[0]
        self.XX, self.YY = np.meshgrid(self.x, self.x)
        self.r = np.sqrt(self.XX**2 + self.YY**2)
        
        # Initialize fields
        self.fields = np.zeros((n_fields, grid_size, grid_size))
        self.field_velocities = np.zeros((n_fields, grid_size, grid_size))
        
        # Fourier space
        self.kx = fftfreq(grid_size, d=self.dx) * 2 * np.pi
        self.KX, self.KY = np.meshgrid(self.kx, self.kx)
        self.k_squared = self.KX**2 + self.KY**2
    
    def initialize_vortex_ensemble(self, n_vortices=3):
        """Initialize multiple vortices"""
        vortex_positions = []
        
        for i in range(self.n_fields):
            field = np.ones_like(self.XX, dtype=complex)
            
            for _ in range(n_vortices):
                x0 = np.random.uniform(-self.box_size/3, self.box_size/3)
                y0 = np.random.uniform(-self.box_size/3, self.box_size/3)
                vortex_positions.append((x0, y0, i))
                
                charge = np.random.choice([-1, 1])
                theta = np.arctan2(self.YY - y0, self.XX - x0)
                field *= np.exp(1j * charge * theta)
            
            self.fields[i] = np.abs(field)
            self.field_velocities[i] = np.angle(field)
            
        return vortex_positions
    
    def compute_ensemble_stress_energy(self):
        """Stress-energy for ensemble"""
        T00_total = np.zeros((self.grid_size, self.grid_size))
        
        for i in range(self.n_fields):
            psi = self.fields[i] * np.exp(1j * self.field_velocities[i])
            
            # Gradient energy
            grad_x = np.gradient(np.real(psi), self.dx, axis=1)
            grad_y = np.gradient(np.real(psi), self.dx, axis=0)
            grad_energy = 0.5 * (grad_x**2 + grad_y**2)
            
            # Potential energy
            pot_energy = 0.5 * self.m_X**2 * (1 - np.abs(psi)**2)**2
            
            T00_total += grad_energy + pot_energy
        
        return T00_total

def run_simple_ensemble():
    """Run simplified ensemble analysis"""
    print("=== SUBSTRATE ENSEMBLE SIMULATION ===")
    
    # Initialize
    ensemble = SubstrateEnsemble(grid_size=128, box_size=20.0, m_X=0.2, n_fields=2)
    
    # Create vortices
    vortex_positions = ensemble.initialize_vortex_ensemble(n_vortices=3)
    print(f"Created {len(vortex_positions)} vortices")
    
    # Compute energy
    T00 = ensemble.compute_ensemble_stress_energy()
    
    # Plot results
    plt.figure(figsize=(12, 4))
    
    plt.subplot(131)
    for i in range(ensemble.n_fields):
        plt.contourf(ensemble.XX, ensemble.YY, ensemble.fields[i], levels=20)
        plt.colorbar(label=f'Field {i+1} Amplitude')
    plt.title('Field Amplitudes')
    
    plt.subplot(132)
    for i in range(ensemble.n_fields):
        plt.contourf(ensemble.XX, ensemble.YY, ensemble.field_velocities[i], levels=20)
        plt.colorbar(label=f'Field {i+1} Phase')
    plt.title('Field Phases')
    
    plt.subplot(133)
    plt.contourf(ensemble.XX, ensemble.YY, T00, levels=20)
    plt.colorbar(label='Energy Density')
    plt.title('Total Stress-Energy T⁰⁰')
    
    # Mark vortex positions
    for x, y, field_idx in vortex_positions:
        plt.scatter(x, y, color='red', s=50, marker='x')
    
    plt.tight_layout()
    plt.savefig('ensemble_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"Total energy: {np.sum(T00):.3f}")
    print(f"Energy per field: {np.sum(T00)/ensemble.n_fields:.3f}")
    
    # Analyze vortex distribution
    if vortex_positions:
        positions = np.array([(x, y) for x, y, _ in vortex_positions])
        distances = []
        for i in range(len(positions)):
            for j in range(i+1, len(positions)):
                dist = np.sqrt(np.sum((positions[i] - positions[j])**2))
                distances.append(dist)
        
        if distances:
            mean_dist = np.mean(distances)
            print(f"Mean vortex separation: {mean_dist:.2f}")
            if mean_dist < 4.0:
                print("✅ Vortex clustering detected")
            else:
                print("❌ No strong clustering")

if __name__ == "__main__":
    run_simple_ensemble()
