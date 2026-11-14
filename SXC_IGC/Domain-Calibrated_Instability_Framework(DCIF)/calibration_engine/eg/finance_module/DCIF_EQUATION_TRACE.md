# DCIF Equation Trace
## Finance Module — Equation-by-Equation Mapping to Parent Framework

**Audit date:** 2026-10-17  
**Git commit:** `6738ed05`  
**Auditor:** Forensic audit (kiro-cli)

---

## 1. Authoritative Parent Framework Equations

Two distinct mathematical forms exist in the parent framework. Both are audited here.

### 1.1 Static DCII Equation (MODULE_TUTORIAL.md)

Source: `calibration_engine/MODULE_TUTORIAL.md`, Section 2  
```
T = α|∇ρ| + βE - γF
```

| Symbol | Meaning | Role |
|--------|---------|------|
| ρ | Density / concentration | Structural pressure |
| \|∇ρ\| | Density gradient | Spatial or network tension |
| E | Excitation | Rate of destabilizing activity |
| F | Damping | Friction / resistance / stabilization |
| T | Instability Index | Escalation likelihood |
| α, β, γ | Calibrated scalars | Domain-local coefficients |

Calibration procedure: Solve linear system Ax=b from two anchor points (stable state T≈0, crisis state T≈0.5–0.7).

### 1.2 Dynamic Omega Engine Equation (SXC_V12_CORE.py)

Source: `calibration_engine/SXC_V12_CORE.py`  
```
dT_sys/dt = E(signal)·β - γ_eff·γ·T_sys
```
Discretized as:
```
T_sys += (inflow - outflow) * dt
inflow  = E(signal) * beta         # where beta=3.5
outflow = gamma_eff * gamma * T_sys # where gamma_eff=2.2 in FIREWALL, 1.0 in NOMINAL
```
With phase transitions: FIREWALL when T_sys > 1.0; revert to NOMINAL when T_sys < 0.4.

### 1.3 Transport PDE (v12_validate/transport_layer.py)

