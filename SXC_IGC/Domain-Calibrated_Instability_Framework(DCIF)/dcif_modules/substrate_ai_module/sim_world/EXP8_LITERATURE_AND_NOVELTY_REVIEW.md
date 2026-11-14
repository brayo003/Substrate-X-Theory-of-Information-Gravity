# EXP8 Literature and Novelty Review

**Scope:** Targeted review for operations demonstrated in Task 8.  
**Internet research:** Conducted 2026-11-13.

---

## 1. Closest related research areas

| Area | Relevance to Task 8 |
|---|---|
| Reaction–diffusion / excitable-media computing | Spatial coincidence, AND-like junctions, wave logic |
| Bistable media / threshold dynamics | High-basin latch, hysteresis |
| Stigmergy / digital pheromones | Shared environmental fields as coordination media |
| Morphological / physical / reservoir computing | Body/field dynamics as computation; readout separation |
| Telegraph / hyperbolic diffusion | Finite-speed propagation + inertia (τ term) |

---

## 2. Key sources (cited)

1. **Motoike & Yoshikawa / Gorecka et al.** — Logical functions and coincidence detection on excitable chemical media (cross junctions; BZ).  
   - Gorecka & Gorecki, *J. Phys. Chem. A* (cross-junction coincidence). DOI: [10.1021/jp011072v](https://doi.org/10.1021/jp011072v)  
   - Gorecki et al., “Direction Detector on an Excitable Field” (arXiv:nlin/0405063).

2. **Adamatzky et al.** — Reaction–diffusion computers; geometrically constrained BZ logic, coincidence detectors, adders.  
   - Survey context in *Phil. Trans. R. Soc. A* chemical computing (DOI: [10.1098/rsta.2014.0219](https://doi.org/10.1098/rsta.2014.0219)); arXiv:1006.1900 compartmentalised BZ.

3. **Parunak / Sauter et al.** — Digital pheromones as stigmergic scalar fields (deposit, evaporate, propagate) for multi-agent coordination.  
   - WSC 2009 pheromone-as-probability-fields; AIAA digital-pheromone swarming demos.

4. **Hauser / morphological & reservoir computing** — Physical dynamics as a computational reservoir; separate trained or fixed readout.  
   - e.g. reservoir view of morphological computation; spatial physical reservoirs (Phys. Rev. Applied 20, 044057).

5. **Grassé (stigmergy)** — Classical ethological root of environment-mediated coordination (cited via pheromone literature).

---

## 3. Mapping Task 8 operations to prior art

| Operation | Closest prior art | Task 8 distinction |
|---|---|---|
| A Coincidence / AND latch | Excitable-media coincidence gates; RD AND junctions | **Bistable reaction-telegraph** scalar field with high-basin decoder; agent-deposit encoding; explicit linear / readout-only / no-prop ablations in `sim_world` |
| B Temporal integration | Time-window coincidence in excitable junctions | Finite memory window under bistable telegraph; order discrimination **not** claimed (aligns with Task 7 temporal failure) |
| C Spatial discrimination | Pattern geometry in RD / pheromone fields | Equal-mass cluster vs dispersed under fixed total amplitude |
| D Threshold / hysteresis | Bistable switching, Schmitt-trigger analogues | Quantified forward amp and reverse drop on implemented cubic reaction |
| E Conflict | Signed superposition; multi-flavor pheromones | Scalar polarity cancel = linear; **no** multi-semantic channels |
| F “Completion” | Attractor recovery / associative memory | Demonstrated **attractor retention after damage**, not multi-feature pattern completion |

---

## 4. Novelty assessment (disciplined)

**Not claimed:** Unprecedented invention of field computation, stigmergy, or bistable logic.

**Supported contribution type:**

1. **Implementation + characterization** of a reaction-telegraph bistable substrate inside the SXC-IGC `sim_world` stack.  
2. **Operating-regime map** (amp × separation response surface; temporal window; equal-mass spatial tests).  
3. **Causal ablation suite** separating reaction nonlinearity from linear telegraph, readout-only peak detection, and (for overlapping deposits) propagation.  
4. **Methodological correction:** high-basin threshold (θ=0.85) so coincidence is not credited to instantaneous deposit overlap (Task 7 thr=0.40 confound relative to peak0).  
5. **Behavioural bridge** showing agents can use the latch without symbolic messaging, while honestly retaining that symbolic baselines still achieve F1=1.0.

**Not supported:** Level-5 “distinctive architectural superiority” over matched conventional systems. Messaging/blackboard/symbolic distance remain competitively sufficient for the tested tasks (Task 7 T9; Task 8 symbolic baseline).

---

## 5. Literature gaps / outstanding

- Formal comparison to FitzHugh–Nagumo / Oregonator gate libraries on identical task batteries.  
- Multi-channel / multi-flavor fields for semantic conflict (beyond signed scalar cancel).  
- Learned readouts (reservoir-style) vs fixed threshold decoders.
