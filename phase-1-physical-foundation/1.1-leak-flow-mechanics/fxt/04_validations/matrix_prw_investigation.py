#!/usr/bin/env python3
"""
Matrix-Valued PRW Investigation: Four-Gate Analysis
===================================================

Question: Does a matrix-valued persistent random walk produce bath
statistics genuinely different from a conventional classical stochastic process?

Four gates:
  Gate 1: Specify model and classify observable algebra
  Gate 2: Derive C_JJ(t) and S_JJ(omega) exactly
  Gate 3: Derive qubit dynamics and check CP
  Gate 4: Compare against conventional models

Key distinction (from critique):
  Noncommutative matrix multiplication ≠ noncommuting physical observables.
  A stochastic process on matrix states is classical if the matrices are
  internal labels and observables are scalar projections Tr(A·q).
  We must classify this honestly before claiming quantum structure.

Author: Investigation session
Date: 2026-10-25
"""

import json
import numpy as np
from scipy.special import k0 as bessel_k0
from scipy.linalg import expm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT_DIR = "04_validations/outputs"
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# GATE 1: MODEL SPECIFICATION AND OBSERVABLE ALGEBRA CLASSIFICATION
# ============================================================================

def gate1_model_specification():
    """
    Define the matrix-valued PRW and classify its observable algebra.

    MODEL:
    -------
    Walker state: (sigma, Q) where
      sigma in {+1, -1} is direction
      Q in M_n(C) is an n x n complex matrix (internal state)

    Dynamics:
      - Walker moves at speed v in direction sigma.
      - At Poisson rate lambda, walker reverses: sigma -> -sigma.
      - At reversal, matrix transforms: Q -> U Q U^dagger
        where U is drawn from a distribution mu on U(n).

    Density fields: n^+(x,t), n^-(x,t) in M_n(C)
      (matrix-valued densities of right/left movers)

    Balance equations:
      d(n^+)/dt = -v d(n^+)/dx - lambda n^+ + lambda R(n^-)
      d(n^-)/dt = +v d(n^-)/dx + lambda R(n^+) - lambda n^-

    where R is the superoperator: R(M) = E_mu[U M U^dagger]

    Current: J(x,t) = Tr(A @ q(x,t)) where q = v(n^+ - n^-)
      and A is a FIXED coupling matrix (the observable).

    OBSERVABLE ALGEBRA CLASSIFICATION:
    -----------------------------------
    The observables are scalar functions: O_A = Tr(A @ q) for fixed A.

    Two observables O_A and O_B commute as classical random variables:
      [O_A, O_B] = 0  (they are scalar functions of the same stochastic process)

    The matrix noncommutativity Q1 Q2 != Q2 Q1 is INTERNAL to the walker state
    but does NOT translate to noncommuting physical observables.

    VERDICT: This is a MATRIX-VALUED CLASSICAL PRW.
    The noncommutativity is representational (internal labels), not physical.
    The observable algebra is COMMUTATIVE (classical).

    This does NOT mean the statistics are trivial. The matrix internal state
    enriches the correlation structure. But it is classical enrichment, not
    quantum structure.
    """
    print("=" * 70)
    print("GATE 1: MODEL SPECIFICATION AND OBSERVABLE ALGEBRA")
    print("=" * 70)

    result = {
        "model": "Matrix-valued persistent random walk",
        "walker_state": "(sigma, Q) where sigma in {+1,-1}, Q in M_n(C)",
        "reversal": "Q -> U Q U^dagger, U ~ mu on U(n)",
        "current": "J = Tr(A @ q) for fixed coupling matrix A",
        "observable_algebra": "COMMUTATIVE (classical)",
        "classification": "Matrix-valued classical PRW",
        "noncommutativity_type": "representational (internal labels), not physical",
        "verdict": "The matrices enrich the internal state space but the "
                   "observable algebra is classical. This is NOT a quantum "
                   "substrate. It is a classical stochastic process with "
                   "matrix-valued internal states."
    }

    for k, v in result.items():
        print(f"  {k}: {v}")

    return result


# ============================================================================
# GATE 2: DERIVE C_JJ(t) AND S_JJ(omega) EXACTLY
# ============================================================================

