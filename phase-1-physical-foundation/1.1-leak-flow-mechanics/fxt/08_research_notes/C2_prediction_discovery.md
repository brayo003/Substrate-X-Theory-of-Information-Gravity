# C2 Prediction Discovery Program — Final Report
**Date:** 2026-07-24  
**Authority:** C2_FOUNDATIONS.md (frozen), C2_prediction_audit.md (prior audit)  
**Mandate:** Find every quantitative prediction that distinguishes C2 from all accepted physical theories.  
**Rules:** No new axioms. No repair of C2. Search existing mathematics only.  
**Elimination policy:** Immediate elimination if the prediction reduces to EIT, GENERIC, Maxwell, Lindblad, Schrödinger, GR, QFT, standard Markov theory, standard stochastic processes, category theory, optimal transport, or known waveguide theory.

---

## METHODOLOGY

This program searches every C2 subsystem for unavoidable observable consequences that satisfy all five criteria simultaneously:

1. Already implied by current C2 mathematics (no new postulates)
2. Do not require adding new axioms
3. Differ quantitatively from every accepted theory
4. Are experimentally testable
5. Are testable with public data, IBM Quantum, open databases, or inexpensive lab experiments

The search proceeds in five passes:

- **Pass 1:** Eliminate all subsystems already shown to be identical to existing theories
- **Pass 2:** Detailed analysis of individual subsystems not yet eliminated
- **Pass 3:** Cross-subsystem combinations not previously examined
- **Pass 4:** Final structural search — the FPUT-quantum bridge
- **Pass 5:** Complete elimination table and surviving candidates

The program treats the prior audit (C2_prediction_audit.md, 2026-07-24) as established context but does not assume its conclusions. Every surviving candidate is re-examined independently.

---

## PASS 1 — IMMEDIATE ELIMINATIONS

The following subsystems are mathematically equivalent to existing accepted theories. This was established by Theorem EQ-MAIN (substrate_final_audit.md) and confirmed across all prior audits. These subsystems are eliminated without further analysis.

| Subsystem | Identical to | Theorem |
|-----------|-------------|---------|
| PRW (Goldstein-Kac) | Telegrapher / Maxwell-Cattaneo equation | PRW-1, KR |
| FPUT normal mode dispersion | Standard harmonic lattice dispersion | FPUT-1, KR |
| Master equation [ME] core | EIT / GENERIC (full equivalence) | ME-EQ-MAIN, T |
| Master equation [ME] advection term | Standard advection-diffusion | EQ-ADV, T |
| Telegrapher dispersion ω(k) | Cattaneo 1948 | DISP-SOL, KR |
| BGK diffusion limit (τ→0) | Fick's law / diffusion equation | EQ-2, T |
| Wave equation limit (τ→∞) | Standard wave equation | EQ-3, T |
| Born rule reconstruction | Gleason's theorem applied to Hilbert space | CCA-9, KR |
| Schrödinger equation | Stone's theorem on unitary groups | SCC+Stone, KR |
| Bloch-Redfield T₁, T₂ structure | Standard Bloch-Redfield theory | HC-1, KR |
| T₂ ≤ 2T₁ bound | Standard quantum channel inequality | HC-4, T |
| Gibbs partition function Z_β | Statistical mechanics Boltzmann weight | CCA-6, IDENTICAL |
| Markov mixing time t_mix | Standard Markov chain theory | C2-Hthm, IDENTICAL |
| Shannon entropy H(A) | Shannon 1948 | CCA-5, IDENTICAL |
| Causal depth rank r(m) | Standard poset rank function | CCA-3, IDENTICAL |
| Substrate energy-momentum tensor | EIT energy-momentum tensor | ET/PT, IDENTICAL |
| CCA classical coarse-graining | Standard stochastic mechanics | CCA-10, T |
| T-reversal breaking in PRW | Standard irreversible transport | PRW review, KR |

**18 subsystems eliminated in Pass 1. No further analysis required.**

---

## PASS 2 — INDIVIDUAL SUBSYSTEM ANALYSIS

Each remaining subsystem is examined independently.

---

### CANDIDATE P-I — Q Diagnostic: Local Transport-Phase Boundary

**Prediction ID:** P-I  
**Mathematical origin:** Theorem Q-5 (C2_FOUNDATIONS.md §Subsystem 5)

**Q diagnostic definition:**
$$Q(x,t) = 4c^2\tau^2|\nabla\ln s(x,t)|^2 - 1$$

**Observable:** The zero-surface $Q(x,t) = 0$ in a spatially heterogeneous transport field. This surface partitions the field into oscillatory ($Q > 0$) and overdamped ($Q < 0$) regions.

**Existing prediction (standard theory):**  
WKB stability criterion for the telegrapher equation. Define the local wavenumber $k_{\text{eff}}(x,t) = |\nabla\ln s|$. The telegrapher equation has critical wavenumber $k_c = 1/(2c\tau)$. WKB criterion: oscillatory iff $k_{\text{eff}} > k_c$.

**C2 prediction:**  
$$Q(x,t) = \left(\frac{k_{\text{eff}}}{k_c}\right)^2 - 1 \quad \text{where} \quad k_{\text{eff}} = |\nabla\ln s|, \quad k_c = \frac{1}{2c\tau}$$

**Exact mathematical difference:**
$$\Delta \equiv Q_{\text{C2}} - Q_{\text{WKB}} = \left(\frac{k_{\text{eff}}}{k_c}\right)^2 - 1 - \left[\left(\frac{k_{\text{eff}}}{k_c}\right)^2 - 1\right] = 0$$

**Novelty test:** Can every existing accepted theory reproduce this?  
**YES.** Q is algebraically identical to the WKB criterion for the telegrapher equation. The expression $(k_{\text{eff}}/k_c)^2 - 1$ is what any physicist writing down the local stability of the telegrapher would produce.

**Existing experiments:** Not applicable — zero physical difference from WKB.

**Experimental feasibility:** N/A.

**STATUS: FAILED.**  
Elimination reason: Q is the WKB evanescent criterion for the telegrapher equation, known since Cattaneo (1948), repackaged in coordinate-invariant notation. Mathematical difference = 0.

---

### CANDIDATE P-II — Cutoff Attenuation Near Q = 0

**Prediction ID:** P-II  
**Mathematical origin:** Q-diagnostic evanescent branch, Q → 0⁻ (Theorem Q-5 applied to the regime boundary)

**Observable:** Amplitude decay rate of a field pattern near the critical wavenumber $k_c$.

**C2 prediction:**
$$\Gamma_{\text{dec}} \approx \frac{1}{2\tau}\sqrt{|Q|} \quad \text{for } Q \to 0^-$$

**Existing prediction (waveguide theory):**  
Standard attenuation near cutoff frequency $f_c = c/(4\pi\tau)$ for the telegrapher / telegraph-mode waveguide:
$$\alpha = \sqrt{k_c^2 - k^2} = k_c\sqrt{1 - (k/k_c)^2}$$

For $k \to k_c^-$, using $Q = (k/k_c)^2 - 1 \to 0^-$:
$$\alpha = k_c\sqrt{|Q|/(1+|Q|)} \approx k_c\sqrt{|Q|}$$

Since $k_c = 1/(2c\tau)$, the amplitude decay rate is $\alpha \cdot c = (c/2c\tau)\sqrt{|Q|} = (1/2\tau)\sqrt{|Q|}$.

**Exact mathematical difference:**
$$\Delta = \frac{1}{2\tau}\sqrt{|Q|} - \frac{1}{2\tau}\sqrt{|Q|} = 0$$

**Novelty test:** Can every existing accepted theory reproduce this?  
**YES.** This is the standard cutoff attenuation formula for the telegraph-mode waveguide, known from classical waveguide theory.

**STATUS: FAILED.**  
Elimination reason: Standard waveguide cutoff formula. Mathematical difference = 0.

---

### CANDIDATE P-III — Dephasing Scaling $\Gamma_\phi = k_{\text{rot}} \cdot \omega_{\text{rot}}^2$

**Prediction ID:** P-III  
**Mathematical origin:** Theorems HC-1, HC-2 (Lindblad reduction) + kinematic result [ESTABLISHED-VAR]

**C2 derivation chain:**
$$\langle(\delta J)^2\rangle = \frac{2}{3}s_0^2\omega_{\text{rot}}^2 r_q^2 \quad \text{[ESTABLISHED-VAR]}$$
$$\Gamma_\phi = \frac{2g^2}{\hbar^2}\int_0^\infty C_{JJ}(t)\,dt = \frac{2g^2}{\hbar^2}\langle(\delta J)^2\rangle\tau$$
$$\Gamma_\phi = k_{\text{rot}}\cdot\omega_{\text{rot}}^2, \quad k_{\text{rot}} = \frac{8g^2 s_0^2 r_q^2\tau}{3\hbar^2}$$

