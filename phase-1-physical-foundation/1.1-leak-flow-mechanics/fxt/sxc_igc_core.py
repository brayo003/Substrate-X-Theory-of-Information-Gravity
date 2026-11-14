#!/usr/bin/env python3
"""
sxc_igc_core.py
Canonical shared module for SXC-IGC pre-hardware audit.

VERSION: 2  (corrected parity-based joint estimator)
SEED policy: callers pass their own RNG; this module is stateless.

Contents:
  1. Hardware constants (Brisbane calibration)
  2. Qubit geometry constructor
  3. Physical model: Ramsey decay (exact non-Markovian)
  4. CORRECT joint measurement estimator (meas_joint)
  5. Synthetic data generator (generate_dataset)
  6. Spatial covariance models: M0,M1,M2,M5,M7,M8,M9,M10,M11
  7. C_Gamma extractor
  8. Joint K0+null fitter (fit_joint_k0)
  9. Null-only fitter (fit_null_family)
 10. Two-stage test procedure
 11. QPU budget checker

ESTIMATOR CORRECTNESS (VERIFIED):
  IBM simultaneous two-qubit X-basis measurement gives 4 outcome counts.
  The correct estimator for <sigma_x,i * sigma_x,j> is the parity estimator:
    ZZ_est = (n_++ - n_+- - n_-+ + n_--) / N_shots
  NOT the product of two independent single-qubit measurements.
  The prior bug (applying single-qubit readout model to W_i*W_j) introduced
  a constant +0.137 additive bias, invalidating all prior simulation results.
  See ESTIMATOR_AUDIT_FINAL.md for full derivation and proof.
"""

import numpy as np
from scipy.special import k0 as bessel_k0
from scipy.optimize import curve_fit

# ── Hardware constants (Brisbane, from 06_datasets/props_brisbane.json) ──────
A_M           = 200e-6       # m, heavy-hex lattice spacing (UV cutoff)
T2_MEDIAN     = 150e-6       # s, median T2
T1_MEDIAN     = 300e-6       # s, median T1 for selected qubits
GAMMA_PHI_0   = 1.0/T2_MEDIAN   # rad/s
GAMMA_RELAX_0 = 1.0/(2*T1_MEDIAN)
TAU_B_DEFAULT = 5e-6         # s, substrate bath correlation time
READOUT_ERR   = 0.020        # symmetric per-qubit readout misclassification
XTALK_TRUE    = 0.015        # EM crosstalk amplitude (nearest-neighbor)
XI_EM_DEFAULT = 300e-6       # m, EM crosstalk decay length
QPU_BUDGET_S  = 600.0        # s, total QPU time budget


# ─────────────────────────────────────────────────────────────────────────────
# 1. QUBIT GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────

def make_geometry(n_qubits=12, spacing=A_M):
    """
    Linear chain of n_qubits with given spacing.
    Returns: positions (n_qubits,), pairs list [(i,j,r_ij), ...], R_ARR (n_pairs,)
    """
    positions = np.arange(n_qubits) * spacing
    pairs = [(i, j, abs(positions[i] - positions[j]))
             for i in range(n_qubits) for j in range(i+1, n_qubits)]
    R_ARR = np.array([p[2] for p in pairs])
    return positions, pairs, R_ARR


# ─────────────────────────────────────────────────────────────────────────────
# 2. PHYSICAL MODEL: EXACT NON-MARKOVIAN RAMSEY DECAY
# ─────────────────────────────────────────────────────────────────────────────

def ramsey(t_arr, gamma_phi=GAMMA_PHI_0, gamma_relax=GAMMA_RELAX_0,
           tau_B=TAU_B_DEFAULT):
    """
    Exact non-Markovian Ramsey decay (Kubo 1963, DERIVED from PRW substrate).
    W(t) = exp(-Phi(t)) * exp(-gamma_relax * t)
    Phi(t) = gamma_phi * tau_B * [t/tau_B - 1 + exp(-t/tau_B)]
    Valid for all t; reduces to exp(-gamma_phi*t) as tau_B -> 0.
    """
    t = np.asarray(t_arr)
    phi = gamma_phi * tau_B * (t / tau_B - 1.0 + np.exp(-t / tau_B))
    return np.exp(-phi) * np.exp(-gamma_relax * t)


