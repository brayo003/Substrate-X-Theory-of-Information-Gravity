# Document 20 — Joint C2 Test Results (Simulation)
## Phase 9: c_C2 = d_c / τ_B

**Date:** 2026-08-21  
**Script:** `scripts/p20_joint_c2_test.py`

---

## 1. Inputs

| Quantity | Value | Source |
|----------|-------|--------|
| d_c measured | 11.3 ± 218.1 µm | p19 spatial fit |
| d_c injected | 50,000 µm | design |
| τ_B mean (fitted) | 5.34 µs | p18 temporal fit |
| τ_B injected | 5.00 µs | design |
| ΔAIC(null−exp) | −9.88 | p19 |

---

## 2. c_C2 = d_c / τ_B Per Qubit

| Qubit | τ_B (µs) | c_C2 (m/s) | Uncertainty (m/s) |
|-------|----------|------------|-------------------|
| Q00   | 5.12     | 2.2        | ±42.6             |
| Q01   | 4.59     | 2.5        | ±47.5             |
| Q02   | 4.89     | 2.3        | ±44.6             |
| Q03   | 6.38     | 1.8        | ±34.2             |
| Q04   | 5.63     | 2.0        | ±38.8             |
| Q05   | 5.14     | 2.2        | ±42.4             |
| Q06   | 5.65     | 2.0        | ±38.6             |

- **c_C2 injected:** 1.0 × 10⁴ m/s
- **c_C2 measured mean:** 2.1 m/s
- **Ratio (measured/injected):** 0.00021 — off by factor ~4,700
- **Fractional uncertainty:** 1923% (d_c dominates completely)
- **CV across qubits:** 0.10 (internally consistent — but irrelevant given scale of error)

---

## 3. Why the Joint Test Failed

The failure is direct consequence of d_c being unresolvable (Document 19). Since d_c is off by 4,400×, c_C2 = d_c/τ_B is off by the same factor. The τ_B extraction is accurate (bias < 7%), but it cannot rescue an unresolvable d_c.

**Subset stability test:** half1 = 2.34 m/s, half2 = 2.00 m/s, ratio = 1.17 — internally stable, but both wrong by the same factor. Consistency ≠ correctness here.

---

## 4. Verdict

**COMPATIBLE / UNDERDETERMINED**

The joint test was attempted but cannot yield a meaningful constraint because d_c is not resolvable on a 7-qubit chip with ξ_c >> chip size. The null model is preferred spatially. The c_C2 estimate has 1923% uncertainty and is off from the injection value by 4 orders of magnitude.

This is not falsification. It is a geometric impossibility: the decisive test requires chip_size ~ ξ_c.

---

## 5. Figure

- `outputs/figures/fig_c2_joint_test.png` — c_C2 per qubit, d_c vs τ_B plane
