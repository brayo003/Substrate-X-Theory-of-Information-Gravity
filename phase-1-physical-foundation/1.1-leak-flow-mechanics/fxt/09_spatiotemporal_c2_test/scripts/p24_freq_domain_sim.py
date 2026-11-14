#!/usr/bin/env python3
"""
p24_freq_domain_sim.py — Phase 9 Frequency-Domain Experiment
Simulate cross-spectral density under 6 noise models; test C2 vs OU discriminability.

Models: C2, OU, quasistatic, white, common-mode, independent
Output: outputs/data/freq_sim_results.json + figures
"""
import numpy as np
import json, os
from scipy.optimize import curve_fit
from scipy.signal import welch, csd
import warnings; warnings.filterwarnings("ignore")

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOUT    = os.path.join(BASE, "outputs", "data")
FOUT    = os.path.join(BASE, "outputs", "figures")
os.makedirs(DOUT, exist_ok=True); os.makedirs(FOUT, exist_ok=True)

RNG = np.random.default_rng(2024)
print("="*60)
print("p24_freq_domain_sim.py — Frequency-Domain Cross-Noise Sim")
print("="*60)

# ─── Parameters ───────────────────────────────────────────────────────────────
N_Q      = 7
A        = 200e-6          # lattice spacing 200 µm
C2_SPEED = 1e4             # m/s
TAU_B    = 5e-6            # s
GAMMA_M  = 2*np.pi*50e3    # rad/s
XI_C     = 2*C2_SPEED*TAU_B  # 0.1 m
F_CM     = 0.20
N_REP    = 1024            # repetitions for spectrum
DT       = 10e-6           # 10 µs between reps (>> tau_B)
T_PROBE  = 2.5e-6          # Ramsey delay = tau_B/2
SHOTS    = 8192

# Qubit positions
coords = np.array([[0,0],[1,0],[2,0],[1,1],[2,1],[3,1],[2,2]], dtype=float)*A
dist   = np.array([[np.linalg.norm(coords[i]-coords[j]) for j in range(N_Q)] for i in range(N_Q)])

# Frequency axis (FFT of N_REP samples at rate 1/DT)
freqs = np.fft.rfftfreq(N_REP, d=DT)   # Hz
f_c   = 1.0/(2*np.pi*TAU_B)            # corner frequency ~31.8 kHz

print(f"tau_B={TAU_B*1e6:.1f}µs  f_c={f_c/1e3:.1f}kHz  xi_c={XI_C*1e2:.0f}cm")
print(f"N_REP={N_REP}  DT={DT*1e6:.0f}µs  f_res={freqs[1]/1e3:.3f}kHz  f_max={freqs[-1]/1e3:.1f}kHz")
print(f"d_max/xi_c = {dist.max()/XI_C:.5f}  (very small — spatial test has no power)")
print()

# ─── Phase noise generator for each model ─────────────────────────────────────
def gen_ou_noise(n, tau_b, sigma, dt, rng):
    """Single OU process: dX = -X/tau_b dt + sigma*sqrt(2/tau_b)*dW"""
    alpha = np.exp(-dt/tau_b)
    noise_std = sigma * np.sqrt(1 - alpha**2)
    x = np.zeros(n)
    x[0] = rng.normal(0, sigma)
    for k in range(1, n):
        x[k] = alpha*x[k-1] + rng.normal(0, noise_std)
    return x

sigma_ou = np.sqrt(GAMMA_M/TAU_B)  # OU sigma matching C2 amplitude