**Observable:** Ramsey $T_2$ decay rate as a function of the rotating-frame frequency $\omega_{\text{rot}}$.

**Existing prediction (general Lindblad with super-Ohmic bath):**  
For a bath with spectral density $S(\omega) \propto \omega^2$:
$$\Gamma_\phi = \frac{g^2}{\hbar^2}S(\omega_q) = \frac{g^2}{\hbar^2}\cdot A\omega_q^2 = k_{\text{std}}\cdot\omega_{\text{rot}}^2$$

The $\omega_{\text{rot}}^2$ scaling is identical.

**Exact mathematical difference:**  
Scaling exponent: $\Delta\alpha = 2 - 2 = 0$.  
Prefactor: $\Delta k = k_{\text{rot}}^{\text{C2}} - k_{\text{rot}}^{\text{std}}$. Both reduce to one free fit parameter. Cannot be differentiated experimentally without independently measuring $g$, $s_0$, $r_q$, $\tau$.

**Existing experiments:** IBM Quantum Ramsey dataset (local: `aaG/ramsey_dataset/gamma_dataset.csv`). Fitted $k_{\text{rot}} = 4.5\times10^{-7}$ s. Scaling confirmed. Result is consistent with C2 but not unique to it.

**Novelty test:** Can every existing accepted theory reproduce the $\omega_{\text{rot}}^2$ scaling?  
**YES** — any super-Ohmic bath ($S(\omega) \propto \omega^2$) gives the same scaling.

**Experimental feasibility:** **A** — IBM Quantum, zero cost, data already collected.

**STATUS: PARTIAL.**  
Confirmed in IBM dataset. Not uniquely discriminating: free parameter $k_{\text{rot}}$ absorbs any multiplicative difference. The $\omega_{\text{rot}}^2$ scaling is one possible exponent among $\{0, 1, 2\}$ observed in different qubit systems and operating points.

---

### CANDIDATE P-IV — Pure Dephasing: $T_1 = \infty$

**Prediction ID:** P-IV  
**Mathematical origin:** Theorem HC-3 (interaction_hamiltonian_uniqueness.md): uniqueness of $A = \sigma_z$ under longitudinal coupling.

**C2 derivation:**  
Under $H_{\text{int}} = g J(x_q,t)\sigma_z$ (Assumption A-HC5: linear coupling; A-HC6: local coupling), the unique Lindblad jump operator is $A = \sigma_z$. Since $\sigma_z$ is diagonal in the energy eigenbasis:
$$\frac{d\rho_{00}}{dt} = \frac{\Gamma_\phi}{2}(\langle 0|\sigma_z|0\rangle^2 - 1)\rho_{00} = 0$$
$$\therefore T_1 = \infty \quad \text{(no population relaxation)}$$

**Observable:** $T_1$ via inversion recovery; ratio $T_2/T_1$.

**Existing prediction (general Lindblad):**  
Jump operators $\sigma_\pm$ allowed $\Rightarrow$ $T_1 < \infty$.  
Standard transmon: $T_1 \sim 100\,\mu\text{s}$, $T_2 \sim 100\,\mu\text{s}$, $T_2/T_1 \approx 1$.

**Exact mathematical difference:**
$$\Delta T_1 = T_1^{\text{C2}} - T_1^{\text{meas}} = \infty - T_1^{\text{meas}} \neq 0$$

**Novelty test:** Can every existing accepted theory reproduce $T_1 = \infty$?  
**NO** — general Lindblad with transverse coupling gives finite $T_1$.  
**YES** — phenomenological pure-dephasing model ($\sigma_z$-bath only) also gives $T_1 = \infty$.  
**Result: UNKNOWN** — C2 prediction is not unique (any longitudinal-only bath model gives the same).

**Existing experiments:** IBM Quantum calibration: $T_1 \approx 100\,\mu\text{s}$ (finite). This is because real qubits have multiple noise sources beyond the substrate coupling channel. The C2 prediction applies only to the substrate-coupling channel in isolation.

**Experimental feasibility:** **A** — IBM Quantum $T_1$ data publicly available.

**STATUS: PARTIAL.**  
Distinguishes C2 from generic Lindblad with transverse coupling. Does not distinguish C2 from a phenomenological $\sigma_z$-only bath. Conditional on isolating the substrate coupling channel from all other decoherence mechanisms. Not falsified by existing data, but not uniquely confirmable.

---

### CANDIDATE P-V — CCA Gibbs Distribution with Rank Weighting

**Prediction ID:** P-V  
**Mathematical origin:** CCA Theorem CCA-6 (partition function $Z_\beta = \sum_s e^{-\beta r(s)}$) and the maximum-entropy equilibrium $\mu^* \propto e^{-\beta r}$.

**Observable:** The equilibrium distribution of occupation probabilities across normal modes of a harmonic lattice.

**C2 prediction:**  
$$\mu^*_{\{n_k\}} \propto e^{-\beta_r \sum_k n_k} \quad \text{(weighted by total causal rank } r = \sum_k n_k\text{)}$$

Mean occupation per mode:
$$\langle n_k\rangle_{\text{C2}} = \frac{1}{e^{\beta_r} - 1} \quad \text{for all } k \text{ — mode-independent}$$

**Existing prediction (standard canonical ensemble):**  
$$\langle n_k\rangle_{\text{std}} = \frac{1}{e^{\beta\hbar\omega_k} - 1} \quad \text{(Bose-Einstein, mode-dependent)}$$

**Exact mathematical difference:**  
For two modes with $\omega_1 \neq \omega_2$:
$$\Delta\langle n\rangle = \langle n_1\rangle_{\text{C2}} - \langle n_1\rangle_{\text{std}} = \frac{1}{e^{\beta_r}-1} - \frac{1}{e^{\beta\hbar\omega_1}-1} \neq 0 \quad \text{when } \beta_r \neq \beta\hbar\omega_1$$

The C2 Gibbs distribution predicts **equal occupation for all modes regardless of frequency** — equivalent to the Rayleigh-Jeans ultraviolet catastrophe.

**Existing experiments:**  
Planck's blackbody radiation law (1900) and all subsequent spectroscopic measurements directly falsify equal mode occupation. High-frequency modes are exponentially suppressed. The Planck spectrum $I(\nu) \propto \nu^3/(e^{h\nu/k_BT}-1)$ is confirmed to 1 part in $10^4$ from COBE/FIRAS data.

**Novelty test:** Can every existing accepted theory reproduce this result?  
**NO** — this is a *new* prediction, but one that is immediately and catastrophically falsified.

**STATUS: FAILED.**  
The C2 rank-weighted Gibbs distribution predicts equal occupation for all harmonic modes, contradicting the Planck spectrum and all thermodynamic spectroscopy. Falsified by Planck 1900 and every subsequent measurement.

---

### CANDIDATE P-VI — CCA Discrete Causal Structure as Spacetime Candidate

**Prediction ID:** P-VI  
**Mathematical origin:** Theorem CCA-7 (Alexandrov topology on $(M,\leq)$ generates discrete causal set).

**Observable:** Any physical signature of Planck-scale spacetime discreteness — Lorentz invariance violation, non-locality in propagators, stochastic fluctuations of proper times.

**C2 prediction:** The CCA causal order $(M,\leq)$ is a locally finite partial order generating a discrete causal set. Physical spacetime is discrete at some scale.

**Quantitative content:** None. C2 does not specify the discreteness scale. It could be the Planck length ($\ell_P \approx 10^{-35}$ m), the substrate coherence length $\xi_c$, or anything in between. Without a derived scale, no numerical prediction follows.

**Existing prediction (causal set theory):** Bombelli, Lee, Meyer, Sorkin (1987) — same discrete causal set structure, with substantially more developed phenomenology (Lorentz invariance, propagator corrections, diffuse gamma-ray observations).

**Novelty test:** Can every existing accepted theory reproduce this result?  
**UNKNOWN** — depends on the scale. But C2 produces no scale, so no test exists.

**STATUS: FAILED.**  
No quantitative prediction without a derived discreteness scale. The causal set structure is already covered by the Bombelli-Lee-Meyer-Sorkin program.

---

---

## PASS 2 (continued) — INDIVIDUAL SUBSYSTEM ANALYSIS

---

### CANDIDATE P-VII — NC-2: Probability Weight ε as Axiom (Action Inversion)

