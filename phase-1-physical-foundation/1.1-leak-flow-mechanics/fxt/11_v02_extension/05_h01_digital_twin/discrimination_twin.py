"""Multi-mount H01 digital twin: quadratic signal versus mechanical artifact."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from digital_twin import fit_ramsey, load_config, ramsey_probabilities

HERE = Path(__file__).resolve().parent


def generate(config, injected_k, seed, fast=False):
    rng = np.random.default_rng(seed)
    omega = np.asarray(config["rotation_rad_s"], float)
    t = np.asarray(config["ramsey_times_s"], float)
    shots = int(config["shots_per_time"])
    mounts = [("soft", 2.5), ("reference", 1.0), ("damped", 0.25)]
    thermal_gamma = float(config.get("thermal_gamma_per_rad_s2", 0.0))
    monitor_bias = float(config.get("vibration_monitor_bias", 0.0))
    rows = []
    for name, gain in mounts:
        for w in omega:
            vibration = config["vibration_gamma_per_rad_s2"] * gain * w*w
            # A gain error may differ by mount. This is the dangerous calibration
            # failure that can make a mechanical signal look like a residual.
            mount_bias = monitor_bias * {"soft": 1.0, "reference": 0.0, "damped": -1.0}[name]
            monitor = vibration * (1 + mount_bias + rng.normal(0, config["monitor_fractional_noise"]))
            gamma = config["gamma0_s_inv"] + vibration + thermal_gamma*w*w + injected_k*w*w
            # The fast branch is the closed-form solution of the same pure-z
            # dephasing Ramsey model used by QuTiP above. It is used only for
            # large Monte Carlo sweeps after the QuTiP core has been validated.
            if fast:
                p = np.clip((1 + np.exp(-gamma*t)*np.cos(config["omega_q_rad_s"]*t))/2, 1e-9, 1-1e-9)
            else:
                p = ramsey_probabilities(t, gamma, config["omega_q_rad_s"])
            counts = rng.binomial(shots, p)
            (gfit, _), chi2 = fit_ramsey(t, counts, shots, config["omega_q_rad_s"])
            rows.append((name, gain, w, monitor, gamma, gfit, chi2))
    dtype = [("mount", "U16"), ("gain", float), ("omega", float), ("vibration_monitor", float),
             ("gamma_true", float), ("gamma_fit", float), ("chi2", float)]
    return np.array(rows, dtype=dtype)


def compare(data, seed):
    rng = np.random.default_rng(seed + 990)
    n = len(data); train = np.zeros(n, bool)
    # Stratified-ish random holdout across mount/rotation rows.
    train[rng.choice(n, size=int(.70*n), replace=False)] = True
    y = data["gamma_fit"]
    X_mech = np.column_stack([np.ones(n), data["vibration_monitor"]])
    X_full = np.column_stack([X_mech, data["omega"]**2])
    def fit(X):
        c, *_ = np.linalg.lstsq(X[train], y[train], rcond=None)
        return c, X@c
    cm, pm = fit(X_mech); cf, pf = fit(X_full)
    test = ~train
    return {"train": train, "pred_mech": pm, "pred_full": pf, "coef_mech": cm, "coef_full": cf,
            "rmse_mech": float(np.sqrt(np.mean((y[test]-pm[test])**2))),
            "rmse_full": float(np.sqrt(np.mean((y[test]-pf[test])**2))),
            "quadratic_coefficient": float(cf[-1])}


def run_case(config, label, injected_k, seed, out):
    data = generate(config, injected_k, seed)
    a = compare(data, seed)
    summary = {"label": label, "injected_k_s": injected_k, "scope": "synthetic discrimination benchmark only",
               "rmse_mechanical_only": a["rmse_mech"], "rmse_mechanical_plus_quadratic": a["rmse_full"],
               "quadratic_coefficient_estimate": a["quadratic_coefficient"]}
    (out / f"{label}_summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    np.savez_compressed(out / f"{label}_data.npz", data=data, **a)
    return data, a, summary


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--config", default=str(HERE / "config" / "default.json"))
    args = ap.parse_args(); config = load_config(args.config)
    out = HERE / "outputs" / "mechanical_discrimination"; out.mkdir(parents=True, exist_ok=True)
    sig_data, sig_a, sig = run_case(config, "signal_injected", config["k_injected_s"], config["seed"], out)
    null_data, null_a, null = run_case(config, "null", 0.0, config["seed"]+1, out)
    plt.figure(figsize=(6.7,4.3))
    for mount in np.unique(sig_data["mount"]):
        d=sig_data[sig_data["mount"]==mount]
        plt.scatter(d["omega"], d["gamma_fit"], label=mount)
    plt.xlabel("rotation rate Omega (rad/s)"); plt.ylabel("fitted dephasing rate (1/s)")
    plt.title("Same rotation schedule, changed mechanical transfer")
    plt.grid(alpha=.25); plt.legend(frameon=False); plt.tight_layout(); plt.savefig(out / "mount_comparison.png", dpi=160); plt.close()
    plt.figure(figsize=(6.7,4.3))
    for label, d, a in [("signal injection",sig_data,sig_a),("null",null_data,null_a)]:
        res=d["gamma_fit"]-a["pred_mech"]
        plt.scatter(d["omega"],res,label=label,alpha=.7)
    plt.axhline(0,color="black",lw=.8); plt.xlabel("rotation rate Omega (rad/s)")
    plt.ylabel("mechanical-model residual (1/s)"); plt.title("Residual after calibrated vibration monitor")
    plt.grid(alpha=.25); plt.legend(frameon=False); plt.tight_layout(); plt.savefig(out / "residual_discrimination.png", dpi=160); plt.close()
    report={"status":"SIMULATION_COMPLETE","purpose":"tests whether changing mechanical transfer breaks Omega^2 degeneracy",
            "signal_case":sig,"null_case":null,
            "interpretation":"Success means the synthetic design can separate its own declared models; it is not evidence for a substrate contribution."}
    (out / "report.json").write_text(json.dumps(report,indent=2)+"\n")
    (out / "run.log").write_text("multi-mount mechanical discrimination twin\nSTATUS: SIMULATION_COMPLETE\n")
    print(json.dumps(report,indent=2))

if __name__ == "__main__": main()
