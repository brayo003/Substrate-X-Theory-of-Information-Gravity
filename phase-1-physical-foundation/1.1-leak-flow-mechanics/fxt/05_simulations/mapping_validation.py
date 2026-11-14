"""
mapping_validation.py
=====================
Independent algebraic validator for mapping_derivation.md.

This script is structurally independent of mapping_sympy.py.
It checks every claimed equality used in the derivation using
a different approach: numerical sampling over random inputs.

If any identity fails, the script exits with code 1.

Strategy: For each algebraic claim, generate N random numerical
instances and verify the identity holds to floating-point precision.
This is independent of SymPy's symbolic engine.

Run:
    python mapping_validation.py
"""

import numpy as np
import sys

PASS = "PASS"
FAIL = "FAIL"
failures = []
N = 10_000   # random samples per test
RNG = np.random.default_rng(42)

def validate(name, lhs_fn, rhs_fn, n=N, tol=1e-10):
    """Sample n random inputs, compare lhs and rhs, fail if any mismatch."""
    errors = []
    for _ in range(n):
        try:
            lhs = lhs_fn()
            rhs = rhs_fn()
            err = np.max(np.abs(np.asarray(lhs) - np.asarray(rhs)))
            errors.append(err)
        except Exception as e:
            print(f"  [{FAIL}] {name}  (exception: {e})")
            failures.append(name)
            return
    max_err = max(errors)
    status = PASS if max_err < tol else FAIL
    print(f"  [{status}] {name}  (max_err={max_err:.2e})")
    if status == FAIL:
        failures.append(name)

def rand_vec():
    return RNG.standard_normal(3)

def rand_scalar(lo=0.1, hi=10.0):
    return float(RNG.uniform(lo, hi))

def cross3(a, b):
    return np.cross(a, b)

print("=" * 60)
print("INDEPENDENT ALGEBRAIC VALIDATOR — mapping_derivation.md")
print("=" * 60)

# ------------------------------------------------------------------ #
# V1: Cross product anti-symmetry: omega x r = -(r x omega)         #
# ------------------------------------------------------------------ #
print("\n--- V1: Cross product identities ---")

# V1a: anti-symmetry omega x r = -(r x omega) using paired vectors
v1a_errors = []
for _ in range(N):
    a, b = rand_vec(), rand_vec()
    v1a_errors.append(np.max(np.abs(cross3(a, b) + cross3(b, a))))
s = PASS if max(v1a_errors) < 1e-14 else FAIL
print(f"  [{s}] V1a: omega x r = -(r x omega)  (max_err={max(v1a_errors):.2e})")
if s == FAIL:
    failures.append("V1a: omega x r = -(r x omega)")

# Re-seed so both lambdas use matching vectors
def v1b_lhs():
    global _v1b_a, _v1b_b
    _v1b_a = rand_vec(); _v1b_b = rand_vec()
    return cross3(_v1b_a, _v1b_b)

def v1b_rhs():
    return -cross3(_v1b_b, _v1b_a)

validate("V1b: anti-symmetry verified with shared vectors", v1b_lhs, v1b_rhs, n=1000)

# ------------------------------------------------------------------ #
# V2: |omega x r|^2 = |omega|^2 |r|^2 - (omega.r)^2  (Lagrange)   #
# ------------------------------------------------------------------ #
print("\n--- V2: Lagrange identity ---")

def _v2():
    global _om, _r
    _om = rand_vec(); _r = rand_vec()

def v2_lhs():
    _v2()
    return np.dot(cross3(_om, _r), cross3(_om, _r))

def v2_rhs():
    return np.dot(_om, _om)*np.dot(_r, _r) - np.dot(_om, _r)**2

validate("V2: |omega x r|^2 = |omega|^2|r|^2 - (omega.r)^2", v2_lhs, v2_rhs, n=1000)

# ------------------------------------------------------------------ #
# V3: Angular average of sin^2(theta) = 2/3                         #
# ------------------------------------------------------------------ #
print("\n--- V3: Angular average <sin^2(theta)> = 2/3 ---")

def v3_avg():
    """Monte Carlo estimate of <sin^2(theta)> over sphere."""
    theta = np.arccos(RNG.uniform(-1, 1, 100_000))
    return np.mean(np.sin(theta)**2)

avg_val = v3_avg()
err = abs(avg_val - 2/3)
status = PASS if err < 5e-3 else FAIL  # Monte Carlo tolerance
print(f"  [{status}] V3: <sin^2(theta)>_sphere = {avg_val:.6f}  (expected 2/3={2/3:.6f}, err={err:.2e})")
if status == FAIL:
    failures.append("V3: <sin^2(theta)> = 2/3")