Source: `v12_validate/transport_layer.py`, docstring header  
Telegraph equation (1D temporal):
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∂²s/∂t²
```
Derived transport discriminant:
```
Q = 4(cτ)² |∇ln(s)|² − 1
```
With default parameters c=1.0, τ=5.0 bars (25 minutes at 5-min bars).

---

## 2. Equation-to-Implementation Mapping Table

| Parent Framework Concept | Authoritative Source & Equation | Finance Implementation | Exact Code Location | Status |
|---|---|---|---|---|
| **Static DCII equation** T = α\|∇ρ\| + βE - γF | MODULE_TUTORIAL.md §2 | `DCIIEquation.compute()` computes β×mean(signals) - γ×std(signals) + α×sum(gradient_terms). Replaces (E-F) decomposition with mean-std heuristic. No domain-specific calibration of ρ, E, F signals. | `src/dcii_core.py` lines 20–44 | **Simplified approximation** |
| **Density ρ (structural pressure)** | MODULE_TUTORIAL.md §4.3 | Not distinctly defined. In `src/finance_module.py`, signals are combined uniformly without separation into ρ, E, F roles. | `src/finance_module.py` lines 42–60 | **Missing** |
| **Excitation E (destabilizing rate)** | MODULE_TUTORIAL.md §4.1 | Not distinctly implemented in active pipeline. Tutorial assigns generic VIX-type signals without distinguishing rate-based from structural signals. | `src/finance_module.py` | **Missing** |
| **Damping F (stabilizing force)** | MODULE_TUTORIAL.md §4.2 | Not distinctly implemented. `γ×std(signals)` is used as resilience proxy — this measures signal dispersion, not a physical stabilizing force. | `src/dcii_core.py` lines 31–37 | **Unrelated conventional method** |
| **Calibration of α, β, γ (Ax=b from anchors)** | MODULE_TUTORIAL.md §6 | Tutorial `FinanceDCIIModule` uses simulated data (np.random.seed(42)). Anchors are hard-coded as uniform 0.2/0.5/0.8 across all signals — not derived from any real market condition. | `src/finance_module.py` lines 91–110 | **Simplified approximation with simulated data** |
| **Dynamic T_sys evolution** dT/dt = Eβ - γT | `calibration_engine/SXC_V12_CORE.py` | `SXCOmegaEngineStable` correctly imports and uses canonical `SXCOmegaEngine` from parent. Gamma decay disabled for long runs (documented). Input signal scaled to median=8 to place quiet periods below FIREWALL threshold (~10.3). | `v12_validate/engine_runner.py` lines 73–99 | **Faithfully implemented** (with documented γ modification) |
| **Transport PDE** τ∂²s/∂t² + ∂s/∂t = c²τ∂²s/∂t² | `v12_validate/transport_layer.py` docstring | IMEX semi-implicit discretization implemented. The PDE is solved over a 1D temporal sequence (not spatial field). The resulting s_transport is computed but its primary use is to compute grad_ln_s. | `v12_validate/transport_layer.py` lines 93–133 | **Faithfully implemented** (in 1D temporal only) |
| **Transport discriminant Q** = 4(cτ)²\|∇ln(s)\|² − 1 | `v12_validate/transport_layer.py` | Correctly implemented as Q = 4×(c×τ)²×(ln(s_t/s_{t-1}))² − 1 using backward difference. Causally sound. Reduces algebraically to: COHERENT iff \|log-return of composite\| > 1/(2cτ) = 0.1 at default params. | `v12_validate/transport_layer.py` lines 135–141 | **Faithfully implemented** — but see §3 |
| **Coherence length** ξ_c = 2cτ | `v12_validate/transport_layer.py` | ξ_c = 2×1.0×5.0 = 10 bars = 50 minutes. Documented in TransportCalibration class. Not used as a decision variable anywhere in the trading pipeline. | `v12_validate/transport_layer.py` lines 260–288 | **Faithfully implemented** (unused in decisions) |
| **Regime classification** Q>0 ↔ COHERENT | `v12_validate/transport_layer.py` | Implemented. Extended to 5-level classification using global Q quantiles (q05, q95) in `p1_data_stream.py`. Thresholds frozen from IS period. | `v12_validate/transport_layer.py` line 143; `p1_data_stream.py` `classify_q_global()` | **Faithfully implemented** |
| **Domain-specific signal normalization** | MODULE_TUTORIAL.md §3 | In active pipeline: 6 microstructure signals (volatility, volume_ratio, spread_ratio, tick_frequency, momentum_20min, momentum_1hr) are z-score normalized with 99th-percentile clipping, then sigmoid → (0,1). | `v12_validate/signals.py` `normalize_signals()` lines 71–90 | **Faithfully implemented** |
| **s(x,t) substrate field** | Inferred from transport_layer.py docstring | `composite` signal = row-mean of 6 normalized signals. Described as the "normalized composite market stress field." This is a plausible operationalization of s for a financial domain. | `v12_validate/signals.py` `build_composite()` lines 92–109 | **Partially implemented** (defensible mapping but not derived from theory) |
| **Spatial gradient \|∇ρ\|** | MODULE_TUTORIAL.md §4.3 | Reduced to 1D temporal log-derivative: grad_ln_s = ln(s_t/s_{t-1})/dt. A time-series operation, not spatial. Justification given in docstring. | `v12_validate/transport_layer.py` lines 135–141 | **Modified with documented justification** |

---

## 3. Critical Mathematical Finding: Q is a Monotone Function of its Input

**Finding (verified analytically):**

With c=1.0, τ=5.0, dt=1.0:
```
Q = 4(cτ)²|∇ln(s)|² − 1
  = 4 × 25 × (ln(s_t/s_{t-1}))² − 1
  = 100 × (log-return of composite)² − 1
