"""
run_transition_test.py
======================
Independent transition-detection test for Q.

Goal: determine whether Q detects independently defined transitions
better than simple alternatives, without using Q's own threshold
as the transition definition.

Independent transition labels defined here:
    A "volatility-regime shift" occurs at bar t if:
      RV_post(t) = median(rv5[t+1 .. t+12]) and
      RV_pre(t)  = median(rv5[t-12 .. t-1])
      and RV_post / RV_pre >= 2.0  (a doubling of volatility in the next 60 min)

    A "volatility-calm" occurs at bar t if:
      RV_post / RV_pre <= 0.5  (halving of volatility)

    Both are independently defined from price alone, with no reference to Q or s.

Detectors compared:
    1. Q > 0                      (coherent, the actual system threshold)
    2. Q >= q95 = 1.732           (strong coherent)
    3. |rv5| > rv5_p75            (simple absolute-volatility threshold)
    4. |delta_s| > delta_s_p75    (absolute 1-bar change in composite s)
    5. Q > q_p75                  (Q at its own 75th percentile)

Metrics: precision, recall, F1, false-positive rate.
Note on horizon: detection is at bar t; transition target looks 1..12 bars ahead.
The detector does not use any future information.

Outputs written to results/final_metric_audit/:
    transition_detection_results.csv
    transition_detection_summary.txt
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE  = Path(__file__).resolve().parent.parent.parent  # = finance_module/
_AUDIT = _HERE / "results" / "final_metric_audit"

sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE / "v12_validate"))


# ── Load cached Q series ──────────────────────────────────────────────────

def load_q_series():
    """Load the full cached Q + composite series from monthly parquets."""
    cache_dir = _HERE / "cache"
    frames = []
    for pq in sorted(cache_dir.glob("ohlc_transport_*.parquet")):
        df = pd.read_parquet(pq, columns=["close", "tr_Q", "tr_grad_ln_s",
                                           "composite_norm", "realized_vol_5",
                                           "T_sys"])
        frames.append(df)
    if not frames:
        raise FileNotFoundError("No monthly cache parquets found in cache/")
    full = pd.concat(frames).sort_index()
    full = full[~full.index.duplicated(keep="first")]
    return full


# ── Build independent transition labels ──────────────────────────────────

def build_transition_labels(df: pd.DataFrame,
                             pre_window: int = 12,
                             post_window: int = 12,
                             vol_up_ratio: float = 2.0,
                             vol_dn_ratio: float = 0.5) -> pd.DataFrame:
    """
    Construct independent transition labels from price data alone.
    rv5 is the 5-bar realized volatility of EUR/USD close.
    Label = 1 at bars where the next post_window bars have >2x higher
    median vol than the prior pre_window bars.
    Label = -1 for the reverse (vol halving).
    Label = 0 otherwise.
    """
    close = df["close"]
    log_ret = np.log(close / close.shift(1))

    # rv5: 5-bar realized vol (used as both input and target building block)
    rv5 = log_ret.rolling(5).std()

    # Build pre and post medians at each bar
    rv5_pre  = rv5.rolling(pre_window).median()
    rv5_post = rv5.shift(-post_window).rolling(post_window).median()

    ratio = rv5_post / (rv5_pre + 1e-12)

    labels = pd.Series(0, index=df.index, dtype=np.int8)
    labels[ratio >= vol_up_ratio]  =  1   # volatility expansion
    labels[ratio <= vol_dn_ratio]  = -1   # volatility contraction

    # Drop bars where label cannot be computed (NaN in rv5 windows)
    valid = (~rv5_pre.isna()) & (~rv5_post.isna())
    labels[~valid] = 0

    result = df[["tr_Q", "tr_grad_ln_s", "composite_norm",
                 "realized_vol_5", "T_sys"]].copy()
    result["rv5"]       = rv5
    result["rv5_pre"]   = rv5_pre
    result["rv5_post"]  = rv5_post
    result["ratio"]     = ratio
    result["label_up"]  = (labels == 1).astype(int)
    result["label_dn"]  = (labels == -1).astype(int)
    result["label_any"] = (labels != 0).astype(int)
    return result


# ── Detection metrics ─────────────────────────────────────────────────────

def detection_metrics(detector: pd.Series, label: pd.Series) -> dict:
    """Compute precision, recall, F1, FPR for binary detector vs label."""
    valid = ~(detector.isna() | label.isna())
    d = detector[valid].astype(bool)
    l = label[valid].astype(bool)

    tp = int((d & l).sum())
    fp = int((d & ~l).sum())
    fn = int((~d & l).sum())
    tn = int((~d & ~l).sum())

    n = tp + fp + fn + tn
    precision = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    recall    = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + np.nan_to_num(recall)) > 0 else np.nan)
    fpr       = fp / (fp + tn) if (fp + tn) > 0 else np.nan
    base_rate = l.mean()

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn, "n": n,
        "precision": precision, "recall": recall, "f1": f1,
        "fpr": fpr, "base_rate": base_rate,
    }


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print("Loading cached data…", flush=True)
    df = load_q_series()
    print(f"  {len(df):,} bars loaded, {df.index.min()} → {df.index.max()}")

    print("Building transition labels…", flush=True)
    data = build_transition_labels(df)

    n_up  = data["label_up"].sum()
    n_dn  = data["label_dn"].sum()
    n_any = data["label_any"].sum()
    n_tot = len(data)
    print(f"  Volatility expansion events (2× in 60 min): {n_up:,} ({n_up/n_tot:.1%})")
    print(f"  Volatility contraction events (½× in 60 min): {n_dn:,} ({n_dn/n_tot:.1%})")
    print(f"  Any transition: {n_any:,} ({n_any/n_tot:.1%})")

    Q          = data["tr_Q"]
    grad_ln_s  = data["tr_grad_ln_s"].abs()   # |grad_ln_s| = direct Q input
    rv5        = data["rv5"]
    T_sys      = data["T_sys"]

    # Thresholds
    q95  = -0.9979956145675514   # q05 from manifest — wait, q95 is 1.732
    # Correct values from manifest:
    Q_Q95  = 1.7322887804197729   # 95th pct of Q (Strong_Coherent threshold)
    Q_Q05  = -0.9979956145675514  # 5th pct of Q (Deep_Incoherent threshold)
    Q_p75  = float(Q.quantile(0.75))
    rv5_p75 = float(rv5.quantile(0.75))
    gs_p75  = float(grad_ln_s.quantile(0.75))
    T_p75   = float(T_sys.quantile(0.75))

    print(f"\n  Detector thresholds:")
    print(f"    Q > 0           (coherent): fraction={( Q > 0).mean():.3f}")
    print(f"    Q >= {Q_Q95:.3f}  (strong_coherent): fraction={(Q >= Q_Q95).mean():.3f}")
    print(f"    Q > {Q_p75:.3f}   (Q p75): fraction={(Q > Q_p75).mean():.3f}")
    print(f"    rv5 > {rv5_p75:.6f}  (rv5 p75): fraction={(rv5 > rv5_p75).mean():.3f}")
    print(f"    |grad_ln_s| > {gs_p75:.4f}  (grad p75): fraction={(grad_ln_s > gs_p75).mean():.3f}")
    print(f"    T_sys > {T_p75:.3f}   (T_sys p75): fraction={(T_sys > T_p75).mean():.3f}")

    detectors = {
        "Q>0 (coherent)"           : Q > 0,
        "Q>=q95 (Strong_Coherent)" : Q >= Q_Q95,
        "Q>p75"                    : Q > Q_p75,
        "|grad_ln_s|>p75 (Q input)": grad_ln_s > gs_p75,
        "rv5>p75 (simple vol)"     : rv5 > rv5_p75,
        "T_sys>p75"                : T_sys > T_p75,
    }

    targets = {
        "vol_expansion (2x)"  : data["label_up"],
        "vol_contraction (½x)": data["label_dn"],
        "any_transition"      : data["label_any"],
    }

    rows = []
    for det_name, det in detectors.items():
        for tgt_name, tgt in targets.items():
            m = detection_metrics(det, tgt)
            rows.append({
                "detector"   : det_name,
                "target"     : tgt_name,
                "precision"  : round(m["precision"], 4) if not np.isnan(m["precision"]) else np.nan,
                "recall"     : round(m["recall"],    4) if not np.isnan(m["recall"])    else np.nan,
                "f1"         : round(m["f1"],        4) if not np.isnan(m["f1"])        else np.nan,
                "fpr"        : round(m["fpr"],       4) if not np.isnan(m["fpr"])       else np.nan,
                "base_rate"  : round(m["base_rate"], 4),
                "tp"         : m["tp"],
                "fp"         : m["fp"],
                "fn"         : m["fn"],
                "tn"         : m["tn"],
                "n"          : m["n"],
            })

    results = pd.DataFrame(rows)
    out_csv = _AUDIT / "transition_detection_results.csv"
    results.to_csv(out_csv, index=False)
    print(f"\nFull results → {out_csv}")

    # ── Human-readable summary ─────────────────────────────────────────
    summary_path = _AUDIT / "transition_detection_summary.txt"
    with open(summary_path, "w") as f:
        f.write("TRANSITION DETECTION TEST — Q vs SIMPLE BASELINES\n")
        f.write("=" * 60 + "\n")
        f.write(f"Data: {len(df):,} bars, {df.index.min()} → {df.index.max()}\n")
        f.write(f"Independent label: RV_post/RV_pre ratio (pre/post = 12 bars each)\n")
        f.write(f"  Expansion events (ratio >= 2.0): {n_up:,} ({n_up/n_tot:.2%})\n")
        f.write(f"  Contraction events (ratio <= 0.5): {n_dn:,} ({n_dn/n_tot:.2%})\n\n")
        f.write("NOTE: All detectors use only information available at bar t.\n")
        f.write("      Label uses RV from t+1 to t+12 — strictly future, not in detector.\n\n")

        for tgt_name in targets:
            f.write(f"\n--- Target: {tgt_name} ---\n")
            sub = results[results["target"] == tgt_name].copy()
            base = sub["base_rate"].iloc[0]
            f.write(f"  Base rate: {base:.4f} ({base:.2%} of bars are transitions)\n\n")
            f.write(f"  {'Detector':<36} {'Prec':>6} {'Rec':>6} {'F1':>6} {'FPR':>6}\n")
            f.write(f"  {'-'*36} {'-'*6} {'-'*6} {'-'*6} {'-'*6}\n")
            for _, row in sub.iterrows():
                f.write(f"  {row['detector']:<36} "
                        f"{row['precision']:>6.4f} "
                        f"{row['recall']:>6.4f} "
                        f"{row['f1']:>6.4f} "
                        f"{row['fpr']:>6.4f}\n")

        f.write("\n\nINTERPRETATION NOTES\n")
        f.write("-" * 60 + "\n")
        f.write("1. Precision = TP/(TP+FP): of all bars flagged, what fraction\n")
        f.write("   precede a transition? Higher is better.\n")
        f.write("2. Recall = TP/(TP+FN): of all transitions, what fraction were\n")
        f.write("   flagged? Higher is better.\n")
        f.write("3. F1 = harmonic mean of precision and recall.\n")
        f.write("4. FPR = FP/(FP+TN): false alarm rate.\n")
        f.write("5. A detector with no skill matches the base rate in precision\n")
        f.write("   and has F1 ≈ 2*base_rate/(1+base_rate).\n")
        f.write("6. |grad_ln_s| is the direct mathematical input to Q.\n")
        f.write("   If Q and |grad_ln_s| have identical F1, Q adds nothing\n")
        f.write("   beyond its own input for transition detection.\n")

    print(f"Summary   → {summary_path}")

    # Quick print of key F1 row for vol_expansion
    print("\nKey results (vol_expansion target, F1 comparison):")
    sub = results[results["target"] == "vol_expansion (2x)"][["detector","precision","recall","f1","fpr","base_rate"]]
    print(sub.to_string(index=False))


if __name__ == "__main__":
    main()
