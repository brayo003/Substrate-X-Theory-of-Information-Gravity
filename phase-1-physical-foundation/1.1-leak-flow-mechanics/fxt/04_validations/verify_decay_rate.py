#!/usr/bin/env python3
"""
Independent verification of the matrix PRW decay rate formula.

The code claims: decay_rate_k = lambda * (1 + r_k)

This comes from balance equations:
  dn^+_k/dt = -v dn^+_k/dx - lambda n^+_k + lambda r_k n^-_k
  dn^-_k/dt = +v dn^-_k/dx + lambda r_k n^+_k - lambda n^-_k

Derivation of the current equation:
  dq_k/dt = v * d(n^+_k - n^-_k)/dt

  v*dn^+_k/dt = v[-v dn^+_k/dx - lam n^+_k + lam r_k n^-_k]
  v*dn^-_k/dt = v[+v dn^-_k/dx + lam r_k n^+_k - lam n^-_k]

  dq_k/dt = v*dn^+_k/dt - v*dn^-_k/dt
           = -v^2 dn^+_k/dx - v*lam n^+_k + v*lam r_k n^-_k
             - v^2 dn^-_k/dx - v*lam r_k n^+_k + v*lam n^-_k
           = -v^2 d(n^+_k + n^-_k)/dx
             - v*lam*(n^+_k + r_k n^+_k) + v*lam*(r_k n^-_k + n^-_k)
           = -v^2 ds_k/dx - v*lam*(1+r_k)*n^+_k + v*lam*(1+r_k)*n^-_k
           = -v^2 ds_k/dx - lam*(1+r_k) * v*(n^+_k - n^-_k)
           = -v^2 ds_k/dx - lam*(1+r_k) * q_k

So the decay rate IS lambda*(1+r_k). This is correct.

Let's verify numerically.
"""

import numpy as np

def verify_decay_rate(r_k, lam=1.0, v=1.0, dt=0.0001, n_steps=100000):
    """Simulate balance equations for uniform initial condition."""
    n_plus = 1.0
    n_minus = 0.0

    q_history = []
    t_history = []

    for step in range(n_steps):
        t = step * dt
        dn_plus = (-lam * n_plus + lam * r_k * n_minus) * dt
        dn_minus = (lam * r_k * n_plus - lam * n_minus) * dt
        n_plus += dn_plus
        n_minus += dn_minus

        q = v * (n_plus - n_minus)
        q_history.append(q)
        t_history.append(t)

    t_arr = np.array(t_history)
    q_arr = np.array(q_history)

    valid = np.abs(q_arr) > 1e-10
    if np.sum(valid) < 10:
        return {"r_k": r_k, "rate_predicted": lam*(1+r_k), "rate_measured": None,
                "error": "insufficient data"}

    log_q = np.log(np.abs(q_arr[valid]))
    t_fit = t_arr[valid]
    coeffs = np.polyfit(t_fit, log_q, 1)
    rate_measured = -coeffs[0]
    rate_predicted = lam * (1.0 + r_k)
    error = abs(rate_measured - rate_predicted) / rate_predicted

    return {
        "r_k": r_k,
        "rate_predicted": rate_predicted,
        "rate_measured": float(rate_measured),
        "relative_error": float(error),
    }


def verify_correlation_and_twobath():
    """Verify Wiener-Khinchin transform and two-bath equivalence."""
    lam = 1.0
    omega_arr = np.linspace(0, 10, 1000)

    S_I = 0.5
    S_sz = 0.5
    rate_I = 2.0 * lam
    rate_sz = 1.0 * lam

    sjj_matrix = S_I * 2.0 * rate_I / (omega_arr**2 + rate_I**2) + \
                 S_sz * 2.0 * rate_sz / (omega_arr**2 + rate_sz**2)

    tau1 = 1.0 / rate_I
    tau2 = 1.0 / rate_sz
    sjj_twobath = S_I * 2.0 * tau1 / (1.0 + omega_arr**2 * tau1**2) + \
                  S_sz * 2.0 * tau2 / (1.0 + omega_arr**2 * tau2**2)

    max_diff = np.max(np.abs(sjj_matrix - sjj_twobath))

    # FFT verification of Wiener-Khinchin
    t_arr = np.linspace(-50, 50, 100000)
    dt = t_arr[1] - t_arr[0]
    cjj = S_I * np.exp(-rate_I * np.abs(t_arr)) + S_sz * np.exp(-rate_sz * np.abs(t_arr))
    sjj_fft = np.fft.fftshift(np.fft.fft(cjj)) * dt
    omega_fft = np.fft.fftshift(np.fft.fftfreq(len(t_arr), dt)) * 2 * np.pi

    valid = (omega_fft > 0) & (omega_fft < 10)
    sjj_fft_pos = np.real(sjj_fft[valid])
    omega_fft_pos = omega_fft[valid]

    sjj_anal_interp = S_I * 2.0 * rate_I / (omega_fft_pos**2 + rate_I**2) + \
                      S_sz * 2.0 * rate_sz / (omega_fft_pos**2 + rate_sz**2)

    max_diff_fft = np.max(np.abs(sjj_fft_pos - sjj_anal_interp))

    return {
        "max_diff_matrix_vs_twobath": float(max_diff),
        "max_diff_fft_vs_analytical": float(max_diff_fft),
    }


def main():
    print("=" * 70)
    print("INDEPENDENT VERIFICATION OF MATRIX PRW DECAY RATE FORMULA")
    print("=" * 70)

    print("\n1. Decay rate verification (balance equation simulation):")
    print(f"   Predicted: decay_rate = lambda * (1 + r_k)\n")

    for r_k in [0.0, 0.5, 0.9, 1.0]:
        result = verify_decay_rate(r_k)
        print(f"   r_k={r_k:.1f}: predicted={result['rate_predicted']:.4f}, "
              f"measured={result['rate_measured']:.6f}, "
              f"rel_error={result['relative_error']:.2e}")

    print("\n2. Wiener-Khinchin and two-bath equivalence:")
    result = verify_correlation_and_twobath()
    print(f"   Max |S_matrix - S_twobath|: {result['max_diff_matrix_vs_twobath']:.2e}")
    print(f"   Max |S_fft - S_analytical|: {result['max_diff_fft_vs_analytical']:.2e}")

    print("\n3. Analytical derivation:")
    print("   dq_k/dt = -v^2 ds_k/dx - lambda*(1+r_k) * q_k")
    print("   Decay rate = lambda*(1+r_k)  [VERIFIED]")

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
