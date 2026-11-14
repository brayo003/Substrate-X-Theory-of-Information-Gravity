## Nairobi Module — Cross-Domain Instability Probe (DCIF)

### Purpose of This Directory

This directory contains a **self-contained analytical probe** applied to Nairobi-specific data.  
It is designed for inspection, not persuasion.

The intent is strictly:

- to demonstrate a **generic instability-compression workflow**,
- to show how heterogeneous real-world signals can be **mapped into a reduced tension variable**,
- to allow domain experts to judge whether the **logic, assumptions, and outputs are sane and interpretable**.

---

### What This Module Is

- A **domain-level analytical experiment**
- A **cross-signal reduction exercise**
- A **sanity check on sign structure, anchoring logic, and regime detection**
- A transparent example of how multiple urban indicators can be combined into a single stress/tension measure

Everything here should be readable as an **applied systems analysis**.

---

### What This Module Is NOT

- Not a proof of a new physical theory  
- Not a claim of causal completeness  
- Not a predictive or policy-ready model  
- Not a statistical fit intended to optimize accuracy  
- Not an implementation of a master or governing equation  

Experts should evaluate this as they would:
- a prototype model,
- a reduced-order diagnostic,
- or an exploratory systems-engineering construct.

---

### Conceptual Model (Local to This Directory)

The module uses a **minimal linear tension model**:

    T = β·E − γ·F

Where:
- **E (Excitation)**  
  Signed deviation or disturbance input  
  (e.g., agricultural stress or surplus)

- **F (Friction)**  
  System resistance or damping  
  (e.g., real interest rate / financial drag)

- **T (Tension)**  
  Observable macro-level stress indicator  
  (here proxied by CPI inflation)

This formulation is used **only as a local analytical tool** to check coherence, not as a universal law.

---

### Data Used

#### Agricultural Signal
`agricultural_entropy_base.csv`

- Signed deviations from agricultural baseline
- Positive → disorder / stress
- Negative → ordering / surplus

#### Urban / Financial Signal
`urban_tension_base.csv`, `fintech_tension_base.csv`

- Real interest rates (nominal − inflation)
- Used as a friction proxy

#### Tension Reference
- CPI inflation (%)
- Used solely as an observable system-level stress indicator

Mixed units are intentional; all variables are treated as **normalized, signed indicators**, not physical quantities.

---

### Calibration Logic (`calibrate_nairobi.py`)

Calibration is performed using **two anchor states**:

- **2022** — high stress / disorder phase
- **2024** — stabilization phase

The coefficients β and γ are solved exactly from these anchors.

This step:
- is deterministic, not statistical,
- does not involve curve-fitting,
- exists to test **sign consistency and damping logic**.

The resulting signs and magnitudes are the object of inspection.

---

### Diagnostic Engine (`omega_nairobi.py`)

The Omega engine:

- applies the calibrated relation year-by-year,
- computes instantaneous system tension,
- assigns qualitative regimes based on thresholds.

The regime labels (e.g. “NOMINAL”, “CRITICAL”) are **descriptive flags**, not physical singularities.

This file exists to make system behavior **visible and interpretable**, not to forecast outcomes.

---

### How You Should Read the Results

The primary questions this module invites are:

- Do stress years map to higher computed tension?
- Do recovery years map to lower or negative tension?
- Are sign changes temporally coherent?
- Does friction behave as damping or amplification, and does that interpretation make sense?
- Are the assumptions explicit and critique-able?

Agreement is not required.  
Clarity and interpretability are.

---

### Relationship to the Larger Repository

This directory can be understood **on its own**.

If additional context is desired, readers may start from the repository root and follow documentation outward.  
Nothing here requires acceptance of any broader framework to be evaluated on its own merits.

---

### Summary

This module is a **transparent, limited-scope analytical probe**.

Its value lies in whether experts can:
- understand what is being done,
- trace how inputs map to outputs,
- and judge whether the reasoning is internally coherent.

Nothing more is claimed.

