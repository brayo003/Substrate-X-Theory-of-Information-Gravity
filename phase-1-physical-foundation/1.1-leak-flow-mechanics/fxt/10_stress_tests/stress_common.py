"""Shared, reproducible utilities for the frozen-framework stress tests.

The functions in this module implement diagnostics only.  They do not alter any
repository equation: the reference prediction is Gamma_phi = k_rot omega_rot^2.
"""
import json, os, platform, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.linalg import expm

ROOT = os.path.dirname(__file__)
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)
sx = np.array([[0, 1], [1, 0]], complex)
sy = np.array([[0, -1j], [1j, 0]], complex)
sz = np.array([[1, 0], [0, -1]], complex)
sm = np.array([[0, 1], [0, 0]], complex)
sp = sm.T.conj()
I2 = np.eye(2, dtype=complex)
PAULI = {"x": sx, "y": sy, "z": sz}

def paths(stem):
    return (os.path.join(OUT, stem + ext) for ext in (".json", ".log", ".npz"))

def write_artifacts(stem, summary, arrays=None, lines=None):
    js, log, data = paths(stem)
    with open(js, "w") as f: json.dump(summary, f, indent=2, sort_keys=True)
    with open(log, "w") as f:
        f.write("Reproducibility: numpy=%s; python=%s; seed recorded in JSON.\n" % (np.__version__, sys.version.split()[0]))
        for line in lines or []: f.write(str(line) + "\n")
        f.write("STATUS: %s\n" % summary.get("status", "UNSET"))
    np.savez_compressed(data, **(arrays or {}))

def savefig(stem):
    plt.tight_layout(); plt.savefig(os.path.join(OUT, stem + ".png"), dpi=160); plt.close()

def rate(g=1., s0=1., rq=1., tau=1., hbar=1., omega=1.):
    return 8*g*g*s0*s0*rq*rq*tau*omega*omega/(3*hbar*hbar)

def finite_memory_envelope(t, gamma_markov, tau):
    """Exact Gaussian exponential-correlator envelope normalized to its Markov rate.
    This is a stress countermodel for the Markov replacement, not a new theory.
    """
    return np.exp(-gamma_markov * (t - tau * (1 - np.exp(-t/tau))))

def dissipator(L, rho):
    return L @ rho @ L.conj().T - .5*(L.conj().T@L@rho + rho@L.conj().T@L)

def gksl_super(H, jumps):
    basis=[]
    for a in range(2):
        for b in range(2):
            E=np.zeros((2,2),complex); E[a,b]=1; basis.append(E)
    cols=[]
    for E in basis:
        d=-1j*(H@E-E@H)
        for strength,L in jumps: d += strength*dissipator(L,E)
        cols.append(d.reshape(4))
    return np.column_stack(cols)

def evolve_gksl(t, rho0, H, jumps):
    S=gksl_super(H,jumps)
    # One diagonalisation evaluates an entire time grid; this is also less prone
    # to accumulated stepping error than repeatedly integrating the same LTI ODE.
    vals, vecs = np.linalg.eig(S)
    inv = np.linalg.inv(vecs)
    coeff = inv @ rho0.reshape(4)
    out = np.array([vecs @ (np.exp(vals*x)*coeff) for x in t])
    return np.real_if_close(out.reshape(-1,2,2), tol=1000)

def random_state(rng):
    A=rng.normal(size=(2,2))+1j*rng.normal(size=(2,2)); rho=A@A.conj().T
    return rho/np.trace(rho)

def classify(x, green, yellow):
    return "green" if x < green else ("yellow" if x < yellow else "red")

def heatmap(z, x, y, title, xlabel, ylabel, stem, cmap="RdYlGn_r"):
    plt.figure(figsize=(6.0,4.2)); im=plt.pcolormesh(x,y,z,shading="auto",cmap=cmap)
    plt.colorbar(im); plt.xlabel(xlabel); plt.ylabel(ylabel); plt.title(title); savefig(stem)
