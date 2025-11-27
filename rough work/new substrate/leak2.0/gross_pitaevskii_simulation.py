import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fftn, ifftn, fftfreq
import matplotlib.animation as animation

class GrossPitaevskiiSolver:
    def __init__(self, grid_size=256, box_size=20.0, m_X=0.2, g=1.0):
        self.grid_size = grid_size
        self.box_size = box_size
        self.m_X = m_X
        self.g = g  # Nonlinear coupling strength
        
        # Spatial grid
        self.x = np.linspace(-box_size/2, box_size/2, grid_size)
        self.dx = self.x[1] - self.x[0]
        self.XX, self.YY = np.meshgrid(self.x, self.x)
        self.r = np.sqrt(self.XX**2 + self.YY**2)
        
        # Fourier space for spectral methods
        self.kx = fftfreq(grid_size, d=self.dx) * 2 * np.pi
        self.KX, self.KY = np.meshgrid(self.kx, self.kx)
        self.k_squared = self.KX**2 + self.KY**2
        
        # Wavefunction
        self.psi = np.ones((grid_size, grid_size), dtype=complex)
        
        # Time step (CFL condition)
        self.dt = 0.01 * self.dx**2
        
    def initialize_vortices(self, n_vortices=4):
        """Initialize vortex configuration"""
        for _ in range(n_vortices):
            x0 = np.random.uniform(-self.box_size/3, self.box_size/3)
            y0 = np.random.uniform(-self.box_size/3, self.box_size/3)
            charge = np.random.choice([-1, 1])  # Vortex/antivortex
            
            # Add vortex phase winding
            theta = np.arctan2(self.YY - y0, self.XX - x0)
            vortex_phase = np.exp(1j * charge * theta)
            self.psi *= vortex_phase
            
        # Add some initial noise for interesting dynamics
        noise = 0.1 * (np.random.normal(0,1,self.psi.shape) + 
                       1j * np.random.normal(0,1,self.psi.shape))
        self.psi += noise
        self.psi /= np.sqrt(np.mean(np.abs(self.psi)**2))  # Normalize
        
    def spectral_laplacian(self, field):
        """Compute Laplacian using spectral methods"""
        field_hat = fftn(field)
        laplacian_hat = -self.k_squared * field_hat
        return ifftn(laplacian_hat)
    
    def time_step(self):
        """Single time step using split-step Fourier method"""
        # Kinetic term (in Fourier space)
        psi_hat = fftn(self.psi)
        psi_hat = psi_hat * np.exp(-1j * 0.5 * self.k_squared * self.dt)
        self.psi = ifftn(psi_hat)
        
        # Nonlinear + potential term (in real space)
        nonlinear = self.m_X**2 * (1 - np.abs(self.psi)**2) * self.psi + \
                   self.g * np.abs(self.psi)**2 * self.psi
        self.psi = self.psi * np.exp(-1j * nonlinear * self.dt)
        
        # Kinetic term again
        psi_hat = fftn(self.psi)
        psi_hat = psi_hat * np.exp(-1j * 0.5 * self.k_squared * self.dt)
        self.psi = ifftn(psi_hat)
    
    def compute_density(self):
        """Compute probability density |ψ|²"""
        return np.abs(self.psi)**2
    
    def compute_phase(self):
        """Compute phase of wavefunction"""
        return np.angle(self.psi)
    
    def compute_velocity_field(self):
        """Compute velocity field from phase gradient"""
        phase = self.compute_phase()
        vx = np.gradient(phase, self.dx, axis=1)
        vy = np.gradient(phase, self.dx, axis=0)
        return vx, vy
    
    def compute_vortices(self):
        """Detect vortex positions and charges"""
        phase = self.compute_phase()
        vortices = []
        
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # Compute phase winding around plaquette
                phase_diff = (phase[i+1, j] - phase[i, j] + 
                             phase[i+1, j+1] - phase[i+1, j] +
                             phase[i, j+1] - phase[i+1, j+1] +
                             phase[i, j] - phase[i, j+1])
                
                phase_diff = (phase_diff + np.pi) % (2 * np.pi) - np.pi
                
                if np.abs(phase_diff) > 3.0:  # Vortex detected
                    charge = np.sign(phase_diff)
                    vortices.append({
                        'position': (self.x[i], self.x[j]),
                        'charge': charge,
                        'density': np.abs(self.psi[i, j])**2
                    })
        
        return vortices
    
    def simulate(self, n_steps=1000, save_every=50):
        """Run simulation and save frames"""
        frames = []
        vortices_history = []
        
        print("Running Gross-Pitaevskii simulation...")
        for step in range(n_steps):
            self.time_step()
            
            if step % save_every == 0:
                density = self.compute_density()
                phase = self.compute_phase()
                vortices = self.compute_vortices()
                
                frames.append({
                    'density': density.copy(),
                    'phase': phase.copy(),
                    'vortices': vortices.copy(),
                    'time': step * self.dt
                })
                vortices_history.append(vortices)
                
                print(f"Step {step}/{n_steps}, Vortices: {len(vortices)}")
        
        return frames, vortices_history

