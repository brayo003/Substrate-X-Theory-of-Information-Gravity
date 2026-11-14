import numpy as np
import matplotlib.pyplot as plt
from qutip import (basis, sigmax, sigmaz, mesolve, Options, fidelity,
                   entropy_vn, Qobj)

# ---------- parameters ----------
Gamma0 = 5e5                # s⁻¹ (NV T2*)
rabi_detuning = 2*np.pi*1e6 # 1 MHz detuning
free_time = 2e-6            # 2 µs free evolution
times = np.linspace(0, free_time, 200)

# Substrate X
k_rot = 4.5e-7
omega_max = 1e6

omega_vals = np.logspace(3, 8, 8)   # 1e3..1e8

# initial state |+>
psi0 = (basis(2,0) + basis(2,1)).unit()

# operators
sx = sigmax()
sz = sigmaz()

# Hamiltonian = (Delta/2) sigma_z
H = 0.5 * rabi_detuning * sz

# QuTiP options – store states explicitly
opts = Options(store_states=True, store_final_state=True)

visibility_std = []
visibility_sub = []
purity_std = []
purity_sub = []
trace_std = []
trace_sub = []

for w in omega_vals:
    Gamma_sub = Gamma0 + k_rot * w**2 / (1 + (w/omega_max)**2)

    # Standard
    result_std = mesolve(H, psi0, times,
                         c_ops=[np.sqrt(Gamma0) * sz],
                         e_ops=[sx],
                         options=opts)
    sx_std = result_std.expect[0]
    vis_std = (max(sx_std) - min(sx_std)) / 2
    visibility_std.append(vis_std)
    rho_final_std = result_std.final_state
    purity_std.append(rho_final_std.purity())
    trace_std.append(rho_final_std.tr().real)

    # Substrate
    result_sub = mesolve(H, psi0, times,
                         c_ops=[np.sqrt(Gamma_sub) * sz],
                         e_ops=[sx],
                         options=opts)
    sx_sub = result_sub.expect[0]
    vis_sub = (max(sx_sub) - min(sx_sub)) / 2
    visibility_sub.append(vis_sub)
    rho_final_sub = result_sub.final_state
    purity_sub.append(rho_final_sub.purity())
    trace_sub.append(rho_final_sub.tr().real)

# ----- Quick consistency check -----
print("Trace (should be 1):")
for w, tr_s, tr_sub in zip(omega_vals, trace_std, trace_sub):
    print(f"ω={w:.1e}: std={tr_s:.6f}, sub={tr_sub:.6f}")
print("Min purity std:", min(purity_std), "  sub:", min(purity_sub))

# ----- plots -----
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.semilogx(omega_vals, visibility_std, 'bo-', label='Standard QM')
plt.semilogx(omega_vals, visibility_sub, 'rs-', label='QM + Substrate X')
plt.xlabel('ω (rad/s)')
plt.ylabel('Ramsey visibility')
plt.legend()
plt.grid(True, alpha=0.3)
plt.title('Visibility at fixed free evolution')

plt.subplot(1,2,2)
plt.semilogx(omega_vals, purity_std, 'bo-', label='Standard QM')
plt.semilogx(omega_vals, purity_sub, 'rs-', label='QM + Substrate X')
plt.xlabel('ω (rad/s)')
plt.ylabel('Final purity')
plt.legend()
plt.grid(True, alpha=0.3)
plt.title('Purity after Ramsey sequence')

plt.tight_layout()
plt.savefig('stage3_qutip_ramsey_fixed.png', dpi=150)
print("Stage 3 corrected simulation complete. Plot saved.")
