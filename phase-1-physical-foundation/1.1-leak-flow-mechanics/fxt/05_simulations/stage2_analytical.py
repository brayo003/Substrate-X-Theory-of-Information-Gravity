import numpy as np
import matplotlib.pyplot as plt

# Substrate constants
k_rot = 4.5e-7          # s
omega_max = 1e6          # rad/s
Gamma0 = 1e3             # base rate (example)

def Gamma(omega):
    return Gamma0 + k_rot * omega**2 / (1 + (omega/omega_max)**2)

omega = np.logspace(3, 8, 100)   # 1e3 to 1e8

# Choose an observation time – typical Ramsey free evolution time
t_obs = 1e-6   # 1 µs

# Analytical expressions for a qubit initially in |+> under pure dephasing
# rho(t) = 0.5 * ( I + exp(-Gamma*t) * sigma_x )
# Bloch vector length = exp(-Gamma*t)
# Purity = (1 + exp(-2*Gamma*t)) / 2
G = Gamma(omega)
T2 = 1.0 / G
bloch_length = np.exp(-G * t_obs)
purity = 0.5 * (1 + np.exp(-2 * G * t_obs))
visibility = bloch_length   # for Ramsey, visibility = exp(-Gamma*t)

plt.figure(figsize=(12,8))

plt.subplot(2,2,1)
plt.loglog(omega, G)
plt.axvline(omega_max, color='gray', linestyle='--')
plt.xlabel('ω (rad/s)'); plt.ylabel('Γ (s⁻¹)')
plt.title('Decoherence rate')
plt.grid(True, alpha=0.3)

plt.subplot(2,2,2)
plt.loglog(omega, T2)
plt.axvline(omega_max, color='gray', linestyle='--')
plt.xlabel('ω (rad/s)'); plt.ylabel('T₂ (s)')
plt.title('Coherence time')
plt.grid(True, alpha=0.3)

plt.subplot(2,2,3)
plt.semilogx(omega, purity)
plt.axvline(omega_max, color='gray', linestyle='--')
plt.xlabel('ω (rad/s)'); plt.ylabel('Purity')
plt.title(f'Purity at t = {t_obs:.0e} s')
plt.grid(True, alpha=0.3)

plt.subplot(2,2,4)
plt.semilogx(omega, bloch_length)
plt.axvline(omega_max, color='gray', linestyle='--')
plt.xlabel('ω (rad/s)'); plt.ylabel('Bloch vector length')
plt.title(f'Coherence at t = {t_obs:.0e} s')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('stage2_analytical.png', dpi=150)
print("Analytical benchmark curves saved to stage2_analytical.png")