**Prediction ID:** P-VII  
**Mathematical origin:** NC-2 from C2_NOVELTY_AUDIT.md. In C2, the causal action is derived from the probability weight:
$$S_{\text{causal}}(m) = -\log\varepsilon(m) + r(m)$$

This inverts the standard logic where probability is derived from action ($p \propto e^{-S}$). In C2, $\varepsilon$ is the axiom (Ax4) and $S_{\text{causal}}$ is the derived quantity.

**Observable:** Any physical quantity that depends on the ordering of action vs. probability as primitives. Specifically: does the C2 causal action $S_{\text{causal}}$ predict a different probability for any process than the standard $e^{-S}$ prescription?

**Analysis:**  
Given the same $\varepsilon(m)$ values, both frameworks assign identical probabilities to all processes. The distinction between "probability as axiom" and "action as axiom" is purely foundational — both frameworks produce the same numerical predictions for any given configuration. The inversion only generates a new prediction if C2 can derive the values of $\varepsilon(m)$ from its axioms independently of specifying $S$. It cannot: Ax4 only normalizes $\sum_m \varepsilon(m) = 1$; the individual values are free parameters.

**Exact mathematical difference:**  
$$\Delta p(m) = \varepsilon^{\text{C2}}(m) - e^{-S^{\text{std}}(m)}/Z = 0$$

when $\varepsilon(m) \equiv e^{-S^{\text{std}}(m)}/Z$ (which is always achievable by choosing $S^{\text{std}} = -\log\varepsilon + \log Z$).

**Novelty test:** Can every existing accepted theory reproduce this result? **YES.**

**STATUS: FAILED.**  
Philosophical inversion of action-probability logic. No new numerical prediction. Any value of $\varepsilon$ is reproducible by an appropriately chosen standard action.

---

### CANDIDATE P-VIII — NC-3: Causal Entropy Non-Decrease as Modified Second Law

**Prediction ID:** P-VIII  
**Mathematical origin:** CCA conjecture CCA-C2 (C2_FOUNDATIONS.md §Subsystem 6): $H_c(B) \geq H_c(A)$ for all causal $m: A \to B$, where $H_c = H + \lambda r$.

**Observable:** A process where $\Delta H < 0$ but $\Delta r > |\Delta H|/\lambda$. The C2 causal second law permits entropy decrease compensated by causal depth increase.

**Standard-theory prediction (thermodynamics):** $\Delta H \geq 0$ (entropy never decreases in an isolated system). Entropy decrease is absolutely forbidden.

**C2 prediction (if CCA-C2 holds):** $\Delta H + \lambda\Delta r \geq 0$. Entropy decrease allowed if causal depth increases:
$$\Delta H \geq -\lambda\Delta r$$

**Exact mathematical difference:**  
$$\Delta(\text{second-law constraint}) = \lambda\Delta r > 0 \quad \text{for any } \Delta r > 0$$

This is a genuine, non-trivial departure from the standard second law.

**Critical problem:** CCA-C2 is an **unproved conjecture**. The F9 research program (F9_causal_entropy_research.md, F9A_investigation.md) established rigorously that CCA-C2 follows from Ax1–Ax5 **only if** Ax4* (doubly stochastic causal morphisms) holds. Ax4* is logically independent of Ax1–Ax5 (Theorem F9A-MASTER). Therefore CCA-C2 is not a theorem of current C2 mathematics.

**STATUS: FAILED.**  
CCA-C2 is an unproved conjecture. Current C2 mathematics does not imply $H_c$ non-decrease. Requires Ax4*, which is a new axiom — adding it is forbidden by the task mandate.

---

### CANDIDATE P-IX — NC-5: Derivation of U(1) from Clifford Algebra Cl(2,0)

**Prediction ID:** P-IX  
**Mathematical origin:** Obstruction audit, Theorems 5.1–5.2. The even subalgebra of the 2D Clifford algebra satisfies $\text{Cl}^+(2,0) \cong \mathbb{C}$, giving $U(1) \cong SO(2)$ as a derived symmetry group.

**Observable:** The $U(1)$ phase group of quantum amplitudes and its consequences (interference, Aharonov-Bohm, Berry phase).

**C2 prediction:** $U(1)$ emerges from the geometry of the minimal 2D state space. Same $U(1)$ as in standard QM.

**Existing prediction (QM):** $U(1)$ phase symmetry postulated as part of the Hilbert space structure.

**Exact mathematical difference:**  
$$\Delta[\text{physical prediction}] = 0$$

Both frameworks produce the same $U(1)$ operator algebra. No experiment can distinguish "postulated $U(1)$" from "derived $U(1)$" when both yield identical operator algebras.

**Novelty test:** Can every existing accepted theory reproduce this result? **YES.**

**STATUS: FAILED.**  
The derivation of $U(1)$ is foundationally novel (NC-5 in the novelty audit) but produces zero new observable predictions. Same physical consequences as standard QM.

---

### CANDIDATE P-X — SCC Haar Measure: Specific State Distribution

**Prediction ID:** P-X  
**Mathematical origin:** SCC (Theorems SCC-1 through SCC-6) + Peter-Weyl theorem. SCC with compact symmetry group $G$ generates the Haar measure as the unique $G$-invariant measure on the state space.

**Observable:** The distribution of quantum states in a random quantum circuit (average over pure states on the Bloch sphere).

**C2 prediction:** Haar measure on $SU(2)$ — uniform distribution on the Bloch sphere.

**Existing prediction (standard QM):** Haar measure on $SU(2)$ — identical.

**Exact mathematical difference:** $\Delta = 0$.

The Haar measure on $SU(2)$ is the unique rotationally invariant measure. Both C2 and standard QM produce the same mathematical object.

**STATUS: FAILED.**  
Identical to standard quantum mechanics. C2 derives what QM postulates, but the physical prediction is unchanged.

---

### CANDIDATE P-XI — $r_q^2$ Geometric Scaling of Dephasing Rate

**Prediction ID:** P-XI  
**Mathematical origin:** Kinematic result [ESTABLISHED-VAR] from the solid-angle average:
$$\langle(\delta J)^2\rangle = \frac{1}{4\pi}\int_{\mathbb{S}^2}(s_0\omega_{\text{rot}} r_q\sin\theta)^2\,d\Omega = \frac{2}{3}s_0^2\omega_{\text{rot}}^2 r_q^2$$

Therefore:
$$\Gamma_\phi = k_{\text{rot}}\cdot\omega_{\text{rot}}^2, \quad k_{\text{rot}} = \frac{8g^2 s_0^2\tau}{3\hbar^2}\cdot r_q^2$$

**Observable:** $\Gamma_\phi$ as a function of the qubit spatial extent $r_q$ — the physical separation between the two coupling points of the qubit to the substrate field.

**Existing prediction (local-bath Lindblad):** For a spatially point-like bath:
$$\Gamma_\phi = \frac{g^2}{\hbar^2}S(\omega_q) \quad [\text{independent of } r_q]$$

**C2 prediction vs. local bath:**
$$\Delta\Gamma_\phi = \frac{8g^2 s_0^2\tau\omega_{\text{rot}}^2}{3\hbar^2}r_q^2 - \frac{g^2 S(\omega_q)}{\hbar^2}$$

This difference grows as $r_q^2$, distinguishing C2 from any local-bath model.

**Competing theories for $r_q$ scaling:**

| Bath model | $\Gamma_\phi(r_q)$ | Distinguishable from C2? |
|---|---|---|
| Local (point) bath | $r_q^0$ | YES — different scaling |
| 1D correlated bath: $C(r)\propto r$ | $r_q^1$ | YES — different exponent |
| 2D correlated bath: $C(r)\propto r^2$ | $r_q^2$ | NO — same scaling |
| EM dipole coupling: $\Gamma \propto d^2$ | $r_q^2$ | NO — same scaling |

The C2 $r_q^2$ prediction is distinguishable from local baths, but coincides with electromagnetic dipole coupling and any bath with quadratic spatial correlations.

**Existing experiments:**  
No systematic study of $\Gamma_\phi$ vs. $r_q$ at fixed $\omega_{\text{rot}}$ in the published literature. This experimental gap is genuine.

**Experimental feasibility:** **B/C** — requires comparing qubits of different physical size or geometry on the same chip, at identical operating conditions. IBM chip calibration data contains some qubit-to-qubit variation in geometry but not a controlled $r_q$ sweep.

**Novelty test:** Can every existing accepted theory reproduce the $r_q^2$ scaling?  
**NO** for local-bath models.  
**YES** for electromagnetic dipole coupling or any $C(r)\propto r^2$ bath.

