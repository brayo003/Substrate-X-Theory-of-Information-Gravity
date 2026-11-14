"""
decoherence_prediction.py
=========================
Substrate-X Decoherence Validation Pipeline
Against IBM Quantum Ramsey Spectroscopy Data (ibm_marrakesh, qubit 0)

Model:
    Γ(ω) = Γ₀ + k_rot * ω² / (1 + (ω / ω_max)²)

    Fixed parameters:
        k_rot  = 4.5e-7  s
        ω_max  = 1e6     rad/s

    Free parameter (estimated from data):
        Γ₀     = baseline dephasing rate (s⁻¹)

Usage:
    python decoherence_prediction.py

All outputs are written to the working directory.
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats, optimize
from datetime import datetime, timezone

# Optional statsmodels — graceful degradation if absent
try:
    import statsmodels.api as sm
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    warnings.warn("statsmodels not available; some diagnostics will be skipped.")

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
np.random.seed(0)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
NPZ_PATH   = os.path.join(BASE_DIR, "nunu", "ramsey_dataset", "experiment_results.npz")
OUT_DIR    = BASE_DIR  # All outputs land in fxt/

# Output file names
CSV_OUT    = os.path.join(OUT_DIR, "decoherence_results.csv")
NPZ_OUT    = os.path.join(OUT_DIR, "decoherence_results.npz")
PNG_GAMMA  = os.path.join(OUT_DIR, "gamma_prediction.png")
PNG_RESID  = os.path.join(OUT_DIR, "gamma_residuals.png")
PNG_QQ     = os.path.join(OUT_DIR, "qq_plot.png")
PNG_PRED   = os.path.join(OUT_DIR, "prediction_vs_measurement.png")
PNG_SENS   = os.path.join(OUT_DIR, "sensitivity_analysis.png")

# ---------------------------------------------------------------------------
# Model fixed parameters
# ---------------------------------------------------------------------------
K_ROT  = 4.5e-7   # s  (rotational coupling coefficient)
W_MAX  = 1.0e6    # rad/s (saturation frequency)

# Sensitivity analysis perturbations (fractional)
SENS_PERTURBATIONS = [-0.20, -0.10, -0.05, 0.0, +0.05, +0.10, +0.20]

# ---------------------------------------------------------------------------
# Matplotlib style
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.dpi":        150,
    "font.size":         11,
    "axes.titlesize":    12,
    "axes.labelsize":    11,
    "legend.fontsize":   9,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "lines.linewidth":   1.8,
    "axes.grid":         True,
    "grid.alpha":        0.35,
    "figure.facecolor":  "white",
})

COLORS = {
    "data":    "#2166AC",
    "model":   "#D6604D",
    "resid":   "#4DAC26",
    "zero":    "#888888",
    "fill":    "#FDDBC7",
}

# ---------------------------------------------------------------------------
# Section 1: Load dataset
# ---------------------------------------------------------------------------
def load_dataset(npz_path: str) -> list[dict]:
    """
    Load experiment archive from NPZ.
    Returns list of experiment dicts for all accepted experiments.
    """
    print(f"[load] Reading {npz_path}")
    data = np.load(npz_path, allow_pickle=True)
    archive = data["archive"].item()          # unwrap 0-d object array
    dataset = archive["dataset"]             # list of experiment dicts
    accepted = [exp for exp in dataset if exp.get("accepted", False)]
    print(f"[load] Total experiments : {len(dataset)}")
    print(f"[load] Accepted          : {len(accepted)}")
    return accepted


# ---------------------------------------------------------------------------
# Section 2: Extract quantities of interest
# ---------------------------------------------------------------------------
def extract_observables(experiments: list[dict]) -> pd.DataFrame:
    """
    Pull Γ, σ_Γ, Ω, σ_Ω, detuning, R², T2*, timestamps from each experiment.
    Verifies internal consistency: Ω ≈ 2π * detuning_hz (within fit tolerance).
    Returns sorted DataFrame.
    """
    rows = []
    for exp in experiments:
        detuning_hz = float(exp["detuning_hz"])
        Gamma       = float(exp["Gamma"])
        Gamma_err   = float(exp["Gamma_err"])
        Omega       = float(exp["Omega"])
        Omega_err   = float(exp["Omega_err"])
        R2          = float(exp["R2"])
        T2star      = float(exp["T2star"])
        timestamp   = exp.get("timestamp", "")
        job_id      = exp.get("job_id", "")
        backend     = exp.get("backend", "")
        reduced_chi2 = float(exp.get("reduced_chi2", np.nan))
        RMSE        = float(exp.get("RMSE", np.nan))
        A           = float(exp.get("A", np.nan))
        A_err       = float(exp.get("A_err", np.nan))
        Phi         = float(exp.get("Phi", np.nan))
        Phi_err     = float(exp.get("Phi_err", np.nan))
        shots       = int(exp.get("shots", 0))
        n_delays    = len(exp.get("delay_seconds", []))

        # Consistency check: Ω vs 2π·detuning
        omega_expected = 2.0 * np.pi * detuning_hz
        omega_discrepancy_pct = abs(Omega - omega_expected) / omega_expected * 100.0

        rows.append({
            "detuning_hz":           detuning_hz,
            "Omega_rad_s":           Omega,
            "Omega_err_rad_s":       Omega_err,
            "Omega_expected_rad_s":  omega_expected,
            "Omega_discrepancy_pct": omega_discrepancy_pct,
            "Gamma_s1":              Gamma,
            "Gamma_err_s1":          Gamma_err,
            "T2star_s":              T2star,
            "R2":                    R2,
            "reduced_chi2":          reduced_chi2,
            "RMSE":                  RMSE,
            "A":                     A,
            "A_err":                 A_err,
            "Phi":                   Phi,
            "Phi_err":               Phi_err,
            "shots":                 shots,
            "n_delays":              n_delays,
            "backend":               backend,
            "job_id":                job_id,
            "timestamp":             timestamp,
        })

    df = pd.DataFrame(rows).sort_values("detuning_hz").reset_index(drop=True)

    print("\n[extract] Consistency check — Ω vs 2π·detuning:")
    for _, row in df.iterrows():
        status = "OK" if row["Omega_discrepancy_pct"] < 15.0 else "WARN"
        print(f"  detuning={row['detuning_hz']/1e6:.1f} MHz  "
              f"Ω_fit={row['Omega_rad_s']:.3e}  "
              f"Ω_expected={row['Omega_expected_rad_s']:.3e}  "
              f"Δ={row['Omega_discrepancy_pct']:.1f}%  [{status}]")

    return df


# ---------------------------------------------------------------------------
# Section 3: Model prediction
# ---------------------------------------------------------------------------
def gamma_model(omega: np.ndarray, gamma0: float,
                k_rot: float = K_ROT, w_max: float = W_MAX) -> np.ndarray:
    """
    Substrate-X macro decoherence model:
        Γ(ω) = Γ₀ + k_rot * ω² / (1 + (ω/ω_max)²)
    """
    return gamma0 + k_rot * omega**2 / (1.0 + (omega / w_max)**2)


def compute_predictions(df: pd.DataFrame, gamma0: float) -> pd.DataFrame:
    """Add Gamma_pred column to dataframe."""
    df = df.copy()
    df["Gamma_pred_s1"] = gamma_model(df["Omega_rad_s"].values, gamma0)
    df["residual_s1"]   = df["Gamma_s1"] - df["Gamma_pred_s1"]
    df["norm_residual"]  = df["residual_s1"] / df["Gamma_err_s1"]
    return df


# ---------------------------------------------------------------------------
# Section 4: Estimate Γ₀ via weighted least squares
# ---------------------------------------------------------------------------
def estimate_gamma0(df: pd.DataFrame) -> dict:
    """
    Estimate Γ₀ using weighted least squares (weights = 1/σ²).
    The model is linear in Γ₀:
        Γ_exp = Γ₀ + f(ω)   where f(ω) = k_rot*ω²/(1+(ω/ω_max)²)
    So:
        y_i = Γ_exp,i - f(ω_i)  →  WLS fit of y_i = Γ₀

    Also performs scipy.optimize.curve_fit as cross-check.
    """
    omega  = df["Omega_rad_s"].values
    gamma  = df["Gamma_s1"].values
    sigma  = df["Gamma_err_s1"].values
    w      = 1.0 / sigma**2           # weights

    # Fixed contribution from k_rot term
    f_omega = K_ROT * omega**2 / (1.0 + (omega / W_MAX)**2)

    # Residual after subtracting model term
    y = gamma - f_omega              # shape (N,)

    # WLS: Γ₀ = Σ(w_i * y_i) / Σ(w_i)
    gamma0_wls    = np.sum(w * y) / np.sum(w)
    gamma0_var    = 1.0 / np.sum(w)
    gamma0_std    = np.sqrt(gamma0_var)
    gamma0_ci_low = gamma0_wls - 1.96 * gamma0_std
    gamma0_ci_hi  = gamma0_wls + 1.96 * gamma0_std

    # Cross-check with curve_fit (1-parameter fit)
    def model_1param(omega_arr, g0):
        return gamma_model(omega_arr, g0)

    p0_cf  = [gamma0_wls]
    try:
        popt, pcov_cf = optimize.curve_fit(
            model_1param, omega, gamma,
            p0=p0_cf, sigma=sigma, absolute_sigma=True,
            maxfev=5000
        )
        gamma0_cf     = float(popt[0])
        gamma0_cf_std = float(np.sqrt(pcov_cf[0, 0]))
        cf_success    = True
    except Exception as exc:
        gamma0_cf     = np.nan
        gamma0_cf_std = np.nan
        cf_success    = False
        warnings.warn(f"curve_fit failed: {exc}")

    result = {
        "gamma0_wls":         gamma0_wls,
        "gamma0_std":         gamma0_std,
        "gamma0_var":         gamma0_var,
        "gamma0_ci_95_low":   gamma0_ci_low,
        "gamma0_ci_95_hi":    gamma0_ci_hi,
        "gamma0_cf":          gamma0_cf,
        "gamma0_cf_std":      gamma0_cf_std,
        "cf_success":         cf_success,
        "n_points":           len(gamma),
        "dof":                len(gamma) - 1,
    }

    print(f"\n[gamma0] WLS estimate:  Γ₀ = {gamma0_wls:.2f} ± {gamma0_std:.2f} s⁻¹")
    print(f"[gamma0] 95% CI:        [{gamma0_ci_low:.2f}, {gamma0_ci_hi:.2f}] s⁻¹")
    if cf_success:
        print(f"[gamma0] curve_fit:     Γ₀ = {gamma0_cf:.2f} ± {gamma0_cf_std:.2f} s⁻¹")

    return result


# ---------------------------------------------------------------------------
# Section 5: Comprehensive statistics
# ---------------------------------------------------------------------------
def compute_statistics(df: pd.DataFrame, gamma0_result: dict) -> dict:
    """
    Compute full suite of validation statistics:
    RMSE, MAE, R², reduced χ², AIC, BIC, Pearson r, Spearman ρ, residual tests.
    """
    n       = len(df)
    k       = 1                           # free parameter (Γ₀ only)
    dof     = n - k

    residuals     = df["residual_s1"].values
    norm_res      = df["norm_residual"].values
    gamma_exp     = df["Gamma_s1"].values
    gamma_pred    = df["Gamma_pred_s1"].values
    sigma         = df["Gamma_err_s1"].values

    # Basic metrics
    RMSE  = np.sqrt(np.mean(residuals**2))
    MAE   = np.mean(np.abs(residuals))
    bias  = np.mean(residuals)

    # R² (coefficient of determination vs experimental values)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((gamma_exp - np.mean(gamma_exp))**2)
    R2     = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan

    # Reduced chi-squared (weighted)
    chi2        = np.sum((residuals / sigma)**2)
    chi2_red    = chi2 / dof

    # Log-likelihood (Gaussian errors)
    log_lik = -0.5 * np.sum(np.log(2 * np.pi * sigma**2) + (residuals / sigma)**2)

    # AIC / BIC
    AIC = 2 * k - 2 * log_lik
    BIC = k * np.log(n) - 2 * log_lik

    # Pearson correlation
    pearson_r, pearson_p = stats.pearsonr(gamma_exp, gamma_pred)

    # Spearman correlation
    spearman_r, spearman_p = stats.spearmanr(gamma_exp, gamma_pred)

    # --- Residual normality tests ---
    # Shapiro-Wilk (most powerful for small n)
    if n >= 3:
        sw_stat, sw_p = stats.shapiro(residuals)
    else:
        sw_stat, sw_p = np.nan, np.nan

    # D'Agostino-Pearson (requires n ≥ 8)
    if n >= 8:
        dp_stat, dp_p = stats.normaltest(residuals)
    else:
        dp_stat, dp_p = np.nan, np.nan

    # Kolmogorov-Smirnov vs N(0, σ_res)
    sigma_res = np.std(residuals, ddof=1)
    ks_stat, ks_p = stats.kstest(residuals, "norm",
                                  args=(0.0, sigma_res)) if n >= 3 else (np.nan, np.nan)

    # --- Zero-mean test ---
    if n >= 2:
        t_stat, t_p = stats.ttest_1samp(residuals, 0.0)
    else:
        t_stat, t_p = np.nan, np.nan

    # --- Autocorrelation of residuals (Durbin-Watson proxy) ---
    # DW = Σ(e_i - e_{i-1})² / Σe_i²
    if n >= 3:
        diff_res = np.diff(residuals)
        dw_stat  = np.sum(diff_res**2) / np.sum(residuals**2)
    else:
        dw_stat  = np.nan

    # Runs test for randomness (sign-based)
    signs  = np.sign(residuals - np.median(residuals))
    runs   = 1 + np.sum(np.abs(np.diff(signs)) > 0)
    n_pos  = np.sum(signs > 0)
    n_neg  = np.sum(signs <= 0)
    # Expected runs under H0
    runs_expected = (2 * n_pos * n_neg / n) + 1 if n > 0 else np.nan

    # Weighted mean absolute percentage error (MAPE)
    mape = np.mean(np.abs(residuals / gamma_exp)) * 100.0

    stats_dict = {
        # Fit quality
        "n":                n,
        "k":                k,
        "dof":              dof,
        "RMSE_s1":          RMSE,
        "MAE_s1":           MAE,
        "bias_s1":          bias,
        "MAPE_pct":         mape,
        "R2":               R2,
        "chi2":             chi2,
        "chi2_red":         chi2_red,
        "log_likelihood":   log_lik,
        "AIC":              AIC,
        "BIC":              BIC,
        # Correlations
        "pearson_r":        pearson_r,
        "pearson_p":        pearson_p,
        "spearman_r":       spearman_r,
        "spearman_p":       spearman_p,
        # Residual diagnostics
        "residual_mean":    np.mean(residuals),
        "residual_std":     sigma_res,
        "residual_min":     np.min(residuals),
        "residual_max":     np.max(residuals),
        "norm_res_mean":    np.mean(norm_res),
        "norm_res_std":     np.std(norm_res, ddof=1),
        # Normality tests
        "shapiro_stat":     sw_stat,
        "shapiro_p":        sw_p,
        "dagostino_stat":   dp_stat,
        "dagostino_p":      dp_p,
        "ks_stat":          ks_stat,
        "ks_p":             ks_p,
        # Zero-mean test
        "t_stat_zero_mean": t_stat,
        "t_p_zero_mean":    t_p,
        # Autocorrelation
        "durbin_watson":    dw_stat,
        "runs_observed":    runs,
        "runs_expected":    runs_expected,
    }

    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION STATISTICS")
    print("=" * 60)
    print(f"  N experiments        : {n}")
    print(f"  Free parameters      : {k}  (Γ₀ only)")
    print(f"  Degrees of freedom   : {dof}")
    print(f"  RMSE                 : {RMSE:.2f} s⁻¹")
    print(f"  MAE                  : {MAE:.2f} s⁻¹")
    print(f"  Bias                 : {bias:.2f} s⁻¹")
    print(f"  MAPE                 : {mape:.2f} %")
    print(f"  R²                   : {R2:.4f}")
    print(f"  χ²                   : {chi2:.4f}")
    print(f"  Reduced χ²           : {chi2_red:.4f}")
    print(f"  AIC                  : {AIC:.4f}")
    print(f"  BIC                  : {BIC:.4f}")
    print(f"  Pearson r            : {pearson_r:.4f}  (p={pearson_p:.4f})")
    print(f"  Spearman ρ           : {spearman_r:.4f}  (p={spearman_p:.4f})")
    print(f"  Shapiro-Wilk p       : {sw_p:.4f}  ({'normal' if sw_p > 0.05 else 'non-normal'} at α=0.05)")
    print(f"  t-test zero mean p   : {t_p:.4f}  ({'zero mean' if t_p > 0.05 else 'non-zero mean'} at α=0.05)")
    print(f"  Durbin-Watson        : {dw_stat:.4f}  (2=no autocorr)")
    print(f"  Runs (obs/exp)       : {runs} / {runs_expected:.1f}")
    print("=" * 60)

    return stats_dict


# ---------------------------------------------------------------------------
# Section 6: Uncertainty propagation
# ---------------------------------------------------------------------------
def uncertainty_propagation(df: pd.DataFrame, gamma0_result: dict) -> pd.DataFrame:
    """
    Propagate uncertainties in Ω into Γ_pred using partial derivatives.

    ∂Γ_pred/∂ω = k_rot * 2ω(ω_max² - ω²) / (ω_max² + ω²)²
                  (via quotient rule on ω²/(1+(ω/ω_max)²))

    Total uncertainty on prediction (combining Γ₀ uncertainty and Ω uncertainty):
        σ_pred² = σ_Γ0² + (∂Γ_pred/∂ω)² * σ_Ω²
    """
    df = df.copy()
    omega   = df["Omega_rad_s"].values
    sigma_omega = df["Omega_err_rad_s"].values
    w_max2  = W_MAX**2

    # Partial derivative of k_rot*ω²/(1+(ω/ω_max)²) with respect to ω
    denom   = (1.0 + (omega / W_MAX)**2)**2
    d_f_d_omega = K_ROT * 2.0 * omega * w_max2 / ((w_max2 + omega**2)**2 / w_max2**2 * w_max2**2)
    # Simplified form: d/dω [ ω²/(1+(ω/wm)²) ] = 2ω*wm²/(wm²+ω²)²  * wm²
    # Let u = ω²/(1+(ω/wm)²) = ω²*wm²/(wm²+ω²)
    # du/dω = (2ω*(wm²+ω²) - ω²*2ω) / (wm²+ω²)² * wm²
    #       = 2ω*wm⁴ / (wm²+ω²)²
    d_f_d_omega = K_ROT * 2.0 * omega * W_MAX**4 / (W_MAX**2 + omega**2)**2

    sigma_gamma0 = gamma0_result["gamma0_std"]

    sigma_pred = np.sqrt(sigma_gamma0**2 + (d_f_d_omega * sigma_omega)**2)
    df["Gamma_pred_sigma"] = sigma_pred
    df["d_f_d_omega"]      = d_f_d_omega

    print("\n[uncertainty] Propagated prediction uncertainties (s⁻¹):")
    for _, row in df.iterrows():
        print(f"  detuning={row['detuning_hz']/1e6:.1f} MHz  "
              f"σ_pred={row['Gamma_pred_sigma']:.1f}  "
              f"σ_exp={row['Gamma_err_s1']:.1f}")

    return df


# ---------------------------------------------------------------------------
# Section 7: Sensitivity analysis
# ---------------------------------------------------------------------------
def sensitivity_analysis(df: pd.DataFrame, gamma0: float) -> dict:
    """
    Vary k_rot by ±5%, ±10%, ±20% and compute Γ_pred at each Ω.
    Returns dict of perturbation → array of predictions.
    Does NOT refit Γ₀.
    """
    results = {}
    omega = df["Omega_rad_s"].values

    for frac in SENS_PERTURBATIONS:
        k_rot_varied = K_ROT * (1.0 + frac)
        gamma_pred   = gamma_model(omega, gamma0, k_rot=k_rot_varied)
        label        = f"{frac:+.0%}"
        results[label] = {
            "k_rot":      k_rot_varied,
            "frac":       frac,
            "Gamma_pred": gamma_pred,
        }
        print(f"[sensitivity] k_rot {label:>5s}  →  k_rot={k_rot_varied:.3e}  "
              f"Γ_pred range [{gamma_pred.min():.0f}, {gamma_pred.max():.0f}] s⁻¹")

    return results


# ---------------------------------------------------------------------------
# Section 8: Figures
# ---------------------------------------------------------------------------

def _omega_label(omega_rad_s: float) -> str:
    """Human-readable Ω label in Mrad/s."""
    return f"{omega_rad_s / 1e6:.2f}"


def fig_gamma_prediction(df: pd.DataFrame, gamma0: float,
                         gamma0_result: dict, stats_dict: dict,
                         out_path: str) -> None:
    """
    Figure 1 – Γ vs Ω: measured data with error bars + model curve.
    """
    omega_data  = df["Omega_rad_s"].values
    gamma_data  = df["Gamma_s1"].values
    gamma_err   = df["Gamma_err_s1"].values
    gamma_pred  = df["Gamma_pred_s1"].values

    # Smooth model curve
    omega_range = np.linspace(omega_data.min() * 0.5,
                              omega_data.max() * 1.05, 500)
    gamma_curve = gamma_model(omega_range, gamma0)

    fig, ax = plt.subplots(figsize=(8, 5))

    # Measured
    ax.errorbar(omega_data / 1e6, gamma_data / 1e3,
                yerr=gamma_err / 1e3,
                fmt="o", color=COLORS["data"], capsize=5, capthick=1.4,
                markersize=7, label="IBM Quantum (ibm_marrakesh)", zorder=5)

    # Predicted points
    ax.scatter(omega_data / 1e6, gamma_pred / 1e3,
               marker="x", s=80, color=COLORS["model"],
               linewidths=2.0, label="Model prediction (at measured Ω)", zorder=6)

    # Model curve
    ax.plot(omega_range / 1e6, gamma_curve / 1e3,
            color=COLORS["model"], lw=1.8, alpha=0.8,
            label=r"$\Gamma(\omega)=\Gamma_0 + k_{rot}\,\omega^2/(1+(\omega/\omega_{max})^2)$")

    ax.set_xlabel(r"$\Omega$ (Mrad/s)")
    ax.set_ylabel(r"$\Gamma$ (ks$^{-1}$)")
    ax.set_title("Substrate-X Decoherence Model vs IBM Quantum Ramsey Data")

    textstr = (
        f"$\\Gamma_0$ = {gamma0/1e3:.2f} ± {gamma0_result['gamma0_std']/1e3:.2f} ks⁻¹\n"
        f"$k_{{rot}}$ = {K_ROT:.1e} s\n"
        f"$\\omega_{{max}}$ = {W_MAX:.1e} rad/s\n"
        f"$R^2$ = {stats_dict['R2']:.4f}\n"
        f"RMSE = {stats_dict['RMSE_s1']/1e3:.2f} ks⁻¹"
    )
    ax.text(0.02, 0.97, textstr, transform=ax.transAxes,
            verticalalignment="top", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8))

    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[figure] Saved {out_path}")


def fig_residuals(df: pd.DataFrame, out_path: str) -> None:
    """
    Figure 2 – Residual analysis panel:
        (a) Residuals vs Ω
        (b) Normalised residuals vs Ω
        (c) Residual histogram
    """
    omega       = df["Omega_rad_s"].values
    residuals   = df["residual_s1"].values
    norm_res    = df["norm_residual"].values

    fig = plt.figure(figsize=(12, 4))
    gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.38)

    # (a) Raw residuals
    ax0 = fig.add_subplot(gs[0])
    ax0.scatter(omega / 1e6, residuals / 1e3,
                color=COLORS["resid"], s=70, zorder=5)
    ax0.axhline(0, color=COLORS["zero"], lw=1.2, ls="--")
    for i, (x, y) in enumerate(zip(omega / 1e6, residuals / 1e3)):
        ax0.annotate(f"{df['detuning_hz'].iloc[i]/1e6:.1f}", (x, y),
                     textcoords="offset points", xytext=(4, 4), fontsize=7)
    ax0.set_xlabel(r"$\Omega$ (Mrad/s)")
    ax0.set_ylabel(r"$\Gamma_{exp} - \Gamma_{pred}$ (ks$^{-1}$)")
    ax0.set_title("Residuals")

    # (b) Normalised residuals
    ax1 = fig.add_subplot(gs[1])
    ax1.scatter(omega / 1e6, norm_res,
                color=COLORS["data"], s=70, zorder=5)
    ax1.axhline(0,  color=COLORS["zero"], lw=1.2, ls="--")
    ax1.axhline(+2, color="orange", lw=1.0, ls=":", alpha=0.8)
    ax1.axhline(-2, color="orange", lw=1.0, ls=":", alpha=0.8)
    ax1.set_xlabel(r"$\Omega$ (Mrad/s)")
    ax1.set_ylabel(r"$(\Gamma_{exp} - \Gamma_{pred})\,/\,\sigma_\Gamma$")
    ax1.set_title("Normalised Residuals")

    # (c) Histogram
    ax2 = fig.add_subplot(gs[2])
    bins = max(4, int(np.ceil(np.sqrt(len(residuals)))))
    ax2.hist(residuals / 1e3, bins=bins, color=COLORS["resid"],
             edgecolor="white", alpha=0.85, density=True)
    # Overlay Gaussian with same mean and std
    mu, sig = np.mean(residuals / 1e3), np.std(residuals / 1e3, ddof=1)
    if sig > 0:
        x_g = np.linspace(mu - 4 * sig, mu + 4 * sig, 200)
        ax2.plot(x_g, stats.norm.pdf(x_g, mu, sig),
                 color="black", lw=1.4, label=f"N({mu:.2f}, {sig:.2f}²)")
        ax2.legend(fontsize=7)
    ax2.set_xlabel(r"Residual (ks$^{-1}$)")
    ax2.set_ylabel("Density")
    ax2.set_title("Residual Histogram")

    fig.suptitle("Residual Diagnostics — Substrate-X vs IBM Quantum", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[figure] Saved {out_path}")


def fig_qq_plot(df: pd.DataFrame, stats_dict: dict, out_path: str) -> None:
    """
    Figure 3 – Q-Q plot of normalised residuals vs standard normal.
    """
    norm_res = df["norm_residual"].values
    n        = len(norm_res)

    # Theoretical quantiles
    sorted_res   = np.sort(norm_res)
    quantile_pos = (np.arange(1, n + 1) - 0.5) / n
    theoretical  = stats.norm.ppf(quantile_pos)

    # 45° reference line
    ref_min = min(theoretical.min(), sorted_res.min()) - 0.3
    ref_max = max(theoretical.max(), sorted_res.max()) + 0.3

    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.scatter(theoretical, sorted_res, color=COLORS["data"], s=80, zorder=5)
    ax.plot([ref_min, ref_max], [ref_min, ref_max],
            color=COLORS["zero"], lw=1.3, ls="--", label="y = x (ideal)")

    # Annotate each point with detuning
    for i, (xt, ys) in enumerate(zip(theoretical, sorted_res)):
        idx = np.argsort(norm_res)[i]
        ax.annotate(f"{df['detuning_hz'].iloc[idx]/1e6:.1f} MHz",
                    (xt, ys), textcoords="offset points",
                    xytext=(5, 3), fontsize=7)

    sw_p = stats_dict["shapiro_p"]
    ax.set_xlabel("Theoretical N(0,1) quantiles")
    ax.set_ylabel("Sample normalised residual quantiles")
    ax.set_title(f"Q-Q Plot — Normalised Residuals\n"
                 f"Shapiro-Wilk p = {sw_p:.4f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[figure] Saved {out_path}")


def fig_prediction_vs_measurement(df: pd.DataFrame, stats_dict: dict,
                                   out_path: str) -> None:
    """
    Figure 4 – Γ_pred vs Γ_exp scatter with 1:1 line.
    """
    gamma_exp  = df["Gamma_s1"].values
    gamma_pred = df["Gamma_pred_s1"].values
    gamma_err  = df["Gamma_err_s1"].values

    all_vals = np.concatenate([gamma_exp, gamma_pred])
    lo = all_vals.min() * 0.9 / 1e3
    hi = all_vals.max() * 1.1 / 1e3

    fig, ax = plt.subplots(figsize=(5.5, 5))

    ax.errorbar(gamma_exp / 1e3, gamma_pred / 1e3,
                xerr=gamma_err / 1e3,
                fmt="o", color=COLORS["data"], capsize=5, capthick=1.4,
                markersize=7, label="Experiments", zorder=5)

    ax.plot([lo, hi], [lo, hi],
            color=COLORS["zero"], lw=1.3, ls="--", label="1:1 line")

    # Annotate
    for _, row in df.iterrows():
        ax.annotate(f"{row['detuning_hz']/1e6:.1f} MHz",
                    (row["Gamma_s1"] / 1e3, row["Gamma_pred_s1"] / 1e3),
                    textcoords="offset points", xytext=(5, 2), fontsize=7)

    ax.set_xlabel(r"$\Gamma_{exp}$ (ks$^{-1}$)")
    ax.set_ylabel(r"$\Gamma_{pred}$ (ks$^{-1}$)")
    ax.set_title(f"Prediction vs Measurement\n"
                 f"Pearson r = {stats_dict['pearson_r']:.4f}  "
                 f"R² = {stats_dict['R2']:.4f}")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[figure] Saved {out_path}")


def fig_sensitivity(df: pd.DataFrame, gamma0: float,
                    sens_results: dict, out_path: str) -> None:
    """
    Figure 5 – Sensitivity analysis: Γ_pred curves for varied k_rot.
    """
    omega_data  = df["Omega_rad_s"].values
    gamma_data  = df["Gamma_s1"].values
    gamma_err   = df["Gamma_err_s1"].values

    omega_range = np.linspace(omega_data.min() * 0.5,
                              omega_data.max() * 1.05, 500)

    fig, ax = plt.subplots(figsize=(9, 5.5))

    # Colourmap for perturbations
    cmap = plt.get_cmap("RdYlGn", len(SENS_PERTURBATIONS))

    for ci, (label, entry) in enumerate(sens_results.items()):
        frac  = entry["frac"]
        k_var = entry["k_rot"]
        curve = gamma_model(omega_range, gamma0, k_rot=k_var)
        lw    = 2.5 if frac == 0.0 else 1.2
        ls    = "-"  if frac == 0.0 else "--"
        alpha = 1.0  if frac == 0.0 else 0.75
        ax.plot(omega_range / 1e6, curve / 1e3,
                color=cmap(ci), lw=lw, ls=ls, alpha=alpha,
                label=f"k_rot {label}")

    # Measurements
    ax.errorbar(omega_data / 1e6, gamma_data / 1e3,
                yerr=gamma_err / 1e3,
                fmt="o", color="black", capsize=5, capthick=1.4,
                markersize=7, label="IBM Quantum data", zorder=10)

    ax.set_xlabel(r"$\Omega$ (Mrad/s)")
    ax.set_ylabel(r"$\Gamma$ (ks$^{-1}$)")
    ax.set_title(r"Sensitivity Analysis: $k_{rot}$ varied ±5%, ±10%, ±20%")
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[figure] Saved {out_path}")


# ---------------------------------------------------------------------------
# Section 9: Save outputs
# ---------------------------------------------------------------------------
def save_csv(df: pd.DataFrame, stats_dict: dict,
             gamma0_result: dict, out_path: str) -> None:
    """Write per-experiment results CSV."""
    out = df[[
        "detuning_hz", "Omega_rad_s", "Omega_err_rad_s",
        "Gamma_s1", "Gamma_err_s1",
        "Gamma_pred_s1", "residual_s1", "norm_residual",
        "Gamma_pred_sigma",
        "T2star_s", "R2", "reduced_chi2", "RMSE",
        "backend", "job_id", "timestamp",
    ]].copy()

    # Rename for clarity
    out.columns = [
        "detuning_hz", "Omega_rad_s", "Omega_err_rad_s",
        "Gamma_exp_s1", "Gamma_exp_err_s1",
        "Gamma_pred_s1", "residual_s1", "norm_residual",
        "pred_uncertainty_s1",
        "T2star_s", "Ramsey_R2", "Ramsey_reduced_chi2", "Ramsey_RMSE",
        "backend", "job_id", "timestamp",
    ]
    out.to_csv(out_path, index=False)
    print(f"[save] CSV written to {out_path}")


def save_npz(df: pd.DataFrame, stats_dict: dict,
             gamma0_result: dict, sens_results: dict,
             out_path: str) -> None:
    """Write complete results NPZ."""
    # Convert sensitivity results to saveable form
    sens_labels  = list(sens_results.keys())
    sens_k_rots  = np.array([v["k_rot"]  for v in sens_results.values()])
    sens_fracs   = np.array([v["frac"]   for v in sens_results.values()])
    sens_preds   = np.array([v["Gamma_pred"] for v in sens_results.values()])

    np.savez(
        out_path,
        # Per-experiment arrays
        detuning_hz         = df["detuning_hz"].values,
        Omega_rad_s         = df["Omega_rad_s"].values,
        Omega_err_rad_s     = df["Omega_err_rad_s"].values,
        Gamma_exp_s1        = df["Gamma_s1"].values,
        Gamma_exp_err_s1    = df["Gamma_err_s1"].values,
        Gamma_pred_s1       = df["Gamma_pred_s1"].values,
        residuals_s1        = df["residual_s1"].values,
        norm_residuals      = df["norm_residual"].values,
        pred_uncertainty_s1 = df["Gamma_pred_sigma"].values,
        T2star_s            = df["T2star_s"].values,
        Ramsey_R2           = df["R2"].values,
        # Model parameters
        gamma0_wls          = np.float64(gamma0_result["gamma0_wls"]),
        gamma0_std          = np.float64(gamma0_result["gamma0_std"]),
        gamma0_ci_95        = np.array([gamma0_result["gamma0_ci_95_low"],
                                        gamma0_result["gamma0_ci_95_hi"]]),
        k_rot               = np.float64(K_ROT),
        w_max               = np.float64(W_MAX),
        # Statistics (stored as object array)
        stats               = np.array(stats_dict, dtype=object),
        # Sensitivity
        sens_labels         = np.array(sens_labels),
        sens_k_rots         = sens_k_rots,
        sens_fracs          = sens_fracs,
        sens_Gamma_pred     = sens_preds,
    )
    print(f"[save] NPZ written to {out_path}")


# ---------------------------------------------------------------------------
# Section 10: Text report helper
# ---------------------------------------------------------------------------
def format_report_block(df: pd.DataFrame, stats_dict: dict,
                        gamma0_result: dict) -> str:
    """Return a formatted text block for inclusion in the Markdown report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = []
    lines.append(f"Report generated: {now}")
    lines.append(f"Backend        : ibm_marrakesh  (qubit 0)")
    lines.append(f"N experiments  : {stats_dict['n']}")
    lines.append("")
    lines.append("Per-experiment summary:")
    header = (f"{'detuning(MHz)':>14} {'Ω(Mrad/s)':>11} "
              f"{'Γ_exp(ks⁻¹)':>12} {'±σ':>8} "
              f"{'Γ_pred(ks⁻¹)':>13} {'resid(ks⁻¹)':>12} {'norm_res':>9} {'R²':>7}")
    lines.append(header)
    lines.append("-" * len(header))
    for _, row in df.iterrows():
        lines.append(
            f"{row['detuning_hz']/1e6:>14.3f} "
            f"{row['Omega_rad_s']/1e6:>11.3f} "
            f"{row['Gamma_s1']/1e3:>12.3f} "
            f"{row['Gamma_err_s1']/1e3:>8.3f} "
            f"{row['Gamma_pred_s1']/1e3:>13.3f} "
            f"{row['residual_s1']/1e3:>12.3f} "
            f"{row['norm_residual']:>9.3f} "
            f"{row['R2']:>7.4f}"
        )
    lines.append("")
    lines.append(f"Γ₀ estimate (WLS) : {gamma0_result['gamma0_wls']:.2f} ± "
                 f"{gamma0_result['gamma0_std']:.2f} s⁻¹")
    lines.append(f"95% CI            : [{gamma0_result['gamma0_ci_95_low']:.2f}, "
                 f"{gamma0_result['gamma0_ci_95_hi']:.2f}] s⁻¹")
    lines.append("")
    lines.append("Validation metrics:")
    for key in ["RMSE_s1","MAE_s1","bias_s1","MAPE_pct","R2",
                "chi2_red","AIC","BIC",
                "pearson_r","spearman_r",
                "shapiro_p","t_p_zero_mean","durbin_watson"]:
        lines.append(f"  {key:<25}: {stats_dict[key]:.6g}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("Substrate-X Decoherence Validation Pipeline")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # 1. Load
    experiments = load_dataset(NPZ_PATH)

    # 2. Extract
    df = extract_observables(experiments)

    # 3. Estimate Γ₀
    gamma0_result = estimate_gamma0(df)
    gamma0        = gamma0_result["gamma0_wls"]

    # 4. Compute predictions
    df = compute_predictions(df, gamma0)

    # 5. Uncertainty propagation
    df = uncertainty_propagation(df, gamma0_result)

    # 6. Statistics
    stats_dict = compute_statistics(df, gamma0_result)

    # 7. Sensitivity analysis
    print("\n[sensitivity] k_rot perturbation study:")
    sens_results = sensitivity_analysis(df, gamma0)

    # 8. Figures
    print("\n[figures] Generating publication-quality figures...")
    fig_gamma_prediction(df, gamma0, gamma0_result, stats_dict, PNG_GAMMA)
    fig_residuals(df, PNG_RESID)
    fig_qq_plot(df, stats_dict, PNG_QQ)
    fig_prediction_vs_measurement(df, stats_dict, PNG_PRED)
    fig_sensitivity(df, gamma0, sens_results, PNG_SENS)

    # 9. Save outputs
    print("\n[outputs] Saving data files...")
    save_csv(df, stats_dict, gamma0_result, CSV_OUT)
    save_npz(df, stats_dict, gamma0_result, sens_results, NPZ_OUT)

    # 10. Print report block
    report_block = format_report_block(df, stats_dict, gamma0_result)
    print("\n" + "=" * 60)
    print("REPORT SUMMARY")
    print("=" * 60)
    print(report_block)

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print(f"Outputs written to: {OUT_DIR}")
    print("  decoherence_results.csv")
    print("  decoherence_results.npz")
    print("  gamma_prediction.png")
    print("  gamma_residuals.png")
    print("  qq_plot.png")
    print("  prediction_vs_measurement.png")
    print("  sensitivity_analysis.png")
    print("=" * 60)

    # Return results for programmatic use
    return {
        "df":              df,
        "gamma0_result":   gamma0_result,
        "stats_dict":      stats_dict,
        "sens_results":    sens_results,
        "report_block":    report_block,
    }


if __name__ == "__main__":
    results = main()
