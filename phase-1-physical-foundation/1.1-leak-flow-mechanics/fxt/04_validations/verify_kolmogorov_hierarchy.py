#!/usr/bin/env python3
"""
Minimal verification of the three-level equivalence hierarchy for classical
stochastic representations of quantum dephasing.

Tests the key formula from Lonigro & Chruściński (2022), Prop 4.1:

For a Markovian qubit dephasing process with dephasing function
    φ(t,s) = exp(-(γ/2 + iε)(t-s))

the Kolmogorov violation is:
    Δ = P_2(x3,t2;x1,t1) - Σ_{x2} P_3(x3,t3;x2,t2;x1,t1)
      = (1/8)(-1)^{x3-x1} exp(-γ(t3-t1)/2) sin(ε(t3-t2)) sin(ε(t2-t1))

Level 1 (single-time RU): trivial for qubits (unital ⟹ RU)
Level 2 (all-time classical process): always achievable for qubits (Crow-Joynt)
Level 3 (multitime classicality): iff φ is real (ε = 0) for Markovian qubit

This script verifies:
  (a) For ε = 0 (real φ): Kolmogorov violation = 0 (classical at Level 3)
  (b) For ε ≠ 0 (complex φ): Kolmogorov violation ≠ 0 (quantum at Level 3)
  (c) The matrix PRW (which has real φ) achieves Level 3 classicality
"""

import numpy as np


def dephasing_channel_qubit(rho, phi, basis='z'):
    """
    Apply a qubit dephasing channel with dephasing factor phi.
    
    Λ(ρ) = |0><0|ρ|0><0| + |1><1|ρ|1><1| + phi * |0><1|ρ_{01} + phi* * |1><0|ρ_{10}
    
    In the computational (dephasing) basis:
        ρ_00 → ρ_00
        ρ_11 → ρ_11  
        ρ_01 → phi * ρ_01
        ρ_10 → phi* * ρ_10
    """
    rho_out = rho.copy()
    rho_out[0, 1] = phi * rho[0, 1]
    rho_out[1, 0] = np.conj(phi) * rho[1, 0]
    return rho_out


def multitime_probability(n, outcomes, times, phi_func, rho0, measurement_basis='mub'):
    """
    Compute the n-time joint probability for sequential measurements on a
    Markovian qubit dephasing process.
    
    Parameters:
        n: number of measurements
        outcomes: list of outcomes (0 or 1)
        times: list of times (t_1, ..., t_n), with t_0 = 0
        phi_func: function (t, s) -> dephasing factor phi(t, s)
                  For time-translation invariant: phi(t, s) = phi_exp(t-s)
                  For general: phi(t, s) = exp(-(Gamma(t) - Gamma(s)))
        rho0: initial density matrix (2x2)
        measurement_basis: 'mub' for mutually unbiased basis (|±⟩ = (|0⟩±|1⟩)/√2)
                         'dephasing' for computational basis
    
    Returns: P_n(x_n, t_n; ...; x_1, t_1)
    """
    d = 2
    
    if measurement_basis == 'mub':
        # MUB basis: |m_0> = (|0>+|1>)/sqrt(2), |m_1> = (|0>-|1>)/sqrt(2)
        m_states = np.array([
            [1, 1],
            [1, -1]
        ]) / np.sqrt(2)
    else:
        # Dephasing basis
        m_states = np.array([
            [1, 0],
            [0, 1]
        ], dtype=complex)
    
    # Projectors P_x = |x><x|
    projectors = [np.outer(m_states[:, x], np.conj(m_states[:, x])) for x in range(d)]
    
    # Build the multitime probability using the regression formula (Markovian case)
    # P_n = Tr[P_{x_n} Λ_{t_n,t_{n-1}} ... P_{x_1} Λ_{t_1,t_0} (ρ_0)]
    
    # Start with initial state
    state = rho0.copy()
    t_prev = 0.0  # t_0 = 0
    
    for k in range(n):
        if k > 0:
            # Apply dephasing channel from t_{k-1} to t_k
            t_curr = times[k]
            t_prev_step = times[k-1]
            phi = phi_func(t_curr, t_prev_step)
            state = dephasing_channel_qubit(state, phi)
        
        # Apply measurement projector
        x = outcomes[k]
        state = projectors[x] @ state @ projectors[x]
    
    return np.real(np.trace(state))


