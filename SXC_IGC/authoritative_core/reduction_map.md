# Reduction Map — Domain → x(t)

## Definition of Observable

x(t) is defined per domain as a **normalized scalar instability proxy**.

General form:

x(t) = (Q(t) − ⟨Q⟩) / σ_Q

Where:
Q(t) is a domain-specific measurable quantity.

---

## Domain Reduction Table

### Particle Physics
Q(t): anomaly residual (e.g., g−2, Atomki excess)
x(t): normalized deviation from SM baseline

### Quantum Decoherence
Q(t): inverse coherence time or error accumulation
x(t): normalized decoherence pressure

### Cosmology
Q(t): density perturbation amplitude or rotation residual
x(t): normalized instability density

### Ecology / Biology
Q(t): population stress metric
x(t): normalized deviation from equilibrium

### Urban / Socio-Technical
Q(t): load, congestion, or pressure metric
x(t): normalized instability index

---

## Reduction Operator

For all domains:

𝓡: {raw variables} → Q(t) → x(t)

𝓡 must satisfy:
- x(t) dimensionless
- mean(x) ≈ 0
- variance(x) ≈ 1 (unless otherwise stated)

---

## REQUIRED ARTIFACT PER MODULE

Each module must provide:

- Q(t) definition
- Normalization procedure
- Script producing x(t)

---

## UNKNOWN / TODO

- Whether alternative normalization schemes change α
- Sensitivity of reduction to windowing / smoothing
- Formal error propagation from Q(t) → x(t)