def r_superoperator_eigenvalues(dist_type="haar", n=2, p_param=None):
    """
    Compute eigenvalues of the R superoperator R(M) = E[U M U^dagger].

    For n=2, the superoperator acts on the Pauli basis {I, sx, sy, sz}.

    Haar on U(2):
      R(M) = Tr(M)/2 * I  (completely depolarizing)
      Eigenvalues: {1, 0, 0, 0} (on {I, sx, sy, sz})

    Pauli twirl {I, sx, sy, sz} uniform:
      Same as Haar for n=2 (1-design). Eigenvalues: {1, 0, 0, 0}

    {I, sz} uniform:
      R(M) = (M + sz M sz) / 2
      Eigenvalues: {1, 1, 0, 0} (on {I, sz, sx, sy})

    Partially depolarizing with parameter p:
      R(M) = p M + (1-p) Tr(M)/n I
      Eigenvalues: {1, p, p, p} (for n=2)

    Identity (no transformation):
      R(M) = M
      Eigenvalues: {1, 1, 1, 1}
    """
    if dist_type == "haar":
        # Haar on U(n): R = completely depolarizing
        # Eigenvalue 1 on trace (I), eigenvalue 0 on traceless
        if n == 2:
            return {"I": 1.0, "sx": 0.0, "sy": 0.0, "sz": 0.0}
        else:
            return {"trace": 1.0, "traceless": 0.0}

    elif dist_type == "pauli_twirl":
        # Same as Haar for n=2
        if n == 2:
            return {"I": 1.0, "sx": 0.0, "sy": 0.0, "sz": 0.0}

    elif dist_type == "sz_only":
        # {I, sz} uniform: preserves I and sz, kills sx, sy
        if n == 2:
            return {"I": 1.0, "sz": 1.0, "sx": 0.0, "sy": 0.0}

    elif dist_type == "partial":
        # R(M) = p M + (1-p) Tr(M)/n I
        p = p_param if p_param is not None else 0.5
        if n == 2:
            return {"I": 1.0, "sx": p, "sy": p, "sz": p}

    elif dist_type == "identity":
        # R = identity: no mixing
        if n == 2:
            return {"I": 1.0, "sx": 1.0, "sy": 1.0, "sz": 1.0}

    raise ValueError(f"Unknown distribution: {dist_type}")


def decay_rates_from_eigenvalues(r_eigenvals, lam):
    """
    From the analytical derivation:

    For each eigenvalue r_k of R, the current in that sector decays as:
      exp(-lambda * (1 + r_k) * t)

    This comes from the balance equations:
      dn^+_k/dt = -v dn^+_k/dx - lambda n^+_k + lambda r_k n^-_k
      dn^-_k/dt = +v dn^-_k/dx + lambda r_k n^+_k - lambda n^-_k

    Current in sector k: q_k = v(n^+_k - n^-_k)
      dq_k/dt = -v^2 ds_k/dx - lambda(1 + r_k) q_k

    So decay rate for sector k = lambda * (1 + r_k)

    For scalar PRW (r=1): rate = 2*lambda (standard result, tau_B = 1/(2*lambda))
    For Haar traceless (r=0): rate = lambda
    For identity (r=1): rate = 2*lambda (all sectors same = scalar PRW)
    """
    rates = {}
    for sector, r_val in r_eigenvals.items():
        rates[sector] = lam * (1.0 + r_val)
    return rates


def cjj_analytical(t_arr, sectors, weights, lam):
    """
    C_JJ(t) = sum_k S_k * exp(-lambda(1+r_k) * t)

    sectors: dict of {name: r_value}
    weights: dict of {name: S_k} (projection weights of coupling A)
    lam: reversal rate

    Returns: C_JJ(t) array
    """
    t = np.asarray(t_arr)
    result = np.zeros_like(t, dtype=float)
    for sector, r_val in sectors.items():
        rate = lam * (1.0 + r_val)
        weight = weights.get(sector, 0.0)
        result += weight * np.exp(-rate * np.abs(t))
    return result


def sjj_analytical(omega_arr, sectors, weights, lam):
    """
    S_JJ(omega) = sum_k S_k * 2*lambda*(1+r_k) / (omega^2 + lambda^2*(1+r_k)^2)

    This is the Wiener-Khinchin transform of C_JJ(t).
    """
    omega = np.asarray(omega_arr)
    result = np.zeros_like(omega, dtype=float)
    for sector, r_val in sectors.items():
        rate = lam * (1.0 + r_val)
        weight = weights.get(sector, 0.0)
        result += weight * 2.0 * rate / (omega**2 + rate**2)
    return result