**STATUS: PARTIAL/UNKNOWN.**  
Distinguishes C2 from point-source baths. Does not distinguish from dipole-coupling models or quadratically correlated baths. Without independent measurement of $g$, $s_0$, $\tau$, the coefficient $k_{\text{rot}} \propto r_q^2$ is a compound free parameter. Experimental gap exists.

---

### CANDIDATE P-XII — Rotating-Frame Vorticity $\Omega_J = -2s\omega_{\text{sub}}$

**Prediction ID:** P-XII  
**Mathematical origin:** Steady-state rotating-frame result [VORT-SS] from the substrate transport equations.

**C2 prediction:**
$$\Omega_J = -2s\cdot\omega_{\text{sub}}$$

where $\Omega_J$ is the vorticity of the substrate current field $\mathbf{J}$ and $\omega_{\text{sub}}$ is the substrate angular velocity in steady state.

**Existing prediction (standard fluid mechanics, EIT rotating frame):**  
For a fluid with density $s$ rotating at angular velocity $\omega$, the steady-state vorticity in the rotating frame is $\boldsymbol{\Omega} = -2\rho\boldsymbol{\omega}$ (Coriolis-induced vorticity for a scalar density field — the factor of 2 from the Coriolis term). Under the substitution $\rho \to s$, this is identical.

**Exact mathematical difference:** $\Delta = 0$.

**STATUS: FAILED.**  
Standard rotating-frame fluid mechanics. The Coriolis vorticity $-2\rho\omega$ is a textbook result under variable renaming $\rho \to s$.

---

### CANDIDATE P-XIII — Uniqueness of $A = \sigma_z$ Lindblad Operator

**Prediction ID:** P-XIII  
**Mathematical origin:** Theorem HC-3 (interaction_hamiltonian_uniqueness.md): Under A-HC5 (linear coupling) and A-HC6 (local coupling), $A = \sigma_z$ is the unique Lindblad jump operator.

**Observable:** The structure of the Lindblad dissipator — whether it contains only dephasing ($\sigma_z$) or also relaxation ($\sigma_\pm$) channels.

**C2 prediction:**
$$\mathcal{L}[\rho] = \frac{\Gamma_\phi}{2}(\sigma_z\rho\sigma_z - \rho) \quad \text{(no } \sigma_\pm \text{ terms)}$$

**Existing prediction (phenomenological pure-dephasing Lindblad):**  
Any phenomenological model with purely longitudinal noise ($\sigma_z$ coupling to bath) produces the identical dissipator. This is standard in the literature (e.g., flux-noise-dominated transmons, spin-echo measurements).

**Exact mathematical difference:** $\Delta\mathcal{L} = 0$ compared to any $\sigma_z$-only bath model.

**Novelty test:** Can every existing accepted theory reproduce this result?  
**YES** — any phenomenological bath with longitudinal coupling gives the same Lindblad structure.

**STATUS: FAILED.**  
Identical to standard phenomenological pure-dephasing Lindblad. The uniqueness theorem derives the same structure that any $\sigma_z$-bath model assumes directly.

---

### CANDIDATE P-XIV — Microscopic Candidates C1–C5: Born Rule and Schrödinger Equation

**Prediction ID:** P-XIV  
**Mathematical origin:** CCA Theorem CCA-9 (†-compact SMC → categorical QM, [KR]) + Gleason's theorem → Born rule; SCC + Stone's theorem → Schrödinger equation.

**Observable:** Quantum measurement probabilities; unitary time evolution.

**C2 prediction:** Born rule $p = |\langle\phi|\psi\rangle|^2$; $i\hbar\partial_t|\psi\rangle = H|\psi\rangle$.

**Existing prediction:** Identical — these are the standard axioms of QM.

**Exact mathematical difference:** $\Delta = 0$.

The C2 framework reconstructs QM from foundational principles. This is scientifically important (it derives what QM assumes) but produces zero new observable predictions.

**STATUS: FAILED.**  
Identical to standard quantum mechanics. Reconstruction, not new prediction.

---

---

## PASS 3 — CROSS-SUBSYSTEM ANALYSIS

Predictions arising from the intersection of two or more subsystems not previously examined together.

---

### CANDIDATE P-XV — PRW Flip Rate = Causal Depth Rate

**Prediction ID:** P-XV  
**Mathematical origin:** PRW Theorem PRW-1 ($\tau = 1/(2\lambda)$) × CCA Theorem CCA-3 (rank $r$ increments by 1 per causal event). Each PRW velocity reversal is one causal step: $dr/dt = \lambda = 1/(2\tau)$.

**Observable:** The rate of increase of causal depth should equal the PRW flip rate.

**Existing prediction (telegrapher theory):**  
The telegrapher decay rate is $\gamma = 1/(2\tau)$. This is the standard damping rate known since Cattaneo (1948).

**Exact mathematical difference:** $\Delta = dr/dt - \gamma = 0$.

**STATUS: FAILED.** Standard telegrapher damping rate. No new prediction.

---

### CANDIDATE P-XVI — F9/Ax4* Doubly Stochastic Morphisms

**Prediction ID:** P-XVI  
**Mathematical origin:** F9 research + Ax4*: every causal morphism $m: A \to B$ induces a doubly stochastic transition matrix $T_m$. By Birkhoff-von Neumann, $T_m$ is a convex combination of permutation matrices.

**Observable:** The transition probability matrix for a sequence of causal steps. If doubly stochastic, the uniform distribution is invariant under causal evolution: all states equally probable in equilibrium.

**Standard-theory prediction:**  
Classical Markov chains: $T$ doubly stochastic only under detailed balance with the uniform distribution — not guaranteed generally.  
Quantum channels: unital (doubly stochastic) only for specific noise models.

**C2 prediction (if Ax4* holds):** $T_m \cdot u_{n_A} = u_{n_B}$ — uniform distribution preserved.

**Critical problem:** Ax4* is logically **independent** of Ax1–Ax5 (Theorem F9A-MASTER, F9A_investigation.md). It cannot be derived from current C2. Using it requires adding a new axiom — forbidden.

**STATUS: FAILED.**  
Ax4* is a new axiom, not a consequence of current C2 mathematics. Adding it violates the mandate.

---

### CANDIDATE P-XVII — FPUT Recurrence × PRW Coherence Length

**Prediction ID:** P-XVII  
**Mathematical origin:** Theorem FPUT-3 (PRW unique local projection of FPUT harmonic chain). The projection theorem links FPUT mode structure to the PRW parameters: $c = v_{\text{acoustic}} = a\sqrt{K/m}$ (lattice acoustic speed), $\tau = 1/(2\lambda)$ (mean free time), coherence length $\xi_c = 2c\tau = v_{\text{acoustic}}/\lambda$.

**Observable:** Coherence length of the PRW projected from the FPUT lattice.

**Existing prediction (kinetic theory):**  
Mean free path $\ell = v_{\text{acoustic}}/\lambda_{\text{scatter}}$ — standard result from kinetic theory of phonons.

**Exact mathematical difference:** $\xi_c = 2c\tau = 2(v_{\text{acoustic}})/(2\lambda) = v_{\text{acoustic}}/\lambda = \ell$.

$\Delta = \xi_c - \ell_{\text{kinetic}} = 0$.

**STATUS: FAILED.** Mean free path formula. Standard kinetic theory.

---

### CANDIDATE P-XVIII — Spatial Q-Map on IBM Quantum Chip

**Prediction ID:** P-XVIII  
**Mathematical origin:** Q diagnostic + IBM Quantum multi-qubit chip spatial structure.

**Scenario:** On a 127-qubit IBM Eagle processor with heavy-hex connectivity, if the substrate field $s(x_i)$ varies spatially (e.g., due to chip inhomogeneity), the Q diagnostic predicts spatial regions of coherent and incoherent substrate transport.

**Observable:** Spatial correlation of $\Gamma_\phi(i)$ across qubits $i$. If $s(x_i) \propto \Gamma_\phi(i)^{-1}$ (substrate density inversely proportional to dephasing rate at each site), then:
$$Q(x_i) = 4c^2\tau^2\left|\nabla\ln\Gamma_\phi(x_i)\right|^2 - 1$$

**Standard-theory prediction (per-qubit Lindblad):** No spatial correlation predicted. Each qubit decoheres independently; $\Gamma_\phi(i)$ are independent parameters.

**C2 prediction:** Spatial gradients in $\Gamma_\phi$ correlate according to the Q-field topology. Specifically: the zero-surface $Q = 0$ separates spatial regions where the substrate field transitions from oscillatory to overdamped.

