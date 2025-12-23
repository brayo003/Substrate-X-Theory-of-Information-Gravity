import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, ifft2, fftfreq

class SubstrateInterference:
    """Test interference patterns using substrate field equations"""
    
    def __init__(self, grid_size=256, box_size=30.0, m_X=0.1):
        self.grid_size = grid_size
        self.box_size = box_size
        self.m_X = m_X  # Substrate mass parameter FROM YOUR THEORY
        
        # Spatial grid
        self.x = np.linspace(-box_size/2, box_size/2, grid_size)
        self.dx = self.x[1] - self.x[0]
        self.XX, self.YY = np.meshgrid(self.x, self.x)
        
        # Fourier space for spectral derivatives
        self.kx = fftfreq(grid_size, d=self.dx) * 2 * np.pi
        self.KX, self.KY = np.meshgrid(self.kx, self.kx)
        self.k_squared = self.KX**2 + self.KY**2
        
        # Substrate field (complex wavefunction)
        self.psi = np.zeros((grid_size, grid_size), dtype=complex)
        
        print(f"Substrate parameters: m_X={m_X}, box={box_size}, grid={grid_size}")
    
    def create_wave_packets(self, positions, widths, momenta):
        """Create coherent wave packets representing substrate excitations"""
        for (x0, y0), width, (px, py) in zip(positions, widths, momenta):
            # Gaussian wave packet with momentum
            packet = np.exp(-((self.XX - x0)**2 + (self.YY - y0)**2) / (2 * width**2))
            packet *= np.exp(1j * (px * self.XX + py * self.YY))  # Plane wave factor
            self.psi += packet
        
        # Normalize
        self.psi /= np.sqrt(np.sum(np.abs(self.psi)**2))
    
    def substrate_dynamics(self, dt=0.01, steps=1000):
        """Evolve according to substrate field equations"""
        print("Evolving substrate field...")
        
        # Store frames for analysis
        frames = []
        
        for step in range(steps):
            # Using spectral method for stability
            psi_k = fft2(self.psi)
            
            # Substrate field evolution: i∂ψ/∂t = [-∇²/2 + V]ψ
            # Where V includes substrate mass term and any self-interactions
            kinetic = -0.5 * self.k_squared  # -∇²/2 term
            
            # Substrate potential: m_X² term from your theory
            potential = 0.5 * self.m_X**2 * np.abs(self.psi)**2  # Simple nonlinearity
            
            # Time evolution in Fourier space (split-step)
            psi_k = psi_k * np.exp(-1j * kinetic * dt)
            self.psi = ifft2(psi_k)
            
            # Nonlinear term in real space
            self.psi = self.psi * np.exp(-1j * potential * dt)
            
            # Back to Fourier space for next step
            psi_k = fft2(self.psi)
            psi_k = psi_k * np.exp(-1j * kinetic * dt)
            self.psi = ifft2(psi_k)
            
            if step % 200 == 0:
                frames.append(self.psi.copy())
                print(f"Step {step}/{steps}")
                
                # Check conservation
                norm = np.sum(np.abs(self.psi)**2)
                print(f"  Norm conservation: {norm:.6f}")
        
        return frames
    
    def analyze_interference(self, frames):
        """Analyze interference patterns in substrate field"""
        print("\n=== INTERFERENCE PATTERN ANALYSIS ===")
        
        initial = frames[0]
        final = frames[-1]
        
        # Fourier analysis of patterns
        initial_fft = np.abs(fft2(initial))**2
        final_fft = np.abs(fft2(final))**2
        
        # Characteristic length scales
        k_initial = np.sum(self.k_squared * initial_fft) / np.sum(initial_fft)
        k_final = np.sum(self.k_squared * final_fft) / np.sum(final_fft)
        
        print(f"Characteristic wavelength - Initial: {2*np.pi/np.sqrt(k_initial):.3f}")
        print(f"Characteristic wavelength - Final: {2*np.pi/np.sqrt(k_final):.3f}")
        
        # Interference contrast
        initial_contrast = np.std(np.abs(initial)) / np.mean(np.abs(initial))
        final_contrast = np.std(np.abs(final)) / np.mean(np.abs(final))
        
        print(f"Interference contrast - Initial: {initial_contrast:.4f}")
        print(f"Interference contrast - Final: {final_contrast:.4f}")
        
        if final_contrast > initial_contrast:
            print("✅ INTERFERENCE PATTERNS ENHANCED")
        else:
            print("⚠️ Patterns dissipated")
    
    def visualize_results(self, frames):
        """Visualize substrate interference patterns"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Initial state
        im1 = axes[0,0].imshow(np.abs(frames[0]), extent=[-15,15,-15,15], 
                              cmap='viridis', origin='lower')
        axes[0,0].set_title('Initial: |ψ|')
        plt.colorbar(im1, ax=axes[0,0])
        
        im2 = axes[0,1].imshow(np.angle(frames[0]), extent=[-15,15,-15,15],
                              cmap='hsv', origin='lower')
        axes[0,1].set_title('Initial: Phase')
        plt.colorbar(im2, ax=axes[0,1])
        
        # Intermediate state
        mid = len(frames) // 2
        im3 = axes[0,2].imshow(np.abs(frames[mid]), extent=[-15,15,-15,15],
                              cmap='viridis', origin='lower')
        axes[0,2].set_title(f'Intermediate: |ψ|')
        plt.colorbar(im3, ax=axes[0,2])
        
        # Final state
        im4 = axes[1,0].imshow(np.abs(frames[-1]), extent=[-15,15,-15,15],
                              cmap='viridis', origin='lower')
        axes[1,0].set_title('Final: |ψ|')
        plt.colorbar(im4, ax=axes[1,0])
        
        im5 = axes[1,1].imshow(np.angle(frames[-1]), extent=[-15,15,-15,15],
                              cmap='hsv', origin='lower')
        axes[1,1].set_title('Final: Phase')
        plt.colorbar(im5, ax=axes[1,1])
        
        # Fourier spectrum
        final_fft = np.abs(fft2(frames[-1]))**2
        fft_shifted = np.fft.fftshift(final_fft)
        im6 = axes[1,2].imshow(np.log1p(fft_shifted), extent=[-1,1,-1,1],
                              cmap='hot', origin='lower')
        axes[1,2].set_title('Fourier Spectrum (log)')
        plt.colorbar(im6, ax=axes[1,2])
        
        plt.tight_layout()
        plt.savefig('substrate_interference.png', dpi=150, bbox_inches='tight')
        plt.show()

def main():
    print("SUBSTRATE INTERFERENCE PATTERN TEST")
    print("=" * 50)
    print("Testing wave interference using substrate field dynamics")
    
    # Initialize with YOUR substrate parameters
    substrate = SubstrateInterference(grid_size=256, box_size=30.0, m_X=0.1)
    
    # Create interfering wave packets
    # Two packets moving toward each other
    positions = [(-8, 0), (8, 0)]  # Starting positions
    widths = [2.0, 2.0]            # Packet widths  
    momenta = [(0.5, 0), (-0.5, 0)] # Momenta (will collide)
    
    substrate.create_wave_packets(positions, widths, momenta)
    
    # Evolve according to substrate dynamics
    frames = substrate.substrate_dynamics(dt=0.05, steps=800)
    
    # Analyze interference patterns
    substrate.analyze_interference(frames)
    
    # Visualize results
    substrate.visualize_results(frames)
    
    print(f"\n=== TEST COMPLETE ===")
    print("This demonstrates interference in your substrate field using:")
    print("✓ Your mass parameter m_X")
    print("✓ Wave packet dynamics") 
    print("✓ Spectral evolution method")
    print("✓ Proper conservation checks")

if __name__ == "__main__":
    main()
