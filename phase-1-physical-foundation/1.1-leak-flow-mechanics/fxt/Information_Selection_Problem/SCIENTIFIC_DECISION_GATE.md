# SCIENTIFIC_DECISION_GATE

**Date:** 2026-08-24  
**Author:** Independent adversarial audit  
**Scope:** Entire Information_Selection_Problem repository + 11_CUBIC_WEYL_AS_AUDIT

---

## 1. WHAT SXC-IGC IS ACTUALLY CLAIMING

This requires distinguishing what the project **claims** from what it **has derived**.

**The claim** (reconstructed from CHARTER.md, 09_FINAL_FORMULATION.md, 10_DECISION.md, and 08_SXC_IGC_CAPABILITY_AUDIT.md):

The SXC-IGC/Information_Selection_Problem program is pursuing a specific mathematical object: a selection function F: Γ_GR → {0,1} that restricts the physical gravitational initial-data sector to low-Weyl configurations, derived from premises that do not encode low Weyl as input. The mechanism under investigation is whether the Asymptotic Safety UV fixed point, via the cubic Weyl coupling w₃*, can provide this selection function by removing the Kasner saddle from the effective action.

**What the substrate concept was supposed to do:**

The "leak-flow mechanics / Substrate X / information gravity" language in the broader `fxt/` tree was the C2 project framework. The current Information_Selection_Problem program explicitly **does not inherit** this ontology (CHARTER.md §1). The workspace starts from scratch with a blank ontology and is investigating whether any mechanism — including AS — can derive the selection function F. SXC-IGC as a framework is tested for capability in 08_SXC_IGC_CAPABILITY_AUDIT.md and **fails all six tests** as of August 2026.

**The causal chain being constructed:**

```
AS UV fixed point (independent physical theory)
       ↓
w₃* ≠ 0 at the fixed point
       ↓
δ(√g W₃)/δg^μν|_{Kasner} ≠ 0  (variation doesn't vanish on Kasner)
       ↓
Kasner is NOT a saddle of the full AS effective action
       ↓
Kasner is excluded from Γ_phys
       ↓
All of Γ_phys has C² ≈ 0 (only FLRW-type initial data survives)
       ↓
Observed near-zero Weyl curvature of early universe is predicted
       ↓
[UNRESOLVED: distinguishable observational prediction]
```

**What later phases depend on Phase 1:**

Phase 1 (Gate 1 in the W3 chain) = establishing that δ(√g W₃)/δg ≠ 0 on Kasner. This gates everything downstream. The FRGE computation (Phase 2) is irrelevant if Gate 1 fails.

---

## 2. WHAT HAS BEEN ESTABLISHED

The following are established with the specified evidence quality:

