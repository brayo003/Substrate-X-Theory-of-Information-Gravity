# 08_SXC_IGC_CAPABILITY_AUDIT
## What SXC-IGC Would Have to Provide

**Date:** August 2026

**Warning:** This audit applies the same adversarial standard to SXC-IGC that was applied to the 28 killed candidates. No special treatment.

---

## The Central Question

The 28 examined mechanism classes failed to derive Γ_phys ⊊ Γ_GR (the low-Weyl initial-data sector). What mathematical capability would SXC-IGC have to provide that these 28 classes do not?

---

## What SXC-IGC Claims (Based on Available Workspace Documents)

From 06_DERIVATION/, 02_EXISTING_PHYSICS/, and related files, the SXC-IGC framework involves:
- "Leak-flow mechanics" — information leakage between physical systems
- "Substrate X" — a substrate-level description of physical interaction
- "Information gravity" — gravity as an emergent consequence of information structure
- Channel capacity and information-theoretic bounds on physical processes

These are the descriptive elements. The audit must determine which specific mathematical operation each provides for R1.

---

## Test 1: Does leak-flow mechanics define a new measure on Γ_GR?

A new measure on Γ_GR would address the gap identified in 02_MEASURE_AUDIT.md. For this to work:
- The measure must be covariant and gauge-invariant
- It must be derivable from the leak-flow framework without circular input
- It must assign different weights to FLRW-like and Kasner-like initial data

**What would be required:** An explicit functional μ_LF[h_ij, K_ij] → R_≥0 derived from the leak-flow framework, with:
- μ_LF(FLRW) >> μ_LF(Kasner) in appropriate units
- μ_LF(h,K) ≠ 0 for Kasner (otherwise it's a hard exclusion, see Test 2)
- The derivation of μ_LF from first principles of leak-flow mechanics, not from Weyl curvature directly

**Status in SXC-IGC:** Based on available workspace documents, no such functional μ_LF has been derived. The information-theoretic quantities (channel capacity, entropy flux) have been invoked descriptively but no explicit measure on Γ_GR has been constructed. P03 (causal-diamond channel capacity) was generated from this framework and was killed for encoding the conclusion (failure class I: the minimum capacity C_min encoded "compatible with classical structure formation").

**Verdict: NOT PROVIDED.**

---

## Test 2: Does leak-flow mechanics define a new constraint on initial data?

A new constraint C[h,K] = 0 beyond the GR constraints would directly produce Γ_phys ⊊ Γ_GR. For this to work:
- The constraint must be independently derived from leak-flow principles
- It must be background-independent and covariant
- It must not encode low Weyl in its definition (firewall)
- It must exclude Kasner

**What would be required:** An explicit functional equation C_LF[h_ij, K_ij] = 0 with:
- A derivation of C_LF from leak-flow mechanics that does not use Weyl curvature as input
- Evaluation of C_LF on the Kasner metric: C_LF[Kasner] ≠ 0 (Kasner must fail the constraint)

**The Kasner challenge for any leak-flow constraint:** From 05_ADVERSARIAL_TESTS.md, Kasner satisfies every covariant vacuum condition not explicitly targeting C. For C_LF to exclude Kasner, it must depend on C_{αβγδ} or on a property Kasner lacks. If it depends on C_{αβγδ}, it must derive that dependence — not assume it.

**Status in SXC-IGC:** No explicit covariant constraint C_LF[h,K] = 0 has been derived in the workspace. The framework remains at the level of physical motivation and qualitative argument.

**Verdict: NOT PROVIDED.**

---

## Test 3: Does leak-flow mechanics define a new dynamical attractor?

A new attractor mechanism would be Category 2 (dynamical selection). This was the ekpyrotic partial solution. For leak-flow to improve on ekpyrosis:
- The attractor must operate from initial data outside the ekpyrotic basin (i.e., from high-Weyl initial data that ekpyrosis cannot handle)
- The attractor must be independently motivated by leak-flow principles
- The basin must be derivably large

**Status:** Not derived in available documents. The ekpyrotic attractor (slow contraction with w>>1) is already the strongest existing dynamical mechanism (Gate 4 result). Leak-flow would need to extend this, not merely redescribe it.

**Verdict: NOT PROVIDED.**

---

## Test 4: Does leak-flow mechanics define a quantum-state selection mechanism?

This would be Category 3. From AS_QUANTUM_STATE_AUDIT.md, the fundamental challenge is: AS fixes the action, not the state. Leak-flow would need to define a state selection mechanism without importing the desired state.

**What would be required:** Either a wave functional Ψ_LF[h] derived from leak-flow principles (not from no-boundary or equivalent), or a superselection rule that restricts the physical Hilbert space to low-Weyl states.

**Status:** Not derived. The DECOHERENCE_ROLE_AUDIT.md in the workspace explicitly killed decoherence-based selection. Any leak-flow quantum-state selection must avoid this failure mode.

**Verdict: NOT PROVIDED.**

---

## Test 5: Does leak-flow mechanics modify the gravitational equations in a way that removes the Kasner saddle?

This is the C³/w₃* route (Gate 6). Leak-flow would need to modify the gravitational effective action with a term whose variation does not vanish on Kasner.

**What would be required:** An independently motivated modification to the gravitational action S_LF[g] = S_GR + S_leak such that δS_LF/δg|_{Kasner} ≠ 0. The modification S_leak must:
- Be derived from leak-flow principles without encoding Weyl suppression
- Have an independently motivated form
- Produce a non-trivial equation of motion on Kasner

**Status:** Not derived. P03 (channel capacity) was the closest attempt and was killed for encoding the conclusion.

**Verdict: NOT PROVIDED.**

---

## Test 6: Does leak-flow mechanics define a new superselection structure?

A superselection rule would divide the Hilbert space into sectors, with physical states restricted to one sector. If the low-Weyl sector is a superselection sector, the initial state is restricted without dynamic selection.

**What would be required:** An explicit superselection rule derived from leak-flow principles, with low-Weyl and high-Weyl configurations in different sectors. The superselection must be independently motivated.

**Status:** Not derived.

**Verdict: NOT PROVIDED.**

---

## Summary

| Capability required | Provided by SXC-IGC? |
|--------------------|---------------------|
| New measure on Γ_GR | NO |
| New covariant constraint on (h,K) | NO |
| New dynamical attractor beyond ekpyrosis | NO |
| Quantum-state selection from first principles | NO |
| Gravitational action modification removing Kasner saddle | NO |
| New superselection structure | NO |

**None of the six required mathematical capabilities has been derived in the SXC-IGC framework as documented in the workspace.**

---

## What SXC-IGC Would Need to Produce

For SXC-IGC to address R1, it must explicitly derive at least one of the six capabilities above. The derivation must:
1. Start from the leak-flow/substrate framework's own axioms
2. Not import Weyl suppression, homogeneity, or isotropy as inputs
3. Produce an explicit mathematical object (functional, constraint, measure, wave functional, superselection rule)
4. Show that this object excludes Kasner or assigns it exponentially small weight

Until this derivation is produced, SXC-IGC cannot be said to solve R1. The statement "existing theories fail, therefore SXC-IGC is required" is the argument from ignorance and is prohibited per the governance rules.

---

*Document status: SXC-IGC CAPABILITY AUDIT COMPLETE*
*Result: None of the six required capabilities is currently derived in SXC-IGC.*
*Date: August 2026*
