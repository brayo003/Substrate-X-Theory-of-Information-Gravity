import numpy as np
from scipy.fft import fftn, ifftn

def test_linear_perturbation_stability():
    # Grid parameters
    N = 64
    L = 10.0
    dx = L / N
    x = np.linspace(0, L, N, endpoint=False)
    X, Y = np.meshgrid(x, x)
    
    # Initial condition: random perturbation
    np.random.seed(42)
    phi0 = 0.1 * np.random.randn(N, N)
    
    # PDE parameters
    c = 1.0  # Wave speed
    dt = 0.1 * dx / c  # CFL condition
    nsteps = 1000
    
    # Wave number grid
    kx = 2 * np.pi * np.fft.fftfreq(N, d=dx)
    ky = 2 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, ky)
    k_sq = KX**2 + KY**2
    
    # Time stepping
    phi_hat = fftn(phi0)
    phi_prev = phi0.copy()
    
    max_amplitude = 0.0
    for i in range(nsteps):
        # Spectral method for Laplacian
        laplacian_phi_hat = -k_sq * phi_hat
        phi = np.real(ifftn(phi_hat))
        
        # Simple wave equation: ∂ₜₜφ = c²∇²φ
        phi_next = 2*phi - phi_prev + (c*dt)**2 * np.real(ifftn(laplacian_phi_hat))
        
        # Update for next step
        phi_prev = phi
        phi_hat = fftn(phi_next - phi)
        
        # Track maximum amplitude
        max_amplitude = max(max_amplitude, np.max(np.abs(phi_next)))
    
    # Check stability
    assert max_amplitude < 10.0 * np.max(np.abs(phi0)), \
        f"Perturbation grew by factor {max_amplitude/np.max(np.abs(phi0)):.1f}x"

if __name__ == "__main__":
    test_linear_perturbation_stability()
