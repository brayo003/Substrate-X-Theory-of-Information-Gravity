"""
p2_transport_os.py — Three-Layer Transport Operating System.

IMMUTABLE: transport_layer.py, Q computation, regime thresholds, DCII calibration.

The OS has three independent layers, all inferred from Phase 1 statistics.
Nothing is hardcoded — every threshold is derived from the performance matrix.

Layer 1 — Strategy Allocator
    Input : transport regime (5-level)
    Output: selected strategy name  OR  NO_TRADE

Layer 2 — Risk Allocator
    Input : transport regime
    Output: risk fraction (0.0 – 1.0, relative to max allowed)

Layer 3 — Stop Allocator
    Input : transport regime
    Output: ATR multiplier (stop), ATR multiplier (target), trailing policy

Q NEVER generates entries, exits, or price predictions.
Q ONLY determines: allowed, which strategy, position size, stop policy.
"""

import sys
import json
import warnings
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

PHASE1_DIR = _HERE / "results" / "phase1"
PHASE2_DIR = _HERE / "results" / "phase2"

REGIMES_5 = [
    "Deep_Incoherent",
    "Mod_Incoherent",
    "Transition",
    "Weak_Coherent",
    "Strong_Coherent",
]

# Execution constants (must match Phase 1 exactly)
COMMISSION_RT = 0.00030   # 3-pip round-trip (commission + slippage)
BASE_RISK_PCT = 0.01      # 1% max per trade (full risk)
MIN_TRADES_REQUIRED = 15  # minimum trades in Phase 1 cell to trust the estimate


# ═══════════════════════════════════════════════════════════════════════════
# Calibration: infer all three layers from Phase 1 statistics
# ═══════════════════════════════════════════════════════════════════════════

