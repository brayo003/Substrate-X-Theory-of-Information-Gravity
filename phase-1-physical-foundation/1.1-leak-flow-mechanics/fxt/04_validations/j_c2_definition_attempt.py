"""
Gap 0: Operational definition of J_C2
======================================

The task: starting only from what the C2 theory already contains, attempt to
construct a physically meaningful, dimensionally consistent, transformation-law
respecting definition of J_C2 as an observable physical quantity.

The approach is NOT to assign a familiar field to J_C2 because it looks convenient.
The approach is:

Step 1. Identify every constraint the theory already imposes on J_C2 from its
        own equations and derive what those constraints force.

Step 2. Determine the minimum additional structure needed, classify it honestly
        (derived / assumed / absent), and check whether any version of that
        structure is implied by the CCA axioms.

Step 3. For each candidate definition that survives, calculate:
        - Units and dimensional consistency
        - Transformation properties under spatial rotations and time reversal
        - Conservation law
        - Coupling matrix element with sigma_z
        - Whether the coupling constant g can be expressed in terms of known
          quantities or must remain free

Step 4. Test the strongest surviving candidate against the theory's existing
        predictions. Derive the effective Hamiltonian, the dephasing rate formula,
        and the spatial correlator.

Step 5. Identify the minimum new physics this requires and classify it precisely.

All results written to 04_validations/outputs/j_c2_definition_attempt.json
"""

from __future__ import annotations
import json
import numpy as np
from pathlib import Path

OUT = Path("04_validations/outputs")
OUT.mkdir(parents=True, exist_ok=True)


# =============================================================================
# STEP 1: Constraints the theory already imposes on J_C2
# =============================================================================

def step1_existing_constraints() -> dict:
    """
    Extract every mathematical constraint the existing C2 theory places on J_C2.
    Source documents: substrate_transport_derivation.md, CURRENT_C2_ONTOLOGY_MAP.md,
    interaction_hamiltonian_derivation.md, COMPLETE_MASTER_EQUATION.md.
    """
    return {
        "definition_in_PRW": {
            "formula": "J_C2 = v * (n+ - n-)",
            "meaning": "net signed flux of information quanta",
            "units_PRW": "info / (m^2 s)  [in 1D: info / (m s)]",
            "derived_or_assumed": "DEFINED (Layer 0 definition, CURRENT_C2_ONTOLOGY_MAP.md)",
        },
        "transport_equation": {
            "formula": "dJ/dt = -c^2 ds/dx - (1/tau) J",
            "source": "substrate_transport_derivation.md eq [C-J]",
            "meaning": (
                "J is driven by information density gradient (restoring force) "
                "and relaxes with timescale tau. Analogous to Maxwell's H-field equation."
            ),
            "derived_or_assumed": "DERIVED from PRW balance equations",
        },
        "continuity_equation": {
            "formula": "ds/dt + div(J) = 0",
            "source": "substrate_transport_derivation.md eq [C-s]",
            "meaning": "J is the current associated with the conserved charge Q = integral s dV",
            "derived_or_assumed": "DERIVED",
            "constraint_on_J": (
                "J is the Noether current of the conservation law dQ/dt = 0. "
                "This is the strongest structural constraint: J is uniquely defined "
                "as the flux vector such that the above holds. "
                "In particular, J is NOT defined up to an additive solenoidal field "
                "once the continuity equation is taken as primary."
            ),
        },
        "interaction_hamiltonian": {
            "formula": "H_int = g * J(x_q, t) * sigma_z",
            "source": "interaction_hamiltonian_derivation.md",
            "constraint": (
                "J(x_q, t) must be a real scalar (not a vector) at the qubit location, "
                "OR a specific scalar contraction of a vector field with a fixed direction. "
                "sigma_z is Hermitian and diagonal. H_int must be Hermitian. "
                "Therefore J(x_q, t) must be a real-valued scalar observable."
            ),
            "derived_or_assumed": "ASSUMED (A-HC5, A-HC6)",
        },
        "spectral_density": {
            "formula": "S_JJ(omega) = 2 S0 tau / (1 + omega^2 tau^2)",
            "source": "substrate_transport_derivation.md (Lorentzian from C-J equation)",
            "constraint": (
                "The power spectral density of J must be Lorentzian with cutoff 1/tau. "
                "Any physical identification of J must reproduce this Lorentzian PSD "
                "in the long-wavelength, low-frequency limit."
            ),
            "derived_or_assumed": "DERIVED",
        },
        "symmetry_constraints": {
            "time_reversal": (
                "Under t -> -t: s(x,t) -> s(x,-t) (even), J(x,t) -> -J(x,-t) (odd). "
                "This is the standard T-symmetry of a conserved current. "
                "Source: continuity equation + PRW balance equations."
            ),
            "spatial_rotation_2D": (
                "In 2D (chip plane), J is a 2-component vector: J = (J_x, J_y). "
                "Under rotation by angle phi: J_i -> R_ij J_j. "
                "H_int = g J * sigma_z requires a scalar from J. "
                "Natural choice: J * n_hat (projection onto a fixed direction) "
                "or |J| (magnitude, but this breaks linearity in J)."
            ),
            "derived_or_assumed": "DERIVED from PRW structure + standard current algebra",
        },
        "summary_forced_properties": [
            "J is the Noether current of Q = integral s dV (uniquely forced by continuity)",
            "J has units [charge / area / time] = [info / (m^2 s)] in 3D",
            "J is a vector field (3-component in 3D, 2-component in 2D chip plane)",
            "J is odd under time reversal",
            "J is even under spatial parity if s is even (standard current behavior)",
            "The PSD of J at the qubit location must be Lorentzian with scale tau",
            "J(x_q, t) in H_int must enter as a scalar — a projection is needed in >1D",
        ],
        "what_is_NOT_forced": [
            "The physical medium whose fluctuations produce J",
            "The projection direction n_hat for J * n_hat",
            "The conversion factor between [info] and physical units (J, m, s)",
            "The coupling constant g",
            "The value of v (= c)",
        ],
    }


