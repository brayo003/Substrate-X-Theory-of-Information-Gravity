# Document 22 — Synthetic Recovery (Simulation)
## Phase 9: Blind Recovery Map

**Date:** 2026-08-21  
**Script:** `scripts/p22_synthetic_recovery.py`

---

## 1. Setup

- Grid: 5 c values × 6 NMP regimes × 30 trials = 900 total trials
- Metric: fraction recovered within 3× of true c_C2
- Single qubit pair (d = 200 µm); τ_B extracted from Ramsey

---

## 2. Recovery Heatmap (fraction within 3× of true c)

| τ_B/T2* → | 0.01 | 0.10 | 0.50 | 1.00 | 5.00 | 10.00 |
|-----------|------|------|------|------|------|-------|
| c=10² m/s | 0%   | 92%  | 100% | 100% | 77%  | 17%   |
| c=10³ m/s | 100% | 100% | 97%  | 20%  | 0%   | 0%    |
| c=10⁴ m/s | 100% | 7%   | 0%   | 0%   | 0%   | 0%    |
| c=10⁵ m/s | 7%   | 0%   | 0%   | 0%   | 0%   | 0%    |
| c=10⁶ m/s | 0%   | 0%   | 0%   | 0%   | 0%   | 0%    |

**Recovery by NMP regime (mean across all c values):**

| τ_B/T2* | Mean within-3x |
|---------|----------------|
| 0.01    | 41%            |
| 0.10    | 40%            |
| 0.50    | 39%            |
| 1.00    | 24%            |
| 5.00    | 15%            |
| 10.00   | 3%             |

---

## 3. Interpretation

**The recovery problem is dominated by the spatial measurement, not the temporal one.**

The 2-qubit geometry (d = 200 µm, single pair) provides very limited spatial leverage. c_C2 = d_c/τ_B requires that the spatial correlation varies measurably between pairs at different separations. With only one pair and d/ξ_c << 1 for most c values, the d_c estimate has large systematic bias.

**Best-case identifiable regime:** c ~ 10² m/s with τ_B/T2* ~ 0.5–1.0 — but this regime is not predicted by C2 theory and is not the test regime.

**The injected value c = 10⁴ m/s is in the worst recovery zone:** τ_B/T2* ~ 1.6 (actual NMP in main sim), with 0% recovery within 3×. This confirms the main experiment's failure to recover d_c.

---

## 4. What Would Make the Test Work

For 100% recovery of c = 10⁴ m/s, need either:
1. Multiple qubit pairs spanning d ~ ξ_c/2 to 2ξ_c → chip size >> 10 cm
2. Reduce c to ~10² m/s (not a C2 prediction)
3. Reduce τ_B to ~0.5 µs (faster bath → smaller ξ_c, but reduces τ_B identifiability)

None of these are achievable on current 7-qubit chips without changing the physics.

---

## 5. Figure

- `outputs/figures/fig_synthetic_recovery.png` — 2D recovery heatmap