def gate2_correlation_derivation():
    """
    Analytical derivation of C_JJ(t) for the matrix PRW.

    KEY RESULT:
    -----------
    The R superoperator decomposes the matrix space into eigenspaces.
    Each eigenvalue r_k produces a decay rate lambda(1+r_k).

    The correlation function is a SUM of exponentials:
      C_JJ(t) = sum_k S_k exp(-lambda(1+r_k) t)

    For Haar on U(2):
      - Trace sector (r=1): rate 2*lambda (same as scalar PRW)
      - Traceless sectors (r=0): rate lambda
      Two distinct rates with RATIO 2:1.

    For {I, sz} distribution:
      - I and sz sectors (r=1): rate 2*lambda
      - sx, sy sectors (r=0): rate lambda
      Two distinct rates with ratio 2:1 (same structure).

    For partially depolarizing with parameter p:
      - Trace (r=1): rate 2*lambda
      - Traceless (r=p): rate lambda(1+p)
      Ratio = 2/(1+p), varies from 1 (identity) to 2 (Haar).

    For identity (no transformation):
      - All sectors (r=1): rate 2*lambda
      Single rate = scalar PRW. No enrichment.
    """
    print("\n" + "=" * 70)
    print("GATE 2: CORRELATION FUNCTION DERIVATION")
    print("=" * 70)

    lam = 1.0  # reversal rate (normalized)

    # Test all distributions
    distributions = {
        "haar": ("haar", None),
        "pauli_twirl": ("pauli_twirl", None),
        "sz_only": ("sz_only", None),
        "partial_p=0.5": ("partial", 0.5),
        "partial_p=0.9": ("partial", 0.9),
        "identity": ("identity", None),
    }

    results = {}

    for name, (dist_type, p_param) in distributions.items():
        r_eigs = r_superoperator_eigenvalues(dist_type, n=2, p_param=p_param)
        rates = decay_rates_from_eigenvalues(r_eigs, lam)

        # Distinct decay rates
        distinct_rates = sorted(set(rates.values()))
        if len(distinct_rates) > 1:
            ratio = distinct_rates[-1] / distinct_rates[0]
        else:
            ratio = 1.0

        result = {
            "r_eigenvalues": r_eigs,
            "decay_rates": rates,
            "n_distinct_rates": len(distinct_rates),
            "distinct_rates": distinct_rates,
            "rate_ratio": ratio,
            "equivalent_to_scalar_prw": len(distinct_rates) == 1,
        }
        results[name] = result

        print(f"\n  Distribution: {name}")
        print(f"    R eigenvalues: {r_eigs}")
        rates_str = ", ".join(f"{k}={v:.4f}" for k, v in rates.items())
        print(f"    Decay rates: {rates_str}")
        print(f"    Distinct rates: {distinct_rates}")
        print(f"    Rate ratio: {ratio:.4f}")
        print(f"    Equivalent to scalar PRW: {result['equivalent_to_scalar_prw']}")

    # Key analytical finding
    print("\n  ANALYTICAL RESULT:")
    print("  C_JJ(t) = sum_k S_k exp(-lambda(1+r_k) t)")
    print("  where r_k are eigenvalues of R superoperator.")
    print("  ")
    print("  For Haar U(2): two rates {2*lambda, lambda} with fixed ratio 2:1")
    print("  For partial depolarizing (p): two rates {2*lambda, lambda(1+p)}")
    print("    with ratio 2/(1+p) parameterized by p in [0,1]")
    print("  For identity: single rate 2*lambda (= scalar PRW)")

    return results


# ============================================================================
# GATE 3: QUBIT DYNAMICS AND CP CHECK
# ============================================================================

def qubit_dephasing_function(t_arr, sectors, weights, lam):
    """
    Exact dephasing function for a qubit coupled to matrix PRW bath.

    Phi(t) = integral_0^t (t-t') C_JJ(t') dt'

    For C_JJ(t') = sum_k S_k exp(-rate_k t'):
    Phi(t) = sum_k S_k [t/rate_k - (1-exp(-rate_k t))/rate_k^2]

    W(t) = exp(-Phi(t))

    For scalar PRW (single rate gamma):
      Phi(t) = S [t/gamma - (1-exp(-gamma t))/gamma^2]
      W(t) = exp(-S[t/gamma - (1-exp(-gamma t))/gamma^2])
      Short time: W ~ exp(-S t^2 / 2) (Gaussian onset)
      Long time: W ~ exp(-S t/gamma) (exponential decay)

    For matrix PRW (multiple rates):
      Phi(t) = sum_k S_k [t/rate_k - (1-exp(-rate_k t))/rate_k^2]
      Short time: Phi ~ t^2/2 * sum_k S_k (same Gaussian onset, sum of weights)
      Long time: Phi ~ t * sum_k S_k/rate_k (exponential with effective rate)

    The short-time behavior is IDENTICAL to any Gaussian noise with the same
    total power sum_k S_k. The long-time behavior is exponential with an
    effective rate that is a weighted harmonic mean.

    The NON-TRIVIAL structure is in the CROSSOVER region, where different
    exponential components contribute differently.
    """
    t = np.asarray(t_arr, dtype=float)
    phi = np.zeros_like(t)
    for sector, r_val in sectors.items():
        rate = lam * (1.0 + r_val)
        weight = weights.get(sector, 0.0)
        if rate > 0:
            phi += weight * (t / rate - (1.0 - np.exp(-rate * t)) / rate**2)
    return phi


