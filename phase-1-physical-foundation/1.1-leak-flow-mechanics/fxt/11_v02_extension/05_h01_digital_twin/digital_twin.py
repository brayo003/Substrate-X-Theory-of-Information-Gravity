"""H01 rotation digital twin.

QuTiP generates Ramsey data for a two-level system.  Signal injections are
detectability benchmarks only; no injected coefficient is claimed to be a C2
prediction.  The analysis intentionally supports an omitted-vibration scenario
to quantify a false-positive failure mode.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qutip import basis, mesolve, sigmax, sigmaz
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent


def load_config(path):
    return json.loads(Path(path).read_text())


def ramsey_probabilities(t, gamma, detuning):
    """QuTiP Ramsey probabilities under pure dephasing and a z-frequency shift."""
    plus = (basis(2, 0) + basis(2, 1)).unit()
    H = 0.5 * detuning * sigmaz()
    # sqrt(gamma/2) sigma_z makes the coherence decay as exp(-gamma t).
    collapse = [np.sqrt(max(gamma, 0.0) / 2.0) * sigmaz()]
    sx = sigmax()
    result = mesolve(H, plus, t, c_ops=collapse, e_ops=[sx])
    return np.clip((1.0 + np.real(result.expect[0])) / 2.0, 1e-9, 1 - 1e-9)


def fit_ramsey(t, counts, shots, omega_q):
    y = counts / shots
    def residual(theta):
        gamma, delta = theta
        p = np.exp(-gamma * t) * np.cos((omega_q + delta) * t)
        model = (1 + p) / 2
        sigma = np.sqrt(np.maximum(model * (1 - model) / shots, 1e-8))
        return (y - model) / sigma
    out = least_squares(residual, [1.5e4, 0.0], bounds=([0, -2e5], [2e6, 2e5]))
    return out.x, float(np.sum(out.fun**2))


def simulate(config, seed_offset=0):
    rng = np.random.default_rng(int(config["seed"]) + seed_offset)
    omega = np.asarray(config["rotation_rad_s"], float)
    t = np.asarray(config["ramsey_times_s"], float)
    shots = int(config["shots_per_time"])
    gamma0 = float(config["gamma0_s_inv"])
    kinj = float(config["k_injected_s"])
    beta = float(config["beta_injected"])
    vib = float(config["vibration_gamma_per_rad_s2"])
    frac = float(config["monitor_fractional_noise"])
    mag = float(config["magnetic_hz_per_rad_s"])
    therm = float(config["thermal_hz_per_rad_s2"])

    # Monitors are noisy proxies for conventional rotation-correlated artifacts.
    vibration_true = vib * omega**2
    vibration_monitor = vibration_true * (1 + rng.normal(0, frac, len(omega)))
    magnetic_monitor = mag * omega * (1 + rng.normal(0, frac, len(omega)))
    thermal_monitor = therm * omega**2 * (1 + rng.normal(0, frac, len(omega)))
    gamma_true = gamma0 + vibration_true + kinj * omega**2
    delta_true = 2 * np.pi * (mag * omega + therm * omega**2) + beta * omega

    counts = []
    gamma_fit, delta_fit, chi2 = [], [], []
    for g, d in zip(gamma_true, delta_true):
        p = ramsey_probabilities(t, g, config["omega_q_rad_s"] + d)
        c = rng.binomial(shots, p)
        fit, c2 = fit_ramsey(t, c, shots, config["omega_q_rad_s"])
        counts.append(c); gamma_fit.append(fit[0]); delta_fit.append(fit[1]); chi2.append(c2)
    return {
        "omega": omega, "time": t, "counts": np.asarray(counts),
        "gamma_fit": np.asarray(gamma_fit), "delta_fit": np.asarray(delta_fit),
        "gamma_true": gamma_true, "delta_true": delta_true,
        "vibration_monitor": vibration_monitor, "magnetic_monitor": magnetic_monitor,
        "thermal_monitor": thermal_monitor, "fit_chi2": np.asarray(chi2),
    }


def regression(X, y, train):
    coef, *_ = np.linalg.lstsq(X[train], y[train], rcond=None)
    pred = X @ coef
    return coef, pred


def analyse(data, config):
    omega = data["omega"]
    y = data["gamma_fit"]
    rng = np.random.default_rng(int(config["seed"]) + 1000)
    train = np.zeros(len(omega), dtype=bool)
    train[rng.choice(len(omega), size=max(4, int(len(omega)*config["train_fraction"])), replace=False)] = True
    # Conventional model may contain all calibrated monitor channels. The
    # adversarial configuration deliberately omits vibration from this model.
    columns = [np.ones(len(omega)), data["magnetic_monitor"], data["thermal_monitor"]]
    names = ["intercept", "magnetic_monitor", "thermal_monitor"]
    if not config["analysis_omits_vibration"]:
        columns.append(data["vibration_monitor"]); names.append("vibration_monitor")
    X0 = np.column_stack(columns)
    X1 = np.column_stack([X0, omega**2])
    c0, p0 = regression(X0, y, train)
    c1, p1 = regression(X1, y, train)
    test = ~train
    rmse0 = float(np.sqrt(np.mean((y[test]-p0[test])**2)))
    rmse1 = float(np.sqrt(np.mean((y[test]-p1[test])**2)))
    rss0 = float(np.sum((y[train]-p0[train])**2))
    rss1 = float(np.sum((y[train]-p1[train])**2))
    n = int(train.sum())
    aic0 = n*np.log(max(rss0/n, 1e-12)) + 2*X0.shape[1]
    aic1 = n*np.log(max(rss1/n, 1e-12)) + 2*X1.shape[1]
    return {"train": train, "test": test, "names0": names, "coef0": c0, "coef1": c1,
            "pred0": p0, "pred1": p1, "rmse0": rmse0, "rmse1": rmse1,
            "aic0": float(aic0), "aic1": float(aic1), "delta_aic_signal_minus_null": float(aic1-aic0),
            "quadratic_coefficient_estimate": float(c1[-1])}


def plots(out, data, analysis, config):
    omega = data["omega"]
    plt.figure(figsize=(6.2, 4.0))
    plt.scatter(omega, data["gamma_fit"], c=np.where(analysis["train"], "#4477aa", "#cc6677"), label="fitted Ramsey rates")
    grid = np.linspace(omega.min(), omega.max(), 300)
    # Plot predictions only at observed grid points: monitors are measured data.
    plt.plot(omega, analysis["pred0"], "--", label="conventional monitor model")
    plt.plot(omega, analysis["pred1"], "-", label="monitor + quadratic model")
    plt.xlabel("rotation rate Omega (rad/s)"); plt.ylabel("fitted dephasing rate (1/s)")
    plt.title("H01 digital twin: blinded fitted rates"); plt.legend(frameon=False); plt.grid(alpha=.25)
    plt.tight_layout(); plt.savefig(out / "gamma_models.png", dpi=160); plt.close()

    idx = int(np.argmin(abs(omega)))
    p = data["counts"][idx] / int(config["shots_per_time"])
    plt.figure(figsize=(6.2, 4.0)); plt.plot(data["time"]*1e6, p, "o-")
    plt.xlabel("Ramsey delay (microseconds)"); plt.ylabel("measured P(+x)")
    plt.title("Example simulated Ramsey trace at nearest-zero rotation"); plt.grid(alpha=.25)
    plt.tight_layout(); plt.savefig(out / "ramsey_trace.png", dpi=160); plt.close()

    plt.figure(figsize=(6.2, 4.0))
    residual0 = data["gamma_fit"] - analysis["pred0"]
    plt.axhline(0, color="black", lw=.8); plt.scatter(omega, residual0)
    plt.xlabel("rotation rate Omega (rad/s)"); plt.ylabel("conventional-model residual (1/s)")
    plt.title("Residual diagnostic; inspect before unblinding")
    plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(out / "null_model_residual.png", dpi=160); plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "config" / "default.json"))
    ap.add_argument("--unblind", action="store_true", help="write injection truth alongside blinded summary")
    args = ap.parse_args()
    config = load_config(args.config)
    out = HERE / "outputs" / config["scenario"]
    out.mkdir(parents=True, exist_ok=True)
    data = simulate(config)
    a = analyse(data, config)
    plots(out, data, a, config)
    commitment = hashlib.sha256(json.dumps({k: config[k] for k in ("k_injected_s", "beta_injected", "seed")}, sort_keys=True).encode()).hexdigest()
    summary = {
        "status": "SIMULATION_COMPLETE", "scenario": config["scenario"],
        "scope": "detectability simulation only; injected signals are not evidence for C2",
        "blinding_commitment_sha256": commitment,
        "analysis": {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in a.items() if k not in ("pred0", "pred1")},
        "interpretation": "A lower held-out RMSE or AIC for the quadratic model is not a discovery; it only measures distinguishability under the declared synthetic assumptions."
    }
    (out / "blinded_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "run.log").write_text("H01 QuTiP digital twin\nscenario=%s\nstatus=SIMULATION_COMPLETE\n" % config["scenario"])
    np.savez_compressed(out / "intermediate_data.npz", **data, train=a["train"], pred0=a["pred0"], pred1=a["pred1"])
    if args.unblind:
        truth = {k: config[k] for k in ("k_injected_s", "beta_injected", "vibration_gamma_per_rad_s2", "analysis_omits_vibration")}
        (out / "unblinded_truth.json").write_text(json.dumps(truth, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