# ------------------------------------------------------------------ #
# V4: Decoherence formula — low-omega quadratic behaviour           #
# ------------------------------------------------------------------ #
print("\n--- V4: Decoherence formula [DCH] ---")

def gamma(G0, krot, om, om_max):
    return G0 + krot * om**2 / (1 + (om/om_max)**2)

def v4_lowomega():
    G0 = rand_scalar(1, 100)
    krot = rand_scalar(1e-8, 1e-6)
    om_max = rand_scalar(1e5, 1e7)
    om = om_max * rand_scalar(1e-4, 1e-2)   # om << om_max
    lhs = gamma(G0, krot, om, om_max) - G0
    rhs_approx = krot * om**2  # leading order
    # relative error should be < (om/om_max)^2 << 1
    return lhs / rhs_approx  # should be ≈ 1

def v4_rhs():
    return 1.0

validate("V4a: Gamma - Gamma0 ≈ k_rot*omega^2 for omega << omega_max (ratio→1)",
         v4_lowomega, v4_rhs, tol=0.01)

def v4_highomega_lhs():
    G0 = rand_scalar(1, 100)
    krot = rand_scalar(1e-8, 1e-6)
    om_max = rand_scalar(1e5, 1e7)
    om = om_max * rand_scalar(1e3, 1e5)  # om >> om_max
    lhs = gamma(G0, krot, om, om_max) - G0
    rhs_approx = krot * om_max**2
    return lhs / rhs_approx

validate("V4b: Gamma - Gamma0 ≈ k_rot*omega_max^2 for omega >> omega_max (ratio→1)",
         v4_highomega_lhs, v4_rhs, tol=0.01)

def v4_saturation_lhs():
    """At omega = omega_max, value = k_rot * omega_max^2 / 2."""
    krot = rand_scalar(1e-8, 1e-6)
    om_max = rand_scalar(1e5, 1e7)
    G0 = rand_scalar(1, 100)
    val = gamma(G0, krot, om_max, om_max) - G0
    return val

def v4_saturation_rhs():
    return _last_krot * _last_ommax**2 / 2

# Run manually for saturation
sat_errors = []
for _ in range(1000):
    krot = float(RNG.uniform(1e-8, 1e-6))
    om_max = float(RNG.uniform(1e5, 1e7))
    G0 = float(RNG.uniform(1, 100))
    val = gamma(G0, krot, om_max, om_max) - G0
    expected = krot * om_max**2 / 2
    sat_errors.append(abs(val - expected))
max_sat_err = max(sat_errors)
status = PASS if max_sat_err < 1e-10 else FAIL
print(f"  [{status}] V4c: Gamma at omega=omega_max equals Gamma0 + k_rot*omega_max^2/2 (err={max_sat_err:.2e})")
if status == FAIL:
    failures.append("V4c: saturation value")

# ------------------------------------------------------------------ #
# V5: Rotating-frame unitary identity U sigma_x U† numerical check  #
# ------------------------------------------------------------------ #
print("\n--- V5: Rotating-frame unitary (Candidate A) ---")

def make_U(phi):
    """U = exp(i phi/2 sigma_z) = [[exp(i phi/2), 0],[0, exp(-i phi/2)]]"""
    return np.array([[np.exp(1j*phi/2), 0], [0, np.exp(-1j*phi/2)]])

sx_num = np.array([[0,1],[1,0]], dtype=complex)
sy_num = np.array([[0,-1j],[1j,0]], dtype=complex)
sz_num = np.array([[1,0],[0,-1]], dtype=complex)

rot_errors = []
for _ in range(1000):
    phi_val = float(RNG.uniform(0, 2*np.pi))
    U = make_U(phi_val)
    Ud = U.conj().T
    rotated = U @ sx_num @ Ud
    # U = exp(+i phi/2 sz): correct result is cos(phi)sx - sin(phi)sy
    expected = np.cos(phi_val)*sx_num - np.sin(phi_val)*sy_num
    rot_errors.append(np.max(np.abs(rotated - expected)))

status = PASS if max(rot_errors) < 1e-12 else FAIL
print(f"  [{status}] V5a: U sigma_x U† = cos(phi)sigma_x - sin(phi)sigma_y  [+i conv]  (max_err={max(rot_errors):.2e})")
if status == FAIL:
    failures.append("V5a")