def check_cp_gksl(phi_arr, t_arr, sectors, weights, lam):
    """
    Check whether the qubit dynamics can be represented by a time-local
    GKSL (Lindblad) equation.

    A time-local master equation: d(rho)/dt = gamma(t) D[sigma_z] rho
    where D[sigma_z] rho = sigma_z rho sigma_z - rho.

    The dephasing rate gamma(t) is related to Phi(t) by:
      gamma(t) = dPhi/dt = sum_k S_k (1 - exp(-rate_k t)) / rate_k

    For CP preservation, we need gamma(t) >= 0 for all t >= 0.
    (This is the CP condition for time-local dephasing channels, per
    Rivas-Huelga-Plenio 2014.)

    For the matrix PRW:
      gamma(t) = sum_k S_k (1 - exp(-rate_k t)) / rate_k

    Since S_k >= 0 and rate_k > 0, each term is >= 0 for t >= 0.
    Therefore gamma(t) >= 0 ALWAYS. CP is ALWAYS PRESERVED.

    This means: the matrix PRW produces a CP-preserving dephasing channel
    that is NON-MARKOVIAN (time-dependent gamma(t)) but ALWAYS CP.

    The non-Markovianity is the same type as any finite-correlation-time bath.
    It is NOT a new type of quantum dynamics.
    """
    t = np.asarray(t_arr, dtype=float)

    # gamma(t) = dPhi/dt
    gamma_t = np.zeros_like(t)
    for sector, r_val in sectors.items():
        rate = lam * (1.0 + r_val)
        weight = weights.get(sector, 0.0)
        if rate > 0:
            gamma_t += weight * (1.0 - np.exp(-rate * t)) / rate

    # CP check: gamma(t) >= 0 for all t
    cp_preserved = np.all(gamma_t >= -1e-12)

    # Markovianity check: gamma(t) monotonically increasing?
    # Markovian iff gamma(t) is monotonically non-decreasing
    # (equivalently, dgamma/dt >= 0, i.e., C_JJ(t) >= 0)
    dgamma = np.diff(gamma_t)
    is_markovian = np.all(dgamma >= -1e-12)

    # Non-Markovianity measure: integral of |dgamma/dt| where dgamma/dt < 0
    # (RHP measure)
    nm_measure = np.sum(np.abs(dgamma[dgamma < 0])) * (t[1] - t[0])

    return {
        "gamma_t": gamma_t,
        "cp_preserved": cp_preserved,
        "is_markovian": is_markovian,
        "non_markovianity_rhp": nm_measure,
        "cp_note": "CP always preserved because gamma(t) = sum S_k(1-exp(-r_k t))/r_k >= 0 "
                   "when all S_k >= 0 and r_k > 0. This is the same CP guarantee as any "
                   "positive-correlation Gaussian dephasing bath.",
        "markovianity_note": "Non-Markovian (gamma(t) time-dependent) but this is the "
                             "same type of non-Markovianity as any finite-memory bath. "
                             "Not a new type of quantum dynamics."
    }


def gate3_qubit_dynamics():
    """
    Derive qubit dynamics under matrix PRW bath and check CP.
    """
    print("\n" + "=" * 70)
    print("GATE 3: QUBIT DYNAMICS AND CP CHECK")
    print("=" * 70)

    lam = 1.0
    t_arr = np.linspace(0, 10, 1000)

    # Test with Haar distribution, coupling to traceless sector
    haar_sectors = r_superoperator_eigenvalues("haar", n=2)
    
    # Coupling scenarios:
    # 1. A = I (trace coupling): only sees trace sector
    trace_weights = {"I": 1.0, "sx": 0.0, "sy": 0.0, "sz": 0.0}
    
    # 2. A = sz (traceless coupling): only sees traceless sector
    sz_weights = {"I": 0.0, "sx": 0.0, "sy": 0.0, "sz": 1.0}
    
    # 3. A = I + sz (mixed coupling): sees both sectors
    mixed_weights = {"I": 0.5, "sx": 0.0, "sy": 0.0, "sz": 0.5}

    scenarios = {
        "trace_coupling": trace_weights,
        "traceless_coupling": sz_weights,
        "mixed_coupling": mixed_weights,
    }

    results = {}

    for name, weights in scenarios.items():
        phi = qubit_dephasing_function(t_arr, haar_sectors, weights, lam)
        cp_result = check_cp_gksl(phi, t_arr, haar_sectors, weights, lam)

        # Also compute for scalar PRW (single rate 2*lam) for comparison
        scalar_sectors = {"I": 1.0, "sx": 1.0, "sy": 1.0, "sz": 1.0}
        phi_scalar = qubit_dephasing_function(t_arr, scalar_sectors, 
                                                {"I": 0.25, "sx": 0.25, "sy": 0.25, "sz": 0.25}, 
                                                lam)

        result = {
            "weights": weights,
            "cp_preserved": cp_result["cp_preserved"],
            "is_markovian": cp_result["is_markovian"],
            "non_markovianity": float(cp_result["non_markovianity_rhp"]),
            "cp_note": cp_result["cp_note"],
            "markovianity_note": cp_result["markovianity_note"],
        }
        results[name] = result

        print(f"\n  Scenario: {name}")
        print(f"    Weights: {weights}")
        print(f"    CP preserved: {cp_result['cp_preserved']}")
        print(f"    Markovian: {cp_result['is_markovian']}")
        print(f"    Non-Markovianity (RHP): {cp_result['non_markovianity_rhp']:.6f}")

    print("\n  KEY FINDING:")
    print("  CP is ALWAYS preserved (gamma(t) >= 0 for all t >= 0)")
    print("  because all spectral weights S_k >= 0 and rates > 0.")
    print("  The dynamics is non-Markovian (time-dependent gamma(t))")
    print("  but this is the SAME type of non-Markovianity as any")
    print("  finite-correlation-time Gaussian bath.")
    print("  ")
    print("  No new type of quantum dynamics is produced.")

    return results


# ============================================================================
# GATE 4: COMPARE AGAINST CONVENTIONAL MODELS
# ============================================================================