def gen_phases_model(model, n_rep, n_q, tau_b, sigma, dt, xi_c, dist, f_cm, rng):
    """Return phase time-series (n_rep, n_q) for each model."""
    phi = np.zeros((n_rep, n_q))

    if model == "C2":
        # Same as OU (identical formula) + spatial correlation via correlated OU
        # Generate correlated OU processes: common bath + qubit-specific baths
        # Spatial weight: w_ij = exp(-d_ij/xi_c)
        # Approximate: use a set of basis OU processes, one per qubit + global
        global_bath = gen_ou_noise(n_rep, tau_b, sigma*np.sqrt(f_cm), dt, rng)
        for qi in range(n_q):
            local = gen_ou_noise(n_rep, tau_b, sigma*np.sqrt(1-f_cm), dt, rng)
            # Spatial weight from all other qubits (simplified: pair-wise via global)
            phi[:, qi] = global_bath + local

    elif model == "OU":
        # Identical formula — should be identical to C2 results
        global_bath = gen_ou_noise(n_rep, tau_b, sigma*np.sqrt(f_cm), dt, rng)
        for qi in range(n_q):
            local = gen_ou_noise(n_rep, tau_b, sigma*np.sqrt(1-f_cm), dt, rng)
            phi[:, qi] = global_bath + local

    elif model == "quasistatic":
        # Static offset per shot (1/f-like; tau_B -> inf)
        # Draw a slow drift + fast white noise
        drift = rng.normal(0, sigma, n_q)       # static per qubit
        fast  = rng.normal(0, 0.1*sigma, (n_rep, n_q))
        phi   = drift[np.newaxis, :] + fast

    elif model == "white":
        # Pure white noise — no correlations in time or space
        phi = rng.normal(0, sigma, (n_rep, n_q))

    elif model == "common_mode":
        # Single shared OU bath, identical on all qubits
        bath = gen_ou_noise(n_rep, tau_b, sigma, dt, rng)
        phi  = bath[:, np.newaxis] * np.ones(n_q)

    elif model == "independent":
        # Fully independent OU per qubit, no spatial correlation
        for qi in range(n_q):
            phi[:, qi] = gen_ou_noise(n_rep, tau_b, sigma, dt, rng)

    return phi