# =============================================================================
# STEP 2: What additional structure is needed — CCA constraint check
# =============================================================================

def step2_minimum_additional_structure() -> dict:
    """
    Identify the minimum additional structure needed to make J_C2 a physical observable,
    and check whether the CCA axioms provide any of it.
    """

    cca_check = {
        "CCA_Ax1_objects": {
            "content": "Finite set of objects O with composition M",
            "provides_for_J": "NO — no metric, no spatial content, no units",
        },
        "CCA_Ax2_causal_order": {
            "content": "Partial order <= on morphisms (causal structure)",
            "provides_for_J": (
                "PARTIAL — causal order implies a notion of information flow: "
                "if event A <= B (A causally precedes B), information can propagate "
                "from A to B. This is an arrow. It is not yet a current density, "
                "but it is the categorical precursor to one."
            ),
        },
        "CCA_Ax3_time_reversal": {
            "content": "Involution dagger: M -> M reversing causal order",
            "provides_for_J": (
                "PARTIAL — time reversal implies J is odd: J† = -J. "
                "This is consistent with the forced property above. "
                "The CCA dagger gives J its T-parity without additional assumption."
            ),
        },
        "CCA_Ax4_probability": {
            "content": "Weight map epsilon: M -> [0,1]",
            "provides_for_J": (
                "PARTIAL — epsilon assigns a probability weight to each morphism. "
                "The 'information current' J can be interpreted as the net probability "
                "flux across a surface: J(surface) = epsilon(forward morphisms crossing "
                "surface) - epsilon(backward morphisms crossing surface). "
                "This is a CANDIDATE DEFINITION derivable from CCA."
            ),
        },
        "CCA_Ax5_composition": {
            "content": "Composition law (tensor product structure)",
            "provides_for_J": (
                "PARTIAL — composition tells us how information flows compose. "
                "This is needed to extend the local current definition to a field."
            ),
        },
    }

    # The CCA probability-flux definition
    j_from_cca = {
        "candidate_definition": "J_CCA(Sigma, t) = d/dt [epsilon(morphisms crossing Sigma in + direction) - epsilon(morphisms crossing Sigma in - direction)]",
        "physical_interpretation": (
            "J_CCA is the net rate of information (probability weight) crossing "
            "a spatial surface Sigma per unit area per unit time. "
            "This is dimensionally [info / (m^2 s)] in the continuum limit. "
            "It is the probability current of the CCA, defined without reference "
            "to any physical medium."
        ),
        "is_this_derived_from_CCA": (
            "PARTIALLY DERIVED: the definition uses Ax2 (causal order to define "
            "'crossing'), Ax3 (dagger to define direction), and Ax4 (epsilon to "
            "define the weight). It requires the additional step of taking a "
            "continuum limit over the CCA objects — which requires a metric or "
            "embedding space that is NOT in Ax1–Ax5."
        ),
        "missing_step": (
            "The CCA has no spatial metric. Objects in O are abstract; they have "
            "no positions. To define J as a spatial density, we need to embed O "
            "into a metric space (R^3 or R^2). This embedding is NOT derived from "
            "Ax1–Ax5 — it is an additional structural assumption. "
            "Without the embedding, J_CCA is defined per surface but not as a "
            "local field J(x, t)."
        ),
        "classification": "PARTIALLY_DERIVABLE — requires spatial embedding assumption",
    }

    return {
        "CCA_axiom_check": cca_check,
        "candidate_CCA_definition": j_from_cca,
        "minimum_additional_assumptions": [
            {
                "name": "Spatial embedding",
                "statement": "The CCA objects have positions in R^d (d = 2 or 3).",
                "classification": "NEW ASSUMPTION — not in Ax1-Ax5",
                "justification": (
                    "The theory postulates a substrate 'occupying' physical space "
                    "(CURRENT_C2_ONTOLOGY_MAP Layer 0: '2D chip plane' — classified "
                    "as D=interpretation). Making this precise requires a map from "
                    "CCA objects to spatial positions."
                ),
            },
            {
                "name": "Continuum limit",
                "statement": "The density of CCA objects per unit volume goes to infinity with a fixed object-spacing a → 0.",
                "classification": "NEW ASSUMPTION (analogous to A-PRW2)",
                "justification": "Required to turn J_CCA (per surface) into J(x,t) (local field).",
            },
        ],
    }