def analyze_interference_patterns(frames):
    """Analyze emerging interference patterns"""
    print("\n=== INTERFERENCE PATTERN ANALYSIS ===")
    
    # Analyze first and last frames
    first_frame = frames[0]
    last_frame = frames[-1]
    
    # Fourier analysis of density patterns
    first_density_fft = np.abs(fftn(first_frame['density']))
    last_density_fft = np.abs(fftn(last_frame['density']))
    
    # Characteristic length scales
    first_correlation = np.fft.fftshift(first_density_fft)
    last_correlation = np.fft.fftshift(last_density_fft)
    
    print(f"Initial vortex count: {len(first_frame['vortices'])}")
    print(f"Final vortex count: {len(last_frame['vortices'])}")
    
    # Pattern complexity
    first_entropy = -np.sum(first_frame['density'] * np.log(first_frame['density'] + 1e-12))
    last_entropy = -np.sum(last_frame['density'] * np.log(last_frame['density'] + 1e-12))
    print(f"Pattern entropy - Initial: {first_entropy:.3f}, Final: {last_entropy:.3f}")

def main():
    print("GROSS-PITAEVSKII SIMULATION - COHERENT SUBSTRATE FIELD")
    print("=" * 60)
    
    # Initialize solver
    gp = GrossPitaevskiiSolver(grid_size=256, box_size=25.0, m_X=0.2, g=1.0)
    
    # Create initial vortex state
    gp.initialize_vortices(n_vortices=6)
    
    # Run simulation
    frames, vortices_history = gp.simulate(n_steps=2000, save_every=100)
    
    # Analyze results
    analyze_interference_patterns(frames)
    
    # Create visualization
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # First frame
    im1 = axes[0,0].imshow(frames[0]['density'], extent=[-12.5,12.5,-12.5,12.5], 
                          cmap='viridis', origin='lower')
    axes[0,0].set_title('Initial Density |ψ|²')
    plt.colorbar(im1, ax=axes[0,0])
    
    im2 = axes[0,1].imshow(frames[0]['phase'], extent=[-12.5,12.5,-12.5,12.5],
                          cmap='hsv', origin='lower')
    axes[0,1].set_title('Initial Phase')
    plt.colorbar(im2, ax=axes[0,1])
    
    # Mark vortices
    vortices = frames[0]['vortices']
    for v in vortices:
        color = 'red' if v['charge'] > 0 else 'blue'
        axes[0,1].scatter(v['position'][0], v['position'][1], color=color, s=30)
    
    # Middle frame
    mid_idx = len(frames) // 2
    im3 = axes[0,2].imshow(frames[mid_idx]['density'], extent=[-12.5,12.5,-12.5,12.5],
                          cmap='viridis', origin='lower')
    axes[0,2].set_title(f'Intermediate Density (t={frames[mid_idx]["time"]:.1f})')
    plt.colorbar(im3, ax=axes[0,2])
    
    # Final frame
    im4 = axes[1,0].imshow(frames[-1]['density'], extent=[-12.5,12.5,-12.5,12.5],
                          cmap='viridis', origin='lower')
    axes[1,0].set_title('Final Density |ψ|²')
    plt.colorbar(im4, ax=axes[1,0])
    
    im5 = axes[1,1].imshow(frames[-1]['phase'], extent=[-12.5,12.5,-12.5,12.5],
                          cmap='hsv', origin='lower')
    axes[1,1].set_title('Final Phase')
    plt.colorbar(im5, ax=axes[1,1])
    
    # Mark final vortices
    vortices = frames[-1]['vortices']
    for v in vortices:
        color = 'red' if v['charge'] > 0 else 'blue'
        axes[1,1].scatter(v['position'][0], v['position'][1], color=color, s=30)
    
    # Vortex dynamics
    vortex_counts = [len(frame['vortices']) for frame in frames]
    times = [frame['time'] for frame in frames]
    axes[1,2].plot(times, vortex_counts, 'ro-', linewidth=2)
    axes[1,2].set_xlabel('Time')
    axes[1,2].set_ylabel('Number of Vortices')
    axes[1,2].set_title('Vortex Dynamics')
    axes[1,2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('gross_pitaevskii_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n=== SIMULATION COMPLETE ===")
    print(f"Final vortex count: {len(frames[-1]['vortices'])}")
    print(f"Check 'gross_pitaevskii_results.png' for detailed patterns")

if __name__ == "__main__":
    main()
