#!/usr/bin/env python3
"""
p17_ramsey_sim.py — Phase 9, Step 1
Synthetic Ramsey Data Generator using C2 [EXACT-PHI] coherence

Platform: Pure simulation (NumPy/SciPy), no QPU
Geometry: 7-qubit IBM heavy-hex (simulated Falcon r5)
Formula:  C(t) = exp(-Phi(t))  [EXACT-PHI from NM_PREDICTION_AUDIT.md]

Outputs:
  outputs/data/ramsey_sim.npz  — all Ramsey traces + metadata
  stdout: parameter summary
"""

import numpy as np
import os
import json

# ─── Paths ──────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_OUT = os.path.join(BASE, "outputs", "data")
os.makedirs(DATA_OUT, exist_ok=True)

# ─── Reproducibility ─────────────────────────────────────────────────────────
RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)

# ─── Injected Physical Parameters (PREREGISTERED) ────────────────────────────
# From 17_EXPERIMENT_DESIGN.md — set before any analysis

C2_SPEED_INJ   = 1.0e4       # m/s  — substrate propagation speed (injection)
TAU_B_INJ      = 5.0e-6      # s    — bath correlation time (5 µs)
GAMMA_M_INJ    = 2*np.pi*50e3  # rad/s — Markov dephasing rate (2π × 50 kHz)
NMP_INJ        = GAMMA_M_INJ * TAU_B_INJ  # dimensionless non-Markovianity parameter
XI_C_INJ       = 2 * C2_SPEED_INJ * TAU_B_INJ  # m — coherence length

F_COMMON_MODE  = 0.20        # fraction of noise that is common-mode across all qubits

print("=" * 60)
print("p17_ramsey_sim.py — C2 Synthetic Ramsey Generator")
print("=" * 60)
print(f"Injection parameters (PREREGISTERED):")
print(f"  c_C2         = {C2_SPEED_INJ:.3e} m/s")
print(f"  tau_B        = {TAU_B_INJ*1e6:.2f} µs")
print(f"  Gamma_M      = {GAMMA_M_INJ/(2*np.pi)/1e3:.1f} kHz")
print(f"  NMP          = {NMP_INJ:.3f}  (non-Markovian regime: NMP > 0.1)")
print(f"  xi_c         = {XI_C_INJ*1e6:.1f} µm  ({XI_C_INJ*1e2:.1f} cm)")
print(f"  f_common     = {F_COMMON_MODE:.0%}")
print()

# ─── Qubit Geometry: IBM heavy-hex 7-qubit (Falcon r5 simplified) ────────────
# Coordinates in METERS (IBM standard ~200 µm pitch)
A = 200e-6  # lattice spacing = 200 µm

QUBIT_COORDS = np.array([
    [0*A, 0*A],   # Q00
    [1*A, 0*A],   # Q01
    [2*A, 0*A],   # Q02
    [1*A, 1*A],   # Q03
    [2*A, 1*A],   # Q04
    [3*A, 1*A],   # Q05
    [2*A, 2*A],   # Q06
], dtype=float)  # shape (7, 2), units meters

N_QUBITS = len(QUBIT_COORDS)

# Compute pairwise distances
dist_matrix = np.zeros((N_QUBITS, N_QUBITS))
for i in range(N_QUBITS):
    for j in range(N_QUBITS):
        dist_matrix[i, j] = np.linalg.norm(QUBIT_COORDS[i] - QUBIT_COORDS[j])

print(f"Qubit geometry: {N_QUBITS} qubits, heavy-hex")
print(f"  Lattice spacing: {A*1e6:.0f} µm")
print(f"  Max separation:  {dist_matrix.max()*1e6:.0f} µm")
print(f"  xi_c / max_d:    {XI_C_INJ / dist_matrix.max():.1f}  "
      f"(> 1 means chip << coherence length)")
print()

# ─── Timing Grid ─────────────────────────────────────────────────────────────
N_DELAYS   = 50
T_MIN      = 100e-9    # 100 ns
T_MAX      = 500e-6    # 500 µs
SHOTS      = 8192

t_delays = np.logspace(np.log10(T_MIN), np.log10(T_MAX), N_DELAYS)

