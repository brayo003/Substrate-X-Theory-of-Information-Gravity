import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, ifft2, fftfreq

class VortexFormationTest:
    """Test if substrate can form topological vortices"""
    
    def __init__(self, grid_size=256, box_size=25.0, m_X=0.1, g=20.0):
        self.grid_size = grid_size
        self.box_size = box_size
        self.m_X = m_X
        self.g = g  # VERY strong nonlinearity
        
        self.x = np.linspace(-box_size/2, box_size/2, grid_size)
        self.dx = self.x[1] - self.x[0]
        self.XX, self.YY = np.meshgrid(self.x, self.x)
        
        self.kx = fftfreq(grid_size, d=self.dx) * 2 * np.pi
        self.KX, self.KY = np.meshgrid(self.kx, self.kx)
        self.k_squared = self.KX**2 + self.KY**2
        
        self.psi = np.ones((grid_size, grid_size), dtype=complex)  # Start uniform
        
        print(f"Testing vortex formation: m_X={m_X}, g={g}")
    
    def add_phase_defects(self):
        """Artificially create phase defects to seed vortex formation"""
        # Add phase windings that could evolve into vortices
        x0, y0 = 0, 0
        r = np.sqrt((self.XX - x0)**2 + (self.YY - y0)**2)
        theta = np.arctan2(self.YY - y0, self.XX - x0)
        
        # Add multiple phase windings
        self.psi *= np.exp(1j * 2 * theta)  # Double vortex
        self.psi *= np.exp(1j * np.sin(0.5 * self.XX) * np.cos(0.5 * self.YY))  # Complex phase
        
        # Add noise to break symmetry
        noise = 0.1 * (np.random.normal(0,1,self.psi.shape) + 
                      1j * np.random.normal(0,1,self.psi.shape))
        self.psi += noise
        
        print("Added phase defects and noise")
    
    def detect_vortices(self):
        """Count topological defects in the field"""
        phase = np.angle(self.psi)
        vortex_count = 0
        antivortex_count = 0
        
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # Compute phase winding around plaquette
                phase_diff = (phase[i+1,j] - phase[i,j] + 
                             phase[i+1,j+1] - phase[i+1,j] +
                             phase[i,j+1] - phase[i+1,j+1] +
                             phase[i,j] - phase[i,j+1])
                
                # Normalize and check for vortex
                phase_diff = (phase_diff + np.pi) % (2 * np.pi) - np.pi
                
                if np.abs(phase_diff) > 3.0:  # Vortex detected
                    if phase_diff > 0:
                        vortex_count += 1
                    else:
                        antivortex_count += 1
        
        return vortex_count, antivortex_count
    
    def evolve_to_vortices(self, dt=0.005, steps=1000):
        """Evolve with strong nonlinearity to form vortices"""
        print("Evolving to form vortices...")
        frames = []
        vortex_history = []
        
        for step in range(steps):
            # Spectral evolution
            psi_k = fft2(self.psi)
            kinetic = -0.5 * self.k_squared
            psi_k = psi_k * np.exp(-1j * kinetic * dt)
            self.psi = ifft2(psi_k)
            
            # VERY strong nonlinear potential
            density = np.abs(self.psi)**2
            potential = 0.5 * self.m_X**2 * (1 - density) + self.g * density**2
            
            self.psi = self.psi * np.exp(-1j * potential * dt)
            
            # Kinetic term again
            psi_k = fft2(self.psi)
            psi_k = psi_k * np.exp(-1j * kinetic * dt)
            self.psi = ifft2(psi_k)
            
            if step % 200 == 0:
                frames.append(self.psi.copy())
                vortices, antivortices = self.detect_vortices()
                vortex_history.append((vortices, antivortices))
                
                print(f"Step {step+1}/{steps}: {vortices} vortices, {antivortices} antivortices")
                
                if vortices + antivortices > 0:
                    print(f"  → TOPOLOGICAL DEFECTS FORMING!")
        
        return frames, vortex_history
    
    def analyze_vortex_formation(self, vortex_history):
        """Analyze vortex formation dynamics"""
        initial_vortices = vortex_history[0][0] + vortex_history[0][1]
        final_vortices = vortex_history[-1][0] + vortex_history[-1][1]
        
        print(f"\n=== VORTEX FORMATION ANALYSIS ===")
        print(f"Initial topological defects: {initial_vortices}")
        print(f"Final topological defects: {final_vortices}")
        
        if final_vortices > initial_vortices:
            print("✅ VORTEX FORMATION CONFIRMED!")
            print("Your substrate CAN form topological structures")
        elif final_vortices > 0:
            print("⚠️ Vortices present but not increasing")
            print("Substrate supports vortices but doesn't create them spontaneously")
        else:
            print("❌ NO VORTEX FORMATION")
            print("Substrate may be in a different phase")

def main():
    print("SUBSTRATE VORTEX FORMATION TEST")
    print("=" * 45)
    print("Testing if substrate can form topological defects")
    
    # Test with very strong nonlinearity
    substrate = VortexFormationTest(m_X=0.1, g=20.0)
    substrate.add_phase_defects()
    
    frames, vortex_history = substrate.evolve_to_vortices(steps=800)
    substrate.analyze_vortex_formation(vortex_history)
    
    # Visualization
    final_psi = frames[-1]
    
    plt.figure(figsize=(15, 5))
    
    plt.subplot(131)
    plt.imshow(np.abs(final_psi), extent=[-12.5,12.5,-12.5,12.5], cmap='viridis')
    plt.colorbar(label='|ψ|')
    plt.title('Field Amplitude')
    
    plt.subplot(132)
    plt.imshow(np.angle(final_psi), extent=[-12.5,12.5,-12.5,12.5], cmap='hsv')
    plt.colorbar(label='Phase')
    plt.title('Field Phase')
    
    # Mark vortices
    vortices, antivortices = substrate.detect_vortices()
    phase = np.angle(final_psi)
    for i in range(1, substrate.grid_size-1):
        for j in range(1, substrate.grid_size-1):
            phase_diff = (phase[i+1,j] - phase[i,j] + 
                         phase[i+1,j+1] - phase[i+1,j] +
                         phase[i,j+1] - phase[i+1,j+1] +
                         phase[i,j] - phase[i,j+1])
            if np.abs(phase_diff) > 3.0:
                color = 'red' if phase_diff > 0 else 'blue'
                plt.scatter(substrate.x[i], substrate.x[j], color=color, s=20)
    
    plt.subplot(133)
    vortex_counts = [v+a for v,a in vortex_history]
    plt.plot(vortex_counts, 'ro-', linewidth=2)
    plt.xlabel('Time Step (x200)')
    plt.ylabel('Total Vortices')
    plt.title('Vortex Formation Dynamics')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('substrate_vortices.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\nFinal state: {vortices} vortices, {antivortices} antivortices")

if __name__ == "__main__":
    main()