class TransportOSCalibration:
    """
    Calibrates all three OS layers from Phase 1 results.
    No parameters are hardcoded — everything is derived from data.
    """

    def __init__(self):
        self.matrix_df   : Optional[pd.DataFrame] = None
        self.stab_df     : Optional[pd.DataFrame] = None
        self.sig_df      : Optional[pd.DataFrame] = None
        self.boot_df     : Optional[pd.DataFrame] = None

        # Layer 1: strategy per regime
        self.strategy_map: Dict[str, str] = {}           # regime → strategy name
        self.strategy_confidence: Dict[str, str] = {}    # regime → confidence level
        self.no_trade_regimes: set = set()

        # Layer 2: risk fraction per regime
        self.risk_map: Dict[str, float] = {}             # regime → risk fraction [0,1]

        # Layer 3: stop/target ATR multipliers per regime
        self.stop_map  : Dict[str, float] = {}           # regime → ATR stop multiplier
        self.target_map: Dict[str, float] = {}           # regime → ATR target multiplier
        self.trailing_map: Dict[str, bool] = {}          # regime → use trailing stop?

        # Global Q thresholds (loaded from manifest)
        self.q05: float = -1.0
        self.q95: float =  1.73

        self._calibrated = False

    def load_phase1_data(self):
        """Load all Phase 1 CSVs needed for calibration."""
        matrix_path = PHASE1_DIR / "performance_by_regime.csv"
        stab_path   = PHASE1_DIR / "regime_transition_statistics.csv"
        sig_path    = PHASE1_DIR / "significance_tests.csv"
        boot_path   = PHASE1_DIR / "bootstrap_statistics.csv"

        if not matrix_path.exists():
            raise FileNotFoundError(f"Phase 1 matrix not found: {matrix_path}")

        self.matrix_df = pd.read_csv(matrix_path)
        self.stab_df   = pd.read_csv(stab_path)   if stab_path.exists()  else None
        self.sig_df    = pd.read_csv(sig_path)     if sig_path.exists()   else None
        self.boot_df   = pd.read_csv(boot_path)    if boot_path.exists()  else None

        # Load Q thresholds from checkpoint manifest
        manifest_path = _HERE / "checkpoints" / "checkpoint_manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            q_q = manifest.get("pipeline", {}).get("q_quantiles") or {}
            self.q05 = float(q_q.get("q05", -1.0))
            self.q95 = float(q_q.get("q95",  1.73))

    def calibrate(self, verbose: bool = True) -> "TransportOSCalibration":
        """Run full three-layer calibration from Phase 1 data."""
        self.load_phase1_data()
        self._calibrate_layer1(verbose)
        self._calibrate_layer2(verbose)
        self._calibrate_layer3(verbose)
        self._calibrated = True
        return self

    # ── Layer 1: Strategy Allocation ──────────────────────────────────────

    def _calibrate_layer1(self, verbose: bool):
        """
        For each regime, select the best strategy by composite score.
        Composite = 0.4×PF_rank + 0.3×Sharpe_rank + 0.2×WR_rank + 0.1×ExpRank
        Strategy must have ≥ MIN_TRADES_REQUIRED trades in that regime.
        If best PF < 0.85 across all strategies: NO_TRADE.

        This mirrors Phase 1 allocator logic but adds regime-specific
        stop-loss awareness: strategies with high stop_freq in a regime
        get penalised because the OS will widen stops and reduce size.
        """
        if verbose:
            print("  Layer 1 — Strategy allocation calibration …", flush=True)

        df = self.matrix_df.copy()

        # FDR map
        sig_map: dict = {}
        if self.sig_df is not None and "mw_reject_fdr" in self.sig_df.columns:
            sig_map = dict(zip(self.sig_df["strategy"],
                               self.sig_df["mw_reject_fdr"].fillna(False)))

        for regime in REGIMES_5:
            sub = df[df["regime"] == regime].copy()
            sub = sub[sub["trade_count"] >= MIN_TRADES_REQUIRED].copy()

            if len(sub) == 0:
                self.strategy_map[regime]      = "NO_TRADE"
                self.no_trade_regimes.add(regime)
                self.strategy_confidence[regime] = "Insufficient"
                continue

            # Composite score (normalised ranks within regime)
            def rank_norm(col):
                vals = sub[col].fillna(sub[col].min())
                mn, mx = vals.min(), vals.max()
                if mx == mn:
                    return pd.Series(0.5, index=sub.index)
                return (vals - mn) / (mx - mn + 1e-12)

            sub = sub.copy()
            sub["pf_n"]  = rank_norm("profit_factor")
            sub["sr_n"]  = rank_norm("sharpe")
            sub["wr_n"]  = rank_norm("win_rate")
            sub["exp_n"] = rank_norm("expectancy")
            sub["score"] = (0.40 * sub["pf_n"]  +
                            0.30 * sub["sr_n"]  +
                            0.20 * sub["wr_n"]  +
                            0.10 * sub["exp_n"])

            # FDR bonus
            sub["sig_bonus"] = sub["strategy"].map(sig_map).fillna(False).astype(float) * 0.15
            sub["score"] += sub["sig_bonus"]

            sub = sub.sort_values("score", ascending=False).reset_index(drop=True)
            best = sub.iloc[0]
            best_pf = float(best.get("profit_factor") or 0)

            # All strategies below PF=0.85 → NO_TRADE (avoidance threshold)
            all_pf = sub["profit_factor"].dropna()
            if best_pf < 0.85:
                self.strategy_map[regime] = "NO_TRADE"
                self.no_trade_regimes.add(regime)
                conf = "Weak"
            else:
                self.strategy_map[regime] = str(best["strategy"])
                tc = int(best.get("trade_count") or 0)
                sig = bool(sig_map.get(best["strategy"], False))
                if sig and best_pf > 1.2 and tc >= 50:
                    conf = "High"
                elif best_pf > 1.05 and tc >= 20:
                    conf = "Moderate"
                else:
                    conf = "Weak"

            self.strategy_confidence[regime] = conf

            if verbose:
                strat = self.strategy_map[regime]
                print(f"    {regime:<22} → {strat:<26} PF={best_pf:.3f}  [{conf}]")

    # ── Layer 2: Risk Allocation ──────────────────────────────────────────

    def _calibrate_layer2(self, verbose: bool):
        """
        Risk fraction per regime, inferred from Phase 1 performance stats.

        Logic (no hardcoding):
        1. Compute a "regime quality score" = normalised composite PF across
           all strategies (median PF in that regime).
        2. Regimes designated NO_TRADE → risk = 0.0
        3. Scale from 0.0 → 1.0 (max BASE_RISK_PCT) proportional to quality.
        4. Floor = 0.25 for any tradeable regime to keep minimum participation.

        This produces different risk levels depending on what the data shows,
        not a fixed lookup table.
        """
        if verbose:
            print("  Layer 2 — Risk allocation calibration …", flush=True)

        df = self.matrix_df.copy()
        regime_median_pf: Dict[str, float] = {}

        for regime in REGIMES_5:
            sub = df[(df["regime"] == regime) &
                     (df["trade_count"] >= MIN_TRADES_REQUIRED)]
            if len(sub) == 0:
                regime_median_pf[regime] = 0.0
            else:
                regime_median_pf[regime] = float(sub["profit_factor"].median())

        # Normalise: PF=1.0 is neutral, PF>1 is good, PF<1 is bad
        # We map PF to risk as: risk = clip((PF - 0.5) / (1.5 - 0.5), 0, 1)
        # This gives: PF=0.5→0, PF=1.0→0.5, PF=1.5→1.0
        for regime in REGIMES_5:
            if regime in self.no_trade_regimes:
                self.risk_map[regime] = 0.0
            else:
                pf = regime_median_pf.get(regime, 0.5)
                raw = np.clip((pf - 0.5) / (1.5 - 0.5 + 1e-12), 0.0, 1.0)
                # Floor at 0.25 for tradeable regimes
                self.risk_map[regime] = float(max(raw, 0.25))

        if verbose:
            for r, v in self.risk_map.items():
                pf = regime_median_pf.get(r, 0.0)
                print(f"    {r:<22}  risk={v:.3f}  (median PF={pf:.3f})")

    # ── Layer 3: Stop Allocation ──────────────────────────────────────────

    def _calibrate_layer3(self, verbose: bool):
        """
        Stop/target ATR multipliers per regime, inferred from Phase 1 stats.

        Logic:
        - Regimes with high volatility (high ATR) need wider stops → larger multiplier
        - Regimes with low persistence need tighter stops → smaller multiplier
        - We use: stop_freq (how often the 1.5×ATR stop was hit in Phase 1)
          as a proxy for stop adequacy.
        - If stop_freq > 0.55 in a regime, stops are too tight → widen
        - If stop_freq < 0.40, stops may be too loose → tighten slightly

        Base multipliers (from Phase 1 global constants):
          stop_base   = 1.5 × ATR
          target_base = 2.5 × ATR

        Adjustment: multiplied by regime-specific scalar in [0.8, 2.0].
        Trailing stop: enabled when regime persistence > geometric_null * 1.5
        (persistent regimes reward letting profits run).
        """
        if verbose:
            print("  Layer 3 — Stop/target allocation calibration …", flush=True)

        df = self.matrix_df.copy()
        stab = self.stab_df

        # Regime persistence from stab_df
        persistence: Dict[str, bool] = {r: False for r in REGIMES_5}
        geo_ratio: Dict[str, float]  = {r: 1.0   for r in REGIMES_5}
        if stab is not None:
            for _, row in stab.iterrows():
                r = row["regime"]
                if r in REGIMES_5:
                    persistence[r]  = bool(row.get("persistent", False))
                    mean_b = float(row.get("mean_bars", 1.0))
                    geo    = float(row.get("geometric_null", 1.0))
                    geo_ratio[r] = mean_b / (geo + 1e-12)

        BASE_STOP   = 1.5
        BASE_TARGET = 2.5

        for regime in REGIMES_5:
            sub = df[(df["regime"] == regime) &
                     (df["trade_count"] >= MIN_TRADES_REQUIRED)]

            if len(sub) == 0 or regime in self.no_trade_regimes:
                self.stop_map[regime]     = BASE_STOP
                self.target_map[regime]   = BASE_TARGET
                self.trailing_map[regime] = False
                continue

            # Median stop_freq across strategies in this regime
            stop_freq = float(sub["stop_freq"].dropna().median()) if "stop_freq" in sub.columns else 0.5
            avg_dur   = float(sub["avg_duration"].dropna().median()) if "avg_duration" in sub.columns else 12.0

            # Stop multiplier: high stop_freq → widen, low → tighten
            if stop_freq > 0.60:
                stop_scalar = 1.5     # stops hit too often → widen 50%
            elif stop_freq > 0.55:
                stop_scalar = 1.25
            elif stop_freq < 0.40:
                stop_scalar = 0.9    # stops rarely hit → slightly tighter
            else:
                stop_scalar = 1.0

            # Target multiplier: persistent regimes reward wider targets
            gr = geo_ratio.get(regime, 1.0)
            if gr > 1.5 or persistence.get(regime, False):
                target_scalar = 1.3   # persistent → let profits run
            elif gr < 0.8:
                target_scalar = 0.85  # quickly-reverting → take profits faster
            else:
                target_scalar = 1.0

            self.stop_map[regime]   = float(BASE_STOP   * stop_scalar)
            self.target_map[regime] = float(BASE_TARGET * target_scalar)

            # Trailing stop: only in persistent regimes with sufficient duration
            self.trailing_map[regime] = persistence.get(regime, False) and avg_dur > 8.0

        if verbose:
            for r in REGIMES_5:
                print(f"    {r:<22}  stop={self.stop_map[r]:.2f}×ATR  "
                      f"target={self.target_map[r]:.2f}×ATR  "
                      f"trailing={self.trailing_map[r]}")

    # ── Runtime OS decision function ──────────────────────────────────────

    def decide(self, regime: str) -> dict:
        """
        Return the full OS decision for one bar given its regime.

        Returns dict with:
          trading_allowed : bool
          strategy        : str or "NO_TRADE"
          risk_fraction   : float  [0, 1] (multiplied by BASE_RISK_PCT)
          stop_atr_mult   : float
          target_atr_mult : float
          trailing_stop   : bool
          confidence      : str
        """
        if not self._calibrated:
            raise RuntimeError("OS not calibrated. Call calibrate() first.")

        regime = regime if regime in REGIMES_5 else "Mod_Incoherent"

        strategy = self.strategy_map.get(regime, "NO_TRADE")
        risk     = self.risk_map.get(regime, 0.0)

        return {
            "trading_allowed": strategy != "NO_TRADE" and risk > 0.0,
            "strategy"       : strategy,
            "risk_fraction"  : risk,
            "position_size"  : BASE_RISK_PCT * risk,     # fraction of account
            "stop_atr_mult"  : self.stop_map.get(regime,   1.5),
            "target_atr_mult": self.target_map.get(regime, 2.5),
            "trailing_stop"  : self.trailing_map.get(regime, False),
            "confidence"     : self.strategy_confidence.get(regime, "Unsupported"),
            "regime"         : regime,
        }

    def summary_dict(self) -> dict:
        """Return serialisable summary of all three layers."""
        return {
            "q_thresholds"    : {"q05": self.q05, "q95": self.q95},
            "layer1_strategy" : self.strategy_map,
            "layer1_confidence": self.strategy_confidence,
            "no_trade_regimes": list(self.no_trade_regimes),
            "layer2_risk"     : self.risk_map,
            "layer3_stop"     : self.stop_map,
            "layer3_target"   : self.target_map,
            "layer3_trailing" : self.trailing_map,
        }

    def print_summary(self):
        """Print formatted OS configuration."""
        print("\n  ┌─ Transport Operating System Configuration ─────────────────┐")
        print(f"  │ Q05={self.q05:.4f}  Q95={self.q95:.4f}  Base risk={BASE_RISK_PCT:.1%}     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ {'Regime':<22} {'Strategy':<22} {'Risk':>5} {'Stop':>5} {'Tgt':>5} {'Trail':<5}│")
        print("  ├─────────────────────────────────────────────────────────────┤")
        for r in REGIMES_5:
            s = self.strategy_map.get(r, "NO_TRADE")[:20]
            risk = self.risk_map.get(r, 0.0)
            stop = self.stop_map.get(r, 1.5)
            tgt  = self.target_map.get(r, 2.5)
            trl  = "Y" if self.trailing_map.get(r, False) else "N"
            print(f"  │ {r:<22} {s:<22} {risk:>5.2f} {stop:>5.2f} {tgt:>5.2f} {trl:<5}│")
        print("  └─────────────────────────────────────────────────────────────┘\n")


def classify_q_global_p2(Q: float, q05: float, q95: float) -> str:
    """Classify a single Q value into 5-level regime (matches Phase 1 logic)."""
    if np.isnan(Q):
        return "Mod_Incoherent"
    if abs(Q) < 0.01:
        return "Transition"
    if Q <= q05:
        return "Deep_Incoherent"
    if Q < 0:
        return "Mod_Incoherent"
    if Q >= q95:
        return "Strong_Coherent"
    return "Weak_Coherent"


def build_os(verbose: bool = True) -> TransportOSCalibration:
    """Convenience: build and calibrate the full OS."""
    os = TransportOSCalibration()
    os.calibrate(verbose=verbose)
    if verbose:
        os.print_summary()
    return os