print(f"Timing: {N_DELAYS} delay points, {T_MIN*1e9:.0f} ns to {T_MAX*1e6:.0f} µs (log-spaced)")
print(f"Shots per point: {SHOTS}")
print()

# ─── [EXACT-PHI] Coherence Function ─────────────────────────────────────────
def phi_exact(t, gamma_m, tau_b):
    """
    C2 non-Markovian dephasing phase [EXACT-PHI]
    From NM_PREDICTION_AUDIT.md eq [EXACT-PHI], verified by nm_01_memory_kernel.py
    
    Phi(t) = gamma_m * tau_b * [t/tau_b - 1 + exp(-t/tau_b)]
    
    Args:
        t: time(s) in seconds (array or scalar)
        gamma_m: Markov dephasing rate [rad/s]
        tau_b: bath correlation time [s]
    Returns:
        Phi(t) — dephasing exponent (non-negative)
    """
    x = t / tau_b
    return gamma_m * tau_b * (x - 1.0 + np.exp(-x))

def coherence_exact(t, gamma_m, tau_b, omega_drive=0.0):
    """
    Ramsey coherence amplitude (magnitude of off-diagonal density matrix element)
    C(t) = exp(-Phi(t))
    With optional detuning oscillation: cos(omega_drive * t) * exp(-Phi(t))
    """
    return np.cos(omega_drive * t) * np.exp(-phi_exact(t, gamma_m, tau_b))

# ─── Spatial Correlation Model ───────────────────────────────────────────────
def spatial_corr_c2(d, xi_c):
    """
    C2 prediction for inter-qubit phase-noise correlation vs. separation d.
    Exponential decay (from 2D PRW at d >> lattice scale):
        corr(d) = exp(-d / xi_c)
    
    Note: the full K0 Bessel function from 02_2D_CORRELATION_DERIVATION.md
    reduces to this exponential for d >> a (lattice spacing). Since d/xi_c << 1
    here, all correlations will be near 1.
    """
    return np.exp(-d / xi_c)

# ─── Per-qubit Γ_M variation (realistic spread) ─────────────────────────────
# Real qubits have spread in T2* due to fabrication. Add ±30% log-normal spread.
log_spread = 0.3  # log-normal sigma
gamma_m_per_qubit = GAMMA_M_INJ * np.exp(
    rng.normal(0, log_spread, N_QUBITS)
)

# Per-qubit τ_B variation: smaller spread (bath correlation is more uniform)
tau_b_per_qubit = TAU_B_INJ * np.exp(
    rng.normal(0, 0.15, N_QUBITS)
)

print("Per-qubit parameters (with realistic fabrication spread):")
print(f"  {'Qubit':5s} {'Gamma_M (kHz)':14s} {'tau_B (µs)':11s} {'T2* (µs)':9s} {'NMP':6s}")
for q in range(N_QUBITS):
    T2star = 1.0 / (gamma_m_per_qubit[q] / (2*np.pi))  # rough T2* = 1/Gamma_M
    nmp_q = gamma_m_per_qubit[q] * tau_b_per_qubit[q]
    print(f"  Q{q:02d}   {gamma_m_per_qubit[q]/(2*np.pi)/1e3:12.1f}   "
          f"{tau_b_per_qubit[q]*1e6:9.2f}   "
          f"{T2star*1e6:7.2f}   "
          f"{nmp_q:6.3f}")
print()

# ─── Generate Ramsey Traces ──────────────────────────────────────────────────
# For each qubit: ideal coherence + shot noise (binomial)
#
# Measurement model:
#   P(|0>) = (1 + C(t)) / 2   (standard Ramsey readout probability)
#   n_counts ~ Binomial(SHOTS, P)
#   measured_signal = (2*n_counts/SHOTS - 1)  in [-1, +1]

N_NOISE_REAL = 500  # noise realizations for phase-noise correlation estimation

print(f"Generating {N_NOISE_REAL} noise realizations × {N_QUBITS} qubits × {N_DELAYS} points...")

# Correlated phase noise: each realization has common-mode + qubit-specific components
# Common-mode: same OU noise for all qubits (f_common fraction)
# Qubit-specific: independent OU noise (1 - f_common fraction)
#
# OU process for phase noise: dν/dt = -ν/τ_B + η_B(t)
# We approximate with a simple realization by drawing from the stationary distribution
# scaled by the accumulated-phase variance at each delay point.