# ─────────────────────────────────────────────────────────────────────────────
# 3. CORRECT JOINT MEASUREMENT ESTIMATOR
# ─────────────────────────────────────────────────────────────────────────────

def meas_joint(Wi_true, Wj_true, ZiZj_true, n_shots, rng,
               readout_err=READOUT_ERR):
    """
    Correct IBM simultaneous two-qubit X-basis measurement.

    DERIVATION (see ESTIMATOR_AUDIT_FINAL.md §2):
    For two qubits in state rho, measuring both in X basis, the four joint
    outcome probabilities are:
      P(+,+) = (1 + Zi + Zj + ZiZj) / 4
      P(+,-) = (1 + Zi - Zj - ZiZj) / 4
      P(-,+) = (1 - Zi + Zj - ZiZj) / 4
      P(-,-) = (1 - Zi - Zj + ZiZj) / 4
    where Zi = <sigma_x,i>, Zj = <sigma_x,j>, ZiZj = <sigma_x,i sigma_x,j>.

    Independent per-qubit readout error e flips each qubit's outcome:
      P'(a,b) = sum_{a',b'} P(a',b') * flip_i(a',a) * flip_j(b',b)
    where flip(+,+) = 1-e, flip(+,-) = e.

    Estimators from the four counts (n_++, n_+-, n_-+, n_--):
      Zi_est  = (n_++ + n_+- - n_-+ - n_--) / N
      Zj_est  = (n_++ - n_+- + n_-+ - n_--) / N
      ZZ_est  = (n_++ - n_+- - n_-+ + n_--) / N   [parity]

    Returns: Wi_est, Wj_est, ZZ_est (all shape matching input arrays)

    PROOF OF UNBIASEDNESS:
      E[ZZ_est] = E[(n_++ - n_+- - n_-+ + n_--)] / N
      E[n_++] - E[n_+-] - E[n_-+] + E[n_--]
        = N * [P'(+,+) - P'(+,-) - P'(-,+) + P'(-,-)]
      After expanding readout error:
        = N * (1-2e)^2 * ZiZj
    So E[ZZ_est] = (1-2e)^2 * ZiZj  [biased by readout, but known bias].
    The denominator Wi_est * Wj_est = (1-2e)*Zi * (1-2e)*Zj = (1-2e)^2 * Zi*Zj.
    Therefore C_ij = ZZ_est / (Wi_est * Wj_est) = ZiZj / (Zi*Zj) + noise.
    The readout error cancels in the ratio.  QED.
    """
    Wi  = np.asarray(Wi_true,    dtype=float)
    Wj  = np.asarray(Wj_true,    dtype=float)
    ZZ  = np.asarray(ZiZj_true,  dtype=float)
    e   = readout_err

    # Joint probabilities (ideal)
    p_pp = np.clip((1 + Wi + Wj + ZZ) / 4, 0, 1)
    p_pm = np.clip((1 + Wi - Wj - ZZ) / 4, 0, 1)
    p_mp = np.clip((1 - Wi + Wj - ZZ) / 4, 0, 1)
    p_mm = np.clip((1 - Wi - Wj + ZZ) / 4, 0, 1)

    # Apply independent per-qubit readout error
    p_pp_r = (1-e)*(1-e)*p_pp + (1-e)*e*p_pm + e*(1-e)*p_mp + e*e*p_mm
    p_pm_r = (1-e)*e*p_pp     + (1-e)*(1-e)*p_pm + e*e*p_mp + e*(1-e)*p_mm
    p_mp_r = e*(1-e)*p_pp     + e*e*p_pm + (1-e)*(1-e)*p_mp + (1-e)*e*p_mm
    p_mm_r = e*e*p_pp         + e*(1-e)*p_pm + (1-e)*e*p_mp + (1-e)*(1-e)*p_mm

    # Normalise
    tot = p_pp_r + p_pm_r + p_mp_r + p_mm_r
    p_pp_r /= tot; p_pm_r /= tot; p_mp_r /= tot; p_mm_r /= tot

    # Multinomial sampling
    probs = np.stack([p_pp_r, p_pm_r, p_mp_r, p_mm_r], axis=-1)
    scalar = probs.ndim == 1
    if scalar:
        probs = probs[np.newaxis, :]

    n_pp = np.zeros(len(probs)); n_pm = np.zeros(len(probs))
    n_mp = np.zeros(len(probs)); n_mm = np.zeros(len(probs))
    for idx in range(len(probs)):
        c = rng.multinomial(n_shots, probs[idx])
        n_pp[idx], n_pm[idx], n_mp[idx], n_mm[idx] = c

    N = float(n_shots)
    Wi_est  = (n_pp + n_pm - n_mp - n_mm) / N
    Wj_est  = (n_pp - n_pm + n_mp - n_mm) / N
    ZZ_est  = (n_pp - n_pm - n_mp + n_mm) / N

    if scalar:
        return float(Wi_est[0]), float(Wj_est[0]), float(ZZ_est[0])
    return Wi_est, Wj_est, ZZ_est