def check_kolmogorov_2classical(phi_func, rho0, t1, t2, t3, measurement_basis='mub'):
    """
    Check the 2-classicality condition:
        Σ_{x1} P_2(x2, t2; x1, t1) = P_1(x2, t2)
    """
    d = 2
    violation = 0.0
    
    for x2 in range(d):
        # P_1(x2, t2) = Tr[P_{x2} Λ_{t2,0}(ρ_0)]
        p1 = multitime_probability(1, [x2], [t2], phi_func, rho0, measurement_basis)
        
        # Σ_{x1} P_2(x2, t2; x1, t1)
        p2_sum = 0.0
        for x1 in range(d):
            p2 = multitime_probability(2, [x2, x1], [t2, t1], phi_func, rho0, measurement_basis)
            p2_sum += p2
        
        violation += abs(p1 - p2_sum)
    
    return violation / d


def check_kolmogorov_3classical(phi_func, rho0, t1, t2, t3, measurement_basis='mub'):
    """
    Check the 3-classicality condition:
        Σ_{x2} P_3(x3, t3; x2, t2; x1, t1) = P_2(x3, t3; x1, t1)
    
    This is the key condition that distinguishes Level 2 from Level 3.
    """
    d = 2
    violation = 0.0
    violations = []
    
    for x3 in range(d):
        for x1 in range(d):
            # P_2(x3, t3; x1, t1) = Tr[P_{x3} Λ_{t3,t1} P_{x1} Λ_{t1,0}(ρ_0)]
            # Note: for Markovian, Λ_{t3,t1} is the channel from t1 to t3
            p2 = multitime_probability(2, [x3, x1], [t3, t1], phi_func, rho0, measurement_basis)
            
            # Σ_{x2} P_3(x3, t3; x2, t2; x1, t1)
            p3_sum = 0.0
            for x2 in range(d):
                p3 = multitime_probability(3, [x3, x2, x1], [t3, t2, t1],
                                           phi_func, rho0, measurement_basis)
                p3_sum += p3
            
            diff = p2 - p3_sum
            violations.append((x3, x1, diff))
            violation += abs(diff)
    
    return violation / (d * d), violations


def analytical_violation(gamma, epsilon, t1, t2, t3):
    """
    Analytical formula from Lonigro & Chruściński (2022), Eq. (57):
    
    P_2(x3,t2;x1,t1) - Σ_{x2} P_3(x3,t3;x2,t2;x1,t1)
        = (1/8)(-1)^{x3-x1} exp(-γ(t3-t1)/2) sin(ε(t3-t2)) sin(ε(t2-t1))
    
    Returns the maximum absolute violation over all (x3, x1), which is
    (1/8) * exp(-γ(t3-t1)/2) * |sin(ε(t3-t2)) * sin(ε(t2-t1))|.
    """
    dt31 = t3 - t1
    dt32 = t3 - t2
    dt21 = t2 - t1
    
    return (1.0/8.0) * np.exp(-gamma * dt31 / 2) * \
           abs(np.sin(epsilon * dt32) * np.sin(epsilon * dt21))