# Frame term: U * dU†/dphi = -i/2 * sigma_z
frame_errors = []
dphi = 1e-7
for _ in range(1000):
    phi_val = float(RNG.uniform(0, 2*np.pi))
    U = make_U(phi_val)
    Ud_plus = make_U(phi_val + dphi).conj().T
    dUd_dphi = (Ud_plus - make_U(phi_val).conj().T) / dphi
    frame_term = U @ dUd_dphi
    expected = -1j/2 * sz_num
    frame_errors.append(np.max(np.abs(frame_term - expected)))

status = PASS if max(frame_errors) < 1e-5 else FAIL
print(f"  [{status}] V5b: U * dU†/dphi = -i/2 * sigma_z  (max_err={max(frame_errors):.2e})")
if status == FAIL:
    failures.append("V5b")

# ------------------------------------------------------------------ #
# V6: Magnus term — commutator [sigma_z, sigma_x] = 2i sigma_y     #
# ------------------------------------------------------------------ #
print("\n--- V6: Magnus commutator ---")

comm = sz_num @ sx_num - sx_num @ sz_num
expected_comm = 2j * sy_num
err = np.max(np.abs(comm - expected_comm))
status = PASS if err < 1e-15 else FAIL
print(f"  [{status}] V6: [sigma_z, sigma_x] = 2i sigma_y  (err={err:.2e})")
if status == FAIL:
    failures.append("V6")

# ------------------------------------------------------------------ #
# V7: delta_J = s0 (omega x r) is linear in both s0 and omega      #
# ------------------------------------------------------------------ #
print("\n--- V7: delta_J linearity ---")

def compute_dJ(s0, om, r):
    return s0 * np.cross(om, r)

lin_s0_errors = []
lin_om_errors = []
for _ in range(1000):
    s0 = rand_scalar()
    lam = rand_scalar()
    om = rand_vec()
    r = rand_vec()
    # Linearity in s0
    lhs_s = compute_dJ(lam*s0, om, r)
    rhs_s = lam * compute_dJ(s0, om, r)
    lin_s0_errors.append(np.max(np.abs(lhs_s - rhs_s)))
    # Linearity in omega
    lhs_o = compute_dJ(s0, lam*om, r)
    rhs_o = lam * compute_dJ(s0, om, r)
    lin_om_errors.append(np.max(np.abs(lhs_o - rhs_o)))

s = PASS if max(lin_s0_errors) < 1e-12 else FAIL
o = PASS if max(lin_om_errors) < 1e-12 else FAIL
print(f"  [{s}] V7a: delta_J linear in s0  (max_err={max(lin_s0_errors):.2e})")
print(f"  [{o}] V7b: delta_J linear in omega  (max_err={max(lin_om_errors):.2e})")
if s == FAIL: failures.append("V7a")
if o == FAIL: failures.append("V7b")

# ------------------------------------------------------------------ #
# V8: The r-cancellation in Gamma_rot = k_rot * omega^2             #
# ------------------------------------------------------------------ #
print("\n--- V8: r-cancellation in decoherence rate ---")

# Gamma_rot = kappa/(hbar * s0^2 * r^2) * (2/3) * s0^2 * omega^2 * r^2
# = (2 kappa)/(3 hbar) * omega^2  -- independent of r and s0
# Validate numerically

def gamma_rot(kappa, hbar, s0, r, om):
    prefactor = kappa / (hbar * s0**2 * r**2)
    avg_dJ_sq = (2/3) * s0**2 * om**2 * r**2
    return prefactor * avg_dJ_sq

cancel_errors = []
for _ in range(1000):
    kappa = rand_scalar(1e-45, 1e-40)
    hbar = 1.0545718e-34
    s0 = rand_scalar(1e10, 1e15)
    r = rand_scalar(1e-9, 1e-3)
    om = rand_scalar(1e2, 1e7)
    k_rot_val = 2*kappa / (3*hbar)
    lhs = gamma_rot(kappa, hbar, s0, r, om)
    rhs = k_rot_val * om**2
    cancel_errors.append(abs(lhs - rhs) / rhs)

status = PASS if max(cancel_errors) < 1e-10 else FAIL
print(f"  [{status}] V8: Gamma_rot = k_rot*omega^2 (r and s0 cancel exactly, max_rel_err={max(cancel_errors):.2e})")
if status == FAIL:
    failures.append("V8")

# ------------------------------------------------------------------ #
# FINAL REPORT                                                        #
# ------------------------------------------------------------------ #
print("\n" + "=" * 60)
if failures:
    print(f"RESULT: {len(failures)} check(s) FAILED:")
    for f in failures:
        print(f"  - {f}")
    print("=" * 60)
    sys.exit(1)
else:
    print("RESULT: ALL CHECKS PASSED")
    print("Every algebraic identity in mapping_derivation.md is independently verified.")
    print("=" * 60)
    sys.exit(0)
