"""
prw_03_ibm_spatial_test.py
==========================
Tasks 5 & 6: Load IBM Brisbane/Kyoto calibration data, extract T2* per qubit
and chip coordinates, compute pairwise T2* correlations as a function of
qubit separation, and compare against the C2 PRW prediction.

WHAT THE THEORY PREDICTS (from prw_02_spatial_correlator.py):
--------------------------------------------------------------
The C2 PRW predicts CORRELATED PHASE NOISE between nearby qubits.
The measurable proxy is the pairwise CORRELATION OF T2* VALUES across the chip:

    rho(d) = Corr(T2*_i, T2*_j) as a function of d = |r_i - r_j|

The C2 prediction (at measurement time T >> tau_B):
    rho(d) ≈ f(d / xi_c)
where f decays from 1 at d=0 to 0 at d >> xi_c, and xi_c = v/lambda = 2c*tau.
The shape is NOT a clean exponential (it is T-dependent) but has a characteristic
scale xi_c. At T ~ 5*tau_B, an exponential with xi_eff ~ 1.3*xi_c is a good fit.

IMPORTANT CAVEATS (from the derivation):
-----------------------------------------
1. The static dephasing RATES are NOT correlated in the PRW — the equilibrium
   density is white noise (Poissonian). The correlation is in the PHASE NOISE,
   not the mean rates.

2. The T2* values measured on a chip are time-averaged and represent both
   the MEAN rate and noise around it. Spatial correlation of measured T2*
   values captures both common-mode drift AND genuine phase noise correlation.

3. The C2 prediction is NOT uniquely distinguishable from:
   - Spatially correlated phonon bath (same exponential form)
   - Common-mode flux noise (d-independent)
   - Fabrication-induced spatial gradients (systematic, not stochastic)

4. The key discriminant is: does xi_c ~ 2*c*tau where tau is independently
   measured from single-qubit T2* data and c is the substrate speed?
   If xi_c is measured and tau is known, c = xi_c / (2*tau) is determined.
   If c matches no known physical speed in the device, it could be substrate.

WHAT THIS ANALYSIS DOES:
-------------------------
1. Extract T2* per qubit from Brisbane and Kyoto calibration data
2. Extract qubit coordinates (in units of chip grid spacing ~ 200 µm)
3. Compute all pairwise T2* correlations vs distance
4. Fit an exponential to get xi_c_fit
5. Compare xi_c_fit to 2*c*tau_B for reasonable substrate parameters
6. Show what competing mechanisms would predict
"""

from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import pearsonr, spearmanr

HERE    = Path(__file__).resolve().parent
DATDIR  = HERE.parent / "06_datasets"
OUTDIR  = HERE / "outputs" / "prw_cjj"
OUTDIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Load calibration data
# ─────────────────────────────────────────────────────────────────────────────