def main():
    print("=" * 70)
    print("THREE-LEVEL EQUIVALENCE HIERARCHY VERIFICATION")
    print("Classical Stochastic Representation of Quantum Dephasing")
    print("=" * 70)
    
    # Parameters
    gamma = 0.5  # dephasing rate
    t0 = 0.0
    t1 = 0.0
    t2 = 1.0
    t3 = 2.0
    
    # Initial state: diagonal in dephasing basis
    # ρ = p|0><0| + (1-p)|1><1| with p = 0.3
    p = 0.3
    rho0 = np.diag([p, 1 - p]).astype(complex)
    
    print(f"\nParameters: γ={gamma}, t1={t1}, t2={t2}, t3={t3}")
    print(f"Initial state: diagonal, p={p}")
    print(f"Measurement basis: MUB (|±⟩)")
    
    # --- Test 1: Real dephasing function (ε = 0) ---
    print("\n" + "-" * 50)
    print("TEST 1: Real dephasing function (ε = 0)")
    print("  φ(t,s) = exp(-(γ/2)(t-s))  [REAL]")
    print("  This is the case for the FXT matrix PRW")
    
    epsilon_real = 0.0
    phi_real = lambda t, s: np.exp(-(gamma / 2 + 1j * epsilon_real) * (t - s))
    
    # Check 2-classicality
    viol_2_real = check_kolmogorov_2classical(phi_real, rho0, t1, t2, t3, 'mub')
    print(f"\n  2-classicality violation: {viol_2_real:.2e}")
    print(f"  2-classical: {'YES' if viol_2_real < 1e-12 else 'NO'}")
    
    # Check 3-classicality
    viol_3_real, violations_real = check_kolmogorov_3classical(
        phi_real, rho0, t1, t2, t3, 'mub')
    print(f"\n  3-classicality violation: {viol_3_real:.2e}")
    print(f"  3-classical: {'YES' if viol_3_real < 1e-12 else 'NO'}")
    
    # Analytical prediction
    anal_real = analytical_violation(gamma, epsilon_real, t1, t2, t3)
    print(f"  Analytical max violation: {anal_real:.2e}")
    
    # --- Test 2: Complex dephasing function (ε ≠ 0) ---
    print("\n" + "-" * 50)
    print("TEST 2: Complex dephasing function (ε ≠ 0)")
    print("  φ(t,s) = exp(-(γ/2 + iε)(t-s))  [COMPLEX]")
    print("  This is the case where Level 3 classicality FAILS")
    
    epsilon_complex = 1.0
    phi_complex = lambda t, s: np.exp(-(gamma / 2 + 1j * epsilon_complex) * (t - s))
    
    # Check 2-classicality
    viol_2_complex = check_kolmogorov_2classical(phi_complex, rho0, t1, t2, t3, 'mub')
    print(f"\n  2-classicality violation: {viol_2_complex:.2e}")
    print(f"  2-classical: {'YES' if viol_2_complex < 1e-12 else 'NO'}")
    
    # Check 3-classicality
    viol_3_complex, violations_complex = check_kolmogorov_3classical(
        phi_complex, rho0, t1, t2, t3, 'mub')
    print(f"\n  3-classicality violation: {viol_3_complex:.2e}")
    print(f"  3-classical: {'YES' if viol_3_complex < 1e-12 else 'NO'}")
    
    # Analytical prediction
    anal_complex = analytical_violation(gamma, epsilon_complex, t1, t2, t3)
    print(f"  Analytical max violation: {anal_complex:.2e}")
    
    # Show individual violations
    print(f"\n  Individual Kolmogorov violations (P2 - ΣP3):")
    for x3, x1, v in violations_complex:
        print(f"    x3={x3}, x1={x1}: {v:.6f}")
    
    # --- Test 3: Matrix PRW dephasing (multi-exponential, real) ---
    print("\n" + "-" * 50)
    print("TEST 3: Matrix PRW dephasing (multi-exponential, REAL)")
    print("  φ(t) = exp(-Γ(t)) where Γ(t) = Σ S_k [t/rate_k - (1-exp(-rate_k*t))/rate_k²]")
    
    # Matrix PRW parameters (Haar U(2), mixed coupling)
    lam = 1.0
    S_trace = 0.5  # weight for trace sector (r=1, rate=2λ)
    S_traceless = 0.5  # weight for traceless sector (r=0, rate=λ)
    rate_trace = 2 * lam
    rate_traceless = lam
    
    def phi_matrix_prw(t, s):
        """Multi-exponential dephasing function (real-valued).
        phi(t,s) = exp(-(Gamma(t) - Gamma(s))) where Gamma is the integral of gamma(u).
        """
        Gamma_t = (S_trace * (t / rate_trace - (1 - np.exp(-rate_trace * t)) / rate_trace**2) +
                   S_traceless * (t / rate_traceless - (1 - np.exp(-rate_traceless * t)) / rate_traceless**2))
        Gamma_s = (S_trace * (s / rate_trace - (1 - np.exp(-rate_trace * s)) / rate_trace**2) +
                   S_traceless * (s / rate_traceless - (1 - np.exp(-rate_traceless * s)) / rate_traceless**2))
        return np.exp(-(Gamma_t - Gamma_s))
    
    # Check 2-classicality
    viol_2_prw = check_kolmogorov_2classical(phi_matrix_prw, rho0, t1, t2, t3, 'mub')
    print(f"\n  2-classicality violation: {viol_2_prw:.2e}")
    print(f"  2-classical: {'YES' if viol_2_prw < 1e-10 else 'NO'}")
    
    # Check 3-classicality
    viol_3_prw, violations_prw = check_kolmogorov_3classical(
        phi_matrix_prw, rho0, t1, t2, t3, 'mub')
    print(f"\n  3-classicality violation: {viol_3_prw:.2e}")
    print(f"  3-classical: {'YES' if viol_3_prw < 1e-10 else 'NO'}")
    
    # --- Test 4: Verify the gap depends on Im(φ) ---
    print("\n" + "-" * 50)
    print("TEST 4: Systematic scan of ε (imaginary part)")
    print("  Verifying: violation ∝ sin(ε·Δt₁)·sin(ε·Δt₂)")
    
    epsilons = np.linspace(0, 3.0, 50)
    violations = []
    analytical = []
    
    for eps in epsilons:
        phi_test = lambda t, s, e=eps: np.exp(-(gamma / 2 + 1j * e) * (t - s))
        v, _ = check_kolmogorov_3classical(phi_test, rho0, t1, t2, t3, 'mub')
        violations.append(v)
        analytical.append(analytical_violation(gamma, eps, t1, t2, t3))
    
    # Check agreement
    max_diff = max(abs(v - a) for v, a in zip(violations, analytical))
    
    print(f"\n  Max |numerical - analytical| over {len(epsilons)} points: {max_diff:.2e}")
    print(f"  Agreement: {'EXCELLENT' if max_diff < 1e-10 else 'POOR'}")
    
    # Print a few sample values
    print(f"\n  {'ε':>8s}  {'Numerical':>12s}  {'Analytical':>12s}")
    for i in range(0, len(epsilons), 10):
        print(f"  {epsilons[i]:8.3f}  {violations[i]:12.6e}  {analytical[i]:12.6e}")
    
    # --- Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Level 1 (single-time RU): 
  - All qubit dephasing channels are RU-representable at any fixed time.
  - TRIVIAL for d=2 (Landau-Streater: unital ⟹ RU for qubits).
  - NONTRIVIAL for d>2 (Kayser et al.: non-RU dephasing channels exist).

Level 2 (all-time classical process):
  - A single classical stochastic process can reproduce the channel at all times.
  - ALWAYS achievable for qubits (Crow-Joynt construction).
  - This is what the FXT matrix PRW achieves.

Level 3 (multitime classicality):
  - Requires Kolmogorov consistency of multitime statistics.
  - Markovian qubit: iff dephasing function φ(t,s) is REAL (ε=0).
  - The FXT matrix PRW has real φ → Level 3 classicality ACHIEVED.
  - Complex φ (ε≠0) → Level 3 FAILS (quantum multitime statistics).

THE GAP (Level 2 → Level 3):
  A classical process reproducing the channel at all times does NOT imply
  classical multitime statistics. The gap is measured by:
    Δ ∝ Im(φ_{t3,t2}) · Im(φ_{t2,t1})
  This vanishes iff φ is real-valued.

IMPLICATION FOR FXT:
  The matrix PRW produces real dephasing functions (no energy splitting),
  so it is locked at Level 3 classicality. To produce genuinely quantum
  multitime statistics, the model would need complex dephasing functions
  (ε≠0), higher dimensions (d>2), or non-Markovian dynamics.
""")
    
    print("VERIFICATION COMPLETE")


if __name__ == "__main__":
    main()