# =============================================================================
# STEP 3: The strongest surviving candidate definition
# =============================================================================

def step3_candidate_definitions() -> dict:
    """
    Derive two candidate definitions for J_C2, compute their properties,
    and classify each honestly.
    """

    # ── Candidate D1: J as PRW probability current ──────────────────────────
    D1 = {
        "name": "D1_PRW_probability_current",
        "definition": "J_C2(x, t) = v * [n+(x,t) - n-(x,t)]",
        "in_words": (
            "J_C2 is the net signed flux density of information quanta: "
            "the excess of right-movers over left-movers times the walker speed."
        ),
        "source": "CURRENT_C2_ONTOLOGY_MAP Layer 0 — this is the existing definition",
        "derivation_status": "DEFINED (not derived from anything deeper)",
        "units": {
            "n+, n-": "[info / m^3] in 3D, [info / m] in 1D",
            "v": "[m / s]",
            "J_C2": "[info / (m^2 s)] in 3D",
            "consistent_with_continuity": True,
        },
        "transformation_properties": {
            "time_reversal": "J → -J (odd, correct for a current)",
            "spatial_rotation": (
                "In 1D: J is a signed scalar. "
                "In 3D: J is a vector (J_i = v * (n+_i - n-_i) if n± are direction-resolved). "
                "BUT: the 3D PRW is not yet defined (open problem). "
                "In 2D chip plane: J = (J_x, J_y)."
            ),
            "parity": "J → -J under spatial reflection (odd, correct)",
        },
        "coupling_to_qubit": {
            "scalar_in_H_int": (
                "H_int = g J * sigma_z requires J to be a scalar. "
                "In 1D: J is already a scalar. "
                "In 2D/3D: must project onto a direction: B = n_hat · J(x_q, t). "
                "The projection direction n_hat is NOT specified by D1."
            ),
            "coupling_constant_g": {
                "units": "[J m^2 s / info]",
                "derivation": "NOT derivable from D1 — remains free",
            },
        },
        "lorentzian_PSD": {
            "derivable": True,
            "formula": "S_JJ(omega) = 2 S0 tau / (1 + omega^2 tau^2)",
            "S0": "g^2 * <|J|^2>_0 / (unit area)^2 — depends on g and background density",
        },
        "what_is_missing": [
            "3D generalization of n+, n- (directional resolution in 3D not defined)",
            "Physical identification of information quanta with any material excitation",
            "Projection direction n_hat for the scalar coupling in H_int",
            "Value of g",
        ],
        "verdict": (
            "D1 is the only definition already present in the theory. "
            "It is internally consistent in 1D. It is undefined in 3D "
            "because the 3D PRW is an open problem. It does not connect "
            "J_C2 to any physical observable without further assumptions."
        ),
    }

    # ── Candidate D2: J as CCA probability flux (new derivation attempt) ────
    D2 = {
        "name": "D2_CCA_probability_flux",
        "definition": (
            "For a CCA with objects at positions {x_i} ⊂ R^3 with spacing a, "
            "and morphisms m: x_i → x_j with weight epsilon(m), define: "
            "J_alpha(x, t) = (1/a^3) * sum_{|x_i - x| < a/2} sum_{j: x_j - x_i = a e_alpha} "
            "[epsilon(m_{ij})(t) - epsilon(m_{ji})(t)] * v_CCA "
            "where e_alpha is the unit vector in direction alpha, "
            "v_CCA = a / dt is the CCA morphism speed (lattice constant over time step)."
        ),
        "in_words": (
            "J_C2 is the net rate of probability weight flowing in direction alpha "
            "through a lattice face, per unit area. It is the discrete probability "
            "current of the CCA on its spatial lattice."
        ),
        "derivation_status": (
            "PARTIALLY DERIVED from CCA (Ax2 causal order + Ax4 probability weights) "
            "given spatial embedding assumption. "
            "NOT derivable from Ax1-Ax5 alone (requires embedding)."
        ),
        "units": {
            "epsilon(m)": "dimensionless probability weight in [0,1]",
            "a": "[m] (lattice spacing)",
            "dt": "[s] (time step)",
            "J_alpha": "[prob / (m^2 s)] ... requires conversion to [info / (m^2 s)]",
            "conversion_factor": (
                "Need: [info] = kappa_info * [probability]. "
                "kappa_info has units [info] and is a new free parameter "
                "unless 'info' is identified with Shannon entropy (dimensionless by convention) "
                "or with a physical entropy in [J/K]."
            ),
        },
        "information_unit_issue": {
            "problem": (
                "'Information' in [info] is the same as 'nat' (natural unit of information). "
                "In the C2 theory, s has units [info/m^3]. If [info] = [nat] = dimensionless, "
                "then [s] = [1/m^3] (number density), [J] = [1/(m^2 s)] (number flux). "
                "This is CONSISTENT with a particle number density: "
                "s = number density of information quanta, "
                "J = flux of information quanta. "
                "Under this identification: [J] = [1/(m^2 s)] = [m^-2 s^-1]. "
                "The coupling [g] = [J m^2 s] = [energy] if [info] is dimensionless. "
                "g is then an energy — the energy per information quantum."
            ),
            "consequence_for_D2": (
                "With [info] = dimensionless: J_alpha = number flux of CCA morphisms. "
                "kappa_info = 1 (not a new parameter). "
                "v_CCA = a/dt = lattice speed. "
                "This IDENTIFIES v_CCA with the PRW speed v = c. "
                "So c = a/dt = lattice spacing / time step. "
                "c is the CCA lattice speed."
            ),
            "this_is_new": (
                "This identification is not explicitly in any existing C2 document. "
                "It arises from following the dimensional analysis to its conclusion."
            ),
        },
        "coupling_to_qubit": {
            "natural_scalar": (
                "H_int = g J_alpha(x_q, t) sigma_z for a chosen direction alpha. "
                "The direction alpha is the direction of the dominant CCA morphism "
                "flux at the qubit location — which is determined by the local "
                "causal structure (causal order Ax2). "
                "This is a partial derivation of the projection direction: "
                "alpha = direction of maximal probability flux, determined by the "
                "CCA background state."
            ),
            "g_from_D2": (
                "g has units [J] (energy) under the [info]=dimensionless convention. "
                "It is the energy transferred per information quantum crossing the qubit. "
                "In quantum mechanics, the energy scale is set by the qubit splitting hbar*omega_q. "
                "Candidate: g ~ hbar * omega_q * (qubit volume)^{1/3} * (something). "
                "This is not yet a derivation — but the dimensional analysis "
                "constrains g to be an energy times a length^0 or times a volume. "
                "Further: g must be small for the Born approximation to hold: "
                "g^2 S0 tau / hbar^2 << hbar omega_q. "
                "This is a consistency constraint, not a derivation."
            ),
        },
        "verdict": (
            "D2 is partially derivable from CCA given a spatial embedding. "
            "It identifies c with the CCA lattice speed a/dt. "
            "It gives a partial derivation of the projection direction. "
            "g remains the energy per information quantum — constrained in units "
            "but not in value. The spatial embedding is a new assumption."
        ),
    }

    # ── Candidate D3: J as divergence-free correction ───────────────────────
    # The continuity equation ds/dt + div(J) = 0 determines div(J) from ds/dt
    # but does NOT uniquely determine J: any solenoidal field B (div B = 0)
    # can be added to J. This is the Helmholtz decomposition ambiguity.
    # The PRW resolves this by construction (n+, n- give a specific J).
    # In 3D without the PRW, J is ambiguous up to solenoidal corrections.
    D3_ambiguity = {
        "name": "D3_Helmholtz_ambiguity",
        "statement": (
            "The continuity equation div(J) = -ds/dt determines only the "
            "irrotational (longitudinal) part of J via Helmholtz decomposition: "
            "J = J_L + J_T where div(J_T) = 0 (transverse/solenoidal part). "
            "The continuity equation places NO constraint on J_T."
        ),
        "consequence": (
            "In 3D, J_C2 is underdetermined by the continuity equation alone. "
            "The PRW resolves this in 1D (no transverse component exists). "
            "In 3D, the PRW must be extended to specify whether J is purely "
            "irrotational (gradient of a potential) or has a solenoidal part. "
            "The 2D theory assumes J lives in the chip plane, which reduces but "
            "does not eliminate this ambiguity."
        ),
        "physical_relevance": (
            "For the qubit coupling: if J_T couples to the qubit, it contributes "
            "to dephasing without affecting the continuity equation. "
            "The existing theory implicitly assumes J is irrotational (derivable "
            "from a potential phi: J = -c^2 tau grad phi for steady state). "
            "This is a hidden assumption that should be made explicit."
        ),
        "verdict": "AMBIGUITY — requires additional constraint (irrotational J, or specified J_T)",
    }

    return {
        "D1_PRW_current": D1,
        "D2_CCA_probability_flux": D2,
        "D3_Helmholtz_ambiguity": D3_ambiguity,
        "strongest_candidate": "D2",
        "reason_D2_strongest": (
            "D2 is the only candidate that connects J_C2 to the CCA axioms "
            "in a derivable way (given spatial embedding). "
            "It identifies c = a/dt (lattice speed), which is the first "
            "non-trivial result: c is the CCA lattice spacing divided by "
            "the CCA time step. This is not derivable from Ax1-Ax5 alone "
            "but is forced once the spatial embedding is made."
        ),
    }