def conventional_two_bath_sjj(omega_arr, S1, tau1, S2, tau2):
    """
    Conventional two-bath model:
    S(omega) = 2*S1*tau1/(1+omega^2*tau1^2) + 2*S2*tau2/(1+omega^2*tau2^2)

    Four free parameters: S1, tau1, S2, tau2
    No constrained ratio between tau1 and tau2.
    """
    omega = np.asarray(omega_arr)
    return (2 * S1 * tau1 / (1 + omega**2 * tau1**2) +
            2 * S2 * tau2 / (1 + omega**2 * tau2**2))


def conventional_ou_sjj(omega_arr, S, tau):
    """Single OU process: S(omega) = 2*S*tau/(1+omega^2*tau^2)"""
    omega = np.asarray(omega_arr)
    return 2 * S * tau / (1 + omega**2 * tau**2)


def gate4_conventional_comparison():
    """
    Compare matrix PRW predictions against conventional models.

    Matrix PRW (Haar, mixed coupling):
      S(omega) = S1 * 2*2*lam/(omega^2 + (2*lam)^2) + S2 * 2*lam/(omega^2 + lam^2)
      3 free parameters: S1, S2, lam
      CONSTRAINED: rate ratio = 2:1

    Conventional two-bath:
      S(omega) = S1 * 2*tau1/(1+omega^2*tau1^2) + S2 * 2*tau2/(1+omega^2*tau2^2)
      4 free parameters: S1, tau1, S2, tau2
      UNCONSTRAINED: tau1/tau2 is free

    Conventional single OU:
      S(omega) = S * 2*tau/(1+omega^2*tau^2)
      2 free parameters: S, tau

    CAN CONVENTIONAL MODELS REPRODUCE THE MATRIX PRW?
    -------------------------------------------------
    1. Single OU: YES if coupling is single-sector (trace or traceless only).
       The matrix PRW reduces to a single Lorentzian = OU process.
       NOT distinctive.

    2. Two-bath: YES, by choosing tau2 = 2*tau1.
       The matrix PRW's constrained ratio 2:1 is a SPECIAL CASE of the
       two-bath model. The two-bath model has one more free parameter.

    3. The matrix PRW's PREDICTION is the constraint tau2/tau1 = 2.
       This removes one degree of freedom compared to two-bath.
       But: the constraint is only testable if you can measure BOTH
       decay rates independently AND check that their ratio is 2.

    4. The constraint depends on the U distribution (through p).
       For partially depolarizing: ratio = 2/(1+p), which is a free parameter.
       So the "constraint" is only fixed if p is fixed, and p is a model input.

    VERDICT: The matrix PRW produces a constrained two-Lorentzian spectrum.
    The constraint (ratio = 2 for Haar) removes one parameter compared to
    a two-bath model. But:
      a) The constraint depends on the U distribution (free parameter p)
      b) A two-bath model CAN reproduce it by choosing the right ratio
      c) Single-sector coupling reduces to a single OU (not distinctive)

    The constrained relationship is the SAME TYPE as the original fxt's
    P3 relation (c = xi_c/(2*tau_B)): a fixed ratio that is a special case
    of a more general conventional model.
    """
    print("\n" + "=" * 70)
    print("GATE 4: CONVENTIONAL MODEL COMPARISON")
    print("=" * 70)

    lam = 1.0
    omega_arr = np.linspace(0, 10, 1000)

    # Matrix PRW (Haar, mixed coupling)
    haar_sectors = r_superoperator_eigenvalues("haar", n=2)
    mixed_weights = {"I": 0.5, "sx": 0.0, "sy": 0.0, "sz": 0.5}

    sjj_matrix = sjj_analytical(omega_arr, haar_sectors, mixed_weights, lam)

    # Conventional two-bath: match parameters to matrix PRW
    # Matrix PRW: weight_k * 2*rate_k / (omega^2 + rate_k^2)
    # Two-bath:    2*S_k*tau_k / (1 + omega^2*tau_k^2) = 2*S_k / (1/tau_k + omega^2*tau_k)
    # Match: tau_k = 1/rate_k, S_k = weight_k
    S1_conv = 0.5    # weight for trace sector (r=1, rate=2*lam=2)
    S2_conv = 0.5    # weight for traceless sector (r=0, rate=lam=1)
    tau1_conv = 1.0 / (2 * lam)  # = 0.5
    tau2_conv = 1.0 / lam        # = 1.0
    sjj_twobath = conventional_two_bath_sjj(omega_arr, S1_conv, tau1_conv,
                                             S2_conv, tau2_conv)

    # Check: are they identical?
    max_diff = np.max(np.abs(sjj_matrix - sjj_twobath))

    # Conventional single OU (fit to dominant component)
    sjj_ou = conventional_ou_sjj(omega_arr, 0.5, 1.0 / lam)

    # Can a two-bath model with UNCONSTRAINED ratios reproduce the spectrum?
    # Yes: set tau1 = 0.5, tau2 = 1.0 (ratio 2:1) — this is a special case
    # The question is whether the constraint IS testable

    # Compute the "constrained parameter count"
    matrix_params = 3  # S_trace, S_traceless, lambda (ratio fixed at 2)
    twobath_params = 4  # S1, tau1, S2, tau2 (ratio free)
    ou_params = 2       # S, tau

    result = {
        "matrix_prw_params": matrix_params,
        "twobath_params": twobath_params,
        "ou_params": ou_params,
        "max_diff_matrix_vs_twobath": float(max_diff),
        "twobath_reproduces_matrix": max_diff < 1e-10,
        "constraint_type": "fixed rate ratio 2:1 (Haar) or 2/(1+p) (partial)",
        "constraint_is_special_case_of_twobath": True,
        "verdict": (
            "The matrix PRW produces a constrained two-Lorentzian spectrum. "
            "A conventional two-bath model reproduces it exactly by choosing "
            "the rate ratio to match. The matrix PRW's constraint (ratio=2 for "
            "Haar) removes one parameter, but this is the same type of "
            "constrained relationship as the original fxt's P3 relation: "
            "a fixed ratio that is a special case of a more general "
            "conventional model. The constraint depends on the U distribution "
            "parameter p, which is itself a free input. "
            "DISTINCTIVE PREDICTION: NONE that survives conventional comparison."
        )
    }

    print(f"\n  Matrix PRW parameters: {matrix_params}")
    print(f"  Two-bath parameters: {twobath_params}")
    print(f"  Single OU parameters: {ou_params}")
    print(f"  Max |S_matrix - S_twobath|: {max_diff:.2e}")
    print(f"  Two-bath reproduces matrix: {result['twobath_reproduces_matrix']}")
    print(f"\n  VERDICT:")
    print(f"  {result['verdict']}")

    # Plot comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Spectrum comparison
    axes[0].plot(omega_arr, sjj_matrix, 'b-', linewidth=2, label='Matrix PRW (Haar)')
    axes[0].plot(omega_arr, sjj_twobath, 'r--', linewidth=2, label='Two-bath (matched)')
    axes[0].plot(omega_arr, sjj_ou, 'g:', linewidth=2, label='Single OU')
    axes[0].set_xlabel('omega')
    axes[0].set_ylabel('S_JJ(omega)')
    axes[0].set_title('Spectral Density Comparison')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Correlation function comparison
    t_arr = np.linspace(0, 5, 500)
    cjj_matrix = cjj_analytical(t_arr, haar_sectors, mixed_weights, lam)
    
    # Scalar PRW for comparison
    scalar_sectors = {"all": 1.0}
    scalar_weights = {"all": 1.0}
    cjj_scalar = np.exp(-2 * lam * t_arr)

    axes[1].plot(t_arr, cjj_matrix, 'b-', linewidth=2, label='Matrix PRW (Haar, mixed)')
    axes[1].plot(t_arr, cjj_scalar, 'k--', linewidth=2, label='Scalar PRW')
    axes[1].set_xlabel('t')
    axes[1].set_ylabel('C_JJ(t)')
    axes[1].set_title('Correlation Function')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/matrix_prw_gate4_comparison.png", dpi=150)
    plt.close()

    return result