# ─────────────────────────────────────────────────────────────────────────────
# 4. SPATIAL COVARIANCE MODELS
# All return arrays of shape (n_pairs,) for R_ARR input.
# ─────────────────────────────────────────────────────────────────────────────

def C_M0(R_ARR):
    """M0: Independent Markovian. No spatial correlation."""
    return np.zeros_like(R_ARR)

def C_M1_K0(R_ARR, xi_c, sub_frac, a=A_M):
    """M1: SXC-IGC substrate. K0 Bessel spatial covariance."""
    if xi_c <= a * 2:
        return np.zeros_like(R_ARR)
    norm = bessel_k0(a / xi_c)
    return sub_frac * bessel_k0(R_ARR / xi_c) / norm

def C_M2_exp(R_ARR, xi, amp):
    """M2: Single exponential / OU bath."""
    return amp * np.exp(-R_ARR / xi)

def C_M5_crosstalk(R_ARR, xi_em=XI_EM_DEFAULT, amp=XTALK_TRUE):
    """M5: EM/circuit crosstalk. Short-range exponential."""
    return amp * np.exp(-R_ARR / xi_em)

def C_M7_powerlaw(R_ARR, amp, r0, alpha):
    """
    M7: Power-law covariance C(r) = amp * (r/r0)^{-alpha}.
    Physical motivation: 1/f noise, diffusive processes, long-range correlations
    from shared control electronics. Exponent alpha in [0.3, 2.0].
    Diverges at r->0; clipped at r >= UV_CUT.
    """
    r = np.maximum(R_ARR, A_M)
    return amp * (r / r0) ** (-alpha)

def C_M8_gaussian(R_ARR, amp, sigma):
    """
    M8: Gaussian covariance C(r) = amp * exp(-(r/sigma)^2).
    Physical motivation: correlated control-line noise with finite bandwidth,
    spatially uniform driving from global heating, Gaussian coupling profile.
    """
    return amp * np.exp(-(R_ARR / sigma) ** 2)

def C_M9_twobath(R_ARR, amp1, xi1, amp2, xi2):
    """
    M9: Two-bath / multi-scale covariance.
    C(r) = amp1*exp(-r/xi1) + amp2*exp(-r/xi2), xi1 != xi2.
    Physical motivation: two independent conventional noise sources (e.g.,
    substrate thermal phonons at short range + correlated control-line noise
    at longer range).
    """
    return amp1 * np.exp(-R_ARR / xi1) + amp2 * np.exp(-R_ARR / xi2)

def C_M10_stretched_exp(R_ARR, amp, xi, beta):
    """
    M10: Stretched exponential C(r) = amp * exp(-(r/xi)^beta), beta in (0,1].
    Physical motivation: disorder-averaged exponential bath with distributed
    coupling strengths. For beta<1, heavier tails than pure exponential.
    """
    return amp * np.exp(-(R_ARR / xi) ** beta)