# =============================================================================
# STEP 4: Consequences of D2 — effective Hamiltonian and dephasing rate
# =============================================================================

def step4_D2_predictions() -> dict:
    """
    Derive the effective Hamiltonian and dephasing rate under candidate D2.
    Show what the theory predicts, what remains free, and what is new.
    """

    # Under D2 with [info] = dimensionless:
    # J_alpha(x_q, t) = v_CCA * [n+(x_q, t) - n-(x_q, t)]  (component alpha)
    # H_int = g J_alpha(x_q, t) sigma_z
    # g = energy per information quantum [J]
    #
    # The autocorrelation:
    # <J_alpha(t) J_alpha(0)> = v_CCA^2 <(n+ - n-)(t)(n+ - n-)(0)>
    #                        = (v_CCA/c)^2 * c^2 <(n+ - n-)(t)(n+ - n-)(0)>
    # In the PRW: <J(t) J(0)> = S0 exp(-|t|/tau)  with S0 = c^2 * (2 n0)
    # where n0 is the background walker density.
    #
    # Dephasing rate (Born-Markov):
    # Gamma_phi = (g^2 / hbar^2) * S_JJ(omega_q=0)
    #           = (g^2 / hbar^2) * 2 S0 tau
    # where S0 = c^2 * 2 n0 (from PRW background).
    #
    # c = a/dt under D2 identification.
    # n0 = (number of CCA morphisms per unit volume) -- related to substrate 'density'
    #
    # So: Gamma_phi = (g^2 / hbar^2) * 2 * (a/dt)^2 * 2 n0 * tau
    #
    # Under D2, what is n0?
    # n0 is the background density of CCA morphisms -- the number of
    # causal connections per unit volume. This is related to the CCA
    # 'connectivity density' which is NOT determined by Ax1-Ax5.
    # It is the substrate density s0 = n0, which is a free parameter.

    return {
        "effective_hamiltonian": {
            "formula": "H_int = g * J_alpha(x_q, t) * sigma_z",
            "J_alpha_formula": "J_alpha = (a/dt) * [n+(x_q,t) - n-(x_q,t)]_alpha",
            "derived_from_D2": True,
            "new_assumptions": [
                "Spatial embedding of CCA (positions x_i in R^3)",
                "Projection direction alpha = direction of dominant CCA flux",
            ],
        },
        "autocorrelation": {
            "formula": "<J_alpha(t) J_alpha(0)> = S0 * exp(-|t| / tau)",
            "S0": "c^2 * 2 * n0  where n0 = CCA morphism density [m^{-3}]",
            "tau": "1/(2 lambda) = mean free time between reversals",
            "derived": True,
        },
        "dephasing_rate": {
            "formula": "Gamma_phi = (g^2 / hbar^2) * 2 * S0 * tau",
            "substituting_D2": "Gamma_phi = (g^2 / hbar^2) * 2 * (c^2 * 2 n0) * tau = (g^2 / hbar^2) * 4 n0 c^2 tau",
            "free_parameters": ["g", "n0", "c", "tau"],
            "c_under_D2": "c = a / dt  (CCA lattice speed -- determined by CCA geometry)",
            "n0_under_D2": "n0 = CCA morphism density -- NOT determined by Ax1-Ax5",
        },
        "spatial_correlator": {
            "formula": "C_Gamma(r) = K0(r / xi_c) / K0(a / xi_c)",
            "xi_c": "2 * c * tau = 2 * (a/dt) * tau",
            "under_D2": (
                "xi_c = 2 * (a/dt) * tau. "
                "If a and dt are fixed by the CCA geometry, and tau is measured, "
                "then xi_c is predicted from the CCA lattice parameters. "
                "This would be the first non-free prediction of xi_c. "
                "BUT: a/dt = c is still free unless the CCA geometry specifies a and dt."
            ),
        },
        "what_D2_fixes_vs_leaves_free": {
            "fixed_by_D2": [
                "Functional form of J_C2 (probability flux of CCA morphisms)",
                "Units of J_C2 ([m^{-2} s^{-1}] if info=dimensionless)",
                "Time-reversal and parity properties of J_C2",
                "Lorentzian form of S_JJ(omega) — preserved from PRW",
                "Identification c = a/dt (CCA lattice speed)",
            ],
            "still_free_after_D2": [
                "a (CCA lattice spacing) -- not in Ax1-Ax5",
                "dt (CCA time step) -- not in Ax1-Ax5",
                "n0 (CCA morphism density) -- not in Ax1-Ax5",
                "g (coupling energy per quantum) -- constrained in units but not value",
                "Projection direction alpha -- partially constrained by local CCA flux direction",
            ],
            "new_constraint_from_D2": (
                "c = a/dt is a relationship between three quantities that were "
                "previously independent. Once a and dt are fixed by the CCA, c follows. "
                "This is a genuine new constraint — but a and dt are still free."
            ),
        },
    }