**Critical limitation:** This requires:
1. Independent calibration of $c\tau$ from a separate experiment.
2. Identification of $s(x_i)$ with a measurable qubit quantity.
3. Spatial resolution $\Delta x < \xi_c$.

Without knowing $c\tau$, the Q-map cannot be normalized to give a quantitative prediction. The Q diagnostic tells you the **sign** of $Q$ (coherent vs. incoherent) but the threshold $4c^2\tau^2 = 1$ requires knowing both $c$ and $\tau$.

**Experimental feasibility:** **A** — IBM calibration data is public; spatial analysis is free.

**STATUS: PARTIAL/UNKNOWN.**  
Structurally novel application. Quantitative prediction blocked by unknown $c\tau$. No published study exists testing this spatial correlation.

---

### CANDIDATE P-XIX — $T_2/T_1$ Scaling with $\omega_{\text{rot}}$

**Prediction ID:** P-XIX  
**Mathematical origin:** P-III ($\Gamma_\phi = k_{\text{rot}}\omega_{\text{rot}}^2$) combined with P-IV ($T_1 = \infty$):
$$\frac{T_2}{T_1}\bigg|_{\text{C2}} = \frac{1/\Gamma_\phi}{\infty} \to 0$$

This is the same prediction as P-IV. No independent content.

**STATUS: FAILED (merged with P-IV).** No new prediction beyond P-III and P-IV.

---

### CANDIDATE P-XX — Substrate Energy-Momentum Tensor Stress Form

**Prediction ID:** P-XX  
**Mathematical origin:** Substrate energy [ET]: $E_{\text{sub}} = \frac{1}{2}c^2 s^2 + \frac{1}{2}J^2$; momentum [PT]: $P_{\text{sub}} = sJ$.

**Existing prediction (EIT):** EIT energy-momentum tensor for Maxwell-Cattaneo/telegrapher is $E_{\text{EIT}} = \frac{1}{2}\kappa\tau J^2 + \frac{1}{2}\rho c^2$, $P_{\text{EIT}} = \rho J$.

Under $s \leftrightarrow \rho$, $c^2 \leftrightarrow \kappa\tau$: identical to C2.

**Exact mathematical difference:** $\Delta T^{\mu\nu} = 0$.

**STATUS: FAILED.** Identical to EIT under variable renaming.

---

## PASS 4 — THE FPUT-QUANTUM BRIDGE SEARCH

This is the final search. It examines the unique structural feature of C2 that the prior audit did not fully probe: the **direct connection** between the classical FPUT/PRW parameters ($c$, $\tau$, $D$) and the quantum decoherence parameter ($k_{\text{rot}}$) via a single unified substrate.

---

### CANDIDATE P-XXI — Cross-Medium Consistency: $k_{\text{rot}} \propto \tau$

**Prediction ID:** P-XXI  
**Mathematical origin:** The compound decoherence parameter is:
$$k_{\text{rot}} = \frac{8g^2 s_0^2 r_q^2\tau}{3\hbar^2} = \frac{8g^2 s_0^2 r_q^2}{3\hbar^2}\cdot\frac{D}{c^2}$$

If the **same physical substrate** provides both the classical transport (measurable $D$, $c$) and the quantum decoherence (measurable $k_{\text{rot}}$), then varying the substrate changes both $D/c^2$ and $k_{\text{rot}}$ proportionally.

**The prediction:** Across different substrate conditions (temperature, pressure, medium) that change $\tau = D/c^2$:
$$\frac{\partial\ln k_{\text{rot}}}{\partial\ln\tau}\bigg|_{g,\, s_0,\, r_q} = 1$$

i.e., $k_{\text{rot}}$ scales exactly linearly with the classical relaxation time $\tau$.

**Standard-theory prediction:**  
For an arbitrary quantum bath with spectral density $S(\omega)$:
$$k_{\text{rot}} = \frac{g^2}{\hbar^2}\cdot\frac{S''(\omega_q)}{2}$$

A change in classical transport ($D$, $c$) need not correlate with a change in $S''(\omega_q)$. These are independent quantities in general Lindblad theory.

**Exact mathematical difference:**
$$\Delta\left(\frac{\partial\ln k_{\text{rot}}}{\partial\ln\tau}\right) = 1 - \frac{\partial\ln S''(\omega_q)}{\partial\ln\tau}$$

This difference is nonzero unless $S''(\omega_q) \propto \tau$ exactly.

**Critical analysis — Fluctuation-Dissipation Theorem (FDT):**  
For a classical bath: $C_{JJ}(t) = \langle J^2\rangle e^{-|t|/\tau}$, so $\tilde{C}_{JJ}(0) = \langle J^2\rangle\tau$.
Therefore: $k_{\text{rot}} = (2g^2/\hbar^2)\langle J^2\rangle\tau$, which gives $k_{\text{rot}} \propto \tau$.

**This is the classical FDT.** The linear scaling $k_{\text{rot}} \propto \tau$ is a consequence of the fluctuation-dissipation theorem applied to **any** classical stochastic process (not just the C2 substrate). It does not require the C2 structure. Any classical bath with exponentially decaying correlations (which includes EIT, Maxwell-Cattaneo, Ornstein-Uhlenbeck) gives $k_{\text{rot}} \propto \tau$ automatically.

**STATUS: FAILED.**  
The $k_{\text{rot}} \propto \tau$ cross-prediction is a consequence of the fluctuation-dissipation theorem applied to any classical Markovian bath. Not unique to C2.

---

### CANDIDATE P-XXII — Specific Geometric Coefficient $\frac{2}{3}$ in Current Variance

**Prediction ID:** P-XXII  
**Mathematical origin:** The solid-angle average of the rotating current variance:
$$\langle(\delta J)^2\rangle = \frac{1}{4\pi}\int_{\mathbb{S}^2}(s_0\omega_{\text{rot}} r_q\sin\theta)^2\,d\Omega = \frac{2}{3}s_0^2\omega_{\text{rot}}^2 r_q^2$$

The factor $\frac{2}{3}$ comes from $\frac{1}{4\pi}\int\sin^2\theta\,d\Omega = \frac{2}{3}$.

**Observable:** The numerical coefficient in $\Gamma_\phi = k_{\text{rot}}\omega_{\text{rot}}^2$. Specifically, the coefficient $\frac{2}{3}$ vs. $1$ vs. $\frac{1}{3}$ as predicted by different geometric averaging assumptions.

**C2 prediction:** $\langle(\delta J)^2\rangle = \frac{2}{3}s_0^2\omega_{\text{rot}}^2 r_q^2$ (isotropic 3D sphere average).

**Alternative averaging schemes:**

| Geometry | Coefficient | Result |
|---|---|---|
| 3D isotropic (C2): $\langle\sin^2\theta\rangle_{4\pi}$ | $\frac{2}{3}$ | $k_{\text{rot}} = \frac{8g^2 s_0^2 r_q^2\tau}{3\hbar^2}$ |
| 2D circular average: $\langle\sin^2\phi\rangle_{2\pi}$ | $\frac{1}{2}$ | $k_{\text{rot}} = \frac{g^2 s_0^2 r_q^2\tau}{\hbar^2}$ |
| 1D linear coupling | $1$ | $k_{\text{rot}} = \frac{2g^2 s_0^2 r_q^2\tau}{\hbar^2}$ |
| Isotropic point source | $0$ (local) | $k_{\text{rot}}$ independent of $r_q$ |

**The discriminating test:**  
The factor $\frac{2}{3}$ vs. $\frac{1}{2}$ is a 33% difference. If $k_{\text{rot}}$ can be measured precisely and if $g$, $s_0$, $r_q$, $\tau$ can be determined independently (four separate experiments), the coefficient distinguishes 3D isotropic coupling (C2) from 2D planar coupling.

**Critical problem:** The coefficient $\frac{2}{3}$ is absorbed into $k_{\text{rot}}$ as a single fit parameter. Without independently measuring $g$, $s_0$, $r_q$, $\tau$, the coefficient cannot be isolated.

**STATUS: UNKNOWN.**  
The $\frac{2}{3}$ factor is a genuine geometric prediction of 3D isotropic substrate coupling. It is not uniquely C2 (any 3D isotropic bath gives the same factor), but it is distinguishable from 2D planar coupling. Currently experimentally inaccessible because $k_{\text{rot}}$ is a compound parameter.

---

### CANDIDATE P-XXIII — Obstruction O1 × Qubit: Minimum Decoherence from Complex Structure

