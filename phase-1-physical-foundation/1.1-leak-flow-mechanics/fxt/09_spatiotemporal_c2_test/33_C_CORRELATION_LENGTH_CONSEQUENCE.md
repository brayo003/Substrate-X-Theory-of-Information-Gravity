# 33 — C2 Correlation Length: Consequences of the Speed Audit

**Phase 9e — C2 Quantum Layer Theoretical Audit**
**Date:** 2026-08-21
**Script:** `scripts/p28_correlation_length_audit.py`
**Data:** `outputs/data/correlation_length_consequence.json`
**Depends on:** 32_C_PRW_SPEED_DERIVATION_AUDIT.md

---

## Purpose

Given the result of the speed audit (c is CONDITIONALLY PREDICTED as
v_s = 6000 m/s under [PHON]), determine the numerical predictions for
the correlation length ξ_c and assess whether the K₀ spatial
discriminator is experimentally accessible.

---

## 1. Correlation Length Formula

From the PRW telegrapher derivation (FPUT-3 + P1):

    ξ_c = 2 c τ_B

where:
- c = propagation speed (CONDITIONALLY DERIVED as v_s = 6000 m/s)
- τ_B = 1/(2γ) = bath correlation time (DERIVED from PRW relaxation)

Both factors are derived once c is fixed; ξ_c is a **non-free
numerical prediction** under [PHON].

---

## 2. ξ_c at Project τ_B Values (c = v_s = 6000 m/s)

These are τ_B values actually used in prior project phases:

| τ_B source | τ_B (µs) | ξ_c (cm) | Accessible on current hardware? |
|------------|----------|----------|--------------------------------|
| Tuna-17 median | 5.00 | 6.000 | NO — >> all chips |
| NM_PREDICTION_AUDIT fitted | 0.75 | 0.900 | Marginal on Heron/Ankaa |
| Simulation injection | 5.00 | 6.000 | NO |
| Phase 9 Ramsey fits | 5.34 | 6.408 | NO |

**Observation:** The τ_B values measured/fitted from real hardware
(Tuna-17 median ~5 µs, Phase 9 fits ~5.3 µs) give ξ_c >> all chip
sizes. The K₀ discriminator is blocked at the τ_B values the
substrate actually has on current hardware.

---

## 3. τ_B Required for ξ_c to Match Chip Size

For the K₀ vs exponential spatial discriminator to be active, the
chip span d must satisfy d/ξ_c ~ 1. Smaller d/ξ_c means the spatial
profile is nearly flat across the chip — K₀ and exponential are
indistinguishable.

| Platform | Max span d | τ_B needed | NMP at Γ_M = 50 kHz |
|----------|------------|------------|----------------------|
| IBM 7-qubit (sim) | 0.63 mm | 0.053 µs | 0.017 [Markov — τ_B unidentifiable] |
| Rigetti Ankaa-3 84q | ~8 mm | 0.667 µs | 0.209 [identifiable] |
| IBM Heron 133q | ~12 mm | 1.000 µs | 0.314 [identifiable] |
| IBM Eagle 127q | ~14 mm | 1.167 µs | 0.367 [identifiable] |

**NMP interpretation:**
- NMP < 0.01 → Markovian regime → τ_B shape not visible in Ramsey → τ_B cannot be independently confirmed
- NMP 0.1–5 → Non-Markovian → τ_B identifiable from Ramsey
- NMP > 10 → Quasistatic → shape saturates

For the 7-qubit simulation platform: NMP = 0.017, meaning τ_B cannot
be independently confirmed from Ramsey shape at the chip scale where
ξ_c ≈ chip span. This is a self-consistency failure: the experiment
would need τ_B ~ 0.05 µs to achieve ξ_c ≈ 0.63 mm, but at that τ_B
the system is Markovian and τ_B itself cannot be extracted.

---

## 4. K₀ vs Exponential Discriminator — Numerical Analysis

The C2 spatial correlator predicts:

    C_C2(r) ~ K₀(r/ξ_c)        [modified Bessel function of the second kind]

The conventional OU/Markov model predicts:

    C_OU(r) ~ exp(−r/ξ_c)      [exponential decay]

