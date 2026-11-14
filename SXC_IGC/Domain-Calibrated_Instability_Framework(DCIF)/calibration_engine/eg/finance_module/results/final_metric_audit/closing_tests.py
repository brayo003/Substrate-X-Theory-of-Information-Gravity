"""
closing_tests.py
================
Two decisive closing tests.

TEST 1 — Q reproducibility / algebraic-equivalence check
---------------------------------------------------------
Q = 100 * grad_ln_s^2 - 1  is a monotone function of |grad_ln_s|.
For the Q>0 threshold, the algebraically equivalent |grad_ln_s| threshold
is |grad_ln_s| > 0.1.  For Q >= q95 = 1.732, the equivalent is
|grad_ln_s| > sqrt((1.732+1)/100) = sqrt(0.02732) = 0.16529.

Using the SAME independent transition labels, dates, and thresholds as the
prior test (transition_detection_results.csv), the two detectors must
produce identical TP/FP/FN/TN counts.  Any divergence indicates a bug
or a mismatch in threshold mapping.

TEST 2 — T_sys incremental value, HELD-OUT period
--------------------------------------------------
Does T_sys improve forward-volatility predictions after conditioning on
recent realized volatility, in the 2026 out-of-sample period?

Two OLS models, evaluated in strict chronological order on 2026 data only:
  Model A (baseline):  fwd_vol ~ rv5            (rv5 = 5-bar realized vol at t)
  Model B (augmented): fwd_vol ~ rv5 + T_sys

Horizons: k = 3, 6, 12 bars forward (matching the calibration-period test).
Evaluation: out-of-sample R^2 (variance explained), residual MSE, and the
t-statistic on the T_sys coefficient in Model B.

"Held-out" here means: the 2026 parquet was never used to fit any model
parameter in the calibration pipeline.  The OLS coefficients are fitted on
the CALIBRATION period (2023-2025) and applied to 2026 data — no data
from 2026 enters the coefficient estimates.

Outputs: closing_tests_results.txt
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

_HERE  = Path(__file__).resolve().parent.parent.parent   # finance_module/
_AUDIT = _HERE / "results" / "final_metric_audit"
sys.path.insert(0, str(_HERE))

OUT = _AUDIT / "closing_tests_results.txt"

# ── Data loading ──────────────────────────────────────────────────────────

def load_calibration():
    """Load all calibration-period monthly parquets."""
    cache = _HERE / "cache"
    frames = []
    for pq in sorted(cache.glob("ohlc_transport_*.parquet")):
        df = pd.read_parquet(pq, columns=[
            "close", "tr_Q", "tr_grad_ln_s", "T_sys", "realized_vol_5"
        ])
        frames.append(df)
    full = pd.concat(frames).sort_index()
    return full[~full.index.duplicated(keep="first")]


def load_oos():
    """Load the 2026 OOS parquet. realized_vol_5 absent; compute from close."""
    oos_path = (_HERE / "results" / "bounded_validation_corrected"
                / "df_2026_cached.parquet")
    df = pd.read_parquet(oos_path, columns=[
        "close", "tr_Q", "tr_grad_ln_s", "T_sys"
    ])
    df = df[~df.index.duplicated(keep="first")]
    # Compute rv5 identically to the calibration pipeline: rolling(5).std() of log-returns
    log_ret = np.log(df["close"] / df["close"].shift(1))
    df["realized_vol_5"] = log_ret.rolling(5).std()
    return df


# ── Shared helpers ────────────────────────────────────────────────────────

def make_fwd_vol(close: pd.Series, k: int) -> pd.Series:
    """Forward k-bar realized volatility starting at t+1."""
    log_ret = np.log(close / close.shift(1))
    # Sum of squared log-returns over bars t+1 .. t+k
    # = rolling sum of lr^2 shifted back by k
    sq = log_ret ** 2
    fwd = sq.shift(-1).rolling(k).sum().shift(-(k - 1))
    return fwd


def detection_metrics(det: pd.Series, label: pd.Series) -> dict:
    valid = ~(det.isna() | label.isna())
    d = det[valid].astype(bool)
    l = label[valid].astype(bool)
    tp = int((d & l).sum())
    fp = int((d & ~l).sum())
    fn = int((~d & l).sum())
    tn = int((~d & ~l).sum())
    prec = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    rec  = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    f1   = (2*prec*rec/(prec+rec)
            if not (np.isnan(prec) or np.isnan(rec) or prec+rec == 0) else np.nan)
    fpr  = fp / (fp + tn) if (fp + tn) > 0 else np.nan
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, prec=prec, rec=rec, f1=f1, fpr=fpr)


# ═══════════════════════════════════════════════════════════════════════════
# TEST 1 — Algebraic equivalence / reproducibility
# ═══════════════════════════════════════════════════════════════════════════

def test1_equivalence(cal: pd.DataFrame, lines: list):
    lines.append("=" * 70)
    lines.append("TEST 1 — Q vs |grad_ln_s|: Algebraic Equivalence Check")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Theory: Q = 100 * grad_ln_s^2 - 1")
    lines.append("  Q > 0   ↔  |grad_ln_s| > 0.10000  (exact)")
    lines.append("  Q >= q95 = 1.732  ↔  |grad_ln_s| > sqrt(2.732/100) = 0.16529")
    lines.append("")

    Q         = cal["tr_Q"]
    grad_abs  = cal["tr_grad_ln_s"].abs()
    close     = cal["close"]

    # Independent transition labels — same definition as prior test
    log_ret   = np.log(close / close.shift(1))
    rv5       = log_ret.rolling(5).std()
    rv5_pre   = rv5.rolling(12).median()
    rv5_post  = rv5.shift(-12).rolling(12).median()
    ratio     = rv5_post / (rv5_pre + 1e-12)
    label_up  = ((ratio >= 2.0) & rv5_pre.notna() & rv5_post.notna()).astype(int)

    n_events  = label_up.sum()
    n_total   = label_up.notna().sum()
    lines.append(f"Transition label: RV_post/RV_pre >= 2.0 over next 12 bars")
    lines.append(f"  Events: {n_events:,} of {n_total:,} bars ({n_events/n_total:.2%})")
    lines.append("")

    # Threshold pairs
    pairs = [
        ("Q > 0",
         Q > 0,
         "|grad_ln_s| > 0.10000",
         grad_abs > 0.10000),
        ("Q >= 1.732 (q95)",
         Q >= 1.7322887804197729,
         "|grad_ln_s| > 0.16529",
         grad_abs > np.sqrt(2.7322887804197729 / 100.0)),
        ("Q > -0.208 (Q p75, from prior test)",
         Q > -0.208,
         "|grad_ln_s| > 0.08888",
         grad_abs > np.sqrt(((-0.208) + 1.0) / 100.0)),
    ]

    all_match = True
    for q_label, q_det, g_label, g_det in pairs:
        mq = detection_metrics(q_det, label_up)
        mg = detection_metrics(g_det, label_up)

        # Check exact integer match
        tp_match = (mq["tp"] == mg["tp"])
        fp_match = (mq["fp"] == mg["fp"])
        fn_match = (mq["fn"] == mg["fn"])
        tn_match = (mq["tn"] == mg["tn"])
        match = tp_match and fp_match and fn_match and tn_match

        # Also verify detector series are identical
        valid   = ~(q_det.isna() | g_det.isna())
        det_match = (q_det[valid] == g_det[valid]).all()

        all_match = all_match and match and det_match

        lines.append(f"  Threshold pair:")
        lines.append(f"    Q-form:    {q_label}")
        lines.append(f"    Grad-form: {g_label}")
        lines.append(f"    Q    → TP={mq['tp']:,}  FP={mq['fp']:,}  FN={mq['fn']:,}  TN={mq['tn']:,}"
                     f"  F1={mq['f1']:.6f}")
        lines.append(f"    Grad → TP={mg['tp']:,}  FP={mg['fp']:,}  FN={mg['fn']:,}  TN={mg['tn']:,}"
                     f"  F1={mg['f1']:.6f}")
        lines.append(f"    Detector series identical: {det_match}")
        lines.append(f"    Confusion matrix identical: {match}")
        lines.append("")

    lines.append(f"RESULT: All threshold pairs produce identical outputs: {all_match}")
    lines.append("")
    if all_match:
        lines.append("Interpretation: Q and |grad_ln_s| are confirmed algebraically")
        lines.append("equivalent for any threshold-based detection task. The Q transform")
        lines.append("(squaring + scaling + offset) adds zero information for classification.")
        lines.append("If |grad_ln_s| is retained as a detector, Q is redundant.")
        lines.append("If Q is retained, its threshold of 0 corresponds exactly to")
        lines.append("|grad_ln_s| = 0.10 — a 10% relative change in the composite field.")
    else:
        lines.append("WARNING: Mismatch detected — check threshold mapping.")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 2 — T_sys incremental value on held-out 2026 data
# ═══════════════════════════════════════════════════════════════════════════

def fit_ols(X: np.ndarray, y: np.ndarray):
    """OLS via normal equations. X already includes intercept column."""
    XtX = X.T @ X
    Xty = X.T @ y
    try:
        beta = np.linalg.solve(XtX, Xty)
    except np.linalg.LinAlgError:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return beta


def oos_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Out-of-sample R^2 = 1 - SS_res / SS_tot."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan


def test2_tsys_oos(cal: pd.DataFrame, oos: pd.DataFrame, lines: list):
    lines.append("=" * 70)
    lines.append("TEST 2 — T_sys Incremental Value: Held-Out 2026 Evaluation")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Design:")
    lines.append("  Model A: fwd_vol ~ intercept + rv5")
    lines.append("  Model B: fwd_vol ~ intercept + rv5 + T_sys")
    lines.append("  Fit: OLS on calibration period (2023-01-01 to 2025-10-24)")
    lines.append("  Evaluate: OOS R^2 and residual MSE on 2026 data only")
    lines.append("  Horizons: k = 3, 6, 12 bars forward (15, 30, 60 minutes)")
    lines.append("")
    lines.append(f"  Calibration bars: {len(cal):,}")
    lines.append(f"  OOS bars (2026):  {len(oos):,}")
    lines.append("")

    for k in [3, 6, 12]:
        lines.append(f"--- Horizon k={k} ({k*5} minutes) ---")

        # ── Calibration set ──────────────────────────────────────────────
        cal_fv  = make_fwd_vol(cal["close"], k)
        cal_rv5 = cal["realized_vol_5"]
        cal_T   = cal["T_sys"]

        cal_df = pd.DataFrame({
            "fwd_vol": cal_fv,
            "rv5":     cal_rv5,
            "T_sys":   cal_T,
        }).dropna()

        n_cal = len(cal_df)
        y_cal = cal_df["fwd_vol"].values

        # Model A: intercept + rv5
        Xa = np.column_stack([np.ones(n_cal), cal_df["rv5"].values])
        ba = fit_ols(Xa, y_cal)

        # Model B: intercept + rv5 + T_sys
        Xb = np.column_stack([np.ones(n_cal), cal_df["rv5"].values, cal_df["T_sys"].values])
        bb = fit_ols(Xb, y_cal)

        # ── OOS set ──────────────────────────────────────────────────────
        oos_fv  = make_fwd_vol(oos["close"], k)
        oos_rv5 = oos["realized_vol_5"]
        oos_T   = oos["T_sys"]

        oos_df = pd.DataFrame({
            "fwd_vol": oos_fv,
            "rv5":     oos_rv5,
            "T_sys":   oos_T,
        }).dropna()

        n_oos = len(oos_df)
        y_oos = oos_df["fwd_vol"].values

        # OOS predictions using calibration-fitted coefficients
        Xa_oos = np.column_stack([np.ones(n_oos), oos_df["rv5"].values])
        Xb_oos = np.column_stack([np.ones(n_oos), oos_df["rv5"].values, oos_df["T_sys"].values])

        pred_a = Xa_oos @ ba
        pred_b = Xb_oos @ bb

        r2_a = oos_r2(y_oos, pred_a)
        r2_b = oos_r2(y_oos, pred_b)
        mse_a = float(np.mean((y_oos - pred_a) ** 2))
        mse_b = float(np.mean((y_oos - pred_b) ** 2))

        delta_r2  = r2_b - r2_a
        delta_mse = mse_b - mse_a   # negative = improvement

        # T_sys coefficient and its in-sample t-statistic
        tsys_coef = bb[2]
        # In-sample residuals for SE
        resid_b = y_cal - (Xb @ bb)
        s2      = np.sum(resid_b**2) / (n_cal - 3)
        XtX_inv = np.linalg.inv(Xb.T @ Xb)
        se_tsys = np.sqrt(s2 * XtX_inv[2, 2])
        t_stat  = tsys_coef / se_tsys if se_tsys > 0 else np.nan

        lines.append(f"  Calibration n={n_cal:,}  |  OOS n={n_oos:,}")
        lines.append(f"  Calibration-period OLS coefficients:")
        lines.append(f"    Model A: intercept={ba[0]:.6f}  rv5={ba[1]:.4f}")
        lines.append(f"    Model B: intercept={bb[0]:.6f}  rv5={bb[1]:.4f}  T_sys={bb[2]:.6f}")
        lines.append(f"    T_sys coef in-sample t-stat: {t_stat:.3f}"
                     f"  (significant if |t| > 2)")
        lines.append(f"")
        lines.append(f"  OOS 2026 performance:")
        lines.append(f"    Model A (rv5 only):    OOS R^2 = {r2_a:.6f}   MSE = {mse_a:.2e}")
        lines.append(f"    Model B (rv5 + T_sys): OOS R^2 = {r2_b:.6f}   MSE = {mse_b:.2e}")
        lines.append(f"    ΔR^2 (B − A):          {delta_r2:+.6f}")
        lines.append(f"    ΔMSE (B − A):          {delta_mse:+.2e}"
                     f"  ({'improvement' if delta_mse < 0 else 'degradation'})")
        lines.append("")

    # ── Summary verdict ──────────────────────────────────────────────────
    lines.append("RESULT SUMMARY:")
    lines.append("  The ΔR^2 values above quantify T_sys's incremental contribution")
    lines.append("  on strictly held-out 2026 data, after rv5 has already been used.")
    lines.append("  A positive ΔR^2 means T_sys adds predictive information.")
    lines.append("  A negative or near-zero ΔR^2 means T_sys adds noise or nothing.")
    lines.append("")
    lines.append("  Threshold for retention in predictive core:")
    lines.append("  ΔR^2 > 0.005 (0.5 percentage points) on OOS data would constitute")
    lines.append("  meaningful incremental value. Below that threshold, retaining T_sys")
    lines.append("  in the predictive core is not justified by this evidence.")
    lines.append("")
    lines.append("  If ΔR^2 is negative, T_sys actively degrades OOS predictions —")
    lines.append("  the calibration-period in-sample fit has overfit the T_sys signal.")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print("Loading data…", flush=True)
    cal = load_calibration()
    oos = load_oos()
    print(f"  Calibration: {len(cal):,} bars  {cal.index.min()} → {cal.index.max()}")
    print(f"  OOS 2026:    {len(oos):,} bars  {oos.index.min()} → {oos.index.max()}")

    lines = []
    lines.append("CLOSING TESTS — Q Equivalence and T_sys OOS Incremental Value")
    lines.append(f"Run date: 2026-10-11 | Git commit: 6738ed05")
    lines.append(f"Calibration: {cal.index.min()} → {cal.index.max()} ({len(cal):,} bars)")
    lines.append(f"OOS period:  {oos.index.min()} → {oos.index.max()} ({len(oos):,} bars)")
    lines.append("")

    print("\nRunning Test 1 — Q algebraic equivalence…", flush=True)
    test1_equivalence(cal, lines)

    print("Running Test 2 — T_sys OOS incremental value…", flush=True)
    test2_tsys_oos(cal, oos, lines)

    text = "\n".join(lines)
    OUT.write_text(text)
    print(f"\nResults written to {OUT}")
    print()
    print(text)


if __name__ == "__main__":
    main()
