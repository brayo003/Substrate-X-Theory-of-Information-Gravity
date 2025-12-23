import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, ifft2, fftfreq

class NonlinearSubstrate:
    """Test with enhanced nonlinearity to sustain interference"""
    
    def __init__(self, grid_size=256, box_size=30.0, m_X=0.1, g=5.0):
        self.grid_size = grid_size
        self.box_size = box_size
        self.m_X = m_X
        self.g = g  # Nonlinear coupling strength
        
        # Spatial grid
        self.x = np.linspace(-box_size/2, box_size/2, grid_size)
        self.dx = self.x[1] - self.x[0]
        self.XX, self.YY = np.meshgrid(self.x, self.x)
        
        # Fourier space
        self.kx = fftfreq(grid_size, d=self.dx) * 2 * np.pi
        self.KX, self.KY = np.meshgrid(self.kx, self.kx)
        self.k_squared = self.KX**2 + self.KY**2
        
        self.psi = np.zeros((grid_size, grid_size), dtype=complex)
        
        print(f"Parameters: m_X={m_X}, nonlinearity g={g}")
    
    def create_interfering_waves(self):
        """Create multiple wave packets for complex interference"""
        # Four wave packets with different momenta
        positions = [(-6, -6), (-6, 6), (6, -6), (6, 6)]
        widths = [1.5, 1.5, 1.5, 1.5]
        momenta = [(0.3, 0.3), (0.3, -0.3), (-0.3, 0.3), (-0.3, -0.3)]
        
        for (x0, y0), width, (px, py) in zip(positions, widths, momenta):
            packet = np.exp(-((self.XX - x0)**2 + (self.YY - y0)**2) / (2 * width**2))
            phase_factor = np.exp(1j * (px * self.XX + py * self.YY))
            packet = packet.astype(complex) * phase_factor
            self.psi += packet
        
        # Normalize
        norm = np.sqrt(np.sum(np.abs(self.psi)**2))
        if norm > 0:
            self.psi /= norm
    
    def nonlinear_dynamics(self, dt=0.01, steps=600):
        """Evolve with strong nonlinearity"""
        print("Evolving with enhanced nonlinearity...")
        frames = []
        
        for step in range(steps):
            # Spectral evolution
            psi_k = fft2(self.psi)
            
            # Kinetic term
            kinetic = -0.5 * self.k_squared
            psi_k = psi_k * np.exp(-1j * kinetic * dt)
            self.psi = ifft2(psi_k)
            
            # STRONG nonlinear potential
            density = np.abs(self.psi)**2
            potential = 0.5 * self.m_X**2 * density + self.g * density**2
            
            self.psi = self.psi * np.exp(-1j * potential * dt)
            
            # Kinetic term again
            psi_k = fft2(self.psi)
            psi_k = psi_k * np.exp(-1j * kinetic * dt)
            self.psi = ifft2(psi_k)
            
            if step % 150 == 0:
                frames.append(self.psi.copy())
                current_step = step + 1
                print(f"Step {current_step}/{steps}")
                
                # Track pattern complexity
                contrast = np.std(np.abs(self.psi)) / np.mean(np.abs(self.psi))
                print(f"  Pattern contrast: {contrast:.4f}")
        
        return frames
    
    def analyze_pattern_persistence(self, frames):
        """Analyze if nonlinearity sustains patterns"""
        initial = frames[0]
        final = frames[-1]
        
        initial_contrast = np.std(np.abs(initial)) / np.mean(np.abs(initial))
        final_contrast = np.std(np.abs(final)) / np.mean(np.abs(final))
        
        print(f"\n=== NONLINEAR PATTERN ANALYSIS ===")
        print(f"Initial contrast: {initial_contrast:.4f}")
        print(f"Final contrast: {final_contrast:.4f}")
        print(f"Contrast change: {final_contrast/initial_contrast:.3f}x")
        
        if final_contrast > 0.8 * initial_contrast:
            print("✅ NONLINEARITY SUSTAINS PATTERNS!")
            return True
        else:
            print("⚠️ Patterns still dissipate")
            return False

def main():
    print("NONLINEAR SUBSTRATE INTERFERENCE TEST")
    print("=" * 50)
    
    # Test with stronger nonlinearity
    substrate = NonlinearSubstrate(m_X=0.1, g=5.0)  # Enhanced g parameter
    substrate.create_interfering_waves()
    
    frames = substrate.nonlinear_dynamics(dt=0.03, steps=600)
    pattern_persisted = substrate.analyze_pattern_persistence(frames)
    
    # Visualization
    plt.figure(figsize=(12, 4))
    
    plt.subplot(131)
    plt.imshow(np.abs(frames[0]), extent=[-15,15,-15,15], cmap='viridis')
    plt.colorbar()
    plt.title('Initial |ψ|')
    
    plt.subplot(132) 
    plt.imshow(np.abs(frames[len(frames)//2]), extent=[-15,15,-15,15], cmap='viridis')
    plt.colorbar()
    plt.title('Intermediate |ψ|')
    
    plt.subplot(133)
    plt.imshow(np.abs(frames[-1]), extent=[-15,15,-15,15], cmap='viridis')
    plt.colorbar()
    plt.title('Final |ψ|')
    
    plt.tight_layout()
    plt.savefig('nonlinear_substrate.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    if pattern_persisted:
        print("\n🎯 Your substrate CAN sustain interference with nonlinearity!")
    else:
        print("\n🔧 May need even stronger nonlinear terms or different dynamics")

if __name__ == "__main__":
    main()