| Claim | Status | Evidence |
|---|---|---|
| R1 is a genuine residual (cosmological initial-state problem not closed by known physics) | VERIFIED | Full audit of 28 candidate mechanisms in GATE6_P01_FINAL_VERDICT.md |
| Kasner satisfies Bach tensor = 0 exactly | VERIFIED — PROVEN | Exact result from contracted Bianchi identity in vacuum; no calculation required beyond algebra |
| C² mechanism (β* weighting) fails to exclude Kasner | VERIFIED — PROVEN | Bach = 0 is an exact structural result; C² Kasner saddle is exact for any β |
| β* ≈ 0.01–0.1 (AS truncation results) | VERIFIED — LITERATURE | Falls-Litim 2014; Ohta-Percacci 2016; Knorr-Platania 2022; flat trend across truncations |
| β* required for exponential Kasner suppression ≈ 23 | VERIFIED — COMPUTED | From ∫C²√g ~ O(1) per Planck volume on Kasner; gap factor 230–2300 |
| W₃ = C_{abcd}C^{ab}_{ef}C^{cdef} = 32/9 on S²×S² (equal radii) | VERIFIED — COMPUTED | Direct rational arithmetic, three independent index contractions; project docs citing 128/27 are wrong |
| C²_bar = 16/3 on S²×S² | VERIFIED — COMPUTED | Direct computation |
| All Weyl tensor algebraic identities on S²×S² | VERIFIED — COMPUTED | 0 violations in exhaustive 4D enumeration |
| Background W₃ Hessian p⁴ principal symbol computed | VERIFIED — COMPUTED | Two independent computational routes agree; K_W3 ∈ {−2, +2, −2, +1, +1} for 5 TT modes |
| 3·C̄·C̄·δ²C contributes zero to p⁴ | VERIFIED — COMPUTED | Phase B derivative-order table; p² and p⁰ only |
| Algebraic part A_{μν} of δ(√g W₃)/δg is nonzero on Kasner | VERIFIED — COMPUTED | Closed-form result via E_i = (p_i − 1/3)/t; A_{μν} = −4δ_{μν}TrE³ + 3(E³)_{μν} ≠ 0 for anisotropic Kasner |
| N_eff = 4 (TT modes on S²×S²) | DERIVED | Mode decomposition (2 in-sector + 2 cross-sector) |
| A_W3 ≠ 0 and A_W3 > 0 (W3 source coefficient in FRGE) | DERIVED — NUMERICALLY EVALUATED FROM ASSUMED INPUTS | Formula derived from Hessian structure; A_W3(Litim) = 12.22 evaluated at fixed-point values |
| AS provides action, not quantum state | VERIFIED — CATEGORICAL | Category distinction; AS = theory of dynamics, not boundary conditions |

---

## 3. WHAT HAS NOT BEEN ESTABLISHED

| Claim | Status | Gap |
|---|---|---|
| δ(√g W₃)/δg = E_{μν} ≠ 0 on Kasner (FULL variation, not just algebraic part) | NOT ESTABLISHED | Derivative terms B_{μν} and D_{μν} not computed; cancellation between algebraic and derivative parts not ruled out |
| w₃* ≠ 0 at the AS UV fixed point | NOT COMPUTED | No published result; no independent computation in this project |
| No operator-mixing cancellation at fixed point (adversarial route K4) | NOT ESTABLISHED | Higher-order Weyl couplings w₄*, w₅*, ... could in principle cancel the w₃* contribution on Kasner |
| η_{W₃} (anomalous dimension) | NOT COMPUTED | Sector-split {−2, +2, −2, +1, +1} means no unique K_W3; FRGE normalization factor N unresolved |
| Coupled fixed-point solution (g*, λ*, c₂*, w₃*) | NOT COMPUTED | Blocked by η_{W₃} |
| Self-consistency of truncation | NOT COMPUTED | Blocked by coupled fixed point |
| Any distinguishable observational prediction | NOT ESTABLISHED | Inflation erasure problem: all Planck-scale initial-state mechanisms produce observationally indistinguishable predictions at CMB scales |
| α₂ = 8 by independent first-principles derivation | NOT INDEPENDENTLY REPRODUCED | Cross-checks performed; no first-principles derivation from this project |
| Full W₃ variation (algebraic + derivative) on Kasner | NOT COMPUTED | 12_W3_VARIATION_EXPLICIT.md identifies the gap; derivative terms require CAS computation |
| Any capability of SXC-IGC's original substrate formulation | NOT PROVIDED | 08_SXC_IGC_CAPABILITY_AUDIT.md: 0/6 capabilities derived |

---

## 4. CURRENT THEORY DEPENDENCY GRAPH

```
WHAT MUST ALL BE TRUE FOR THE MECHANISM TO WORK:

PREREQUISITE GATE 0:  AS has a UV fixed point             [ESTABLISHED in literature]
        ↓
GATE 1A: δ(√g W₃)/δg^μν (algebraic part) ≠ 0 on Kasner  [ESTABLISHED — closed form]
        ↓
GATE 1B: δ(√g W₃)/δg^μν (derivative parts) do NOT cancel algebraic part
                                                            [NOT COMPUTED — gate not passed]
        ↓  
GATE 1:  Full δ(√g W₃)/δg^μν ≠ 0 on Kasner               [OPEN — depends on Gate 1B]
        ↓
GATE 2:  w₃* ≠ 0 at the AS fixed point                    [NOT COMPUTED]
        ↓
GATE 3:  No operator-mixing cancellation at fixed point    [NOT ESTABLISHED]
        ↓
GATE 4:  At least one distinguishable observational prediction
                                                            [STRUCTURALLY FAILS —
                                                             inflation erasure problem]
```

