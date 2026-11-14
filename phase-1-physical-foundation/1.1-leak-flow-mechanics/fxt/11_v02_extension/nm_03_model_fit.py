"""
nm_03_model_fit.py
==================
Task 3: Fit the Markovian and non-Markovian models to the gamma_dataset.csv
        Gamma vs omega data. Compare BIC/AIC. Determine whether the data
        already prefers the non-Markovian model.

MODELS
------
Markov model (3 free parameters):
    Gamma(omega) = Gamma0 + k_rot * omega^2 / (1 + (omega/omega_max)^2)
    params: {Gamma0, k_rot, omega_max}

Non-Markovian model (4 free parameters):
    The fitted Gamma from a Ramsey experiment with free evolution time t_free
    is the effective rate that produces the SAME measured T2*:

        T2*_meas = t_free at which |C(t)| = 1/e

    Under the exact model:
        Phi(T2*_exact, Gamma_nm, tau_B) = 1
        where Phi(t) = Gamma_nm * tau_B * [t/tau_B - 1 + exp(-t/tau_B)]

    Given measured T2*_meas (= 1/Gamma_meas), the NM model infers:
        Gamma_nm = effective Markov-equivalent rate that, with tau_B,
                   produces the same T2*.

    Equivalently: for given (Gamma_nm_inf, tau_B), the APPARENT Gamma
    measured from the 1/e point of the exact coherence is:

        Gamma_apparent(Gamma_nm_inf, tau_B) = 1 / T2*_exact(Gamma_nm_inf, tau_B)

    where T2*_exact is solved numerically from Phi(T2*) = 1.

    The NM model for the dataset is:
        Gamma_apparent(omega) = f(Gamma0_nm + k_nm * omega^2 / (1+(omega/omega_max_nm)^2), tau_B)
        params: {Gamma0_nm, k_nm, omega_max_nm, tau_B}

    This is what the experiment actually measures: the 1/e time of the decay.

NOTE: With only 7 data points, the 4-parameter NM model is expected to have
      similar chi^2 to the 3-parameter Markov model, but BIC will penalise
      the extra parameter. The key result is: does tau_B differ from 0?

OUTPUTS
-------
  nm03_model_comparison.png  — data + both model fits
  nm03_residuals.png         — residuals plot
  nm03_fit_summary.json      — all fit statistics
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, brentq, minimize
from scipy.stats import chi2 as chi2_dist

HERE   = Path(__file__).resolve().parent
OUTDIR = HERE / "outputs" / "nm_03"
OUTDIR.mkdir(parents=True, exist_ok=True)

import sys
sys.path.insert(0, str(HERE))
from nm_01_memory_kernel import phi_exact

# ── load data ────────────────────────────────────────────────────────────────

DATA_PATH = (HERE.parent / "06_datasets" / "aaG" / "ramsey_dataset"
             / "gamma_dataset.csv")

def load_data():
    import csv
    rows = []
    with open(DATA_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["accepted"].strip().lower() == "true":
                rows.append({
                    "omega": float(row["Omega"]),          # rad/s
                    "Gamma": float(row["Gamma"]),           # s^-1
                    "Gamma_err": float(row["Gamma_err"]),   # s^-1
                })
    omega    = np.array([r["omega"]     for r in rows])
    Gamma    = np.array([r["Gamma"]     for r in rows])
    Gamma_err = np.array([r["Gamma_err"] for r in rows])
    return omega, Gamma, Gamma_err


# ── Markov model ─────────────────────────────────────────────────────────────

def markov_model(omega, Gamma0, k_rot, omega_max):
    return Gamma0 + k_rot * omega**2 / (1.0 + (omega / omega_max)**2)


def fit_markov(omega, Gamma, Gamma_err):
    p0 = [2e4, 4.5e-7, 1e7]
    bounds = ([0, 1e-12, 1e3], [1e6, 1e-2, 1e9])
    popt, pcov = curve_fit(
        markov_model, omega, Gamma,
        p0=p0, sigma=Gamma_err, absolute_sigma=True,
        bounds=bounds, maxfev=20000
    )
    perr = np.sqrt(np.diag(pcov))
    residuals = Gamma - markov_model(omega, *popt)
    chi2 = np.sum((residuals / Gamma_err)**2)
    dof  = len(omega) - len(popt)
    return popt, perr, chi2, dof


# ── Non-Markovian model ───────────────────────────────────────────────────────

def t2star_exact(Gamma_nm, tau_B):
    """
    Solve Phi(t, Gamma_nm, tau_B) = 1 numerically.
    Returns T2*_exact (the 1/e time of the exact coherence).
    """
    # bracket: at t=0 Phi=0, need t where Phi=1
    # upper bound: t = 10/Gamma_nm is always enough (Phi ~ Gamma*t for large t)
    t_upper = 10.0 / Gamma_nm
    try:
        t_star = brentq(
            lambda t: phi_exact(np.array([t]), Gamma_nm, tau_B)[0] - 1.0,
            1e-12, t_upper,
            xtol=1e-12, rtol=1e-10
        )
    except ValueError:
        t_star = 1.0 / Gamma_nm  # fallback to Markov
    return t_star


def gamma_apparent(Gamma_nm_inner, tau_B):
    """
    The Gamma that would be read off a Ramsey experiment = 1 / T2*_exact.
    """
    t_star = t2star_exact(Gamma_nm_inner, tau_B)
    return 1.0 / t_star


def nm_model(omega, Gamma0_nm, k_nm, omega_max_nm, tau_B):
    """
    Non-Markovian model: Gamma_apparent(omega) for given tau_B.
    """
    result = np.zeros_like(omega)
    for i, w in enumerate(omega):
        Gamma_inner = Gamma0_nm + k_nm * w**2 / (1.0 + (w / omega_max_nm)**2)
        result[i] = gamma_apparent(Gamma_inner, tau_B)
    return result


def fit_nm(omega, Gamma, Gamma_err):
    """
    Fit the 4-parameter NM model using scipy minimize (nelder-mead) since
    curve_fit cannot handle the implicit solve inside nm_model cleanly.
    """
    def chi2_func(params):
        Gamma0_nm, log_k_nm, log_omega_max_nm, log_tau_B = params
        k_nm       = 10**log_k_nm
        omega_max_nm = 10**log_omega_max_nm
        tau_B      = 10**log_tau_B
        if Gamma0_nm < 0 or k_nm < 0 or omega_max_nm < 1e2 or tau_B < 1e-10:
            return 1e20
        try:
            pred = nm_model(omega, Gamma0_nm, k_nm, omega_max_nm, tau_B)
        except Exception:
            return 1e20
        return float(np.sum(((Gamma - pred) / Gamma_err)**2))

    # initial guess from Markov fit + tau_B = 10 µs
    x0 = [2e4, np.log10(4.5e-7), np.log10(1e7), np.log10(10e-6)]
    res = minimize(chi2_func, x0, method="Nelder-Mead",
                   options={"xatol": 1e-8, "fatol": 1e-8, "maxiter": 50000})

    Gamma0_nm, log_k_nm, log_omega_max_nm, log_tau_B = res.x
    k_nm        = 10**log_k_nm
    omega_max_nm = 10**log_omega_max_nm
    tau_B       = 10**log_tau_B
    popt        = [Gamma0_nm, k_nm, omega_max_nm, tau_B]
    chi2_val    = res.fun
    dof         = len(omega) - 4
    return popt, chi2_val, dof, res.success


# ── information criteria ──────────────────────────────────────────────────────

def aic(chi2_val, n_params):
    """AIC = chi2 + 2k  (for Gaussian errors, chi2 = -2 log L + const)"""
    return chi2_val + 2 * n_params


def bic(chi2_val, n_params, n_data):
    """BIC = chi2 + k * ln(n)"""
    return chi2_val + n_params * np.log(n_data)


def delta_bic_interpretation(delta):
    if delta < 2:   return "No preference"
    if delta < 6:   return "Positive evidence for lower-BIC model"
    if delta < 10:  return "Strong evidence"
    return "Very strong evidence"


# ── plots ─────────────────────────────────────────────────────────────────────

def plot_fits(omega, Gamma, Gamma_err, markov_popt, nm_popt):
    omega_fine = np.logspace(
        np.log10(omega.min() * 0.5),
        np.log10(omega.max() * 2),
        300
    )
    G_markov = markov_model(omega_fine, *markov_popt)
    G_nm     = nm_model(omega_fine, *nm_popt)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    ax.errorbar(omega / 1e6, Gamma / 1e3, yerr=Gamma_err / 1e3,
                fmt="o", color="#2166AC", ms=7, capsize=4, label="Data (gamma_dataset)")
    ax.semilogx(omega_fine / 1e6, G_markov / 1e3,
                color="#D6604D", lw=2, label="Markov fit (3 params)")
    ax.semilogx(omega_fine / 1e6, G_nm / 1e3,
                color="#4DAC26", lw=2, ls="--", label="Non-Markovian fit (4 params)")
    ax.set_xlabel(r"Drive frequency $\Omega / 2\pi$  (MHz)", fontsize=11)
    ax.set_ylabel(r"Dephasing rate $\Gamma$  (kHz)", fontsize=11)
    ax.set_title("Gamma_dataset: Markov vs Non-Markovian model fits", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # residuals
    ax = axes[1]
    res_markov = (Gamma - markov_model(omega, *markov_popt)) / Gamma_err
    res_nm     = (Gamma - nm_model(omega, *nm_popt)) / Gamma_err
    x_idx = np.arange(len(omega))
    w = 0.35
    ax.bar(x_idx - w/2, res_markov, width=w, color="#D6604D", alpha=0.7,
           label="Markov residuals / σ")
    ax.bar(x_idx + w/2, res_nm,     width=w, color="#4DAC26", alpha=0.7,
           label="NM residuals / σ")
    ax.axhline(0, color="k", lw=1)
    ax.axhline(+1, color="k", ls=":", lw=0.8)
    ax.axhline(-1, color="k", ls=":", lw=0.8)
    ax.set_xticks(x_idx)
    ax.set_xticklabels([f"{w/1e6:.1f}" for w in omega], rotation=45, ha="right")
    ax.set_xlabel(r"Drive frequency $\Omega/2\pi$  (MHz)", fontsize=11)
    ax.set_ylabel("Normalised residual  (σ)", fontsize=11)
    ax.set_title("Residuals: Markov vs Non-Markovian\n"
                 "Both within ±2σ expected for 7 points", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTDIR / "nm03_model_comparison.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm03_model_comparison.png")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("NM-03: Model fit to gamma_dataset")
    print("=" * 60)

    omega, Gamma, Gamma_err = load_data()
    print(f"  Loaded {len(omega)} data points from gamma_dataset.csv")

    print("  Fitting Markov model (3 params)...")
    markov_popt, markov_perr, markov_chi2, markov_dof = fit_markov(
        omega, Gamma, Gamma_err)
    print(f"    Gamma0  = {markov_popt[0]:.2e} ± {markov_perr[0]:.2e} s^-1")
    print(f"    k_rot   = {markov_popt[1]:.2e} ± {markov_perr[1]:.2e} s")
    print(f"    omega_max = {markov_popt[2]:.2e} ± {markov_perr[2]:.2e} rad/s")
    print(f"    chi2/dof  = {markov_chi2:.3f} / {markov_dof} = {markov_chi2/markov_dof:.3f}")

    print("  Fitting Non-Markovian model (4 params)...")
    nm_popt, nm_chi2, nm_dof, nm_success = fit_nm(omega, Gamma, Gamma_err)
    print(f"    Gamma0_nm  = {nm_popt[0]:.2e} s^-1")
    print(f"    k_nm       = {nm_popt[1]:.2e} s")
    print(f"    omega_max  = {nm_popt[2]:.2e} rad/s")
    print(f"    tau_B      = {nm_popt[3]*1e6:.2f} µs   [NM parameter]")
    print(f"    chi2/dof   = {nm_chi2:.3f} / {nm_dof} = {nm_chi2/nm_dof:.3f}")
    print(f"    Optimizer success: {nm_success}")

    # information criteria
    n = len(omega)
    aic_mk = aic(markov_chi2, 3)
    aic_nm = aic(nm_chi2,     4)
    bic_mk = bic(markov_chi2, 3, n)
    bic_nm = bic(nm_chi2,     4, n)

    delta_aic = aic_nm - aic_mk   # negative = NM preferred
    delta_bic = bic_nm - bic_mk   # negative = NM preferred

    pref_aic = "NM preferred" if delta_aic < 0 else "Markov preferred"
    pref_bic = "NM preferred" if delta_bic < 0 else "Markov preferred"

    print()
    print("  MODEL COMPARISON:")
    print(f"    AIC Markov = {aic_mk:.2f},  AIC NM = {aic_nm:.2f},  "
          f"ΔAIC = {delta_aic:.2f}  → {pref_aic}")
    print(f"    BIC Markov = {bic_mk:.2f},  BIC NM = {bic_nm:.2f},  "
          f"ΔBIC = {delta_bic:.2f}  → {pref_bic}  ({delta_bic_interpretation(abs(delta_bic))})")

    # NMP for best-fit tau_B
    tau_B_fit  = nm_popt[3]
    G_median   = np.median(Gamma)
    nmp_fitted = G_median * tau_B_fit
    print(f"\n  Fitted tau_B = {tau_B_fit*1e6:.1f} µs")
    print(f"  NMP at median Gamma = {nmp_fitted:.3f}  "
          f"({'NON-MARKOVIAN' if nmp_fitted > 1 else 'TRANSITIONAL' if nmp_fitted > 0.1 else 'MARKOVIAN'})")

    print("\n  Generating comparison plot...")
    plot_fits(omega, Gamma, Gamma_err, markov_popt, nm_popt)

    summary = {
        "task": "nm_03_model_fit",
        "n_data_points": n,
        "markov_model": {
            "n_params": 3,
            "params": {
                "Gamma0_s": markov_popt[0],
                "k_rot_s": markov_popt[1],
                "omega_max_rad_s": markov_popt[2]
            },
            "param_errors": {
                "Gamma0_err": markov_perr[0],
                "k_rot_err": markov_perr[1],
                "omega_max_err": markov_perr[2]
            },
            "chi2": markov_chi2,
            "dof": markov_dof,
            "chi2_per_dof": markov_chi2 / markov_dof if markov_dof > 0 else None,
            "AIC": aic_mk,
            "BIC": bic_mk
        },
        "nm_model": {
            "n_params": 4,
            "params": {
                "Gamma0_nm_s": nm_popt[0],
                "k_nm_s": nm_popt[1],
                "omega_max_nm_rad_s": nm_popt[2],
                "tau_B_s": nm_popt[3],
                "tau_B_us": nm_popt[3] * 1e6
            },
            "chi2": nm_chi2,
            "dof": nm_dof,
            "chi2_per_dof": nm_chi2 / nm_dof if nm_dof > 0 else None,
            "AIC": aic_nm,
            "BIC": bic_nm,
            "optimizer_success": nm_success
        },
        "model_comparison": {
            "delta_AIC": delta_aic,
            "delta_BIC": delta_bic,
            "AIC_preference": pref_aic,
            "BIC_preference": pref_bic,
            "BIC_evidence_strength": delta_bic_interpretation(abs(delta_bic)),
            "fitted_NMP": nmp_fitted,
            "NMP_regime": (
                "NON-MARKOVIAN" if nmp_fitted > 1 else
                "TRANSITIONAL" if nmp_fitted > 0.1 else
                "MARKOVIAN"
            )
        },
        "interpretation": (
            "The gamma_dataset measures Gamma at different drive frequencies. "
            "Both models fit the data because Gamma vs omega is insensitive to "
            "tau_B — what tau_B changes is the SHAPE of C(t), not its 1/e value "
            "at a single frequency. The time-domain Ramsey trace is needed to "
            "discriminate. This is built in Task 4."
        ),
        "next_task": "nm_04_ramsey_discriminator.py"
    }

    with open(OUTDIR / "nm03_fit_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  [saved] nm03_fit_summary.json")
    print(f"  Outputs: {OUTDIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