**Prediction ID:** P-XXIII  
**Mathematical origin:** Obstruction O1 (complex structure required for interference in ≥2D) forces $U(1)$ phase. This implies a geometric (Berry) phase contribution in any closed loop on the Bloch sphere.

**Observable:** Berry phase in a cyclic Ramsey sequence.

**Existing prediction (Berry 1984, standard QM):** Geometric phase $\phi_{\text{geo}} = -\Omega_{\text{solid}}/2$ where $\Omega_{\text{solid}}$ is the solid angle subtended on the Bloch sphere. Identical in C2 and standard QM.

**STATUS: FAILED.** Standard quantum geometric phase. No new prediction.

---

### CANDIDATE P-XXIV — PA1 Microscopic Reversibility as Universal Prediction

**Prediction ID:** P-XXIV  
**Mathematical origin:** PA1 (microscopic reversibility) — fundamental dynamics must be invertible.

**Existing prediction (all accepted fundamental theories):** Hamiltonian mechanics is invertible; unitary QM is invertible; CPT symmetry holds in QFT. PA1 is a universal property of all accepted fundamental theories.

**STATUS: FAILED.** PA1 is shared by all accepted fundamental theories. Not distinguishing.

---

### CANDIDATE P-XXV — CCA-C3 Causal Action Extremization

**Prediction ID:** P-XXV  
**Mathematical origin:** CCA conjecture CCA-C3: physically realized morphisms extremize $S_{\text{causal}}(m) = -\log\varepsilon(m) + r(m)$.

**Observable:** The actual trajectory of a physical system should be the one that extremizes the causal action, predicting specific transition probabilities beyond what standard Lindblad assigns.

**Critical problem:** CCA-C3 is an **unproved conjecture** (status in C2_FOUNDATIONS.md: unproved). It cannot be used as a source of predictions without first being proved from Ax1–Ax5.

**STATUS: FAILED.** Unproved conjecture. Cannot generate predictions from current C2.

---

### CANDIDATE P-XXVI — The Master Cross-Prediction: Three-Way Constraint on $\omega_{\text{rot}}$, $r_q$, $\tau$

**Prediction ID:** P-XXVI  
**Mathematical origin:** All three scaling predictions together:
$$\Gamma_\phi = \frac{8g^2 s_0^2\tau}{3\hbar^2}\cdot r_q^2\cdot\omega_{\text{rot}}^2$$

The prediction has a **trilinear structure** in three independently variable quantities: $r_q$, $\omega_{\text{rot}}$, $\tau$.

**The joint prediction:** At fixed $g$, $s_0$:
$$\Gamma_\phi \propto r_q^2 \cdot \omega_{\text{rot}}^2 \cdot \tau$$

Varying all three simultaneously and confirming the product structure would be a strongly constraining test.

**What this means experimentally:**  
1. Vary $\omega_{\text{rot}}$ (trivial on IBM Quantum — confirmed, $\alpha = 2$)
2. Vary $r_q$ (requires qubits of different physical geometry at fixed frequency)
3. Vary $\tau$ (requires changing the physical substrate — e.g., temperature, applied field, or medium change)

A log-log regression of $\Gamma_\phi$ on $r_q^2\omega_{\text{rot}}^2\tau$ should give slope = 1 with no intercept, and the single compound prefactor $8g^2 s_0^2/(3\hbar^2)$ should be consistent across all data points.

**Standard-theory prediction for the joint test:**  
Standard Lindblad with an arbitrary bath has three separate free functions: $S(\omega)$ (spectral density), $C(r)$ (spatial correlation), $f(\tau)$ (dependence on bath relaxation time). These are three independent parameters. The C2 prediction that $\Gamma_\phi \propto r_q^2\omega_{\text{rot}}^2\tau$ with a single compound prefactor is a strong constraint.

**Exact mathematical difference:**  
Standard: $\Gamma_\phi = A_1(\omega_{\text{rot}}) \cdot A_2(r_q) \cdot A_3(\tau)$ with three independent functions.  
C2: $\Gamma_\phi = K \cdot r_q^2 \cdot \omega_{\text{rot}}^2 \cdot \tau$ with one prefactor $K = 8g^2 s_0^2/(3\hbar^2)$.

**This is a multiplicative separability constraint.** If $\Gamma_\phi$ does NOT factor as $K\cdot r_q^2\cdot\omega_{\text{rot}}^2\cdot\tau$, C2 is falsified. If it does, C2 is confirmed (and so is any bath model with the same separable structure).

**Critical caveat:** The joint prediction still requires knowing which system plays the role of the C2 substrate. The "substrate" in the experiment must be simultaneously the source of the classical transport parameters $D$, $c$, $\tau$ AND the quantum decoherence bath. Identifying this physical system is not specified by C2.

**Existing experiments:** No existing dataset simultaneously measures all three: $\Gamma_\phi$ vs. $(r_q, \omega_{\text{rot}}, \tau)$. The IBM dataset varies $\omega_{\text{rot}}$ only. No systematic $r_q$ or $\tau$ variation is published.

**Experimental feasibility:**  
- $\omega_{\text{rot}}$ variation: **A** (IBM Quantum, free)  
- $r_q$ variation: **C** (requires multiple qubit geometries, specialized chip design ~\$10k–\$100k)  
- $\tau$ variation: **D** (requires changing substrate medium — cryogenic engineering)

**Novelty test:** Can every existing accepted theory reproduce the trilinear structure?  
**NO** for a generic bath with independent $S(\omega)$, $C(r)$, $f(\tau)$.  
**YES** for any bath whose spectral density happens to factor as $S(\omega) = A\omega^2$ AND whose spatial correlation $C(r) = Br^2$ AND whose relaxation time dependence is $f(\tau) = C\tau$. This is a non-generic but possible bath.

**STATUS: PARTIAL.**  
The trilinear separability constraint $\Gamma_\phi = K r_q^2\omega_{\text{rot}}^2\tau$ is the strongest structural prediction extractable from C2. It is conditional on M1, M2, H_int = g·J·σ_z, and 17+ assumptions. The $\omega_{\text{rot}}^2$ factor is confirmed. The $r_q^2$ and $\tau$ factors are untested. No existing data either confirms or refutes the full trilinear structure.

---

## PASS 5 — COMPLETE ELIMINATION TABLE

Full accounting of all 26 candidates:

| ID | Candidate | Status | Elimination reason |
|----|-----------|--------|-------------------|
| P-I | Q = 0 local boundary | **FAILED** | WKB criterion for telegrapher, $\Delta = 0$ |
| P-II | $\Gamma_{\text{dec}} \sim \sqrt{\|Q\|}$ | **FAILED** | Standard waveguide cutoff formula, $\Delta = 0$ |
| P-III | $\Gamma_\phi = k_{\text{rot}}\omega_{\text{rot}}^2$ | **PARTIAL** | Confirmed IBM data; super-Ohmic bath gives same scaling |
| P-IV | $T_1 = \infty$ pure dephasing | **PARTIAL** | Distinguishes from generic Lindblad; not from $\sigma_z$-bath |
| P-V | CCA Gibbs with rank weighting | **FAILED** | Predicts UV catastrophe; falsified by Planck spectrum |
| P-VI | CCA discrete causal structure | **FAILED** | No quantitative scale; covered by causal set theory |
| P-VII | $\varepsilon$ as axiom vs. $e^{-S}$ | **FAILED** | No new numerical prediction, $\Delta p = 0$ |
| P-VIII | $H_c$ non-decrease second law | **FAILED** | CCA-C2 is unproved conjecture; requires Ax4* |
| P-IX | U(1) from Cl(2,0) | **FAILED** | Same physical predictions as standard QM, $\Delta = 0$ |
| P-X | Haar measure state distribution | **FAILED** | Identical to standard QM |
| P-XI | $r_q^2$ dephasing scaling | **PARTIAL/UNKNOWN** | Distinguishes from local bath; coincides with dipole coupling |
| P-XII | Vorticity $\Omega_J = -2s\omega_{\text{sub}}$ | **FAILED** | Standard Coriolis vorticity, $\Delta = 0$ |
| P-XIII | $A = \sigma_z$ uniqueness | **FAILED** | Identical to phenomenological $\sigma_z$-bath |
| P-XIV | Born rule / Schrödinger | **FAILED** | Reconstruction of standard QM, $\Delta = 0$ |
| P-XV | PRW flip rate = causal depth rate | **FAILED** | Standard telegrapher damping rate |
| P-XVI | Ax4* doubly stochastic morphisms | **FAILED** | Requires new axiom — forbidden |
| P-XVII | FPUT coherence length = mean free path | **FAILED** | Standard kinetic theory mean free path |
| P-XVIII | Spatial Q-map on IBM chip | **PARTIAL/UNKNOWN** | Novel application; blocked by unknown $c\tau$ |
| P-XIX | $T_2/T_1$ scaling | **FAILED** | Merged with P-IV; no independent content |
| P-XX | Substrate energy-momentum tensor | **FAILED** | Identical to EIT under variable renaming |
| P-XXI | $k_{\text{rot}} \propto \tau$ cross-medium | **FAILED** | Consequence of FDT for any classical Markovian bath |
| P-XXII | Factor $\frac{2}{3}$ from 3D averaging | **UNKNOWN** | Genuine geometric prediction; absorbed into free parameter |
| P-XXIII | Berry phase from O1 | **FAILED** | Standard quantum geometric phase |
| P-XXIV | PA1 microscopic reversibility | **FAILED** | Universal property of all accepted theories |
| P-XXV | CCA-C3 causal action extremization | **FAILED** | Unproved conjecture; no current theorem |
| P-XXVI | Trilinear $\Gamma_\phi \propto r_q^2\omega_{\text{rot}}^2\tau$ | **PARTIAL** | Strongest structural prediction; $\omega_{\text{rot}}^2$ confirmed; $r_q^2$, $\tau$ untested |