**The dependency structure has four open/failing gates.**  
**Gate 1B is the cheapest to resolve. Gate 4 is the most threatening to the entire program.**

**Gate 4 does not depend on Gates 1–3.** It is a structural problem independent of all calculations. Even if Gates 1–3 were resolved in favor of the mechanism, Gate 4 remains a failure: the mechanism's predictions are observationally indistinguishable from inflation at any currently feasible measurement.

---

## 5. W3: SCIENTIFIC RELEVANCE

**What physical claim depends on η_{W₃}?**

η_{W₃} enters the beta function β_{w₃} = (2 + η_{W₃})w₃ + A_W3, and is needed to determine the self-consistent fixed-point value w₃*. Without η_{W₃}, we have only the symbolic estimate w₃* ≈ −A_W3/(2 + η_{W₃}).

**What downstream quantity depends on it?**

The fixed-point value w₃* determines whether Kasner is excluded from the AS saddle-point equations. If w₃* ≠ 0, the full variation E_{μν} ≠ 0 on Kasner (assuming Gate 1B passes).

**Does obtaining η_{W₃} produce a new physical prediction?**

No direct observational prediction. The chain terminates at Gate 4 (inflation erasure) regardless of whether η_{W₃} is computed. Knowing w₃* allows the conclusion "Kasner is not a vacuum of the AS effective action" — but this structural result produces no currently measurable observational consequence.

**Is η_{W₃} independently constrained by existing physics?**

The η_{W₃} for W₃ in the AS truncation has not been computed in any published paper (confirmed by 02_W3_LITERATURE_AUDIT.md). The C² anomalous dimension η_{C²} is known from AS literature, but the cubic Weyl sector is virgin territory. No external constraint.

**Could the theory be tested without η_{W₃}?**

Yes — one test precedes it in the logical order:

**Gate 1B: Does the full variation δ(√g W₃)/δg cancel on Kasner?**

The algebraic part is nonzero. The derivative parts are nonzero (∂_t C ≠ 0 on Kasner). But no known identity forces cancellation, AND no known identity rules it out. The explicit calculation of B_{μν} and D_{μν} on the Kasner metric using CAS (Cadabra2 with Kasner loaded) is the cheapest remaining gate. This does not require FRGE, does not require S²×S², does not require η_{W₃}.

**If η_{W₃} were calculated tomorrow, what would that answer?**

It would allow computing w₃* numerically. If w₃* ≠ 0, combined with Gate 1B passing, the conclusion is: Kasner is excluded from the AS solution set. This is a structural theoretical result — potentially significant — but produces no prediction distinguishable from ΛCDM + inflation by any measurement accessible with current or near-future technology.

**The sector split {−2, +2, −2, +1, +1}:**

This reflects the S²×S² background's product geometry. It is not an averaging problem or a computational error. The three distinct eigenvalue sectors are a genuine feature of the background. For the FRGE trace, the correct treatment requires the full Lichnerowicz spectrum on S²×S² with sector-by-sector integration, not selection of one eigenvalue. This is a missing computation, not a broken concept. However, since Gate 4 structurally fails regardless, completing this computation does not change the scientific verdict.

---

## 6. STRONGEST POSSIBLE KILL TEST

**Kill Test K1: Gate 1B — Cancellation check on Kasner**