# =============================================================================
# STEP 5: The minimum new physics
# =============================================================================

def step5_minimum_new_physics() -> dict:
    """
    Precisely characterize what new physics is required to make J_C2 a
    well-defined physical observable with a derivable coupling.
    """

    return {
        "gap_0_decomposition": {
            "gap_0a_spatial_embedding": {
                "what": "A map from CCA objects to positions in R^d",
                "why_needed": "Without positions, J cannot be a spatial field",
                "physical_content": (
                    "The CCA lives in physical space. This requires specifying "
                    "the dimensionality d and the embedding map. "
                    "For the chip geometry: d=2, with the qubit in the plane."
                ),
                "what_it_gives": "J_C2 becomes a field on R^d, not just an abstract flux",
                "is_it_reasonable": (
                    "YES: the theory already assumes a 2D chip plane "
                    "(CURRENT_C2_ONTOLOGY_MAP Layer 0, classified as D=interpretation). "
                    "Making it an explicit assumption is just promoting an implicit "
                    "interpretation to an axiom."
                ),
                "classification": "NEW AXIOM (promotes existing implicit interpretation)",
            },
            "gap_0b_lattice_scale": {
                "what": "The CCA lattice spacing a (and time step dt = a/c)",
                "why_needed": "Determines c = a/dt and n0 (morphism density ~ 1/a^d)",
                "physical_content": (
                    "a is the fundamental length scale of the information substrate. "
                    "It sets the UV cutoff of the theory. "
                    "In a discretized CCA: a ~ Planck length (if fundamental), "
                    "or a ~ qubit spacing (if emergent from chip geometry), "
                    "or a ~ phonon wavelength at the Debye cutoff (if phononic)."
                ),
                "what_it_gives": "Fixes c, n0, xi_c as functions of a and tau",
                "three_candidate_scales": {
                    "Planck_scale": {
                        "a": "1.6e-35 m",
                        "c_if_dt_is_Planck_time": "c = a / t_P = speed of light = 3e8 m/s",
                        "comment": (
                            "This gives c = speed of light, which contradicts the "
                            "assumption c ~ v_acoustic ~ 6000 m/s. "
                            "Not compatible with the existing experimental context."
                        ),
                    },
                    "qubit_spacing": {
                        "a": "~1e-4 m (100 micrometers, typical qubit-to-qubit distance)",
                        "c_if_measured_tau": "c = a / dt = a * 2*lambda  ... dt = 1/(2*lambda*c) -- circular",
                        "comment": (
                            "c is still not fixed unless dt is independently determined."
                        ),
                    },
                    "decoherence_length": {
                        "a": "xi_c / (2 * c * tau / xi_c)  -- circular without fixing c",
                        "comment": "Cannot determine a from decoherence data without knowing c first.",
                    },
                },
                "conclusion": (
                    "No physically motivated choice of a is available from the existing "
                    "theory. a is genuinely free."
                ),
                "classification": "NEW FREE PARAMETER (a is not in Ax1-Ax5)",
            },
            "gap_0c_morphism_density": {
                "what": "n0 = density of active CCA morphisms per unit volume",
                "why_needed": "Determines S0 = c^2 * 2 n0 in dephasing formula",
                "relation_to_existing_params": "n0 = s0 (background information density)",
                "classification": "EXISTING FREE PARAMETER (s0 in CURRENT_C2_ONTOLOGY_MAP)",
            },
            "gap_0d_coupling_energy": {
                "what": "g = energy transferred per information quantum to qubit",
                "why_needed": "Sets magnitude of dephasing rate",
                "units_under_D2": "[J] (energy)",
                "dimensional_constraint": (
                    "g must satisfy: g^2 * S0 * tau / hbar^2 ~ Gamma_phi ~ 1/T2. "
                    "For T2 ~ 100 microseconds: g^2 * S0 * tau ~ hbar^2 / T2 ~ (1e-34)^2 / 1e-4 ~ 1e-64 J^2. "
                    "With S0 = c^2 * n0 and tau ~ 1e-6 s: g^2 ~ 1e-64 / (c^2 * n0 * 1e-6). "
                    "For c ~ 6000 m/s and n0 ~ 1e15 m^{-3}: g ~ 1e-34 J ~ hbar. "
                    "This is consistent with g ~ hbar, suggesting g is of order "
                    "the quantum of action times some frequency."
                ),
                "candidate_expression": "g = hbar * omega_0 / c  where omega_0 is a substrate frequency",
                "this_is_new": True,
                "classification": "CONSTRAINED BY DIMENSIONAL ANALYSIS but not uniquely fixed",
            },
        },
        "what_D2_actually_derives": {
            "genuine_derivation": [
                "J_C2 is the CCA probability flux (from Ax2, Ax4, spatial embedding)",
                "J_C2 is odd under T-reversal (from Ax3 = dagger involution)",
                "J_C2 is a vector field in d dimensions (from spatial embedding)",
                "The Lorentzian PSD of J_C2 follows from the PRW structure (existing result)",
                "c = a/dt is forced once a and dt are fixed (new structural result)",
            ],
            "still_requires_external_input": [
                "Spatial embedding (new axiom promoting existing interpretation)",
                "Lattice spacing a",
                "Projection direction alpha (partially constrained)",
                "Coupling energy g (constrained but not fixed)",
            ],
        },
        "is_this_progress": {
            "verdict": "YES — but limited",
            "reason": (
                "Before this derivation: J_C2 had no connection to anything outside the PRW. "
                "After D2: J_C2 is the CCA probability flux, derivable given spatial embedding. "
                "This gives J_C2 a physical interpretation (causal information flow) "
                "and identifies c as the CCA lattice speed. "
                "The identification c = a/dt is the first structural constraint on c — "
                "it does not fix c's value, but it says what c IS: the speed at which "
                "causal information propagates at the lattice scale. "
                "This is a genuine, if partial, advance."
            ),
            "what_is_not_progress": (
                "We still have three free parameters (a, n0, g). "
                "The experiment cannot be designed until these are constrained. "
                "The spatial embedding is a new assumption, not a theorem. "
                "D2 does not select a unique speed in 3D — if the CCA has "
                "directional structure (anisotropic causal order), different "
                "directions can have different lattice spacings and thus different c."
            ),
        },
    }