# Phase accumulated at time t for a single qubit in one noise realization:
# δφ(t) ~ N(0, Var_phase(t)) where Var_phase(t) = 2 * Phi(t)
# Cross-qubit correlation: ρ_ij = F_cm + (1-F_cm) * spatial_corr(d_ij)

# Build correlation matrix for phase noise across qubits
# For a given delay t, the phase noise has covariance:
#   Cov(δφ_i, δφ_j; t) = 2*Phi(t;Q_i) * [f_cm + (1-f_cm)*exp(-d_ij/xi_c)] (approx equal Phi)

# Simplified: use MEAN tau_B for spatial correlation (spatial analysis is across qubits)
tau_b_mean = tau_b_per_qubit.mean()
gamma_m_mean = gamma_m_per_qubit.mean()

# Full spatial correlation matrix (injection values, used to generate noise)
spatial_corr_matrix = np.zeros((N_QUBITS, N_QUBITS))
for i in range(N_QUBITS):
    for j in range(N_QUBITS):
        d = dist_matrix[i, j]
        if i == j:
            spatial_corr_matrix[i, j] = 1.0
        else:
            sc = spatial_corr_c2(d, XI_C_INJ)
            spatial_corr_matrix[i, j] = F_COMMON_MODE + (1 - F_COMMON_MODE) * sc

print(f"  Spatial correlation at NN spacing (200µm): "
      f"{spatial_corr_c2(200e-6, XI_C_INJ):.6f}")
print(f"  Spatial correlation at max spacing ({dist_matrix.max()*1e6:.0f}µm): "
      f"{spatial_corr_c2(dist_matrix.max(), XI_C_INJ):.6f}")
print(f"  NOTE: all spatial correlations ≈ 1 (d/xi_c << 1).")
print(f"  Common-mode dominates spatial signal: f_cm = {F_COMMON_MODE:.0%}")
print()

# Cholesky decomposition for correlated noise generation
L_chol = np.linalg.cholesky(spatial_corr_matrix)

# Generate all Ramsey traces + phase noise realizations
# Shape: ramsey_traces[qubit, delay] = mean over shots
# Shape: phase_noise[realization, qubit, delay] = accumulated phase

ramsey_traces   = np.zeros((N_QUBITS, N_DELAYS))
ramsey_std      = np.zeros((N_QUBITS, N_DELAYS))
phase_noise_arr = np.zeros((N_NOISE_REAL, N_QUBITS, N_DELAYS))

for qi in range(N_QUBITS):
    for di, t in enumerate(t_delays):
        # Ideal coherence from [EXACT-PHI]
        ideal_coh = np.exp(-phi_exact(t, gamma_m_per_qubit[qi], tau_b_per_qubit[qi]))
        # Ramsey probability P(|0>) = (1 + C_ideal) / 2
        p_zero = (1.0 + ideal_coh) / 2.0
        # Shot noise via binomial
        counts = rng.binomial(SHOTS, p_zero, size=SHOTS)  # not needed per-shot
        # Actually: one measurement = SHOTS coin flips
        n_up = rng.binomial(SHOTS, p_zero)
        measured = (2.0 * n_up / SHOTS) - 1.0
        ramsey_traces[qi, di] = measured
        # Shot noise std estimate
        ramsey_std[qi, di] = np.sqrt(p_zero * (1 - p_zero) / SHOTS) * 2.0

# Generate correlated phase noise realizations
# At each delay point, phase variance = 2 * Phi(t; mean params)
# Draw from N(0, sqrt(2*Phi(t))) for each qubit, with cross-qubit correlation
for ri in range(N_NOISE_REAL):
    # Independent unit normals for each qubit
    z = rng.standard_normal(N_QUBITS)
    # Apply Cholesky to introduce cross-qubit correlation
    for di, t in enumerate(t_delays):
        var_phi = 2.0 * phi_exact(t, gamma_m_mean, tau_b_mean)
        sigma_phi = np.sqrt(max(var_phi, 1e-20))
        # Correlated phase noise: L @ z scaled by sigma_phi
        corr_noise = sigma_phi * (L_chol @ z)
        phase_noise_arr[ri, :, di] = corr_noise