Compute the full variation δ(√g W₃)/δg^{μν} on the Kasner metric explicitly, including the derivative terms B_{μν} = −6∇^α∇^β(C_{μανβ}·Q_{αβ}) and D_{μν} (4th-derivative terms). Check whether B_{μν} + D_{μν} = −A_{μν} (exact cancellation).

If cancellation is confirmed: **W₃ route is eliminated**. Kasner satisfies the W₃ saddle equation identically for the same reason Bach = 0 on Ricci-flat. The entire W₃/AS mechanism collapses at zero cost to the FRGE computation.

The C² case provides a template: Bach_{μν} = ∇^α∇^β C_{αμβν} + (1/2)R^{αβ}C_{αμβν} = 0 on vacuum (Ricci-flat) because both terms vanish. For W₃, the analogous identity would require the cubic terms to produce the same structure — structurally less likely given the complexity, but not ruled out.

**Kill Test K2: Gate 4 — Inflation erasure is unfixable**

The prediction problem is not solvable by completing the W₃ calculation. Any Planck-scale initial-state selection mechanism faces:

- Inflation produces ~ 60 e-folds of expansion that erases pre-inflationary correlations.
- The only route to distinguishability is either: (a) absence of inflation (conflicts with flatness/horizon), or (b) a non-Gaussianity or tensor feature that inflation cannot produce.
- W₃ corrections to the tensor power spectrum are suppressed by (H/M_Planck)^4 ~ 10^{-20} relative to observable scales.

**This kill test is not a new calculation — it is already documented in 09_PREDICTION_IMPLICATION.md and confirmed.** The W₃ mechanism, if established, produces no testable prediction distinguishable from ΛCDM + inflation. This alone is sufficient to classify the route as scientifically non-advancing.

**Kill Test K3: SXC-IGC original substrate**

The original SXC-IGC substrate framework ("leak-flow mechanics / information gravity") has failed all six capability tests required to address R1 (08_SXC_IGC_CAPABILITY_AUDIT.md). No derivation from substrate axioms has produced: (1) a measure on Γ_GR, (2) a constraint on initial data, (3) a dynamical attractor, (4) a quantum-state selection mechanism, (5) an action modification, or (6) a superselection rule. This is not an incomplete derivation — it is the absence of any derivation.

---

## 7. STRONGEST POSSIBLE RESCUE PATH

**If the program is to survive scientifically**, the following is the minimal credible path:

**Step 1 (Gate 1B):** Compute the full variation δ(√g W₃)/δg^{μν} on Kasner including ALL derivative terms. Use Cadabra2 with the Kasner metric explicitly loaded and all Christoffel symbols computed. This is a well-defined CAS computation. Estimated effort: a few hours with proper setup.

If this fails (variation cancels): **program terminates this branch immediately**.

**Step 2 (only if Gate 1B passes):** Compute w₃* via FRGE with the full Lichnerowicz spectrum on S²×S² and a specific regulator. This is a significant computation. The sector split {−2, +2, −2, +1, +1} must be handled sector-by-sector, not averaged.

If w₃* = 0 or has the wrong sign: **W₃ route terminated**.

**Step 3 (only if Gates 1B and 2 pass):** Rule out operator-mixing cancellation. This requires computing w₄*, w₅* and verifying they don't cancel the w₃* contribution on Kasner. No known mechanism suggests they would, but no computation rules it out.

**Step 4 (only if all above pass):** Address Gate 4. This requires identifying a prediction that survives inflation. The only viable route identified in 09_PREDICTION_IMPLICATION.md is Prediction P3 (graviton scattering amplitudes in the AS framework) — which requires an independent calculation connecting w₃* to graviton-graviton scattering at sub-Planckian energies via UV/IR mixing.

**The rescue path has four sequential gates.** Failure at any gate terminates the branch. The expected value of this path depends critically on Gate 1B, which is the cheapest and most decisive test.

---

## 8. SHORTEST PATH TO A PHYSICAL PREDICTION

After exhaustive search of the repository, the **current program has no existing route to a physical prediction that satisfies Gate 7** (distinguishable from ΛCDM, measurable). The closest anything comes:

**Candidate 1: AS spectrum of n_s and r** — These predictions exist from the EH + C² truncation and are marginally consistent with observation. They are not unique predictions of the W₃ mechanism. Adding W₃ with w₃* ≠ 0 modifies them at sixth order in derivatives, making corrections ~ 10^{-20} relative to observational precision.

**Candidate 2: Large-scale CMB anomalies** — The low-ℓ "lack of power" in the CMB is observed and unexplained. A Kasner-exclusion mechanism would suppress Bianchi-type initial conditions. But this prediction is also made by inflation. Not distinguishable.

**Candidate 3: UV graviton scattering** — The AS fixed point makes predictions about high-energy graviton scattering that are in principle testable with Planck-scale colliders. Not technologically accessible.

**Candidate 4: Cosmological constant prediction** — Some AS truncations predict a specific relationship between G and Λ at the fixed point. This is testable in principle. But it does not depend on W₃ at all — it comes from the EH sector alone.

**Minimum calculation for any prediction:** The AS framework without W₃ already makes marginal CMB predictions (n_s ≈ 0.96). Adding W₃ does not qualitatively change this. The minimum calculation for a distinct prediction does not involve W₃.

**The honest answer:** There is no calculation currently identified in this repository that would, if completed, produce a **new** falsifiable prediction distinguishable from existing theories. The program has mapped the problem thoroughly, identified the structural difficulty (Gate 4 / inflation erasure), and found that neither W₃ nor any of the 28 previously investigated primitives closes the gap.

---

## 9. DECISION

**REFORMULATE — CURRENT FORMULATION DOES NOT CLOSE**

The specific scientific reasons for this verdict, in order of severity:

**Reason 1 — Gate 4 structurally fails regardless of W₃ calculation outcome:**  
The mechanism operates at Planck scales. Inflation erases Planck-scale initial-state signatures at the level of 10^{-20} in amplitude. No variation of the W₃ calculation changes this. A theoretical result that says "Kasner is excluded from the AS effective action" is not zero value, but it does not constitute a physical prediction distinguishable from ΛCDM + inflation. The selection function F(h,K) may eventually be identified, but F cannot currently be tested. This is the inflation erasure problem documented in 09_PREDICTION_IMPLICATION.md.

**Reason 2 — Gate 1B is structurally uncertain:**  
The algebraic part of δ(√g W₃)/δg is nonzero on Kasner. The derivative parts are also individually nonzero. But exact cancellation between these parts has not been ruled out. The C² analogy (Bach = 0 on Ricci-flat) is a warning: the apparently "obviously nonzero" variation of C² also vanishes on Kasner by an exact identity. The W₃ case is more complex, making cancellation less likely — but "less likely" is not "ruled out." Gate 1B is a real gate, not a formality.

**Reason 3 — SXC-IGC substrate provides nothing:**  
The original SXC-IGC framework has zero derived outputs relevant to R1 after full audit (08_SXC_IGC_CAPABILITY_AUDIT.md). It is investigating R1 from the outside as an external problem to solve, not providing any structural derivation from its own premises.

**Reason 4 — The program has correctly mapped the landscape but not advanced it:**  
The prior work is high-quality adversarial auditing. The 28 candidate mechanisms were properly killed. The W₃ computation chain is technically correct. The identification of Gate 1B as the cheapest decisive test is correct. But the program has been spending cycles on the FRGE computation (η_{W₃}) — which is downstream of Gate 1B, depends on a sector-split problem, and produces no distinguishable prediction even if resolved.

**What "REFORMULATE" means specifically:**

The current formulation is: "Identify the selection function F via AS + W₃."

The reformulation should be: "First compute Gate 1B (full Kasner variation of W₃) — if it passes, the AS mechanism becomes a structural theoretical result, classified as partial progress on R1, but acknowledged as producing no current observable prediction. Then pursue Gate 4 independently: search for an observationally accessible consequence of any initial-state selection mechanism."