def C_M11_matern(R_ARR, amp, xi, nu=1.5):
    """
    M11: Matérn covariance with nu=1.5 (once-differentiable).
    C(r) = amp * (1 + sqrt(3)*r/xi) * exp(-sqrt(3)*r/xi).
    Physical motivation: smooth spatially correlated noise with finite range,
    commonly used in geostatistics and spatial random fields.
    """
    x = np.sqrt(3) * R_ARR / xi
    return amp * (1 + x) * np.exp(-x)

# Full conventional null family (physically motivated, not exhaustive)
NULL_FAMILY = {
    "M0": lambda r, **kw: C_M0(r),
    "M2": lambda r, xi=600e-6, amp=0.10, **kw: C_M2_exp(r, xi, amp),
    "M5": lambda r, **kw: C_M5_crosstalk(r),
    "M7_alpha0.5": lambda r, **kw: C_M7_powerlaw(r, 0.08, A_M, 0.5),
    "M7_alpha1.0": lambda r, **kw: C_M7_powerlaw(r, 0.06, A_M, 1.0),
    "M8": lambda r, **kw: C_M8_gaussian(r, 0.10, 600e-6),
    "M9": lambda r, **kw: C_M9_twobath(r, 0.08, 250e-6, 0.05, 1500e-6),
    "M10": lambda r, **kw: C_M10_stretched_exp(r, 0.10, 600e-6, 0.7),
    "M11": lambda r, **kw: C_M11_matern(r, 0.10, 600e-6),
}


# ─────────────────────────────────────────────────────────────────────────────
# 5. SYNTHETIC DATA GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_dataset(R_ARR, pairs, t_arr, n_shots, rng,
                     C_spatial,           # (n_pairs,) array of true C_Gamma values
                     gamma_phi_mean=GAMMA_PHI_0,
                     gamma_phi_spread=0.10,  # fractional qubit-to-qubit spread
                     gamma_relax=GAMMA_RELAX_0,
                     tau_B=TAU_B_DEFAULT,
                     n_qubits=12):
    """
    Generate one synthetic dataset using the CORRECT joint measurement estimator.

    Inputs:
      R_ARR     : (n_pairs,) separation array
      pairs     : list of (i, j, r_ij) tuples
      t_arr     : (n_time,) measurement time points
      n_shots   : shots per circuit
      rng       : numpy Generator instance (caller-owned)
      C_spatial : (n_pairs,) true spatial correlation profile
      gamma_phi_mean, _spread: per-qubit Gamma_phi variation
      gamma_relax, tau_B: T1 and non-Markovian parameters

    Returns:
      C_gamma_space : (n_pairs, n_time) array of C_Gamma estimates per time point
                      Each entry: ln(C_ij(t)) / (Gamma_phi_est * t)
                      NaN where C_ij <= 0 or undefined.
      gamma_phi_est : float, mean estimated Gamma_phi (used for extraction)

    Physical model (DERIVED, see observable_mapping_audit.md):
      ZiZj_true(t) = Wi(t) * Wj(t) * exp(C_spatial[pair] * Gamma_phi * t)
      C_ij(t) = ZiZj_meas / (Wi_meas * Wj_meas)   [from parity estimator]
      C_Gamma(r) = ln(C_ij(t)) / (Gamma_phi * t)

    The readout error cancels in the ratio C_ij = ZZ/(Wi*Wj) to leading order
    (proved in meas_joint docstring).
    """
    n_time  = len(t_arr)
    n_pairs = len(pairs)

    # Per-qubit Gamma_phi variation (models calibration uncertainty)
    gph_i = gamma_phi_mean * (1.0 + gamma_phi_spread * rng.standard_normal(n_qubits))
    gph_i = np.clip(gph_i, gamma_phi_mean * 0.5, gamma_phi_mean * 2.0)
    gamma_phi_est = float(np.mean(gph_i))

    # Per-qubit Ramsey signals at all time points
    W_all = np.array([ramsey(t_arr, gph_i[k], gamma_relax, tau_B)
                      for k in range(n_qubits)])

    C_gamma_space = np.full((n_pairs, n_time), np.nan)

    for pi, (qi, qj, _) in enumerate(pairs):
        Wi_t  = W_all[qi]   # (n_time,)
        Wj_t  = W_all[qj]
        # True joint observable under correlated Gaussian dephasing (DERIVED)
        ZZ_t  = Wi_t * Wj_t * np.exp(C_spatial[pi] * gamma_phi_mean * t_arr)

        # Apply correct joint measurement estimator
        Wi_m, Wj_m, ZZ_m = meas_joint(Wi_t, Wj_t, ZZ_t, n_shots, rng)

        # Estimate C_ij(t) = ZZ_m / (Wi_m * Wj_m)
        denom = Wi_m * Wj_m
        ok    = np.abs(denom) > 1e-6
        C_ij  = np.where(ok, ZZ_m / denom, np.nan)

        # Extract C_Gamma via log transform
        with np.errstate(divide='ignore', invalid='ignore'):
            C_gamma_space[pi] = np.where(
                (C_ij > 1e-4) & ok,
                np.log(C_ij) / (gamma_phi_est * t_arr),
                np.nan)

    return C_gamma_space, gamma_phi_est