```

The regime boundary Q=0 corresponds exactly to:
```
|log-return of composite| = 1/(2cτ) = 0.1
```

Therefore, the binary COHERENT/INCOHERENT classification is **mathematically identical** to asking whether the composite stress field moved by more than 10% in log-terms in the last 5-minute bar. This is a volatility threshold on the composite field — **not a new quantity**.

This means:
- Q > 0 adds exactly zero information beyond |grad_ln_s| > 0.5 (i.e., |composite log-return| > 0.1).
- The 5-level classification adds quantile structure around this threshold.
- The parent framework's claim that Q distinguishes "oscillatory wave-like" from "overdamped diffusive" behavior is present in the mathematical form, but the financial interpretation collapses to: did the composite stress change by more than 10% in one bar?

This is confirmed by FINAL_AUDIT_VERDICT.md §1.3: "Q > 0 and |grad_ln_s| > p75 produce identical transition detection results to four decimal places."

---

## 4. Two Implementations, Not One

The finance module contains two entirely separate implementations:

### Implementation A: `src/` (Tutorial/Demo Layer)
- Files: `src/dcii_core.py`, `src/finance_module.py`, `src/forex_pipeline.py`
- Data: **Simulated** (np.random.seed(42))
- Uses: The static DCII equation T = α|∇ρ| + βE - γF in modified form
- Status: Tutorial/demo code that is **never run on real market data**
- Equation fidelity: **Poor** — replaces E and F with statistical moments (mean, std) of aggregated signal values

### Implementation B: `v12_validate/` + `p1_*` / `p2_*` pipeline (Active Research Layer)
- Files: `transport_layer.py`, `engine_runner.py`, `signals.py`, `p1_data_stream.py`, `p2_transport_os.py`
- Data: Real Dukascopy EUR/USD tick data (2023–2025)
- Uses: The dynamic T_sys evolution equation AND the transport PDE Q discriminant
- Status: The **active experimental pipeline** — this is what actually ran experiments
- Equation fidelity: **Moderate** — T_sys is implemented faithfully; Q is implemented faithfully but reduces to a volatility threshold

These two implementations do not cross-reference each other. The `src/` layer is dead code for research purposes.

---

## 5. Missing Framework Elements

The following DCIF/Substrate concepts are documented in the parent framework but absent from the finance module:

| Missing Element | Location in Parent Framework | Impact |
|---|---|---|
| Calibration from real domain anchors (stable/crisis scenarios from real market events) | MODULE_TUTORIAL.md §4-6 | Coefficients α, β, γ have no domain validity |
| Distinct ρ (structural pressure) signal | MODULE_TUTORIAL.md §4.3 | No representation of market concentration/density |
| Distinct E (excitation) signal | MODULE_TUTORIAL.md §4.1 | Excitation is not rate-based or event-sensitive |
| Distinct F (damping) signal | MODULE_TUTORIAL.md §4.2 | No true stabilizing force variable |
| Multi-dimensional spatial field for ∇ρ | transport PDE | Only 1D temporal; no spatial topology |
| Calibration validation against OOS domain events | MODULE_TUTORIAL.md §7 | Never performed with real labeled market events |

---

## 6. Summary Verdict on Framework Implementation

The **active pipeline** (v12_validate + p1/p2) implements two genuine components of the parent framework:
1. The dynamic T_sys evolution (SXCOmegaEngine) — faithfully
2. The transport PDE and Q discriminant — faithfully in 1D

Neither produces a trading advantage over simple baselines. T_sys is outperformed by 5-bar realized volatility (ρ=0.48–0.62 vs ρ=0.20–0.27). Q reduces to a volatility threshold on the composite signal.

The **tutorial layer** (`src/`) does not implement the DCIF equation correctly. It uses a β×mean - γ×std formula that shares names but not mathematics with T = α|∇ρ| + βE - γF, and it uses simulated data throughout.

The full DCII framework (with proper ρ, E, F signal decomposition, domain-calibrated from real market events) has **never been implemented** in this module.