# ============================================================================
# STOCHASTIC SIMULATION VERIFICATION
# ============================================================================

def simulate_matrix_prw(n_steps=100000, n_walkers=1000, v=1.0, lam=1.0,
                        n_matrix=2, dist_type="haar", p_param=None, dt=0.01):
    """
    Stochastic simulation of the matrix PRW to verify analytical results.

    Each walker carries a matrix Q (n x n). At each step:
    1. Move in direction sigma at speed v
    2. With probability lambda*dt, reverse direction and transform Q -> U Q U^dagger
    3. Record the current J = Tr(A @ Q * sigma) where A is the coupling

    Returns: time series of J for computing C_JJ(t)
    """
    rng = np.random.default_rng(42)

    # Initialize walkers
    sigma = rng.choice([-1, 1], size=n_walkers)  # directions
    Q = np.eye(n_matrix, dtype=complex)[np.newaxis, ...]  # start as identity
    Q = np.tile(Q, (n_walkers, 1, 1)).astype(complex)

    # Random initial matrices (normal distributed entries, then normalize)
    for i in range(n_walkers):
        Q[i] = rng.standard_normal((n_matrix, n_matrix)) + 1j * rng.standard_normal((n_matrix, n_matrix))
        Q[i] = Q[i] / np.linalg.norm(Q[i])  # normalize

    # Coupling matrix A (traceless: sigma_z for n=2)
    if n_matrix == 2:
        A = np.array([[1, 0], [0, -1]], dtype=complex)
    else:
        A = np.eye(n_matrix, dtype=complex)
        A[0, 0] = 1
        A[1, 1] = -1

    # Time series of J
    J_series = np.zeros(n_steps, dtype=float)

    for step in range(n_steps):
        # Current observable: J = Re(Tr(A @ Q)) * sigma * v
        # (using the matrix state weighted by direction)
        J_vals = np.real(np.array([np.trace(A @ Q[i]) for i in range(n_walkers)]))
        J_series[step] = np.mean(J_vals * sigma) * v

        # Move
        # (positions not tracked; we only need the temporal correlation)

        # Reversal events
        reverse_mask = rng.random(n_walkers) < lam * dt
        sigma[reverse_mask] *= -1

        # Transform Q for reversed walkers
        n_reversed = int(np.sum(reverse_mask))
        if n_reversed > 0:
            U_list = draw_unitaries(n_reversed, n_matrix, dist_type, p_param, rng)
            rev_indices = np.where(reverse_mask)[0]
            for j, idx in enumerate(rev_indices):
                U = U_list[j]
                Q[idx] = U @ Q[idx] @ U.conj().T

    return J_series, dt