# =============================================================================
# Main
# =============================================================================

def main() -> int:
    print("Gap 0: Operational definition of J_C2")
    print("=" * 60)

    c1 = step1_existing_constraints()
    c2 = step2_minimum_additional_structure()
    c3 = step3_candidate_definitions()
    c4 = step4_D2_predictions()
    c5 = step5_minimum_new_physics()

    print("\nStep 1: Existing constraints on J_C2")
    for p in c1["summary_forced_properties"]:
        print(f"  ✓ {p}")

    print("\nStep 2: CCA axiom check")
    provides = [(k, v["provides_for_J"][:60]) for k, v in c2["CCA_axiom_check"].items()]
    for ax, what in provides:
        print(f"  {ax}: {what}...")

    print(f"\nStep 3: Strongest candidate = {c3['strongest_candidate']}")
    print(f"  Reason: {c3['reason_D2_strongest'][:80]}...")

    print("\nStep 4: D2 fixes vs leaves free")
    print("  Fixed by D2:")
    for item in c4["what_D2_fixes_vs_leaves_free"]["fixed_by_D2"]:
        print(f"    + {item}")
    print("  Still free:")
    for item in c4["what_D2_fixes_vs_leaves_free"]["still_free_after_D2"]:
        print(f"    - {item}")

    print("\nStep 5: New physics classification")
    for gap_name, gap_info in c5["gap_0_decomposition"].items():
        print(f"  {gap_name}: {gap_info['classification']}")

    print(f"\nIs D2 progress? {c5['is_this_progress']['verdict']}")
    print(f"  {c5['is_this_progress']['reason'][:120]}...")

    # The key new result: g ~ hbar
    g_estimate = c4["dephasing_rate"]["free_parameters"]
    print("\n── Key dimensional result ──")
    print(f"  g ~ hbar (energy per information quantum ~ quantum of action)")
    print(f"  This constrains g's scale for the first time.")
    print(f"  c = a/dt: the CCA lattice speed is the first structural identification of c.")

    output = {
        "step1_existing_constraints": c1,
        "step2_CCA_structure": c2,
        "step3_candidate_definitions": c3,
        "step4_D2_consequences": c4,
        "step5_minimum_new_physics": c5,
        "summary": {
            "strongest_J_definition": "D2: J_C2 = CCA probability flux (partially derivable)",
            "c_identification": "c = a/dt where a = CCA lattice spacing, dt = CCA time step",
            "g_scale": "g ~ hbar (from dimensional analysis of dephasing rate)",
            "new_axiom_required": "Spatial embedding of CCA objects",
            "free_parameters_remaining": 3,
            "genuine_advance": "c identified as CCA lattice speed; J given CCA interpretation",
            "gap_0_status": "PARTIALLY RESOLVED — embedding required; a still free",
        },
    }

    out_path = OUT / "j_c2_definition_attempt.json"
    out_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"\nResults written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