The reformulated program is not continuing W₃ for its own sake. It is:
1. Execute Gate 1B (cheap, decisive, can terminate the branch immediately).
2. If Gate 1B passes, classify the theoretical structural result and deprioritize further FRGE computation until Gate 4 has a credible route.
3. In parallel, investigate whether any initial-state mechanism produces an observable prediction that survives inflation. The critical question is whether there exists a pre-inflationary observable at all.

---

## 10. NEXT EXPERIMENT

**The single most information-gaining next calculation:**

**Compute the full variation δ(√g W₃)/δg^{μν} on Kasner, including all derivative terms B_{μν} and D_{μν}, and determine whether the total variation vanishes identically.**

Inputs required:
- Kasner metric: g_{μν} = diag(−1, t^{2p₁}, t^{2p₂}, t^{2p₃}) with p₁+p₂+p₃=1, Σp_i²=1
- All Christoffel symbols (closed form, known)
- All Riemann/Weyl components (closed form, known — W₃ on Kasner = 8Σ(p_i−1/3)³/t⁶)
- The derivative variation formula: B_{μν} = −6∇^α∇^β(C_{μανβ}·Σ_{αβ}) where Σ = quadratic in C

Method: Cadabra2 CAS with Kasner metric loaded. All derivatives are purely time-derivatives (∂_i = 0 by spatial homogeneity). This reduces to an ODE problem, tractable with tensor CAS.

Expected output: Either (a) E_{μν}|_{Kasner} = 0 (mechanism eliminated), or (b) E_{μν}|_{Kasner} ≠ 0 with explicit closed-form expression.

**What result supports the theory:** E_{μν}|_{Kasner} ≠ 0 — nonzero, with specific functional form in the Kasner parameters (p₁, p₂, p₃) and time t.

**What result kills the theory:** E_{μν}|_{Kasner} = 0 identically — the W₃ variation vanishes on Kasner by an exact identity analogous to Bach = 0.

**Why this is worth doing:** It is the cheapest decisive gate in the entire dependency graph. It costs a few hours of CAS work. If the answer is "zero," the W₃ route closes immediately and no further FRGE work is needed. If the answer is "nonzero," it upgrades the W₃ route from "heuristic structural argument" to "rigorously established prerequisite for Gate 2."

**What this does NOT do:** It does not resolve Gate 4 (inflation erasure). Even if Gate 1B passes, the current formulation does not advance to a testable prediction. Gate 4 must be addressed separately, and the project should acknowledge honestly that it currently has no route to Gate 4.

---

## FINAL CLASSIFICATION TABLE

| Item | Classification |
|------|---------------|
| W₃ = 32/9 on S²×S² (background value) | VERIFIED |
| W₃ p⁴ principal Hessian eigenvalues {−2, +2, −2, +1, +1} | VERIFIED |
| Algebraic part of δW₃/δg ≠ 0 on Kasner | VERIFIED |
| Full δW₃/δg ≠ 0 on Kasner | UNRESOLVED — Gate 1B |
| w₃* ≠ 0 at AS fixed point | UNRESOLVED — Gate 2 |
| No operator-mixing cancellation | UNRESOLVED — Gate 3 |
| η_{W₃} computed | NOT COMPUTED |
| Gate 4 (distinguishable prediction) | FAILS — structural inflation erasure |
| SXC-IGC substrate capabilities | NOT DERIVED |
| Overall program status | REFORMULATE |

---

*Document: SCIENTIFIC_DECISION_GATE.md*  
*Decision: REFORMULATE — CURRENT FORMULATION DOES NOT CLOSE*  
*Reason: Gate 4 structurally fails (inflation erasure) regardless of W₃ completion;*  
*Gate 1B (full Kasner variation) is unverified; η_{W₃} is blocked and downstream of Gates 1B+2.*  
*Next experiment: Full δ(√g W₃)/δg on Kasner, including derivative terms (Cadabra2 CAS).*  
*Date: 2026-08-24*