def load_backend(name: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns:
        coords : (N, 2) array of qubit [row, col] coordinates
        T2star : (N,)  array of T2* values in seconds
                        (T2 decoherence time — closest to T2* in properties)
    """
    props_file = DATDIR / f"props_{name}.json"
    conf_file  = DATDIR / f"conf_{name}.json"

    with open(props_file) as f:
        props = json.load(f)
    with open(conf_file) as f:
        conf  = json.load(f)

    N = len(props["qubits"])

    # Extract T2 (and T2* if available) from qubit properties
    # Each qubit is a list of parameter dicts: {name, value, unit, ...}
    T2_vals = np.full(N, np.nan)
    T1_vals = np.full(N, np.nan)
    freq_vals = np.full(N, np.nan)

    for i, qubit_params in enumerate(props["qubits"]):
        for param in qubit_params:
            nm   = param.get("name", "")
            val  = param.get("value", np.nan)
            unit = param.get("unit", "")
            # Values are stored in their declared units (us, GHz, etc.)
            # Convert everything to SI (seconds, Hz)
            if nm == "T2":
                if unit in ("us", "µs"):
                    T2_vals[i] = val * 1e-6
                elif unit == "ms":
                    T2_vals[i] = val * 1e-3
                elif unit == "ns":
                    T2_vals[i] = val * 1e-9
                else:
                    T2_vals[i] = val  # assume seconds
            elif nm == "T1":
                if unit in ("us", "µs"):
                    T1_vals[i] = val * 1e-6
                elif unit == "ms":
                    T1_vals[i] = val * 1e-3
                elif unit == "ns":
                    T1_vals[i] = val * 1e-9
                else:
                    T1_vals[i] = val
            elif nm == "frequency":
                if unit == "GHz":
                    freq_vals[i] = val * 1e9
                elif unit == "MHz":
                    freq_vals[i] = val * 1e6
                else:
                    freq_vals[i] = val

    # Qubit coordinates from conf file
    coords_raw = conf.get("coords", [])
    coords = np.array(coords_raw, dtype=float)  # shape (N, 2): [row, col]

    return coords, T2_vals, T1_vals, freq_vals, N


# ─────────────────────────────────────────────────────────────────────────────
# Compute pairwise correlations
# ─────────────────────────────────────────────────────────────────────────────

def pairwise_analysis(coords: np.ndarray, T2: np.ndarray,
                      spacing_um: float = 200.0) -> dict:
    """
    For all qubit pairs (i,j), compute:
      - d_ij = Euclidean distance in physical units (µm)
      - delta_T2_ij = (T2_i - T2_mean) * (T2_j - T2_mean)
    
    Then bin by distance and compute mean correlation.
    """
    N = len(T2)
    valid = ~np.isnan(T2)
    idx   = np.where(valid)[0]
    n     = len(idx)

    T2_valid    = T2[idx]
    coords_valid = coords[idx]
    T2_mean      = np.mean(T2_valid)
    T2_std       = np.std(T2_valid)
    delta_T2     = T2_valid - T2_mean

    # All pairs
    dists   = []
    prods   = []   # delta_T2_i * delta_T2_j
    T2_i_list = []
    T2_j_list = []

    for a in range(n):
        for b in range(a + 1, n):
            row_diff = coords_valid[a, 0] - coords_valid[b, 0]
            col_diff = coords_valid[a, 1] - coords_valid[b, 1]
            d_grid   = np.sqrt(row_diff**2 + col_diff**2)   # in grid units
            d_um     = d_grid * spacing_um                   # in µm
            dists.append(d_um)
            prods.append(delta_T2[a] * delta_T2[b])
            T2_i_list.append(T2_valid[a])
            T2_j_list.append(T2_valid[b])

    dists  = np.array(dists)
    prods  = np.array(prods)
    T2_var = T2_std**2

    # Normalise: rho_ij = <delta_T2_i * delta_T2_j> / Var(T2)
    rho_pairs = prods / T2_var

    # Bin by distance
    d_max  = dists.max()
    n_bins = 25
    bins   = np.linspace(0, d_max * 1.01, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    rho_binned  = np.full(n_bins, np.nan)
    rho_err     = np.full(n_bins, np.nan)
    n_in_bin    = np.zeros(n_bins, dtype=int)

    for b in range(n_bins):
        mask = (dists >= bins[b]) & (dists < bins[b + 1])
        if mask.sum() >= 3:
            rho_binned[b] = np.mean(rho_pairs[mask])
            rho_err[b]    = np.std(rho_pairs[mask]) / np.sqrt(mask.sum())
            n_in_bin[b]   = mask.sum()

    return {
        "N_valid": n,
        "T2_mean_us": T2_mean * 1e6,
        "T2_std_us":  T2_std  * 1e6,
        "dists_um":   dists,
        "rho_pairs":  rho_pairs,
        "bin_centers_um": bin_centers,
        "rho_binned": rho_binned,
        "rho_err":    rho_err,
        "n_in_bin":   n_in_bin,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fit and plot
# ─────────────────────────────────────────────────────────────────────────────

def fit_correlation(bin_centers, rho_binned, rho_err):
    """Fit exponential rho = A*exp(-d/xi) + C to binned data."""
    valid = ~np.isnan(rho_binned)
    x = bin_centers[valid]
    y = rho_binned[valid]
    e = rho_err[valid]

    results = {}

    # Exponential + offset: rho = A * exp(-d/xi) + C
    def exp_offset(d, A, xi, C):
        return A * np.exp(-d / xi) + C

    try:
        p0 = [y[0] - y[-1], x[len(x)//3], np.mean(y[-5:])]
        popt, pcov = curve_fit(exp_offset, x, y, p0=p0, sigma=e + 1e-6,
                               maxfev=5000, bounds=([-2, 1, -2], [2, 5000, 2]))
        perr = np.sqrt(np.diag(pcov))
        results["exp_offset"] = {
            "A": popt[0], "xi_um": popt[1], "C": popt[2],
            "A_err": perr[0], "xi_err": perr[1], "C_err": perr[2],
        }
    except Exception as ex:
        results["exp_offset"] = {"error": str(ex)}

    # Pure exponential: rho = A * exp(-d/xi)
    def exp_pure(d, A, xi):
        return A * np.exp(-d / xi)

    try:
        p0 = [y[0], x[len(x)//3]]
        popt2, pcov2 = curve_fit(exp_pure, x, y, p0=p0, sigma=e + 1e-6,
                                 maxfev=5000, bounds=([0, 1], [2, 5000]))
        perr2 = np.sqrt(np.diag(pcov2))
        results["exp_pure"] = {
            "A": popt2[0], "xi_um": popt2[1],
            "A_err": perr2[0], "xi_err": perr2[1],
        }
    except Exception as ex:
        results["exp_pure"] = {"error": str(ex)}

    return results


def plot_results(name: str, analysis: dict, fit: dict,
                 coords: np.ndarray, T2: np.ndarray):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Chip map coloured by T2
    ax = axes[0, 0]
    valid = ~np.isnan(T2)
    sc = ax.scatter(coords[valid, 1], coords[valid, 0],
                    c=T2[valid] * 1e6, cmap="RdYlGn", s=80,
                    vmin=np.percentile(T2[valid]*1e6, 5),
                    vmax=np.percentile(T2[valid]*1e6, 95))
    plt.colorbar(sc, ax=ax, label="T2 (µs)")
    ax.set_title(f"IBM {name}: T2 spatial map\n"
                 f"mean={analysis['T2_mean_us']:.1f} µs, "
                 f"std={analysis['T2_std_us']:.1f} µs")
    ax.set_xlabel("Column"); ax.set_ylabel("Row")
    ax.set_aspect("equal")

    # 2. T2 histogram
    ax = axes[0, 1]
    ax.hist(T2[valid] * 1e6, bins=20, color="#4393C3", edgecolor="white", alpha=0.8)
    ax.axvline(analysis["T2_mean_us"], color="k", lw=2, ls="--",
               label=f"mean = {analysis['T2_mean_us']:.1f} µs")
    ax.set_xlabel("T2 (µs)"); ax.set_ylabel("Count")
    ax.set_title("T2 distribution across chip")
    ax.legend()

    # 3. Pairwise rho vs distance (scatter + binned)
    ax = axes[1, 0]
    # Subsample scatter for visibility (max 3000 points)
    n_pair = len(analysis["dists_um"])
    step   = max(1, n_pair // 3000)
    ax.scatter(analysis["dists_um"][::step], analysis["rho_pairs"][::step],
               alpha=0.05, s=2, color="#AAAAAA")
    valid_b = ~np.isnan(analysis["rho_binned"])
    ax.errorbar(analysis["bin_centers_um"][valid_b],
                analysis["rho_binned"][valid_b],
                analysis["rho_err"][valid_b],
                fmt="o", ms=6, color="#2166AC", capsize=3, lw=1.5,
                label="Binned mean ± SEM")

    # Overlay fits
    d_fine = np.linspace(0, analysis["dists_um"].max(), 300)
    colors = {"exp_offset": "#D6604D", "exp_pure": "#4DAC26"}
    labels = {"exp_offset": "Exp + offset", "exp_pure": "Pure exp"}
    for key, col in colors.items():
        r = fit.get(key, {})
        if "xi_um" in r:
            xi = r["xi_um"]; A = r["A"]
            C  = r.get("C", 0)
            ax.plot(d_fine, A * np.exp(-d_fine / xi) + C, color=col, lw=2,
                    label=f"{labels[key]}: ξ = {xi:.0f} µm")

    ax.axhline(0, color="k", lw=0.8, ls=":")
    ax.set_xlabel("Qubit separation d (µm)")
    ax.set_ylabel(r"$\rho(d) = \mathrm{Corr}(T2_i, T2_j)$")
    ax.set_title(f"Pairwise T2 correlation vs separation\n{name}")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # 4. Log-scale rho to check exponential form
    ax = axes[1, 1]
    valid_b2 = valid_b & (analysis["rho_binned"] > 0)
    if valid_b2.sum() > 3:
        ax.semilogy(analysis["bin_centers_um"][valid_b2],
                    analysis["rho_binned"][valid_b2],
                    "o-", color="#2166AC", ms=6, lw=1.5, label="Data (binned)")
        # Pure exponential: straight line on log scale
        for key, col in colors.items():
            r = fit.get(key, {})
            if "xi_um" in r:
                xi = r["xi_um"]; A = r["A"]; C = r.get("C", 0)
                pred = A * np.exp(-d_fine / xi) + C
                pred_pos = pred[pred > 0]
                d_pos    = d_fine[pred > 0]
                if len(d_pos) > 0:
                    ax.semilogy(d_pos, pred_pos, "--", color=col, lw=2,
                                label=f"ξ = {xi:.0f} µm")
    ax.set_xlabel("Qubit separation d (µm)")
    ax.set_ylabel(r"$\log \rho(d)$")
    ax.set_title("Log scale: straight line = exponential")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle(f"C2 Spatial Correlation Test — IBM {name.upper()}", fontsize=13)
    fig.tight_layout()
    out = OUTDIR / f"prw03_{name}_spatial.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Physical interpretation
# ─────────────────────────────────────────────────────────────────────────────

def interpret(name: str, analysis: dict, fit: dict):
    """
    Given the fitted xi_c, what does it imply for the C2 substrate?
    And what do competing mechanisms predict?
    """
    xi_fit_um = None
    for key in ["exp_offset", "exp_pure"]:
        r = fit.get(key, {})
        if "xi_um" in r and r.get("xi_err", 1e9) < r["xi_um"]:
            xi_fit_um = r["xi_um"]
            break

    T2_mean_s = analysis["T2_mean_us"] * 1e-6

    print(f"\n  === Physical interpretation for {name} ===")
    print(f"  T2_mean  = {analysis['T2_mean_us']:.1f} µs")
    print(f"  T2_std   = {analysis['T2_std_us']:.1f} µs")

    if xi_fit_um is not None:
        xi_m = xi_fit_um * 1e-6   # convert µm to m
        print(f"  xi_fit   = {xi_fit_um:.0f} µm")
        print()
        print("  C2 substrate interpretation:")
        print(f"    xi_c = 2*c*tau_B = v/lambda  =>  c = xi_c / (2*T2_mean)")
        c_implied = xi_m / (2 * T2_mean_s)
        print(f"    c_implied = {xi_fit_um:.0f} µm / (2 × {analysis['T2_mean_us']:.1f} µs)")
        print(f"              = {c_implied:.4f} m/s  = {c_implied*100:.2f} cm/s")
        print()
        print("  Comparison with known physical speeds:")
        speeds = {
            "Sound in Si (bulk)":         8433,
            "Surface acoustic wave (SAW)": 5080,
            "Speed of light / 1e6":        299.8,
            "Magnon speed in YIG":         7000,
            "Phonon in Al (superconductor)": 6400,
        }
        for label, v_ms in speeds.items():
            ratio = c_implied / v_ms
            print(f"    {label:35s}: v={v_ms} m/s  →  c/v = {ratio:.4f}")
        print()
        print("  Competing mechanisms:")
        print(f"    Phonon bath:  xi_ph = v_ph/(2*gamma_scatter)")
        print(f"      If v_ph = 6000 m/s and xi_ph = {xi_fit_um:.0f} µm:")
        gamma_ph = 6000 / (2 * xi_m)
        print(f"      gamma_scatter = {gamma_ph/1e6:.2f} MHz  "
              f"(phonon scattering rate — {gamma_ph/(1e3*2*np.pi):.1f} kHz×2π)")
        print(f"    Common-mode: would give d-INDEPENDENT correlation (xi -> inf)")
        print(f"    Direct crosstalk: would give 1/d^3 power law, not exponential")
    else:
        print("  [No reliable exponential fit obtained]")

    return xi_fit_um


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("PRW-03: IBM Spatial Correlation Test")
    print("=" * 65)

    all_results = {}

    for name in ["brisbane", "kyoto"]:
        print(f"\n--- Processing IBM {name} ---")
        try:
            coords, T2, T1, freq, N = load_backend(name)
        except FileNotFoundError as e:
            print(f"  Data not found: {e}")
            continue

        n_valid = np.sum(~np.isnan(T2))
        print(f"  {N} qubits, {n_valid} with valid T2")
        print(f"  T2 range: {np.nanmin(T2)*1e6:.1f} – {np.nanmax(T2)*1e6:.1f} µs")
        print(f"  Coord range: rows {coords[:,0].min():.0f}–{coords[:,0].max():.0f}, "
              f"cols {coords[:,1].min():.0f}–{coords[:,1].max():.0f}")

        # IBM heavy-hex chip: qubit spacing ~ 200 µm (from device specs)
        # One grid unit in coords = one qubit pitch
        # Actual physical pitch for Eagle: 200 µm
        PITCH_UM = 200.0

        analysis = pairwise_analysis(coords, T2, spacing_um=PITCH_UM)
        print(f"  {len(analysis['dists_um'])} qubit pairs")
        print(f"  T2 mean = {analysis['T2_mean_us']:.1f} µs,  "
              f"std = {analysis['T2_std_us']:.1f} µs")

        # Pearson correlation at nearest-neighbor distance
        nn_dist_um = PITCH_UM  # nearest neighbors = 1 grid unit
        nn_mask = analysis["dists_um"] < nn_dist_um * 1.5
        if nn_mask.sum() > 0:
            r_nn, p_nn = pearsonr(
                analysis["dists_um"][nn_mask],
                analysis["rho_pairs"][nn_mask]
            ) if nn_mask.sum() > 2 else (np.nan, np.nan)
            print(f"  NN pairs: {nn_mask.sum()},  "
                  f"mean rho(nn) = {analysis['rho_pairs'][nn_mask].mean():.4f}")

        fit = fit_correlation(analysis["bin_centers_um"],
                              analysis["rho_binned"],
                              analysis["rho_err"])
        for key, r in fit.items():
            if "xi_um" in r:
                print(f"  Fit [{key}]:  A={r['A']:.4f}, "
                      f"xi={r['xi_um']:.1f}±{r['xi_err']:.1f} µm, "
                      f"C={r.get('C',0):.4f}")

        plot_results(name, analysis, fit, coords, T2)
        xi = interpret(name, analysis, fit)

        all_results[name] = {
            "N_valid":      int(n_valid),
            "T2_mean_us":   analysis["T2_mean_us"],
            "T2_std_us":    analysis["T2_std_us"],
            "fit":          {k: {kk: float(vv) for kk,vv in v.items()
                                 if isinstance(vv, (int,float))}
                             for k,v in fit.items() if isinstance(v, dict)},
            "xi_fit_um":    float(xi) if xi is not None else None,
        }

    # Summary
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    for name, r in all_results.items():
        xi = r["xi_fit_um"]
        T2m = r["T2_mean_us"]
        if xi is not None:
            c_impl = (xi * 1e-6) / (2 * T2m * 1e-6)
            print(f"  {name}: xi_c = {xi:.0f} µm,  "
                  f"T2_mean = {T2m:.1f} µs,  "
                  f"implied c = {c_impl:.4f} m/s")
        else:
            print(f"  {name}: no reliable fit")
    print()
    print("  C2 prediction: xi_c = 2*c*tau_B = 2*c*T2_mean")
    print("  If xi_c ~ few*100 µm and T2_mean ~ few*10 µs:")
    print("  c_implied ~ few mm/s to cm/s")
    print("  This is MUCH slower than sound (6000 m/s) or phonons.")
    print()
    print("  SCIENTIFIC STATUS of this test:")
    print("  - If rho(d) decays with d: spatial correlation EXISTS")
    print("    (this alone is not C2-specific)")
    print("  - If the decay is EXPONENTIAL: consistent with C2 OR phonon bath")
    print("  - If xi_c ~ 2*c*T2_mean with c = known substrate speed: C2 prediction")
    print("  - The TRUE discriminant needs INDEPENDENT c measurement")
    print("    (e.g., from substrate phonon spectroscopy or SAW resonators)")

    # Save
    out = OUTDIR / "prw03_ibm_results.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  [saved] {out.name}")


if __name__ == "__main__":
    main()