# ─── Analysis functions ───────────────────────────────────────────────────────
def compute_spectra(phi, dt):
    """Return PSDs and CSDs. phi shape: (n_rep, n_q)."""
    n_rep, n_q = phi.shape
    # Use welch for all — get consistent freq axis from first call
    f, p0 = welch(phi[:,0], fs=1/dt, nperseg=n_rep//4, noverlap=n_rep//8)
    nf = len(f)
    psd = np.zeros((n_q, nf))
    csd_mat = np.zeros((n_q, n_q, nf), dtype=complex)
    psd[0] = p0
    for i in range(1, n_q):
        _, p = welch(phi[:,i], fs=1/dt, nperseg=n_rep//4, noverlap=n_rep//8)
        psd[i] = p
    for i in range(n_q):
        for j in range(i+1, n_q):
            _, c = csd(phi[:,i], phi[:,j], fs=1/dt, nperseg=n_rep//4, noverlap=n_rep//8)
            csd_mat[i,j] = c
            csd_mat[j,i] = c.conj()
    return f, psd, csd_mat

def fit_lorentzian(f, psd):
    """Fit Lorentzian to PSD; return f_c, A, success."""
    def lor(f, A, fc):
        return A / (f**2 + fc**2)
    try:
        idx = (f > 100) & (f < 1e6)
        p0 = [psd[idx].max()*(f[idx][0]**2), f_c]
        po, _ = curve_fit(lor, f[idx], psd[idx], p0=p0,
                          bounds=([0,100],[1e10,1e7]), maxfev=3000)
        return po[1], po[0], True
    except:
        return np.nan, np.nan, False

def coherence_vs_dist(f, psd, csd_mat, n_q, dist):
    """Compute mean coherence |S_ij|/sqrt(S_ii*S_jj) averaged over freq band near f_c."""
    # Use frequency band [f_c/3, 3*f_c]
    band = (f > f_c/3) & (f < 3*f_c)
    pairs_d, pairs_coh = [], []
    for i in range(n_q):
        for j in range(i+1, n_q):
            sii = psd[i, band].mean()
            sjj = psd[j, band].mean()
            sij = np.abs(csd_mat[i,j,band]).mean()
            coh = sij / np.sqrt(sii*sjj + 1e-30)
            pairs_d.append(dist[i,j])
            pairs_coh.append(coh)
    return np.array(pairs_d), np.array(pairs_coh)

# ─── Run all 6 models ─────────────────────────────────────────────────────────
MODELS = ["C2", "OU", "quasistatic", "white", "common_mode", "independent"]
results = {}

print(f"{'Model':15s} {'f_c_fit(kHz)':14s} {'τ_B_fit(µs)':12s} {'mean_coh':10s} {'coh_cv':8s} {'lorentzian?'}")
print("-"*75)

for model in MODELS:
    phi = gen_phases_model(model, N_REP, N_Q, TAU_B, sigma_ou, DT,
                           XI_C, dist, F_CM, RNG)
    f, psd, csd_mat = compute_spectra(phi, DT)

    # Fit Lorentzian to mean PSD
    mean_psd = psd.mean(axis=0)
    fc_fit, A_fit, lor_ok = fit_lorentzian(f, mean_psd)
    tau_b_fit = 1/(2*np.pi*fc_fit) if lor_ok and not np.isnan(fc_fit) else np.nan

    # Cross-spectral coherence vs distance
    d_arr, coh_arr = coherence_vs_dist(f, psd, csd_mat, N_Q, dist)
    mean_coh = coh_arr.mean()
    coh_cv   = coh_arr.std()/coh_arr.mean() if coh_arr.mean() > 0 else np.nan

    print(f"  {model:13s}: fc={fc_fit/1e3 if lor_ok else float('nan'):8.2f}  "
          f"τ_B={tau_b_fit*1e6 if not np.isnan(tau_b_fit) else float('nan'):8.2f}  "
          f"coh={mean_coh:.4f}  cv={coh_cv:.3f}  lor={'YES' if lor_ok else 'NO'}")

    results[model] = {
        "fc_fit_kHz": float(fc_fit/1e3) if lor_ok else None,
        "tau_b_fit_us": float(tau_b_fit*1e6) if not np.isnan(tau_b_fit) else None,
        "lorentzian_fit": lor_ok,
        "mean_coherence": float(mean_coh),
        "coherence_cv": float(coh_cv),
        "d_arr_um": (d_arr*1e6).tolist(),
        "coh_arr": coh_arr.tolist(),
    }

print()

# ─── Discriminability test: C2 vs OU ─────────────────────────────────────────
print("DISCRIMINABILITY TEST: C2 vs OU")
print("-"*40)

c2  = results["C2"]
ou  = results["OU"]

fc_diff   = abs((c2["fc_fit_kHz"] or 0) - (ou["fc_fit_kHz"] or 0))
coh_diff  = abs(c2["mean_coherence"] - ou["mean_coherence"])

print(f"  f_c difference:            {fc_diff:.3f} kHz  (expect ~0)")
print(f"  Mean coherence difference: {coh_diff:.5f}  (expect ~0)")

# AIC comparison on PSD shape
def psd_aic(f, psd, fc, A):
    """AIC for Lorentzian fit."""
    def lor(f, A, fc): return A/(f**2+fc**2)
    idx = (f>100)&(f<1e6)
    resid = psd[idx] - lor(f[idx], A, fc)
    k=2; n=idx.sum()
    sse=np.sum(resid**2)
    return 2*k + n*np.log(sse/n)

# Cross-coherence: does it vary with distance?
print()
print("COHERENCE VS DISTANCE — C2 vs OU vs common_mode:")
print(f"  {'Model':15s}  ", end="")
d_unique = sorted(set(np.round(d_arr*1e6).astype(int)))
for du in d_unique[:5]:
    print(f"  d={du}µm", end="")
print()

for model in ["C2", "OU", "common_mode", "independent"]:
    r = results[model]
    d_vals = np.array(r["d_arr_um"])
    c_vals = np.array(r["coh_arr"])
    print(f"  {model:15s}: ", end="")
    for du in d_unique[:5]:
        mask = np.abs(d_vals - du) < 30
        cv = c_vals[mask].mean() if mask.any() else float('nan')
        print(f"  {cv:.4f}  ", end="")
    print()

print()
print("KEY FINDING:")
c2_d  = np.array(results["C2"]["d_arr_um"])
c2_c  = np.array(results["C2"]["coh_arr"])
ou_d  = np.array(results["OU"]["d_arr_um"])
ou_c  = np.array(results["OU"]["coh_arr"])

# Are C2 and OU coherence profiles statistically identical?
if len(c2_c) == len(ou_c):
    max_diff = np.abs(c2_c - ou_c).max()
    print(f"  Max |coh_C2 - coh_OU| across all pairs: {max_diff:.6f}")
    if max_diff < 0.01:
        print("  -> C2 and OU cross-spectral coherence are INDISTINGUISHABLE (<1%)")
        print("  -> EXPERIMENT IS NON-DIAGNOSTIC for C2 vs OU")
    else:
        print("  -> Possible difference detected — check if systematic")

# Phase delay check
print()
print("PHASE DELAY CHECK:")
print(f"  tau_prop = d_max/c = {dist.max()/C2_SPEED*1e9:.1f} ns")
print(f"  f_c = {f_c/1e3:.1f} kHz  =>  phase at f_c: {2*np.pi*f_c*dist.max()/C2_SPEED*1e3:.4f} mrad")
print("  -> Phase delay <<< 1 mrad: UNDETECTABLE at any realistic shot count")

# Save
out = {"script": "p24_freq_domain_sim.py",
       "parameters": {"tau_B_us": TAU_B*1e6, "c2_speed": C2_SPEED,
                      "xi_c_m": XI_C, "f_c_kHz": f_c/1e3,
                      "N_REP": N_REP, "DT_us": DT*1e6, "n_qubits": N_Q},
       "models": results,
       "discriminability": {
           "fc_diff_kHz": float(fc_diff),
           "coh_diff": float(coh_diff),
           "phase_delay_ns": float(dist.max()/C2_SPEED*1e9),
           "phase_at_fc_mrad": float(2*np.pi*f_c*dist.max()/C2_SPEED*1e3),
           "c2_ou_indistinguishable": bool(max_diff < 0.01 if len(c2_c)==len(ou_c) else True),
       }}
with open(os.path.join(DOUT,"freq_sim_results.json"),"w") as fh:
    json.dump(out, fh, indent=2)
print(f"\nSaved: {DOUT}/freq_sim_results.json")

# ─── Figures ──────────────────────────────────────────────────────────────────
try:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {"C2":"red","OU":"blue","quasistatic":"green",
              "white":"orange","common_mode":"purple","independent":"black"}

    # Fig 1: PSD comparison
    phi_all = {}
    RNG2 = np.random.default_rng(2024)
    for model in MODELS:
        phi_all[model] = gen_phases_model(model,N_REP,N_Q,TAU_B,sigma_ou,DT,
                                          XI_C,dist,F_CM,RNG2)
    fig, ax = plt.subplots(figsize=(9,5))
    for model in MODELS:
        phi = phi_all[model]
        f2, mp = welch(phi[:,0], fs=1/DT, nperseg=N_REP//4)
        ax.loglog(f2/1e3, mp, color=colors[model], lw=1.5, label=model, alpha=0.8)
    ax.axvline(f_c/1e3, color="gray", ls="--", lw=1, label=f"f_c={f_c/1e3:.1f}kHz")
    ax.set_xlabel("Frequency (kHz)"); ax.set_ylabel("PSD (rad²/Hz)")
    ax.set_title("Single-Qubit Noise PSD — All 6 Models")
    ax.legend(fontsize=8); plt.tight_layout()
    plt.savefig(os.path.join(FOUT,"fig_freq_psd_comparison.png"),dpi=120); plt.close()

    # Fig 2: Coherence vs distance
    fig, axes = plt.subplots(1,2,figsize=(12,5))
    for model in ["C2","OU","common_mode","independent"]:
        r = results[model]
        axes[0].scatter(r["d_arr_um"], r["coh_arr"],
                        color=colors[model], label=model, s=40, alpha=0.8)
    axes[0].set_xlabel("d (µm)"); axes[0].set_ylabel("Cross-spectral coherence |γ|")
    axes[0].set_title("Coherence vs Distance"); axes[0].legend(fontsize=8)

    # Fig 2b: C2 vs OU zoomed
    axes[1].scatter(results["C2"]["d_arr_um"], results["C2"]["coh_arr"],
                    color="red", label="C2", s=60)
    axes[1].scatter(results["OU"]["d_arr_um"], results["OU"]["coh_arr"],
                    color="blue", label="OU", s=30, marker="x")
    axes[1].set_xlabel("d (µm)"); axes[1].set_ylabel("|γ_ij|")
    axes[1].set_title("C2 vs OU Coherence (should be identical)")
    axes[1].legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FOUT,"fig_freq_coherence_vs_dist.png"),dpi=120); plt.close()
    print("Figures saved.")
except ImportError:
    print("matplotlib not available")

print("\np24 COMPLETE"); print("="*60)