print("Ramsey traces generated.")
print(f"  Shape: {ramsey_traces.shape}  (qubits × delays)")
print(f"  Phase noise array: {phase_noise_arr.shape}  (realizations × qubits × delays)")
print()

# ─── Quick sanity check: T2* estimates ──────────────────────────────────────
print("Sanity check — estimated T2* from Ramsey traces (threshold at C = 1/e):")
for qi in range(N_QUBITS):
    # Find where trace crosses 1/e
    inv_e = 1.0 / np.e
    above = ramsey_traces[qi] > inv_e
    if above.any() and not above.all():
        idx = np.where(above)[0][-1]
        t2star_est = t_delays[idx] if idx < N_DELAYS - 1 else t_delays[-1]
        print(f"  Q{qi:02d}: T2* ≈ {t2star_est*1e6:.1f} µs  "
              f"(tau_B = {tau_b_per_qubit[qi]*1e6:.2f} µs, "
              f"NMP = {gamma_m_per_qubit[qi]*tau_b_per_qubit[qi]:.3f})")
    else:
        print(f"  Q{qi:02d}: T2* > {T_MAX*1e6:.0f} µs (trace did not decay to 1/e)")
print()

# ─── Save Output ─────────────────────────────────────────────────────────────
out_path = os.path.join(DATA_OUT, "ramsey_sim.npz")
np.savez(out_path,
    # Geometry
    qubit_coords=QUBIT_COORDS,
    dist_matrix=dist_matrix,
    n_qubits=np.array(N_QUBITS),
    lattice_spacing=np.array(A),
    # Timing
    t_delays=t_delays,
    n_delays=np.array(N_DELAYS),
    shots=np.array(SHOTS),
    # Injection parameters
    c2_speed_inj=np.array(C2_SPEED_INJ),
    tau_b_inj=np.array(TAU_B_INJ),
    gamma_m_inj=np.array(GAMMA_M_INJ),
    nmp_inj=np.array(NMP_INJ),
    xi_c_inj=np.array(XI_C_INJ),
    f_common_mode=np.array(F_COMMON_MODE),
    # Per-qubit parameters
    gamma_m_per_qubit=gamma_m_per_qubit,
    tau_b_per_qubit=tau_b_per_qubit,
    # Measured data
    ramsey_traces=ramsey_traces,
    ramsey_std=ramsey_std,
    # Phase noise realizations
    phase_noise_arr=phase_noise_arr,
    spatial_corr_matrix=spatial_corr_matrix,
    # Metadata
    rng_seed=np.array(RNG_SEED),
)
print(f"Saved: {out_path}")

# Also save JSON metadata for human inspection
meta = {
    "script": "p17_ramsey_sim.py",
    "date": "2026-08-20",
    "platform": "pure simulation",
    "n_qubits": N_QUBITS,
    "n_delays": N_DELAYS,
    "shots": SHOTS,
    "n_noise_real": N_NOISE_REAL,
    "injection": {
        "c2_speed_m_per_s": C2_SPEED_INJ,
        "tau_B_us": TAU_B_INJ * 1e6,
        "gamma_M_kHz": GAMMA_M_INJ / (2*np.pi) / 1e3,
        "NMP": float(NMP_INJ),
        "xi_c_um": XI_C_INJ * 1e6,
        "f_common_mode": F_COMMON_MODE,
    },
    "geometry": {
        "layout": "heavy-hex (Falcon r5 simplified)",
        "lattice_spacing_um": A * 1e6,
        "max_separation_um": float(dist_matrix.max() * 1e6),
        "d_over_xi_c_max": float(dist_matrix.max() / XI_C_INJ),
    },
    "known_limitations": [
        "d/xi_c << 1 for all pairs: spatial correlations nearly flat",
        "Common-mode fraction dominates spatial signal",
        "Simulation not hardware: no gate errors, crosstalk, or calibration drift",
        "EXACT-PHI == OU process: temporal data alone cannot distinguish C2 from OU",
    ]
}
meta_path = os.path.join(DATA_OUT, "ramsey_sim_meta.json")
with open(meta_path, "w") as f:
    json.dump(meta, f, indent=2)
print(f"Saved: {meta_path}")
print()
print("p17 COMPLETE — ramsey_sim.npz ready for p18 (fitting)")
print("=" * 60)