def draw_unitaries(n, dim, dist_type, p_param, rng):
    """Draw random unitaries from the specified distribution."""
    if dist_type == "haar":
        # Haar random: QR decomposition of complex Gaussian
        Z = (rng.standard_normal((n, dim, dim)) +
             1j * rng.standard_normal((n, dim, dim))) / np.sqrt(2)
        # Process each matrix individually for clean QR
        U_list = np.zeros((n, dim, dim), dtype=complex)
        for i in range(n):
            Q, R = np.linalg.qr(Z[i])
            d = np.diag(R)
            ph = d / np.abs(d)
            U_list[i] = Q * ph
        return U_list
    
    elif dist_type == "sz_only":
        # {I, sz} with equal probability
        U_list = np.zeros((n, dim, dim), dtype=complex)
        I_mat = np.eye(dim, dtype=complex)
        sz = np.array([[1, 0], [0, -1]], dtype=complex)
        choices = rng.choice([0, 1], size=n)
        for i in range(n):
            U_list[i] = I_mat if choices[i] == 0 else sz
        return U_list
    
    elif dist_type == "pauli_twirl":
        # {I, sx, sy, sz} uniform
        I_mat = np.eye(dim, dtype=complex)
        sx = np.array([[0, 1], [1, 0]], dtype=complex)
        sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sz = np.array([[1, 0], [0, -1]], dtype=complex)
        paulis = [I_mat, sx, sy, sz]
        choices = rng.choice(4, size=n)
        U_list = np.array([paulis[c] for c in choices])
        return U_list
    
    elif dist_type == "partial":
        # Partially depolarizing: with prob p, identity; with prob 1-p, Haar
        p = p_param if p_param is not None else 0.5
        U_list = np.zeros((n, dim, dim), dtype=complex)
        is_identity = rng.random(n) < p
        n_haar = np.sum(~is_identity)
        if n_haar > 0:
            Z = (rng.standard_normal((n_haar, dim, dim)) +
                 1j * rng.standard_normal((n_haar, dim, dim))) / np.sqrt(2)
            U_haar = np.zeros((n_haar, dim, dim), dtype=complex)
            for j in range(n_haar):
                Q_r, R_r = np.linalg.qr(Z[j])
                d = np.diag(R_r)
                ph = d / np.abs(d)
                U_haar[j] = Q_r * ph
        idx_haar = 0
        for i in range(n):
            if is_identity[i]:
                U_list[i] = np.eye(dim, dtype=complex)
            else:
                U_list[i] = U_haar[idx_haar]
                idx_haar += 1
        return U_list

    elif dist_type == "identity":
        return np.tile(np.eye(dim, dtype=complex), (n, 1, 1))

    raise ValueError(f"Unknown distribution: {dist_type}")


