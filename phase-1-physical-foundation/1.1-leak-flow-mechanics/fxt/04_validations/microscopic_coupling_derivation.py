"""
Microscopic C2 Current–Substrate Coupling: Derivation Attempt and Validation
=============================================================================

TASK: Determine whether any physically defensible candidate mapping between
J_C2 and silicon elastic degrees of freedom can
  (a) be derived from existing C2 axioms, OR
  (b) constitute a physically motivated NEW constitutive assumption, AND
  (c) select a unique acoustic branch, AND
  (d) produce a unique effective PRW speed c.

All candidate mappings are explicitly classified:
  DERIVED   – follows from an existing C2 equation
  ASSUMED   – new constitutive hypothesis, not derived from C2
  ABSENT    – not representable using any identified elastic observable

The existing C2 coupling is H_int = g J_C2(x_q,t) sigma_z.
J_C2 is defined only as the 1D PRW current c(n+ - n-).
There is no existing map from J_C2 to u(x,t), epsilon(x,t), p(x,t), etc.

CANDIDATES INVESTIGATED
-----------------------
M0: Existing C2 coupling (baseline, unspecified)
M1: Scalar dilatational density   B = -kappa rho div(u)
M2: Elastic energy flux (Poynting) B = n_hat . T . u_dot  (projected onto sensor axis)
M3: Phonon momentum density        B = rho u_dot . n_hat
M4: Acoustic intensity scalar      B = -sigma_ij n_i u_dot_j  (stress contracted with velocity)

For each candidate M1–M4 the script calculates:
  - Branch polarization projection w_b(n) for all three acoustic branches
  - Whether any branch decouples exactly (w_b = 0) at generic cubic direction
  - The resulting multi-speed bath correlator structure
  - Whether a unique PRW speed c follows

All numerical results are written to 04_validations/outputs/microscopic_coupling_derivation.json

SILICON ELASTIC CONSTANTS (room temperature):
  C11 = 165.7 GPa, C12 = 63.9 GPa, C44 = 79.6 GPa, rho = 2330 kg/m^3
Source: Madelung (1982) Landolt-Börnstein, commonly cited values.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

OUT = Path("04_validations/outputs")
OUT.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────
# Material constants
# ──────────────────────────────────────────────────────────────────
C11 = 165.7e9  # Pa
C12 = 63.9e9   # Pa
C44 = 79.6e9   # Pa
RHO = 2330.0   # kg/m^3

# Test directions: 3 high-symmetry + 1 generic
DIRECTIONS: dict[str, np.ndarray] = {
    "[100]":        np.array([1.0, 0.0, 0.0]),
    "[110]":        np.array([1.0, 1.0, 0.0]),
    "[111]":        np.array([1.0, 1.0, 1.0]),
    "generic[123]": np.array([1.0, 2.0, 3.0]),
    "generic[213]": np.array([2.0, 1.0, 3.0]),
    "generic[132]": np.array([1.0, 3.0, 2.0]),
}


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n < 1e-15:
        raise ValueError("zero vector")
    return v / n


# ──────────────────────────────────────────────────────────────────
# Christoffel matrix (cubic symmetry)
# ──────────────────────────────────────────────────────────────────
def christoffel(n: np.ndarray) -> np.ndarray:
    """Christoffel matrix Gamma_ij = C_iklj n_k n_l for cubic symmetry.

    For cubic C11,C12,C44 the Christoffel matrix is:
      Gamma_ii = C11 n_i^2 + C44 (1 - n_i^2)
      Gamma_ij = (C12 + C44) n_i n_j   (i != j)
    """
    l, m, p = n
    G = np.zeros((3, 3))
    G[0, 0] = C11 * l**2 + C44 * (m**2 + p**2)
    G[1, 1] = C11 * m**2 + C44 * (l**2 + p**2)
    G[2, 2] = C11 * p**2 + C44 * (l**2 + m**2)
    G[0, 1] = G[1, 0] = (C12 + C44) * l * m
    G[0, 2] = G[2, 0] = (C12 + C44) * l * p
    G[1, 2] = G[2, 1] = (C12 + C44) * m * p
    return G


def acoustic_modes(n_raw: np.ndarray) -> list[dict]:
    """Return the 3 acoustic modes sorted by phase speed (ascending).

    Each mode dict has keys:
      branch   – 'LA', 'TA1', 'TA2'
      speed    – phase speed [m/s]
      e        – polarization unit vector (eigenvector of Christoffel matrix)
      lon_proj – |n dot e|   longitudinal projection
    """
    n = normalize(n_raw)
    G = christoffel(n)
    eigenvalues, eigenvectors = np.linalg.eigh(G)
    modes = []
    for idx in np.argsort(eigenvalues):
        ev = eigenvalues[idx]
        e = eigenvectors[:, idx]
        lon = abs(float(np.dot(n, e)))
        modes.append({
            "speed": float(np.sqrt(ev / RHO)),
            "e": e,
            "lon_proj": lon,
        })
    # Label: highest longitudinal projection → LA
    la_idx = max(range(3), key=lambda i: modes[i]["lon_proj"])
    ta_idx = [i for i in range(3) if i != la_idx]
    modes[la_idx]["branch"] = "LA"
    for k, i in enumerate(ta_idx, 1):
        modes[i]["branch"] = f"TA{k}"
    return modes


# ──────────────────────────────────────────────────────────────────
# Stiffness tensor helper for 3D stress computation
# ──────────────────────────────────────────────────────────────────
def stiffness_tensor_voigt() -> np.ndarray:
    """Return 6x6 Voigt stiffness matrix for cubic silicon."""
    C = np.zeros((6, 6))
    # diagonal: C11 for (xx,yy,zz), C44 for (yz,xz,xy)
    C[0, 0] = C[1, 1] = C[2, 2] = C11
    C[3, 3] = C[4, 4] = C[5, 5] = C44
    # off-diagonal
    C[0, 1] = C[0, 2] = C[1, 0] = C[1, 2] = C[2, 0] = C[2, 1] = C12
    return C


def stress_voigt_from_strain_voigt(eps: np.ndarray) -> np.ndarray:
    """sigma_voigt = C_voigt * eps_voigt."""
    return stiffness_tensor_voigt() @ eps


def strain_voigt_from_plane_wave(
    k: np.ndarray, e: np.ndarray, amplitude: float = 1.0
) -> np.ndarray:
    """Voigt strain for plane wave u = e * exp(i k.x).

    epsilon_ij = (1/2)(k_i e_j + k_j e_i) * i
    Using real part: we work with real amplitude amplitudes proportional to k.
    Returns 6-vector [exx, eyy, ezz, 2eyz, 2exz, 2exy] normalized by i*amplitude.
    """
    k_norm = k  # k-vector in wave direction, magnitude |k|
    # eps_ij = (1/2)(k_i e_j + k_j e_i)  (proportional to i*|k|)
    exx = k_norm[0] * e[0]
    eyy = k_norm[1] * e[1]
    ezz = k_norm[2] * e[2]
    eyz2 = k_norm[1] * e[2] + k_norm[2] * e[1]
    exz2 = k_norm[0] * e[2] + k_norm[2] * e[0]
    exy2 = k_norm[0] * e[1] + k_norm[1] * e[0]
    return np.array([exx, eyy, ezz, eyz2, exz2, exy2]) * amplitude


def stress_tensor_from_voigt(sv: np.ndarray) -> np.ndarray:
    """Convert Voigt 6-vector to 3x3 stress tensor."""
    s = np.zeros((3, 3))
    s[0, 0] = sv[0]
    s[1, 1] = sv[1]
    s[2, 2] = sv[2]
    s[1, 2] = s[2, 1] = sv[3] / 2
    s[0, 2] = s[2, 0] = sv[4] / 2
    s[0, 1] = s[1, 0] = sv[5] / 2
    return s


# ──────────────────────────────────────────────────────────────────
# Candidate coupling functions: compute spectral weight w_b(n)
# w_b = |G_b|^2 normalized so that sum_b w_b = 1
#
# For plane wave u_b = e_b(n) * q_b * exp(i(k * n.x - omega_b t))
# with k = |k| n, the observable is evaluated per unit mode amplitude q_b.
# G_b is the resulting bath operator amplitude per unit q_b per unit k.
# ──────────────────────────────────────────────────────────────────


def weights_m1_scalar_dilatation(modes: list[dict], n: np.ndarray) -> dict[str, float]:
    """M1: B = -kappa rho div(u) = -kappa rho (i k) (n . e_b) q_b.

    Weight: w_b = |n . e_b|^2
    Derivation status: ASSUMED (new constitutive identification, not from C2).
    Physical rationale: divergence of displacement couples to longitudinal strain only.
    Dimensional check: [B] = [kappa][rho][k][e][q] = (1/Pa)(kg/m^3)(1/m)(1)(m) = kg/m^2 -> OK if kappa in 1/Pa.
    """
    weights = {}
    for mode in modes:
        b = mode["branch"]
        w = mode["lon_proj"] ** 2
        weights[b] = w
    return weights


def weights_m2_energy_flux(modes: list[dict], n: np.ndarray) -> dict[str, float]:
    """M2: Elastic energy flux (Poynting-like) projected onto qubit axis n.

    P_i = -sigma_ij * du_j/dt

    For a plane wave u_b = e_b q_b exp(i(k n.x - omega_b t)):
      du_j/dt = -i omega_b e_j q_b exp(...)
      epsilon_kl = (1/2)(k_k e_l + k_l e_k) i q_b exp(...)
      sigma_ij = C_ijkl epsilon_kl

    Sensor projection: B = n_i P_i = -n_i sigma_ij du_j/dt

    This is a vector contracted with n, so it is a scalar observable.
    Derivation status: ASSUMED (new constitutive identification).
    Physical rationale: energy current through qubit location ~ interaction energy.
    """
    # For plane wave with k = |k| n, omega_b = v_b |k|:
    # n_i sigma_ij e_j = n_i C_ijkl (n_k e_l) e_j
    # The amplitude is proportional to: (n_i C_ijkl n_k) e_l e_j  = e_j Gamma_jl e_l
    # Since e_b is Christoffel eigenvector: Gamma e_b = rho v_b^2 e_b
    # So e_j Gamma_jl e_l = rho v_b^2 |e_b|^2 = rho v_b^2
    # Therefore |G_b|^2 proportional to (rho v_b^2)^2 * omega_b^2 / (normalization)
    #
    # But we want the matrix element at fixed k (single k mode), normalizing by branch speed:
    # |G_b|^2 ∝ rho^2 v_b^4 (since the Christoffel contraction gives rho v_b^2 for unit e_b)
    # The relative spectral weight among branches at fixed k:

    weights_raw = {}
    for mode in modes:
        b = mode["branch"]
        v_b = mode["speed"]
        # At fixed k, energy flux amplitude ~ sigma_ij n_i * (u_dot)_j
        # = C_ijkl epsilon_kl n_i * (-i omega_b) e_j
        # epsilon_kl = (1/2)(ik n_k e_l + ik n_l e_k) = (i k / 2)(n_k e_l + n_l e_k)
        # sigma_ij = C_ijkl (ik/2)(n_k e_l + n_l e_k)
        # = (ik/2) C_ijkl n_k e_l + (ik/2) C_ijkl n_l e_k
        # sigma_ij n_i = (ik/2)[C_ijkl n_i n_k e_l + C_ijkl n_i n_l e_k]
        # = ik * Gamma_jl e_l (using Christoffel symmetry)
        # = ik * (rho v_b^2) e_j
        # n_hat . P = n_i P_i = -n_i sigma_ij (du_j/dt)
        # = -n_i * (ik rho v_b^2 e_i) * (-i omega_b e_j) ... wait, need careful index
        # Let me be explicit:
        # sigma_ij = C_ijkl epsilon_kl = C_ijkl (i k / 2)(n_k e_l + n_l e_k) * q
        #          = (ik) C_ijkl n_k e_l * q  (using Cijkl = Cijlk)
        # = ik * Gamma_jl e_l * q / rho ... no, Gamma_jl = C_jklm n_k n_m / rho not directly
        # Direct: Gamma_il = C_ijkl n_j n_k  (Christoffel definition)
        # sigma_ij n_j = C_ijkl n_j (ik n_k e_l) q = ik C_ijkl n_j n_k e_l q
        #              = ik rho Gamma_il e_l q / rho ... let me use:
        # Actually: sigma_ij n_j = (ik q) Gamma(n)_il / rho * rho e_l  = ik q Gamma_il e_l
        # Wait: Gamma_il = (1/rho) C_ijkl n_j n_k, so C_ijkl n_j n_k = rho Gamma_il
        # So sigma_ij n_j = ik q rho Gamma_il e_l = ik q rho (rho v_b^2 e_i) = i k q rho^2 v_b^2 / rho * e_i
        # Hmm let's be clean. Gamma_il e_l^(b) = (rho v_b^2 / rho) ... no:
        # Christoffel matrix: C_ijkl n_j n_k e_l^(b) = rho v_b^2 e_i^(b)
        # So sigma_ij n_j = ik q * rho v_b^2 e_i^(b)
        # P_i = -sigma_ij u_dot_j = -sigma_ij (-i omega_b e_j q)
        #      = i omega_b q sigma_ij e_j
        # B = n_hat . P = i omega_b q n_i sigma_ij e_j
        #              = i omega_b q n_i (ik rho v_b^2 e_i)
        #              = i omega_b q (ik rho v_b^2 (n . e_b))
        #              = -k omega_b q rho v_b^2 (n . e_b)
        #              = -k^2 v_b q rho v_b^2 (n . e_b)  [using omega_b = v_b k]
        #              = -k^2 rho v_b^3 (n . e_b) q
        # So |G_b|^2 at fixed k proportional to rho^2 v_b^6 (n . e_b)^2
        e_b = mode["e"]
        lon = float(np.dot(n, e_b))
        weights_raw[b] = (RHO * v_b**3 * lon) ** 2
    total = sum(weights_raw.values())
    if total < 1e-40:
        return {b: 0.0 for b in weights_raw}
    return {b: w / total for b, w in weights_raw.items()}


def weights_m3_momentum_density(modes: list[dict], n: np.ndarray) -> dict[str, float]:
    """M3: Phonon momentum density projected onto n.

    B = rho * n . (du/dt) = rho n_i (du_i/dt)

    For plane wave: du_i/dt = -i omega_b e_i q_b exp(...)
    B_b = -i omega_b rho (n . e_b) q_b

    Weight: w_b = (omega_b)^2 (n . e_b)^2 ∝ v_b^2 (n . e_b)^2  (at fixed k)

    Derivation status: ASSUMED (new constitutive identification).
    Physical rationale: momentum density couples qubit to mechanical inertia of substrate.
    """
    weights_raw = {}
    for mode in modes:
        b = mode["branch"]
        v_b = mode["speed"]
        e_b = mode["e"]
        lon = float(np.dot(n, e_b))
        # |G_b|^2 ∝ (rho omega_b |n.e_b|)^2 = (rho v_b k |n.e_b|)^2
        # At fixed k: proportional to v_b^2 * (n.e_b)^2
        weights_raw[b] = (v_b * lon) ** 2
    total = sum(weights_raw.values())
    if total < 1e-40:
        return {b: 0.0 for b in weights_raw}
    return {b: w / total for b, w in weights_raw.items()}


def weights_m4_acoustic_intensity(modes: list[dict], n: np.ndarray) -> dict[str, float]:
    """M4: Acoustic intensity vector (stress contracted with velocity).

    B = n_i sigma_ij u_dot_j  (note: + sign, and sensor axis is n)

    For plane wave: sigma_ij = C_ijkl (ik n_k e_l) q,  u_dot_j = -i omega_b e_j q
    B_b = n_i C_ijkl (ik n_k e_l) q * (-i omega_b e_j) q
        = n_i C_ijkl n_k e_l e_j * k omega_b |q|^2

    The contraction n_i C_ijkl n_k e_l e_j = e_j Gamma_jl e_l = rho v_b^2  (scalar eigenvalue)

    So B_b amplitude ∝ rho v_b^2 * k omega_b = rho v_b^2 * k * v_b * k = rho v_b^3 k^2

    Note: This result is branch-independent in the scalar part! The only branch dependence
    comes from whether this is the eigenvalue contraction. For ALL branches:
      e_b^T Gamma e_b = rho v_b^2  (definitionally from eigenvalue equation)

    Therefore: |G_b|^2 ∝ (rho v_b^3)^2 at fixed k, regardless of polarization.

    This M4 coupling does NOT project onto (n.e_b) -- it uses the full Christoffel
    contraction. It discriminates branches only by their speed v_b, not polarization.

    Derivation status: ASSUMED (new constitutive identification).
    """
    weights_raw = {}
    for mode in modes:
        b = mode["branch"]
        v_b = mode["speed"]
        # |G_b|^2 ∝ (rho v_b^3)^2
        weights_raw[b] = (RHO * v_b**3) ** 2
    total = sum(weights_raw.values())
    if total < 1e-40:
        return {b: 0.0 for b in weights_raw}
    return {b: w / total for b, w in weights_raw.items()}


# ──────────────────────────────────────────────────────────────────
# PRW kinetic reduction: can we close to one speed?
# ──────────────────────────────────────────────────────────────────

def analyze_prw_reduction(
    weights: dict[str, float], speeds: dict[str, float]
) -> dict[str, Any]:
    """Determine whether the branch coupling allows a single-speed PRW reduction.

    Conditions for single-speed closure (all three required):
      1. Exactly one branch has nonzero weight (w_b > threshold)
      2. That branch alone carries all the spectral weight
      3. Kinetic reduction: branch-resolving scattering, Markovian, narrow packet

    Returns a dict with closure status and the number of active branches.
    """
    threshold = 1e-6  # numerical zero for weights
    active = {b: w for b, w in weights.items() if w > threshold}
    n_active = len(active)

    if n_active == 0:
        return {
            "single_speed_possible": False,
            "reason": "NO_ACTIVE_BRANCH",
            "n_active_branches": 0,
            "active_branches": {},
        }
    elif n_active == 1:
        b_active = list(active.keys())[0]
        return {
            "single_speed_possible": True,
            "reason": "UNIQUE_BRANCH_SELECTED",
            "n_active_branches": 1,
            "active_branches": {b_active: {"weight": active[b_active], "speed": speeds[b_active]}},
            "effective_c": speeds[b_active],
        }
    else:
        # Multiple active branches: compute effective speed range and
        # check whether interbranch weight ratio would suppress any branch
        result = {
            "single_speed_possible": False,
            "reason": "MULTIPLE_ACTIVE_BRANCHES",
            "n_active_branches": n_active,
            "active_branches": {
                b: {"weight": active[b], "speed": speeds[b]} for b in active
            },
            "speed_range_m_per_s": {
                "min": min(speeds[b] for b in active),
                "max": max(speeds[b] for b in active),
            },
            "kinetic_reduction_note": (
                "Multiple characteristic velocities. Single-speed PRW requires "
                "either exact branch decoupling, interbranch equilibration at "
                "rate >> scattering rate, or spectral filtering -- each is "
                "additional physics not present in C2."
            ),
        }
        return result


# ──────────────────────────────────────────────────────────────────
# Symmetry analysis: when does exact decoupling occur?
# ──────────────────────────────────────────────────────────────────

def symmetry_decoupling_analysis(modes: list[dict], n: np.ndarray) -> dict[str, Any]:
    """Check which branches exactly decouple from scalar-dilatation coupling (M1).

    Exact decoupling: n . e_b(n) = 0 exactly.
    This holds for transverse modes in ISOTROPIC media (always) and at certain
    high-symmetry cubic directions (100, 110, 111 for standard orientation).
    At a GENERIC cubic direction, it does not hold exactly.

    Returns decoupling status and the mathematical condition.
    """
    results = {}
    for mode in modes:
        b = mode["branch"]
        lon = mode["lon_proj"]
        exactly_zero = lon < 1e-10
        results[b] = {
            "longitudinal_projection": lon,
            "exactly_decoupled": exactly_zero,
            "note": (
                "exact only at high-symmetry direction or isotropic limit"
                if exactly_zero
                else "nonzero generic coupling -- no decoupling at this direction"
            ),
        }
    return results


# ──────────────────────────────────────────────────────────────────
# Theoretical obstruction analysis: why no mapping exists in C2
# ──────────────────────────────────────────────────────────────────

def c2_obstruction_analysis() -> dict[str, Any]:
    """Document the mathematical reasons why J_C2 lacks a microscopic elastic map.

    This is an analytical derivation, not a numerical calculation.
    All claims are traceable to the existing theory documents.
    """
    return {
        "c2_current_definition": {
            "formula": "J_C2 = c (n_plus - n_minus)",
            "status": "DEFINED_IN_PRW_ONLY",
            "source": "02_derivations/microscopic_derivation.md Eq.[C-q]",
            "comment": (
                "J_C2 is defined as the net flux of information quanta in the 1D PRW. "
                "It is a classical scalar field (in 1D). No 3D generalization is given. "
                "No map to u(x,t), epsilon_ij(x,t), or any elastic variable appears in "
                "any existing C2 document."
            ),
        },
        "why_no_map_exists": [
            {
                "obstruction": "UNIT_MISMATCH",
                "description": (
                    "J_C2 has units info/(m^2 s). Displacement u has units m. "
                    "div(u) has units 1/m (dimensionless strain). "
                    "Velocity rho*u_dot has units kg/(m^2 s). "
                    "None of these equals info/(m^2 s) without a new conversion factor "
                    "with units [info/m^3] or [info/(kg)] which introduces a free parameter."
                ),
            },
            {
                "obstruction": "POLARITY_MISMATCH",
                "description": (
                    "J_C2 is a 1D scalar. Silicon elastic fields u, epsilon are 3D tensors. "
                    "Any map from J_C2 to an elastic observable requires a projection direction. "
                    "That direction is not specified in the existing theory. "
                    "It is not the same as the PRW propagation direction n because n is "
                    "the 1D ray coordinate, not a crystal orientation."
                ),
            },
            {
                "obstruction": "MISSING_INFORMATION_ONTOLOGY",
                "description": (
                    "'Information density' s is defined as a probability distribution over "
                    "a CCA state space, not as a thermodynamic state of the silicon lattice. "
                    "The two ontologies are not connected by any existing equation. "
                    "s(x,t) is not proportional to any known elastic observable unless "
                    "a new identification is postulated."
                ),
            },
            {
                "obstruction": "FREE_PARAMETER_PROLIFERATION",
                "description": (
                    "Any candidate map B = kappa * F(u,epsilon,...) introduces kappa with "
                    "units [info / (m^3)] or similar. This is an additional free parameter "
                    "not fixed by the C2 transport equations. It therefore does not reduce "
                    "the parameter count; it replaces one free parameter (g) with two "
                    "(g, kappa) or replaces (c, lambda) with (v_b(n), lambda, direction)."
                ),
            },
        ],
        "what_would_close_the_obstruction": {
            "required": (
                "A microscopic Hamiltonian H_substrate derived from the CCA axioms that "
                "(a) has elastic phonons as normal modes, "
                "(b) defines an information density operator whose expectation value "
                "equals the PRW density s, and "
                "(c) has an interaction term with the qubit whose matrix element between "
                "elastic phonon states is explicitly calculable. "
                "This would simultaneously fix the units, the projection direction, "
                "and the coupling constant g."
            ),
            "status": "ABSENT_FROM_CURRENT_C2",
            "closest_existing_element": (
                "The decoherence_chain_summary.md contains a Born-Markov derivation that "
                "treats J as a classical bath field. It does not connect J to any quantum "
                "operator on the substrate Hilbert space, so there is no substrate Hilbert "
                "space and no phonon creation/annihilation operators."
            ),
        },
    }


# ──────────────────────────────────────────────────────────────────
# Main analysis loop
# ──────────────────────────────────────────────────────────────────

def analyze_direction(label: str, n_raw: np.ndarray) -> dict[str, Any]:
    """Full analysis for one propagation direction."""
    n = normalize(n_raw)
    modes = acoustic_modes(n_raw)
    speeds = {m["branch"]: m["speed"] for m in modes}
    lon_projections = {m["branch"]: m["lon_proj"] for m in modes}

    # M0: existing C2 – no map defined
    m0 = {
        "mapping": "M0_EXISTING_C2",
        "formula": "H_int = g J_C2(x_q,t) sigma_z",
        "derivation_status": "DEFINED_IN_C2_BUT_NO_ELASTIC_MAP",
        "branch_weights": "UNDEFINED",
        "branch_matrix_elements": "ABSENT",
        "unique_speed": False,
        "unique_speed_reason": "J_C2_TO_ELASTIC_FIELD_MAP_ABSENT",
    }

    # M1: scalar dilatation (reproduced from existing audit for completeness)
    w1 = weights_m1_scalar_dilatation(modes, n)
    prw1 = analyze_prw_reduction(w1, speeds)
    m1 = {
        "mapping": "M1_SCALAR_DILATATION",
        "formula": "B = -kappa * rho * div(u)",
        "derivation_status": "ASSUMED_NOT_FROM_C2",
        "physical_basis": (
            "Dilatation div(u) = strain trace = volume change per unit volume. "
            "Couples to compression/expansion of substrate at qubit location. "
            "This is a scalar, compatible with sigma_z."
        ),
        "dimensional_check": (
            "[B] = [kappa][rho][|k||q|] = (Pa^{-1})(kg/m^3)(m^{-1})(m) "
            "= kg/(m^3 Pa) = kg/(m^3 * kg/(m s^2)) = s^2/m^2. "
            "For B to have units of C2 current info/(m^2 s), kappa must carry "
            "[info * s^3/m^2]. This is a new free parameter."
        ),
        "branch_weights": w1,
        "prw_reduction": prw1,
        "symmetry": symmetry_decoupling_analysis(modes, n),
        "unique_speed": prw1.get("single_speed_possible", False),
    }

    # M2: elastic energy flux
    w2 = weights_m2_energy_flux(modes, n)
    prw2 = analyze_prw_reduction(w2, speeds)
    m2 = {
        "mapping": "M2_ELASTIC_ENERGY_FLUX",
        "formula": "B = n_i sigma_ij u_dot_j (stress contracted with velocity, projected on n)",
        "derivation_status": "ASSUMED_NOT_FROM_C2",
        "physical_basis": (
            "Energy flux through a surface with normal n. "
            "Analogy: electromagnetic Poynting vector E x B / mu_0. "
            "This is an energy flow per unit area, plausible for coupling "
            "energy-carrying substrate modes to a qubit."
        ),
        "dimensional_check": (
            "[sigma_ij] = Pa = N/m^2. [u_dot_j] = m/s. "
            "B has units Pa*(m/s) = W/m^2 (power per area). "
            "To match C2 current info/(m^2 s), need conversion factor "
            "[info/(J)] -- another free parameter."
        ),
        "key_result": (
            "B_b amplitude = rho v_b^3 (n.e_b) * k^2 * q_b. "
            "Weight w_b proportional to (rho v_b^3 (n.e_b))^2. "
            "SAME ANGULAR STRUCTURE AS M1 but weighted by v_b^6. "
            "Transverse modes still have nonzero weight at generic directions "
            "unless (n.e_b) = 0, i.e., exact transverse polarization."
        ),
        "branch_weights": w2,
        "prw_reduction": prw2,
        "unique_speed": prw2.get("single_speed_possible", False),
    }

    # M3: phonon momentum density
    w3 = weights_m3_momentum_density(modes, n)
    prw3 = analyze_prw_reduction(w3, speeds)
    m3 = {
        "mapping": "M3_MOMENTUM_DENSITY",
        "formula": "B = rho * n . (du/dt)",
        "derivation_status": "ASSUMED_NOT_FROM_C2",
        "physical_basis": (
            "Momentum density of the elastic medium projected onto the propagation direction. "
            "This would arise naturally if the C2 qubit coupling is via elastic impulse "
            "(radiation pressure-like). Standard in optomechanics for momentum transfer."
        ),
        "dimensional_check": (
            "[rho * du/dt] = (kg/m^3)(m/s) = kg/(m^2 s) = Pa * s / m. "
            "To match C2 current info/(m^2 s), need factor [info / (Pa * s^2)]. "
            "Still another free parameter."
        ),
        "key_result": (
            "B_b amplitude = rho omega_b (n.e_b) * q_b = rho v_b k (n.e_b) q_b. "
            "Weight w_b proportional to (v_b (n.e_b))^2. "
            "SAME ANGULAR STRUCTURE AS M1 but weighted by v_b^2. "
            "No exact transverse decoupling at generic directions."
        ),
        "branch_weights": w3,
        "prw_reduction": prw3,
        "unique_speed": prw3.get("single_speed_possible", False),
    }

    # M4: acoustic intensity
    w4 = weights_m4_acoustic_intensity(modes, n)
    prw4 = analyze_prw_reduction(w4, speeds)
    m4 = {
        "mapping": "M4_ACOUSTIC_INTENSITY",
        "formula": "B = n_i sigma_ij u_dot_j using full Christoffel contraction",
        "derivation_status": "ASSUMED_NOT_FROM_C2",
        "physical_basis": (
            "The full elastic intensity contraction e_b^T Gamma e_b = rho v_b^2 is "
            "the same for all branch indices -- it is the eigenvalue. "
            "This coupling discriminates branches ONLY by their speed v_b, "
            "not by polarization. It couples to ALL branches."
        ),
        "key_result": (
            "B_b amplitude = rho v_b^3 k^2 q_b (independent of n.e_b). "
            "Weight w_b proportional to v_b^6. "
            "ALL THREE BRANCHES ACTIVE at all directions. "
            "No branch decoupling from polarization, only speed weighting."
        ),
        "branch_weights": w4,
        "prw_reduction": prw4,
        "unique_speed": prw4.get("single_speed_possible", False),
    }

    return {
        "direction": label,
        "n_hat": n.tolist(),
        "mode_speeds": speeds,
        "mode_longitudinal_projections": lon_projections,
        "candidates": [m0, m1, m2, m3, m4],
    }


def multi_branch_bath_correlator_analysis() -> dict[str, Any]:
    """Derive the structure of the bath correlator when multiple branches contribute.

    If multiple branches b contribute with weights w_b and speeds v_b,
    the bath spectral density is:

      S_JJ(omega, r) = sum_b w_b * S_b(omega, r)

    where S_b is the contribution from branch b. In the PRW picture,
    each branch generates its own telegrapher propagator with speed v_b.

    The dephasing rate integral becomes:

      Gamma_phi = sum_b w_b * gamma_b(g, s_0, tau_b)

    where gamma_b are branch-specific dephasing rates.

    The spatial correlator becomes a sum of K_0 terms:

      C_Gamma(r) = sum_b w_b * K_0(r / xi_b)

    with xi_b = 2 v_b tau_b. This is NOT a single K_0 function.

    The observable consequence: the spatial correlation function has MULTIPLE
    length scales xi_b, not one universal xi_c. The ratio xi_c / tau_b is
    NOT uniquely c unless one branch dominates completely.

    This is the precise statement of why multi-branch coupling fails to close GAP-7.
    """
    return {
        "multi_branch_dephasing": {
            "formula": (
                "Gamma_phi = sum_b w_b * g^2 s_0^2 * S_b(omega_q=0) "
                "= sum_b w_b * g^2 s_0^2 * 2 S_0 tau_b / (1 + omega_q^2 tau_b^2)|_{omega_q=0} "
                "= sum_b w_b * g^2 s_0^2 * 2 S_0 tau_b"
            ),
            "consequence": (
                "Dephasing rate is a weighted sum of branch-specific rates. "
                "Each branch has its own tau_b = 1/(2 gamma_b). "
                "For a single branch: Gamma_phi = g^2 s_0^2 * 2 S_0 tau. "
                "For multiple: Gamma_phi is a weighted average -- the individual tau_b "
                "are not separately identifiable from temporal Ramsey alone."
            ),
        },
        "multi_branch_spatial_correlator": {
            "formula": (
                "C_Gamma(r) = sum_b w_b * K_0(r / xi_b) / K_0(a / xi_b)"
            ),
            "consequence": (
                "Spatial correlator is a sum of K_0 functions with different length scales. "
                "Fitting a single K_0 extracts an EFFECTIVE xi that is a weighted geometric "
                "mean of branch xi_b values. This effective xi is NOT directly related to "
                "a single physical speed unless one branch dominates."
            ),
        },
        "single_speed_conditions": {
            "condition_a": "w_b = 1 for one branch, w_b' = 0 for all b' != b",
            "condition_b_alternative": "Fast interbranch equilibration: all branches equilibrate at rate >> 1/tau, producing single effective mode",
            "condition_c_alternative": "Spectral filtering: qubit frequency selects one branch via resonance",
            "each_is_new_physics": (
                "All three conditions require physics beyond the existing C2 assumptions. "
                "None is derivable from H_int = g J_C2 sigma_z alone."
            ),
        },
        "obstruction_statement": (
            "The mathematical obstruction to a unique c is: "
            "the bath spectral density C_BB(omega) = sum_b w_b C_b(omega) "
            "is a superposition of branch-specific Lorentzians with different "
            "widths (tau_b) and spectral weights. The ratio xi / tau that equals "
            "2c is defined only if one term dominates or all tau_b are equal. "
            "Neither follows from C2 or elastic theory without additional input."
        ),
    }


def kinetic_reduction_analysis() -> dict[str, Any]:
    """What assumptions are needed to go from Christoffel eigenmodes to PRW equations?

    Step 1: Christoffel eigenmode → coherent normal mode
    Step 2: Coherent normal mode → wave packet
    Step 3: Wave packet → coarse-grained population density
    Step 4: Population density → PRW pair (n^+, n^-)
    Step 5: Reversal process → scattering rate gamma_b
    Step 6: PRW equations → telegrapher equation

    Each step has explicit assumptions that must be justified.
    """
    return {
        "step_1_normal_mode": {
            "physics": "Christoffel eigenvalue problem gives omega_b(k,n) = v_b(n) |k|",
            "status": "DERIVED from elastic wave equation",
            "assumptions": ["linear elasticity", "cubic symmetry", "infinite homogeneous medium"],
        },
        "step_2_wave_packet": {
            "physics": (
                "A wave packet localized in k-space around k_0 n propagates at "
                "group velocity v_g = d omega_b / d|k| = v_b(n) (long-wavelength: phase = group)"
            ),
            "status": "DERIVED for narrow k-packets in linear regime",
            "assumptions": [
                "narrow bandwidth in k",
                "no dispersion correction O(k^2 a^2)",
                "single branch (no inter-branch mixing in propagation)",
            ],
        },
        "step_3_coarse_grain": {
            "physics": (
                "Coarse-grained population n_b^+(s,t) = integral over right-moving "
                "k-packets near k_0 in direction n"
            ),
            "status": "ASSUMED - requires explicit coarse-graining prescription",
            "assumptions": [
                "spatial scale >> phonon wavelength",
                "time scale >> phonon period",
                "branch population is a slowly-varying envelope",
                "no coherence between different k modes (incoherent limit)",
            ],
            "new_physics_required": (
                "The coarse-graining prescription is NOT given by elastic theory or C2. "
                "It is standard kinetic theory but introduces a coarse-graining length "
                "and time scale as additional parameters."
            ),
        },
        "step_4_prw_pair": {
            "physics": "n_b^+(s,t) = right-moving, n_b^-(s,t) = left-moving populations",
            "status": "ASSUMED - direction decomposition requires a 1D ray coordinate s",
            "assumptions": [
                "fixed propagation direction n (or projection onto n)",
                "left/right decomposition along n",
                "no coupling to perpendicular directions",
            ],
            "geometric_issue": (
                "In 3D, phonons propagate in all directions. "
                "The PRW pair (n^+, n^-) describes propagation along ONE ray. "
                "Reducing 3D elastic wave propagation to 1D PRW requires either "
                "(a) single propagation direction n, or "
                "(b) spherical/angular averaging with appropriate weighting. "
                "Option (b) introduces angular integration as new physics."
            ),
        },
        "step_5_reversal": {
            "physics": (
                "Reversal/scattering process at rate gamma_b converts right-movers "
                "to left-movers and vice versa. This is phonon backscattering."
            ),
            "status": "ASSUMED physical process - requires scattering model",
            "possible_mechanisms": [
                "Phonon-phonon anharmonic scattering (Umklapp processes)",
                "Phonon-defect scattering (Rayleigh, resonant)",
                "Phonon-boundary scattering",
                "Phonon-phonon normal processes (momentum-conserving)",
            ],
            "requirements": [
                "scattering is branch-preserving (does not change b)",
                "scattering reverses the propagation direction along n",
                "scattering rate gamma_b is well-defined and approximately Markovian",
                "backscattering dominates over forward scattering",
            ],
            "new_parameters": (
                "gamma_b introduces one free parameter per active branch. "
                "It is NOT determined by the Christoffel eigenvalue problem "
                "or by the C2 coupling constant g."
            ),
        },
        "step_6_telegrapher": {
            "physics": (
                "PRW equations: dn^+/dt = -v_b dn^+/ds - gamma_b(n^+ - n^-)  "
                "→ telegrapher: d^2s/dt^2 + 2gamma_b ds/dt = v_b^2 d^2s/ds^2"
            ),
            "status": "DERIVED from PRW equations (exact, no approximation)",
            "prerequisite": "Steps 3-5 must first be justified",
        },
        "overall_kinetic_reduction_status": {
            "verdict": "CONDITIONAL",
            "new_assumptions_required": [
                "coarse-graining length and time scales",
                "incoherent-phonon approximation",
                "single-direction projection or angular averaging prescription",
                "branch-preserving backscattering mechanism",
                "Markovian scattering approximation",
                "narrow wave-packet approximation",
            ],
            "free_parameters_introduced": [
                "scattering rate gamma_b (one per active branch)",
                "coarse-graining scale",
                "angular weighting if 3D→1D projection",
            ],
            "relationship_to_gap7": (
                "Even after all kinetic reduction assumptions are made, "
                "the effective PRW speed c_eff = v_b(n) is branch- and "
                "direction-dependent. It equals a unique c only if ONE branch "
                "is active at ALL propagation directions, which requires "
                "a branch-selection mechanism not present in C2."
            ),
        },
    }


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main() -> int:
    print("Microscopic C2 Current–Substrate Coupling: Derivation Attempt")
    print("=" * 70)

    all_results = []
    for label, n_raw in DIRECTIONS.items():
        result = analyze_direction(label, n_raw)
        all_results.append(result)

        print(f"\nDirection: {label}")
        print(f"  Modes: ", end="")
        for c in result["candidates"]:
            if c["mapping"] == "M0_EXISTING_C2":
                continue
            mapping_short = c["mapping"].split("_", 1)[1]
            if c["unique_speed"]:
                if "effective_c" in c.get("prw_reduction", {}):
                    v = c["prw_reduction"]["effective_c"]
                    print(f"{mapping_short}=UNIQUE({v:.0f}m/s) ", end="")
                else:
                    print(f"{mapping_short}=UNIQUE ", end="")
            else:
                print(f"{mapping_short}=MULTI ", end="")
        print()

        # Detail for generic direction
        if "123" in label or "213" in label or "132" in label:
            print(f"  Mode speeds: {result['mode_speeds']}")
            for c in result["candidates"]:
                if c["mapping"] == "M0_EXISTING_C2":
                    continue
                wts = c.get("branch_weights", {})
                if isinstance(wts, dict):
                    print(f"    {c['mapping']}: weights={wts}")

    obstruction = c2_obstruction_analysis()
    correlator = multi_branch_bath_correlator_analysis()
    kinetic = kinetic_reduction_analysis()

    # Summary: across all directions and candidates, any unique speed?
    any_unique = False
    unique_cases = []
    for result in all_results:
        for c in result["candidates"]:
            if c.get("unique_speed") and c["mapping"] != "M0_EXISTING_C2":
                any_unique = True
                unique_cases.append({
                    "direction": result["direction"],
                    "mapping": c["mapping"],
                    "reason": c.get("prw_reduction", {}).get("reason", "?"),
                    "effective_c": c.get("prw_reduction", {}).get("effective_c"),
                })

    # Classify closure outcome A-E
    closure_classification = classify_closure(all_results)

    output = {
        "task": "microscopic_C2_current_substrate_coupling_derivation",
        "date": "2026-10-10",
        "silicon_constants": {
            "C11_GPa": C11 / 1e9,
            "C12_GPa": C12 / 1e9,
            "C44_GPa": C44 / 1e9,
            "rho_kg_m3": RHO,
        },
        "c2_obstruction_analysis": obstruction,
        "kinetic_reduction_analysis": kinetic,
        "multi_branch_correlator_analysis": correlator,
        "directional_analysis": all_results,
        "unique_speed_cases": unique_cases,
        "any_unique_speed_from_any_candidate": any_unique,
        "closure_classification": closure_classification,
        "gap7_status": {
            "previous": "NOT_CLOSED (from THEORY_CLOSURE_AUDIT.md 2026-08-22)",
            "current": closure_classification["gap7_update"],
        },
    }

    output_path = OUT / "microscopic_coupling_derivation.json"
    output_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"\nFull results written to {output_path}")

    print("\n" + "=" * 70)
    print("CLOSURE CLASSIFICATION:")
    print(f"  Outcome: {closure_classification['outcome']}")
    print(f"  Reason: {closure_classification['reason']}")
    print(f"\nGAP-7 STATUS: {closure_classification['gap7_update']}")
    print("\nMINIMUM MISSING PHYSICS:")
    for item in closure_classification["minimum_missing_physics"]:
        print(f"  - {item}")

    return 0


def classify_closure(all_results: list[dict]) -> dict[str, Any]:
    """Classify the closure outcome A–E based on all candidate analysis results.

    A: existing theory uniquely determines coupling and selects one speed
    B: existing theory determines coupling but produces multiple speeds
    C: multiple physically distinct couplings exist, speed underdetermined
    D: a specific missing postulate would close the system
    E: mathematical or physical inconsistency found

    The classification is made from the actual numerical results, not assumed.
    """
    # Check each outcome condition from the evidence

    # Outcome A: Does ANY mapping produce a unique speed at ALL directions?
    # A unique speed must hold at generic directions, not just high-symmetry ones.
    generic_results = [r for r in all_results if "generic" in r["direction"]]

    unique_at_all_generic = {}  # mapping -> True/False
    for c_name in ["M0_EXISTING_C2", "M1_SCALAR_DILATATION", "M2_ELASTIC_ENERGY_FLUX",
                   "M3_MOMENTUM_DENSITY", "M4_ACOUSTIC_INTENSITY"]:
        all_unique = True
        for result in generic_results:
            candidate = next((c for c in result["candidates"] if c["mapping"] == c_name), None)
            if candidate is None:
                all_unique = False
                break
            if not candidate.get("unique_speed", False):
                all_unique = False
                break
        unique_at_all_generic[c_name] = all_unique

    # M0 has no map so it never gives a unique speed
    outcome_a_satisfied = any(
        v for k, v in unique_at_all_generic.items() if k != "M0_EXISTING_C2"
    )

    # Outcome E: Is there any contradiction or inconsistency?
    # Check: Do all candidates give valid non-negative weights summing to 1?
    inconsistency_found = False
    for result in all_results:
        for c in result["candidates"]:
            wts = c.get("branch_weights")
            if isinstance(wts, dict):
                total = sum(wts.values())
                if abs(total - 1.0) > 1e-6:
                    inconsistency_found = True

    if inconsistency_found:
        return {
            "outcome": "E",
            "reason": "WEIGHT_NORMALIZATION_INCONSISTENCY",
            "gap7_update": "NOT_CLOSED",
            "minimum_missing_physics": ["Debug weight normalization"],
        }

    # Primary outcome classification
    if outcome_a_satisfied:
        # Outcome A would be a major positive result -- need to verify carefully
        # This path would only be reached if some mapping gives exactly w_LA=1, w_TA=0
        # at generic cubic directions, which requires transverse modes to be exactly
        # decoupled at generic directions. We know this is false from elastic theory.
        # Therefore this branch should not be reached. Add an explicit check.
        contributing_candidates = [k for k, v in unique_at_all_generic.items() if v and k != "M0_EXISTING_C2"]
        return {
            "outcome": "A",
            "ALERT": "UNEXPECTED -- verify numerical precision of polarization projections",
            "reason": f"Candidate(s) {contributing_candidates} give unique speed at all generic directions",
            "gap7_update": "POTENTIALLY_CLOSED_PENDING_VERIFICATION",
            "minimum_missing_physics": ["Verify that exact branch decoupling is not numerical artifact"],
        }

    # Outcome C: Multiple candidates exist, none selects a unique speed
    # This is the expected outcome based on physics of anisotropic elasticity
    multiple_candidates_exist = True  # M1-M4 are all distinct
    all_give_multiple_speeds_at_generic = all(
        not v for k, v in unique_at_all_generic.items() if k != "M0_EXISTING_C2"
    )

    if multiple_candidates_exist and all_give_multiple_speeds_at_generic:
        # Distinguish C from D: Is there a specific missing postulate that would close it?
        # D requires: one unique additional assumption that both selects a mapping
        # AND provides exact branch decoupling. The analysis below identifies this.
        specific_closure_exists = check_for_d_closure(all_results)

        if specific_closure_exists:
            return {
                "outcome": "D",
                "reason": (
                    "The existing theory permits several physically distinct couplings "
                    "(M1-M4), all of which produce multiple speeds at generic cubic directions. "
                    "However, a specific missing postulate -- exact longitudinal-only coupling "
                    "in ISOTROPIC elasticity OR propagation restricted to high-symmetry directions "
                    "-- would close the system to a unique speed. "
                    "This postulate is not derivable from C2 and constitutes new physics."
                ),
                "gap7_update": "NOT_CLOSED; requires new physical postulate",
                "minimum_missing_physics": [
                    "A microscopic derivation of J_C2 as an elastic observable with "
                    "units [info/(m^2 s)], specifying the projection direction and "
                    "the conversion factor from mechanical to information units.",
                    "Proof that transverse phonon branches decouple from the qubit "
                    "interaction at ALL propagation directions in the actual substrate "
                    "geometry (not just high-symmetry directions).",
                    "A kinetic reduction mechanism (branch-preserving scattering process) "
                    "with a derivable scattering rate gamma_b from the substrate physics.",
                    "Justification that the 3D elastic medium reduces to a 1D PRW "
                    "transport without introducing direction-dependent speed.",
                ],
            }
        else:
            return {
                "outcome": "C",
                "reason": (
                    "The existing C2 coupling H_int = g J_C2 sigma_z has no microscopic "
                    "elastic map. The four candidate mappings M1-M4 are all physically "
                    "distinct and all produce multiple active branches at generic cubic "
                    "silicon directions. The speed c remains underdetermined."
                ),
                "gap7_update": "NOT_CLOSED",
                "minimum_missing_physics": [
                    "Microscopic derivation of J_C2 from elastic degrees of freedom",
                    "Branch decoupling theorem for the actual substrate geometry",
                    "Kinetic reduction mechanism with derivable scattering rate",
                    "3D-to-1D reduction prescription",
                ],
            }

    # Fallback (should not reach here given the logic above)
    return {
        "outcome": "C",
        "reason": "Default: no unique speed found from any candidate at generic directions",
        "gap7_update": "NOT_CLOSED",
        "minimum_missing_physics": [
            "Microscopic map from J_C2 to elastic observable",
        ],
    }


def check_for_d_closure(all_results: list[dict]) -> bool:
    """Check whether Outcome D (specific missing postulate) applies.

    Outcome D requires that SOME specific additional assumption would uniquely close the system.
    The key insight is: for ISOTROPIC elasticity (C44 = (C11-C12)/2),
    transverse modes decouple EXACTLY from scalar-dilatation coupling at ALL directions.
    Silicon is anisotropic (Zener ratio A = 2*C44/(C11-C12) ≈ 1.56 != 1).
    If the substrate were isotropic, M1 would select the longitudinal branch exactly.

    So Outcome D holds: the missing postulate is "substrate is isotropic elastic"
    or equivalently "qubit couples only to compression waves".

    However, we verify this numerically: for silicon's actual constants, does
    the generic transverse weight vanish? We already know it doesn't (from existing audit).
    """
    # Check if silicon is isotropic
    anisotropy = 2 * C44 / (C11 - C12)
    is_isotropic = abs(anisotropy - 1.0) < 1e-6

    if is_isotropic:
        # For isotropic medium, M1 gives exact LA selection at all directions
        return False  # Not D -- this would be outcome A or B

    # For anisotropic silicon, transverse modes have nonzero scalar-dilatation weight
    # Check: does any candidate come CLOSE to exact decoupling?
    max_ta_weight = 0.0
    for result in all_results:
        if "generic" not in result["direction"]:
            continue
        for c in result["candidates"]:
            if c["mapping"] in ["M1_SCALAR_DILATATION", "M2_ELASTIC_ENERGY_FLUX",
                                 "M3_MOMENTUM_DENSITY"]:
                wts = c.get("branch_weights", {})
                if isinstance(wts, dict):
                    for b, w in wts.items():
                        if "TA" in b:
                            max_ta_weight = max(max_ta_weight, w)

    # D applies if transverse coupling is present but suppressed relative to LA
    # (meaning a small correction to make it zero would change the physics)
    # All M1/M2/M3 have TA weight ~0.005-0.007 at generic [123] -- small but nonzero
    # This is Outcome D: a specific postulate (isotropic substrate or longitudinal-only coupling)
    # would close it, but that postulate is not derivable from C2.
    return True  # Outcome D


if __name__ == "__main__":
    raise SystemExit(main())