def extract_C_gamma(C_gamma_space):
    """
    Average C_Gamma over time axis.
    Returns: C_gamma (n_pairs,), C_gamma_err (n_pairs,)
    """
    with np.errstate(all='ignore'):
        n_valid = np.sum(~np.isnan(C_gamma_space), axis=1).clip(1)
        C_gamma     = np.nanmean(C_gamma_space, axis=1)
        C_gamma_err = np.nanstd(C_gamma_space, axis=1) / np.sqrt(n_valid)
    # Replace pathological values
    C_gamma     = np.where(np.isfinite(C_gamma), C_gamma, np.nan)
    C_gamma_err = np.where(C_gamma_err > 0, C_gamma_err, 0.02)
    return C_gamma, C_gamma_err


# ─────────────────────────────────────────────────────────────────────────────
# 6. FITTERS
# ─────────────────────────────────────────────────────────────────────────────

def fit_k0_plus_null(R_v, C_v, e_v, xi_hint, xi_em_meas, rng,
                     xtalk_cal_error=0.01):
    """
    Full model: amp_K0 * K0(r/xi_K0)/K0(a/xi_K0) + amp_xt * exp(-r/xi_xt)
    Null model: amp_xt * exp(-r/xi_xt)
    Returns: llr (>0 = K0 preferred), amp_k0, xi_k0_fit
    """
    valid = (~np.isnan(C_v)) & (~np.isnan(e_v)) & (e_v > 1e-9) & np.isfinite(C_v)
    r_v = R_v[valid]; c_v = C_v[valid]; ev = e_v[valid]
    if len(r_v) < 6:
        return 0.0, 0.0, np.nan

    xi_xt = xi_em_meas * (1.0 + xtalk_cal_error * rng.standard_normal())
    xi_xt = np.clip(xi_xt, A_M * 2, 0.005)

    def full_model(r, ak, xk, at, xt):
        xk = max(float(xk), A_M * 2)
        return ak * bessel_k0(r / xk) / bessel_k0(A_M / xk) + at * np.exp(-r / xt)

    def null_model(r, at, xt):
        return at * np.exp(-r / xt)

    try:
        pf, _ = curve_fit(full_model, r_v, c_v, sigma=ev, absolute_sigma=True,
                           p0=[0.05, xi_hint, XTALK_TRUE, xi_xt],
                           bounds=([0, A_M*2, 0, A_M], [1.0, 0.02, 0.5, 0.005]),
                           maxfev=3000)
        ll_f   = -0.5 * np.sum(((c_v - full_model(r_v, *pf)) / ev)**2)
        amp_k0 = float(pf[0]); xi_k0 = float(pf[1])
    except Exception:
        ll_f = -1e9; amp_k0 = 0.0; xi_k0 = np.nan

    try:
        pn, _ = curve_fit(null_model, r_v, c_v, sigma=ev, absolute_sigma=True,
                           p0=[XTALK_TRUE, xi_xt],
                           bounds=([0, A_M], [0.5, 0.005]), maxfev=2000)
        ll_n = -0.5 * np.sum(((c_v - null_model(r_v, *pn)) / ev)**2)
    except Exception:
        ll_n = -1e9

    return float(ll_f - ll_n), amp_k0, xi_k0


