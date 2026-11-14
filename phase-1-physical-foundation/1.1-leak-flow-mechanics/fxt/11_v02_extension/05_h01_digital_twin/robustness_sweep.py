"""Engineering robustness sweep for the multi-mount H01 digital twin.

All signals are synthetic. "Detection" means only that the locked
mechanical-plus-quadratic model beats the locked mechanical model on held-out
data by the declared criterion.
"""
import copy
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from digital_twin import load_config
from discrimination_twin import compare, generate

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "robustness_sweep"


def trial(cfg, k, offset):
    data = generate(cfg, k, int(cfg["seed"]) + offset, fast=True)
    analysis = compare(data, int(cfg["seed"]) + offset)
    improvement = (analysis["rmse_mech"] - analysis["rmse_full"]) / max(analysis["rmse_mech"], 1e-12)
    return improvement > .15 and analysis["quadratic_coefficient"] > 0


def main():
    base = load_config(HERE / "config" / "default.json")
    OUT.mkdir(parents=True, exist_ok=True)
    ks = np.array([0., .25, .5, .75, 1., 1.5, 2., 3.])
    monitor_noise = np.array([0., .02, .05, .10, .20, .35])
    reps = 8
    power = np.empty((len(monitor_noise), len(ks)))
    for i, noise in enumerate(monitor_noise):
        for j, k in enumerate(ks):
            hits = []
            for rep in range(reps):
                cfg = copy.deepcopy(base); cfg["monitor_fractional_noise"] = float(noise)
                hits.append(trial(cfg, float(k), 10000*i + 100*j + rep))
            power[i, j] = np.mean(hits)

    thermal = np.array([0., .25, .5, 1., 1.5, 2.])
    bias = np.array([0., .02, .05, .10, .20])
    fpr = np.empty((len(bias), len(thermal)))
    for i, b in enumerate(bias):
        for j, th in enumerate(thermal):
            hits = []
            for rep in range(reps):
                cfg = copy.deepcopy(base)
                cfg["thermal_gamma_per_rad_s2"] = float(th)
                cfg["vibration_monitor_bias"] = float(b)
                hits.append(trial(cfg, 0., 50000 + 10000*i + 100*j + rep))
            fpr[i, j] = np.mean(hits)

    thresholds = []
    for row in power:
        valid = np.where(row >= .8)[0]
        thresholds.append(float(ks[valid[0]]) if len(valid) else None)
    report = {
        "status": "SIMULATION_COMPLETE", "repetitions_per_cell": reps,
        "detection_rule": "held-out RMSE improvement >15% and positive quadratic coefficient",
        "minimum_k_for_80pct_detection_by_monitor_noise": dict(zip(map(str, monitor_noise), thresholds)),
        "max_false_positive_rate": float(fpr.max()),
        "scope": "engineering sensitivity only; does not establish a physical signal"
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    np.savez_compressed(OUT / "intermediate_data.npz", ks=ks, monitor_noise=monitor_noise,
                        power=power, thermal=thermal, bias=bias, false_positive_rate=fpr)
    (OUT / "run.log").write_text("H01 robustness sweep\nSTATUS: SIMULATION_COMPLETE\n")
    for arr, x, y, title, xlab, ylab, name in [
        (power, ks, monitor_noise, "Detection power versus signal and monitor noise", "injected quadratic k (s)", "vibration-monitor fractional noise", "detection_power.png"),
        (fpr, thermal, bias, "False-positive rate: thermal drift + monitor bias", "thermal quadratic drift (s)", "mount-dependent monitor bias", "false_positive_rate.png"),
    ]:
        plt.figure(figsize=(6.5, 4.2)); image = plt.pcolormesh(x, y, arr, shading="auto", vmin=0, vmax=1, cmap="viridis")
        plt.colorbar(image, label="probability"); plt.xlabel(xlab); plt.ylabel(ylab); plt.title(title)
        plt.tight_layout(); plt.savefig(OUT / name, dpi=160); plt.close()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