**Summary counts:**

| Status | Count | IDs |
|--------|-------|-----|
| FAILED | 19 | P-I, P-II, P-V through P-X, P-XII through P-XVII, P-XIX through P-XXI, P-XXIII through P-XXV |
| PARTIAL | 4 | P-III, P-IV, P-XI, P-XXVI |
| PARTIAL/UNKNOWN | 2 | P-XI, P-XVIII |
| UNKNOWN | 1 | P-XXII |

**After exhaustive search across all 26 candidates:**  
19 candidates FAILED elimination.  
7 candidates survive as PARTIAL, PARTIAL/UNKNOWN, or UNKNOWN.

Of the 7 survivors, all are conditional on M1, M2, and the coupling assumption H_int = g·J·σ_z (17+ independent assumptions). None passes the strict test of being uniquely attributable to C2 rather than to an alternative bath model.

---

---

## FINAL VERDICT

### The Seven Surviving Candidates

Seven candidates survived elimination. This section gives the final verdict on each with exact equations, experimental protocols, and novelty assessment.

---

#### SURVIVOR S-1: $\Gamma_\phi = k_{\text{rot}}\cdot\omega_{\text{rot}}^2$ (P-III)

**What C2 forces:**
$$\Gamma_\phi = \frac{8g^2 s_0^2 r_q^2\tau}{3\hbar^2}\cdot\omega_{\text{rot}}^2$$

**What standard theory predicts:**  
General Lindblad: $\Gamma_\phi = (g^2/\hbar^2)S(\omega_q)$ with $S(\omega)$ arbitrary.

**Difference:** The specific exponent $\alpha = 2$ in $\Gamma_\phi \propto \omega_{\text{rot}}^\alpha$.

**Existing data:** IBM Quantum Ramsey dataset confirms $\alpha = 2$ with $k_{\text{rot}} = 4.5\times10^{-7}$ s.

**Experimental protocol to strengthen:**  
Measure $\Gamma_\phi(\omega_{\text{rot}})$ at $\geq 10$ values of $\omega_{\text{rot}}$ spanning two decades on IBM Quantum. Fit $\log\Gamma_\phi = \alpha\log\omega_{\text{rot}} + \text{const}$. C2 predicts $\alpha = 2.000 \pm\epsilon$. A result $\alpha \neq 2$ (e.g., $\alpha = 1.5$ from 1/f noise) falsifies C2 for this dataset.

**Feasibility:** **A** — IBM Quantum, zero cost.

**Verdict:** PARTIAL. Consistent with C2. Not uniquely C2 (super-Ohmic bath gives same). The prediction is falsifiable: $\alpha \neq 2$ falsifies C2 in this regime.

---

#### SURVIVOR S-2: $T_1 = \infty$ Under Longitudinal Coupling (P-IV)

**What C2 forces:**  
Under $H_{\text{int}} = gJ\sigma_z$: $d\rho_{00}/dt = 0$, therefore $T_1 = \infty$.

**What standard theory predicts:**  
Generic Lindblad with transverse coupling: $T_1 < \infty$.

**Difference:**
$$\Delta\Gamma_1 = \Gamma_1^{\text{std}} - \Gamma_1^{\text{C2}} = \Gamma_1^{\text{std}} - 0 = \Gamma_1^{\text{std}} \neq 0$$

**Experimental protocol:**  
(1) Measure $T_1$ and $T_2$ on IBM Quantum. Public calibration at quantum.ibm.com.  
(2) Look for qubits where $T_1 \gg T_2$ (i.e., $T_2/T_1 \ll 1$). These are dominated by pure dephasing, consistent with C2.  
(3) In systems where $T_1 \approx T_2$ (most transmons), additional relaxation channels dominate; C2 does not account for these, so the prediction is not falsified — it is simply incomplete.  
(4) The definitive test: find a substrate-coupled qubit where ALL other $T_1$ channels are removed (e.g., NV center in isotopically pure diamond at low temperature, where charge noise and phonon relaxation are suppressed). C2 predicts $T_1 \to \infty$ in such a system. Published data: NV center $T_1 > 1$ s at $T < 10$ K, $T_2 \sim 1$ ms (ratio $T_1/T_2 > 1000$ — consistent with $T_1 \gg T_2$ as C2 predicts).

**Feasibility:** **A** — Published NV center data; IBM Quantum calibration data.

**Verdict:** PARTIAL. The prediction $T_1 \gg T_2$ is consistent with NV center data and with flux-sweet-spot transmons. Not falsified. Not uniquely C2 (any $\sigma_z$-only bath gives the same). The prediction is that the substrate coupling channel contributes zero to $T_1$ — experimentally testable by isolating that channel.

---

#### SURVIVOR S-3: $r_q^2$ Geometric Scaling of Dephasing (P-XI)

**What C2 forces:**  
$$k_{\text{rot}} = \frac{8g^2 s_0^2\tau}{3\hbar^2}\cdot r_q^2 \implies \Gamma_\phi \propto r_q^2 \text{ at fixed } \omega_{\text{rot}}, \tau$$

**What a local bath predicts:**  
$$\Gamma_\phi^{\text{local}} = \frac{g^2}{\hbar^2}S(\omega_q) \quad [r_q\text{-independent}]$$

**Difference at fixed $\omega_{\text{rot}}$, $\tau$:**
$$\Delta\Gamma_\phi = \frac{8g^2 s_0^2\tau\omega_{\text{rot}}^2}{3\hbar^2}(r_q^2 - r_{q,0}^2)$$

This grows quadratically with qubit size.

**Experimental protocol:**  
(1) Select qubits with identical frequencies $\omega_q$ but different physical dimensions $r_q$ (e.g., transmon qubits with different shunt capacitor sizes or interdigitated electrode spacings).  
(2) Measure $\Gamma_\phi$ via Ramsey at fixed $\omega_{\text{rot}}$.  
(3) Plot $\Gamma_\phi$ vs. $r_q^2$. C2 predicts a straight line through the origin. A local bath predicts a flat line.  
(4) The transition region $r_q \sim \xi_c = 2c\tau$ (coherence length) may mark the onset of the $r_q^2$ scaling.

**Where to find data:** IBM device layout specifications (qubit pad separations): ibm.com/quantum. Koch et al. (2007) PRA 76, 042319 reports different transmon geometries. Pop et al. (2014) Nature 508, 369 uses different qubit sizes.

**Feasibility:** **C** — Requires a set of qubits with identical frequencies but varying geometry. Not available in standard IBM calibration. Needs custom chip design or analysis of existing multi-chip datasets.

**Verdict:** PARTIAL/UNKNOWN. Distinguishes C2 from local-bath models. Coincides with dipole coupling. No existing systematic $r_q$ variation dataset. Experimental gap is genuine.

---

#### SURVIVOR S-4: Spatial Q-Map Correlation on Quantum Chip (P-XVIII)

**What C2 predicts:**  
The spatial pattern of dephasing rates $\Gamma_\phi(x_i)$ across a multi-qubit chip should not be random — it should reflect the spatial structure of the underlying substrate field $s(x,t)$. Specifically, the gradient $|\nabla\ln\Gamma_\phi|$ should cluster near a critical value $k_c = 1/(2c\tau)$, forming a Q = 0 boundary in the chip's spatial layout.