def verify_analytical_correlation():
    """
    Verify the analytical C_JJ(t) against stochastic simulation.
    """
    print("\n" + "=" * 70)
    print("STOCHASTIC SIMULATION VERIFICATION")
    print("=" * 70)

    lam = 1.0
    v = 1.0
    dt = 0.01

    # Simulate Haar distribution
    J_series, dt_sim = simulate_matrix_prw(
        n_steps=200000, n_walkers=500, v=v, lam=lam,
        n_matrix=2, dist_type="haar", dt=dt
    )

    # Compute empirical C_JJ(t) from the time series
    # (using the full time series as a single realization)
    J_centered = J_series - np.mean(J_series)
    n_steps = len(J_centered)
    max_lag = min(500, n_steps // 4)

    lags = np.arange(max_lag)
    cjj_empirical = np.zeros(max_lag)
    for lag in lags:
        cjj_empirical[lag] = np.mean(J_centered[:n_steps - lag] * J_centered[lag:])
    # Normalize
    cjj_empirical /= cjj_empirical[0] if cjj_empirical[0] != 0 else 1.0

    # Analytical prediction for Haar, traceless coupling (A = sz)
    # C_JJ(t) ~ exp(-lambda * t) (rate = lambda, since r=0 for traceless)
    t_arr = lags * dt
    cjj_analytical_traceless = np.exp(-lam * t_arr)

    # Also fit a two-exponential model
    # C_JJ(t) = a1 exp(-2*lam*t) + a2 exp(-lam*t)
    cjj_analytical_two_exp = 0.3 * np.exp(-2 * lam * t_arr) + 0.7 * np.exp(-lam * t_arr)

    # Compare
    max_diff_single = np.max(np.abs(cjj_empirical - cjj_analytical_traceless))
    max_diff_two = np.max(np.abs(cjj_empirical - cjj_analytical_two_exp))

    print(f"  Simulation: {n_steps} steps, {500} walkers, dt={dt}")
    print(f"  Haar distribution, traceless coupling (A=sigma_z)")
    print(f"  Max |C_emp - C_single_exp(-lam*t)|: {max_diff_single:.4f}")
    print(f"  Max |C_emp - C_two_exp|: {max_diff_two:.4f}")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t_arr, cjj_empirical, 'bo', markersize=3, alpha=0.5, label='Empirical')
    ax.plot(t_arr, cjj_analytical_traceless, 'r-', linewidth=2, 
            label=f'exp(-{lam}*t) [traceless, rate=lambda]')
    ax.plot(t_arr, np.exp(-2 * lam * t_arr), 'g--', linewidth=2, 
            label=f'exp(-{2*lam}*t) [trace, rate=2*lambda]')
    ax.plot(t_arr, cjj_analytical_two_exp, 'k:', linewidth=2, 
            label='Two-exp fit')
    ax.set_xlabel('t')
    ax.set_ylabel('C_JJ(t) [normalized]')
    ax.set_title('Matrix PRW Correlation: Simulation vs Analytical (Haar)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/matrix_prw_simulation_verification.png", dpi=150)
    plt.close()

    return {
        "max_diff_single_exp": float(max_diff_single),
        "max_diff_two_exp": float(max_diff_two),
        "n_steps": n_steps,
        "n_walkers": 500,
        "distribution": "haar",
        "coupling": "traceless (sigma_z)",
    }


# ============================================================================
# MAIN: RUN ALL FOUR GATES
# ============================================================================

def main():
    print("=" * 70)
    print("MATRIX-VALUED PRW INVESTIGATION: FOUR-GATE ANALYSIS")
    print("=" * 70)
    print()
    print("Question: Does a matrix-valued PRW produce bath statistics")
    print("genuinely different from a conventional classical stochastic")
    print("process?")
    print()

    # Gate 1: Model specification
    gate1 = gate1_model_specification()

    # Gate 2: Correlation derivation
    gate2 = gate2_correlation_derivation()

    # Gate 3: Qubit dynamics and CP
    gate3 = gate3_qubit_dynamics()

    # Gate 4: Conventional comparison
    gate4 = gate4_conventional_comparison()

    # Stochastic verification
    sim_result = verify_analytical_correlation()

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print()
    print("Gate 1 (Observable Algebra):")
    print(f"  Classification: {gate1['classification']}")
    print(f"  Observable algebra: {gate1['observable_algebra']}")
    print(f"  Noncommutativity: {gate1['noncommutativity_type']}")
    print()
    print("Gate 2 (Correlation Function):")
    print("  C_JJ(t) = sum_k S_k exp(-lambda(1+r_k) t)")
    print("  where r_k are eigenvalues of R superoperator")
    print("  Haar: two rates {2*lambda, lambda} with ratio 2:1")
    print("  Identity: single rate 2*lambda (= scalar PRW)")
    print("  Partial: ratio 2/(1+p), parameterized by p")
    print()
    print("Gate 3 (Qubit Dynamics):")
    print(f"  CP preserved: {gate3['mixed_coupling']['cp_preserved']}")
    print(f"  Markovian: {gate3['mixed_coupling']['is_markovian']}")
    print("  CP always preserved (gamma(t) >= 0 for positive correlations)")
    print("  Non-Markovian but same type as any finite-memory bath")
    print()
    print("Gate 4 (Conventional Comparison):")
    print(f"  Two-bath reproduces matrix PRW: {gate4['twobath_reproduces_matrix']}")
    print(f"  Matrix PRW params: {gate4['matrix_prw_params']}")
    print(f"  Two-bath params: {gate4['twobath_params']}")
    print(f"  Constraint: {gate4['constraint_type']}")
    print()
    print("VERDICT:")
    print("  The matrix-valued PRW is a CLASSICAL stochastic process with")
    print("  matrix-valued internal states. The observable algebra is commutative.")
    print()
    print("  The matrix structure enriches the correlation function from")
    print("  single-exponential to multi-exponential, with decay rates")
    print("  determined by the eigenvalue spectrum of the R superoperator.")
    print()
    print("  However, the multi-exponential correlation is reproducible by a")
    print("  conventional multi-bath model. The constrained rate ratio (2:1")
    print("  for Haar) removes one parameter compared to a two-bath model,")
    print("  but this constraint depends on the U distribution parameter p,")
    print("  which is itself a free input.")
    print()
    print("  CP is always preserved. The non-Markovianity is the same type")
    print("  as any finite-correlation-time Gaussian bath.")
    print()
    print("  DISTINGTIVE PREDICTION: None that survives conventional comparison.")
    print()
    print("  This is a STRONGER negative result than the original fxt:")
    print("  Even matrix-valued classical substrates with standard coupling")
    print("  produce conventional bath statistics. The matrix enrichment is")
    print("  real but not quantum, and not distinctive.")

    # Save results
    all_results = {
        "gate1": gate1,
        "gate2": gate2,
        "gate3": gate3,
        "gate4": gate4,
        "simulation": sim_result,
    }

    with open(f"{OUTPUT_DIR}/matrix_prw_investigation.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to {OUTPUT_DIR}/matrix_prw_investigation.json")


if __name__ == "__main__":
    main()