Both are normalised to 1 at r = a (nearest-neighbour spacing a = 200 µm).

### Fractional difference |K₀ − exp| / exp at r = 5a (1 mm separation):

| ξ_c | τ_B | Difference at r = 1mm |
|-----|-----|-----------------------|
| 6.0 cm (τ_B = 5 µs) | 5.0 µs | 26.7% |
| 1.4 cm (τ_B = 1.17 µs) | 1.17 µs | 33.1% |
| 0.8 cm (τ_B = 0.67 µs) | 0.67 µs | 35.9% |

Note the apparent paradox: the *largest* ξ_c (τ_B = 5 µs) shows a
26.7% difference at r = 1 mm because K₀ diverges logarithmically as
r/ξ_c → 0. However:

- At ξ_c = 6 cm, the chip span is d = 14 mm = 0.23 ξ_c.
  All pair separations satisfy r/ξ_c << 1, so K₀ ≈ −ln(r/2ξ_c)
  while exp ≈ 1 − r/ξ_c. The shapes look different at small r/ξ_c
  but the K₀ functional form is indistinguishable from a log at
  r << ξ_c — and a log cannot be identified as K₀ vs any other
  function without measurements at r ~ ξ_c.

- **The discriminator requires r ~ ξ_c** to distinguish K₀ from
  exponential with statistical reliability.

For ξ_c = 6 cm and chip span = 14 mm: r_max/ξ_c = 0.23. The
discriminator is geometrically inaccessible.

For ξ_c = 1.4 cm and chip span = 14 mm: r_max/ξ_c ≈ 1.0.
The discriminator is geometrically accessible in principle.

---

## 5. Experimental Branch Classification

### Condition assessment

The K₀ discriminator experiment requires:

1. **[PHON] accepted** — otherwise c is a free parameter and ξ_c is
   not predicted independently (circular experiment)

2. **τ_B ~ 1.2 µs** — this specific value has NOT been measured on
   real IBM hardware (measured values are 5–6 µs). It is required by
   the theory to match Eagle chip size; choosing it *for this reason*
   would be circular.

3. **Eagle-class chip access** — ~127 qubits, ~14 mm span. Not
   currently available to the project.

4. **τ_B independently confirmed** — at τ_B ~ 1.2 µs the NMP ~ 0.37,
   which is in the identifiable range. τ_B CAN in principle be
   extracted from Ramsey shape at this value, avoiding circularity.

### Verdict

```
CONDITIONALLY OPEN

The K₀ spatial discriminator is not blocked by any mathematical
impossibility, but requires three simultaneous conditions:

  (a) [PHON] identification accepted as a named postulate
  (b) τ_B ~ 1.2 µs confirmed on real hardware (not assumed)
  (c) Eagle-class chip access obtained

If any of these three conditions fails, the branch is BLOCKED.

Currently: conditions (b) and (c) are unmet.
The branch is therefore BLOCKED in practice.
It becomes CONDITIONALLY OPEN if (a) is postulated and
a measurement plan is established for (b)+(c).
```

### What NOT to do

Do NOT choose τ_B = 1.17 µs merely because it makes the experiment
feasible. The τ_B value must be confirmed from independent Ramsey
data. If real hardware gives τ_B ~ 5 µs (as Tuna-17 did), then
ξ_c ~ 6 cm and the experiment is blocked.

---

## 6. Summary Table

| Quantity | Status | Value (under [PHON]) |
|----------|--------|----------------------|
| v_s | DERIVED | 6000 m/s |
| c upper bound | DERIVED (C3) | ≤ 6000 m/s |
| c | CONDITIONALLY DERIVED | 6000 m/s |
| ξ_c at τ_B = 5 µs | PREDICTION (CONDITIONAL) | 6.0 cm — blocked |
| ξ_c at τ_B = 1.17 µs | PREDICTION (CONDITIONAL) | 1.4 cm — conditionally accessible |
| K₀ discriminator | CONDITIONALLY OPEN | requires Eagle + τ_B confirmation |
| QPU justified? | **NO** | conditions (b) and (c) unmet |

---

*Script:* `scripts/p28_correlation_length_audit.py`
*Output:* `outputs/data/correlation_length_consequence.json`