def fit_null_family(R_v, C_v, e_v):
    """
    Fit all null models M2, M7, M8, M9, M10, M11 to the data.
    Returns: dict of {model_name: (ll, n_params, fitted_values)}
    Used for model selection across the full null family.
    """
    valid = (~np.isnan(C_v)) & (~np.isnan(e_v)) & (e_v > 1e-9) & np.isfinite(C_v)
    r_v = R_v[valid]; c_v = C_v[valid]; ev = e_v[valid]
    if len(r_v) < 6:
        return {}

    fits = {}

    # M2: single exponential
    try:
        p, _ = curve_fit(lambda r, a, x: a*np.exp(-r/x), r_v, c_v,
                          p0=[0.1, 600e-6], sigma=ev, absolute_sigma=True,
                          bounds=([0, A_M*2], [1, 0.05]), maxfev=2000)
        ll = -0.5*np.sum(((c_v - p[0]*np.exp(-r_v/p[1]))/ev)**2)
        fits["M2"] = (float(ll), 2, p.tolist())
    except Exception:
        fits["M2"] = (-1e9, 2, [])

    # M7: power-law
    try:
        def m7(r, a, alpha): return a * (np.maximum(r, A_M) / A_M) ** (-alpha)
        p, _ = curve_fit(m7, r_v, c_v, p0=[0.08, 0.8], sigma=ev,
                          absolute_sigma=True, bounds=([0, 0.1], [1, 3]), maxfev=2000)
        ll = -0.5*np.sum(((c_v - m7(r_v, *p))/ev)**2)
        fits["M7"] = (float(ll), 2, p.tolist())
    except Exception:
        fits["M7"] = (-1e9, 2, [])

    # M8: Gaussian
    try:
        def m8(r, a, s): return a * np.exp(-(r/s)**2)
        p, _ = curve_fit(m8, r_v, c_v, p0=[0.10, 600e-6], sigma=ev,
                          absolute_sigma=True, bounds=([0, A_M*2], [1, 0.05]), maxfev=2000)
        ll = -0.5*np.sum(((c_v - m8(r_v, *p))/ev)**2)
        fits["M8"] = (float(ll), 2, p.tolist())
    except Exception:
        fits["M8"] = (-1e9, 2, [])

    # M9: two-bath
    try:
        def m9(r, a1, x1, a2, x2): return a1*np.exp(-r/x1) + a2*np.exp(-r/x2)
        p, _ = curve_fit(m9, r_v, c_v, p0=[0.08, 250e-6, 0.05, 1500e-6],
                          sigma=ev, absolute_sigma=True,
                          bounds=([0, A_M*2, 0, A_M*2], [0.5, 0.005, 0.5, 0.05]),
                          maxfev=3000)
        ll = -0.5*np.sum(((c_v - m9(r_v, *p))/ev)**2)
        fits["M9"] = (float(ll), 4, p.tolist())
    except Exception:
        fits["M9"] = (-1e9, 4, [])

    # M10: stretched exponential
    try:
        def m10(r, a, x, b): return a * np.exp(-(r/x)**b)
        p, _ = curve_fit(m10, r_v, c_v, p0=[0.10, 600e-6, 0.7],
                          sigma=ev, absolute_sigma=True,
                          bounds=([0, A_M*2, 0.1], [1, 0.05, 2.0]), maxfev=2000)
        ll = -0.5*np.sum(((c_v - m10(r_v, *p))/ev)**2)
        fits["M10"] = (float(ll), 3, p.tolist())
    except Exception:
        fits["M10"] = (-1e9, 3, [])

    # M11: Matérn
    try:
        def m11(r, a, x): return a*(1 + np.sqrt(3)*r/x)*np.exp(-np.sqrt(3)*r/x)
        p, _ = curve_fit(m11, r_v, c_v, p0=[0.10, 600e-6], sigma=ev,
                          absolute_sigma=True, bounds=([0, A_M*2], [1, 0.05]), maxfev=2000)
        ll = -0.5*np.sum(((c_v - m11(r_v, *p))/ev)**2)
        fits["M11"] = (float(ll), 2, p.tolist())
    except Exception:
        fits["M11"] = (-1e9, 2, [])

    return fits


