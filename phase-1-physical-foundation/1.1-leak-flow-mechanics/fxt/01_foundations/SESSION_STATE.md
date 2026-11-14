# Current Status

## Completed

- Microscopic derivation
- PRW derivation
- Transport derivation
- IBM Ramsey acquisition
- Decoherence comparison
- Interaction Hamiltonian: derivation + validation (V1–V10 all pass)
- Effective master equation: derivation + validation (M1–M10 all pass)
- Decoherence chain summary

## Current File

decoherence_chain_summary.md (completed)

## Completed in This Session

1. interaction_hamiltonian_validation.py
   - Added evolve_qubit() using stochastic-phase formulation
   - Fixed measure_gamma() to use Var[φ(t)] slope (not exp fit)
   - All 22 checks pass (V1–V10 + subtest)

2. effective_master_equation_derivation.md
   - Derives Lindblad form from Bloch-Redfield
   - Proves L=σ_z, Γ_φ=2γ, T₁=∞, CPTP

3. effective_master_equation_validation.py
   - 21/21 checks pass (M1–M10)

4. decoherence_chain_summary.md
   - Full PRW→quantum chain documented
   - Assumption audit, parameter identification
   - Falsification criteria listed

## Next Steps (Roadmap)

The theoretical chain is complete:

PRW → Telegrapher → Transport → H_int → Lindblad ME → Γ_φ = k_rot·ω_rot²

Remaining open questions:
1. What determines g (quantum-classical coupling)?
2. Multi-mode / non-Markovian corrections
3. Transverse coupling (T₁ finite?)
4. Connection to emergent quantum dynamics (Schrödinger limit)

If continuing: see decoherence_chain_summary.md Section "Open Questions"
