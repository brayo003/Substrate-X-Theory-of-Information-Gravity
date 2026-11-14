# EXP8 Theoretical Specification

**Model:** Implemented nonlinear reaction-telegraph field (not a derivation from the Substrate X master equation).  
**Parameters (confirmatory default):** \(r=-0.5,\,a=2,\,b=1,\,\tau=1,\,c=1,\,\Delta t=0.05\).

---

## 1. Governing dynamics

First-order form matching **code** at \(\tau=1\):

\[
\partial_t s=v,\qquad
\partial_t v=\frac{c^2\nabla^2 s+rs+as^2-bs^3+S-v}{\tau}
\]

Homogeneous equilibria: \(s_0=0\) (stable), \(s_-\approx0.293\) (unstable), \(s_+\approx1.707\) (stable).

**Bistability:** With \(r<0\) and \(a>2\sqrt{-br}\), zero and high states are attractors; crossing \(s_-\) locally triggers high-basin entry.

**Spatial coupling:** Laplacian mixes neighbours so nearby subthreshold bumps can jointly exceed \(s_-\) while distant bumps cannot.

**Inertia \(\tau\):** Controls transient overshoot / memory of \(v\). Task 8 confirmatory keeps \(\tau=1\) (docstring/code Laplacian factor agrees). Ablation “no inertia” uses a first-order fallback (see ablations).

**Linear dynamics:** \(r=a=b=0\) → pure telegraph; no bistable latch.

---

## 2. Encoding and decoding (global)

**Encoding** \(I_i=E(x_i,\mathbf{r}_i,t_i)\):

\[
S(\mathbf{r})\leftarrow S(\mathbf{r})+x_i\exp\!\Big(-\frac{\|\mathbf{r}-\mathbf{r}_i\|^2}{2w^2}\Big)
\quad\text{at time }t_i
\]

with \(w=\) `DEPOSIT_WIDTH` (default 2.0). No semantic multi-channel encoding on the scalar field.

**Decoding** (must not re-implement the claimed operation from input records):

\[
O = \mathbf{1}\big[\max_{\|\mathbf{r}-\mathbf{r}_*\|<R}s(\mathbf{r},T) \ge \theta\big]
\]

with confirmatory \(\theta=0.85\) (high-basin evidence). Decoder uses **field values only**, never the deposit log. Ground truth is defined from the **experimental schedule**, not from reading deposits back.

**Why \(\theta=0.85\) rather than Task 7’s \(0.40\):** At operating amp \(0.50\), a near pair’s instantaneous peak is \(\approx0.71>0.40\). A separatrix threshold would pass a readout-only control without evolution. Requiring \(s\gtrsim0.85\) demands dynamical growth into the high basin; linear telegraph and readout-only fail this test under the frozen protocol.

**Readout-only control:** Freeze dynamics after deposits and apply the same decoder — if performance matches the evolved nonlinear field, the “operation” is not dynamical.

---

## 3. Operation catalogue

### A — Nonlinear coincidence detection

\[
\mathcal{C}_A:\{I_1,\ldots,I_n\}\to O\in\{0,1\}
\]

Ground truth: \(O^*=1\) iff at least one spatially compact cluster of inputs has total local mass sufficient to cross \(s_-\) under the frozen protocol (defined by pilot-calibrated separation/amplitude windows; confirmatory uses explicit schedule labels: `single`, `near_pair`, `far_pair`, `triple_near`, …).

Mechanistic dependency (hypothesis): reaction nonlinearity + local spatial overlap.

### B — Temporal integration

\[
\mathcal{C}_B:(I_1@t_1,I_2@t_2)\to O\in\{0,1\}
\]

Ground truth: activation if \(|t_2-t_1|\le W_{\mathrm{mem}}\) and spatial coincidence, else 0. Order sensitivity tested separately (should be weak under scalar bistability).

### C — Spatial discrimination

Equal total input mass \(M=\sum x_i\), different geometries → different \(O\) (e.g. clustered vs dispersed activation). Amplitude-matched control required.

### D — Nonlinear threshold integration / hysteresis

Sweep amplitude or add repeated weak deposits; measure up-threshold, down-threshold, hysteresis width.

### E — Conflict / interference

Competing signed or overlapping deposits. Limitation: scalar polarity ≠ semantic categories. Report predictable amplitude outcomes, not invented semantics.

### F — Pattern completion

Partial pattern after establishing a high-state template. Success requires recovering information **not** in the partial input. If only local amplification occurs → Category ≤1.

---

## 4. Ablation dictionary

| Ablation | Change |
|---|---|
| `nonlinear_full` | Default \(r,a,b,c,\tau\) |
| `linear_telegraph` | \(r=a=b=0\) |
| `reaction_off` | same as linear |
| `no_propagation` | \(c=0\) |
| `no_inertia` | first-order: \(v\leftarrow0\) each step after \(s\leftarrow s+\Delta t\cdot(c^2\nabla^2s+\mathrm{rxn})\) (documented approximation) |
| `readout_only` | deposits then decode without evolution |
| `amp_matched_linear` | linear with rescaled amp so peak deposit matches nonlinear peak |

---

## 5. Classification rubric (Categories 0–5)

See Task 8 brief. Category ≥3 requires linear ablation failure. Category 4 requires response-surface robustness. Category 5 requires behavioural bridge with causal isolation.

---

## 6. What is / is not claimed as computation

| Is computation | Is not |
|---|---|
| Joint subthreshold → high-basin transition | Passive persistence of a deposit |
| Separation-dependent activation | Decoder checking deposit records |
| Hysteretic threshold crossing | Messaging/blackboard symbolic AND (baseline) |