# ─────────────────────────────────────────────────────────────────────────────
# 7. TWO-STAGE TEST PROCEDURE
# ─────────────────────────────────────────────────────────────────────────────

def two_stage_test(C_gamma, C_gamma_err, R_ARR, xi_em_meas, rng,
                   screen_thresh_mm=2.0, llr_threshold=None,
                   xtalk_cal_error=0.01):
    """
    Two-stage test with explicit Phase-1 conditioning.

    Stage 1 (screening): Fit single-exp to estimate correlation scale xi_est.
      - If xi_est > screen_thresh_mm * 1e-3: return ('STOP_SCREEN', None)
      - Otherwise: pass to Stage 2.

    Stage 2 (confirmatory): Fit K0 + null, compute LLR.
      - Decision: LLR > llr_threshold AND amp_k0 > 0.01.

    The llr_threshold should be derived from the null distribution
    conditioned on passing Stage 1, not from the desired power.
    If llr_threshold is None, returns the raw LLR for external calibration.

    Returns: (stage1_result, llr, amp_k0, xi_k0, stage2_decision)
    """
    valid = (~np.isnan(C_gamma)) & np.isfinite(C_gamma) & (C_gamma_err > 1e-9)
    r_v = R_ARR[valid]; c_v = C_gamma[valid]; e_v = C_gamma_err[valid]

    if len(r_v) < 6:
        return 'INSUFFICIENT_DATA', None, None, None, False

    # Stage 1: estimate correlation scale
    try:
        def exp1(r, a, x): return a * np.exp(-r / x)
        ps, _ = curve_fit(exp1, r_v, c_v, p0=[0.1, 1e-3],
                           sigma=e_v, absolute_sigma=True,
                           bounds=([0, A_M*2], [1, 0.05]), maxfev=1000)
        xi_est = float(ps[1])
    except Exception:
        xi_est = 1.0  # failed screen fit: assume large scale

    if xi_est > screen_thresh_mm * 1e-3:
        return 'STOP_SCREEN', None, None, None, False

    # Stage 2: K0 vs null LLR
    llr, amp_k0, xi_k0 = fit_k0_plus_null(
        R_ARR, C_gamma, C_gamma_err, xi_est, xi_em_meas, rng, xtalk_cal_error)

    if llr_threshold is None:
        return 'PROCEED_TO_STAGE2', float(llr), float(amp_k0), xi_k0, None

    decision = (llr > llr_threshold) and (amp_k0 > 0.01)
    return 'PROCEED_TO_STAGE2', float(llr), float(amp_k0), xi_k0, decision


# ─────────────────────────────────────────────────────────────────────────────
# 8. QPU BUDGET CHECKER
# ─────────────────────────────────────────────────────────────────────────────

def check_qpu_budget(n_pairs, n_time, n_shots,
                     circuit_time_s=5e-6,
                     calibration_s=60.0):
    """
    Estimate QPU runtime for the proposed design.
    circuit_time_s: per-shot execution time (realistic IBM batched, 5 µs).
    Returns: (fits_budget: bool, estimated_runtime_s: float)
    """
    runtime = n_pairs * n_time * n_shots * circuit_time_s + calibration_s
    return runtime <= QPU_BUDGET_S, float(runtime)


# ─────────────────────────────────────────────────────────────────────────────
# 9. CLOPPER-PEARSON CONFIDENCE BOUND
# ─────────────────────────────────────────────────────────────────────────────

def clopper_pearson_upper(n_failures, n_trials, confidence=0.95):
    """
    One-sided Clopper-Pearson upper bound on failure probability.
    P(p_true <= result) = confidence.
    For n_failures=0: result = 1 - (1-confidence)^(1/n_trials).
    """
    from scipy.stats import beta as beta_dist
    if n_trials == 0:
        return 1.0
    if n_failures == 0:
        return 1.0 - (1.0 - confidence) ** (1.0 / n_trials)
    return float(beta_dist.ppf(confidence, n_failures + 1, n_trials - n_failures))