**What standard per-qubit Lindblad predicts:**  
$\Gamma_\phi(i)$ are independent per-qubit parameters. No spatial correlation is predicted. The spatial pattern of $\Gamma_\phi$ values across the chip should be random noise around a mean.

**Exact mathematical difference:**  
Standard: $\text{Cov}(\Gamma_\phi(x_i), \Gamma_\phi(x_j)) = 0$ for $i \neq j$.  
C2: $\text{Cov}(\Gamma_\phi(x_i), \Gamma_\phi(x_j)) > 0$ for $|x_i - x_j| < \xi_c$ (correlated within coherence length).

**Experimental protocol — immediately executable:**  
(1) Download IBM Quantum calibration data for a 127-qubit Eagle processor (public API: `from qiskit_ibm_runtime import QiskitRuntimeService`).  
(2) Extract $T_2(i)$ for all 127 qubits and their spatial coordinates $(x_i, y_i)$ on the chip layout.  
(3) Compute $\Gamma_\phi(i) = 1/T_2(i)$.  
(4) Test for spatial correlation: compute the spatial autocorrelation function $\xi(\Delta r) = \langle\Gamma_\phi(x_i)\Gamma_\phi(x_j)\rangle_{|x_i - x_j| = \Delta r}$.  
(5) C2 predicts: $\xi(\Delta r)$ decays with characteristic length $\xi_c$ (unknown but $> 0$).  
Standard theory: $\xi(\Delta r) = \langle\Gamma_\phi\rangle^2$ (delta-function correlation, i.e., no spatial correlation beyond nearest-neighbor chip coupling).  
(6) If $\xi(\Delta r)$ shows a coherent spatial decay over scale $\gg$ qubit spacing: consistent with C2.  
If $\xi(\Delta r) \approx \delta(\Delta r)$: consistent with standard theory.

**Feasibility:** **A** — IBM Quantum public calibration data, zero cost, executable on laptop in < 1 hour.

**Verdict:** PARTIAL/UNKNOWN. The spatial correlation test is novel, directly executable, and has not been performed in any published study in the context of a substrate field model. It does not require knowing $c\tau$. However, any spatially correlated noise source (e.g., two-level system bath with spatial correlations, crosstalk) could also produce spatial correlation. The C2 prediction is not unique, but it is testable and currently untested.

---

#### SURVIVOR S-5: Factor $\frac{2}{3}$ Geometric Coefficient (P-XXII)

**What C2 forces:**  
$$\langle(\delta J)^2\rangle = \frac{2}{3}s_0^2\omega_{\text{rot}}^2 r_q^2$$

The coefficient $\frac{2}{3}$ comes from the solid-angle average $\langle\sin^2\theta\rangle_{4\pi} = 2/3$, which assumes isotropic 3D coupling of the substrate current to the qubit.

**What 2D planar coupling predicts:**  
$$\langle(\delta J)^2\rangle_{2D} = \frac{1}{2}s_0^2\omega_{\text{rot}}^2 r_q^2 \quad \text{(factor } \tfrac{1}{2}\text{ from 2D average)}$$

**Difference:** $\Delta k_{\text{rot}} = (8/3 - 1)\cdot g^2 s_0^2 r_q^2\tau/\hbar^2 = (5/3)\cdot g^2 s_0^2 r_q^2\tau/\hbar^2$

This is a 33% difference in the prefactor depending on whether the coupling geometry is 3D or 2D.

**Critical problem:** The factor $\frac{2}{3}$ is absorbed into $k_{\text{rot}}$ as a single fit parameter. To detect the factor, one would need to measure $g$, $s_0$, $r_q$, $\tau$ independently and compare the product against the fitted $k_{\text{rot}}$. This requires four separate independent experiments.

**Feasibility:** **D** — Requires four independent measurements (coupling constant $g$, substrate density $s_0$, qubit radius $r_q$, relaxation time $\tau$) to disentangle the coefficient.

**Verdict:** UNKNOWN. Genuine geometric prediction of the coupling geometry. Not independently testable with current C2 parameters undetermined.

---

#### SURVIVOR S-6 (merged into S-1, S-3): The Trilinear Constraint $\Gamma_\phi \propto r_q^2\omega_{\text{rot}}^2\tau$ (P-XXVI)

This is the joint statement of S-1, S-3, and the FDT scaling. Its status follows from those two:

**Full prediction:**
$$\log\Gamma_\phi = \log K + 2\log\omega_{\text{rot}} + 2\log r_q + \log\tau$$

A three-dimensional log-log regression with slopes exactly (2, 2, 1) and single intercept $\log K$.

**What distinguishes this from any bath model:** A bath model with separable spectral density $S(\omega) = A\omega^2$, spatial correlation $C(r) = Br^2$, and FDT time-dependence $f(\tau) = C\tau$ gives the same result. These are three independent conditions. The C2 prediction imposes all three simultaneously from a single substrate model — that is the distinguishing structural claim.

**Feasibility:** **D** — Requires systematic variation of all three parameters.

**Verdict:** PARTIAL. Most comprehensive structural prediction. Three-parameter test not yet performed.

---

### PROGRAM CONCLUSION

**The direct answer to the mandate:**

> *Find one quantitative prediction that distinguishes C2 from every existing accepted physical theory.*

**The honest answer from exhaustive search:**

No candidate found in the current C2 mathematics satisfies all five criteria simultaneously:

| Criterion | Best candidate | Satisfied? |
|-----------|---------------|-----------|
| Implied by current mathematics | P-III ($\omega_{\text{rot}}^2$ scaling) | YES (conditional) |
| No new postulates required | P-III | YES (given M1, M2, H_int) |
| Differs quantitatively from EVERY accepted theory | P-III | **NO** — super-Ohmic bath gives same |
| Experimentally testable | P-III, P-IV, P-XXVI | YES |
| Testable with accessible resources | P-III | YES |

**The closest candidate is P-XXVI (the trilinear constraint):**

$$\boxed{\Gamma_\phi = K\cdot r_q^2\cdot\omega_{\text{rot}}^2\cdot\tau, \qquad K = \frac{8g^2 s_0^2}{3\hbar^2}}$$

This is the most specific quantitative prediction that C2 generates beyond standard Lindblad theory. It has been confirmed in the $\omega_{\text{rot}}^2$ direction. The $r_q^2$ and $\tau$ directions are untested. If confirmed in all three directions, it would constitute the strongest evidence for C2 over a standard independent-bath model. It would still not uniquely confirm C2 over a bath model with $S(\omega) = A\omega^2$, $C(r) = Br^2$, $f(\tau) = C\tau$ — but it would narrow the competition substantially.

**The limiting factor** (Theorem ME-PRED-NONE, C2_FOUNDATIONS.md): The transport layer [ME] is equivalent to EIT/GENERIC. All new predictions require M1 and M2, which are independent axioms not derived from [ME] or the PRW. The coupling constant $g$ is undetermined. Without these, no prediction follows from the transport layer alone. With them, the predictions are conditional and share parameter space with alternative bath models.

---

### EXPERIMENTAL PRIORITY RANKING

Ranked by: (1) feasibility, (2) discriminating power, (3) cost.

| Rank | Test | Prediction tested | Feasibility | Cost | Status of data |
|------|------|-------------------|-------------|------|----------------|
| 1 | IBM spatial $\Gamma_\phi$ autocorrelation | S-4 (spatial Q-map) | **A** | \$0 | Not yet done |
| 2 | IBM Ramsey $\alpha$ exponent sweep | S-1 ($\omega_{\text{rot}}^2$ scaling) | **A** | \$0 | Partially done |
| 3 | NV center $T_1/T_2$ ratio | S-2 ($T_1 = \infty$) | **A** | \$0 (pub data) | Consistent, not confirmed |
| 4 | Multi-geometry qubit $r_q$ scan | S-3 ($r_q^2$ scaling) | **C** | \$10k–100k | Not done |
| 5 | Full trilinear regression | S-6 ($r_q^2\omega^2\tau$) | **D** | >\$100k | Not done |

**Immediate action item:** Test S-4 using public IBM Quantum calibration data. Zero cost. Execute today. This is the only prediction that (a) requires no new experiments, (b) has not been tested, and (c) generates a binary outcome (correlated vs. uncorrelated spatial pattern) that distinguishes C2 from standard per-qubit Lindblad theory.

---

*End of C2 Prediction Discovery Program*  
*Date: 2026-07-24*  
*All C2 results treated as established per C2_FOUNDATIONS.md (frozen).*  
*No new axioms introduced. No C2 structure redesigned.*  
*All comparisons made against named standard theories with exact equations.*
