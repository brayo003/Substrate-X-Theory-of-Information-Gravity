# 📖 Build Your First DCII Module
## Domain-Calibrated Instability Index (DCII) Framework Documentation

### **0. Purpose of This Tutorial**

This guide teaches you how to build a **Domain-Calibrated Instability Index (DCII)** module from first principles. By the end, you will have a working, calibrated module that integrates into the SXC-IGC framework.

**Mandatory Principles:**
* No universal constants.
* No cross-domain numeric comparisons.
* No metaphysics.

---

### **1. What DCII Is (and Is Not)**

The framework enforces strict conceptual separation:

| DCII Is:                                                                    | DCII Is Not: |
| :--- | :--- |
| A **calibration-first** instability framework.                           | A universal law or predictor of exact events. |
| A method for detecting escalation and **regime change**.                 | A replacement for deep domain knowledge. |
| Domain-agnostic in structure, **domain-specific in parameters**.         | A generalized regression model. |

The core separation is: **Structure (fixed)**, **Calibration (domain-specific)**, and **Interpretation (taxonomy-based)**.

---

### **2. The Core Equation (Fixed Structure)**

Every DCII module implements the same, fixed instability form. The equation itself **never changes**:

$$
\mathbf{T} = \alpha |\nabla\rho| + \beta \mathbf{E} - \gamma \mathbf{F}
$$

| Symbol         | Meaning             | Role                    | Examples |
| 
| $\mathbf{\rho}$ | Density / concentration | Structural pressure              | Fault stress, Capital concentration, Attention density |
| $|\nabla\rho|$ | Density gradient     | Spatial or network tension           | Migration velocity, Order book imbalance gradient |
| $\mathbf{E}$ | Excitation | Rate of destabilizing activity                   | Moment release rate, Volatility expansion, Posting velocity |
| $\mathbf{F}$ | Damping              | Friction, resistance, stabilization    | Stress margin, Liquidity depth, Moderation/Fatigue |
| $\mathbf{T}$ | Instability Index      | Escalation likelihood                | *The final result of the calibration.* |

**Note:** Only $\mathbf{\alpha}, \mathbf{\beta}, \mathbf{\gamma}$ are calibrated.

---

### **3. Step 1: Define Your Domain System**

Start by clearly defining the system boundary. If you cannot define "instability" operationally (e.g., *“market regime shift”* or *“viral cascade”*) without metaphors, stop here.

---

### **4. Step 2: Define the Three Signals ($\mathbf{\rho}, \mathbf{E}, \mathbf{F}$)**

This is the most critical step. Factors must map physical/systemic reality to the fixed equation structure.

#### **4.1 Excitation ($\mathbf{E}$): The Destabilizer**
$\mathbf{E}$ represents how fast destabilizing energy is injected. It must be **rate-based**, **event-sensitive**, and **spike before** instability, not after.

#### **4.2 Damping ($\mathbf{F}$): The Stabilizer**
$\mathbf{F}$ represents what resists escalation. It must be a **stabilizing force** that opposes $\mathbf{E}$ and is **slowly varying** relative to $\mathbf{E}$. **$\mathbf{F}$ must never be defined as “lack of $\mathbf{E}$”.**

#### **4.3 Density ($\mathbf{\rho}$): The Structural Pressure**
$\mathbf{\rho}$ represents how much "stuff" is packed into the system. It is used to calculate the gradient $|\nabla\rho|$, which measures spatial or network tension.

---

### **5. Step 3: Normalize Signals (Critical)**

DCII requires dimensionless, bounded inputs, typically normalized to the range **[0, 1]**.

* **Rule:** Each signal must be normalized **within its domain**.
* **Forbidden:** Cross-domain scaling or post-hoc rescaling of $\mathbf{T}$.
* *Normalization choices must be documented in the module's README.*

---

### **6. Step 4: Define Target States (Anchoring)**

Calibration requires human-defined anchors ($\mathbf{T}_{\text{target}}$). Targets are **imposed, not learned**.

1.  **Stable State:** System functioning normally. **Target: $\mathbf{T} \approx 0$**
2.  **Escalation State:** Clear regime shift/instability. **Target: $\mathbf{T} \approx 0.5–0.7$**

---

### **7. Step 5: Choose Stress Taxonomy (Classification Only)**

Before calibration, classify the domain structure (e.g., Excitation-dominant, Damping-controlled). This sets expectations for the resulting coefficients but **does not set the parameters**.

* *Example: Social Media is classified as **Excitation-Overwhelming**.*

---

### **8. Step 6: Calibrate $\mathbf{\alpha}, \mathbf{\beta}, \mathbf{\gamma}$**

Calibration solves the linear system $\mathbf{A} \mathbf{x} = \mathbf{b}$ across the defined scenarios using the core solver:

1.  Assemble mean factor values ($\mathbf{E}, \mathbf{F}$) for the Stable and Crisis scenarios.
2.  Call the core function: `solve_dcii_coefficients_two_anchor`.
3.  The output coefficients ($\mathbf{\alpha}, \mathbf{\beta}, \mathbf{\gamma}$) are **domain-local**.

---

### **9. Step 7: Validate the Module**

Validation is mandatory. Test out-of-sample periods and noise injection. The module is successful if $\mathbf{T}$ remains near $0$ in stable regimes and rises smoothly into escalation.

---

### **10. Step 8: Interpret Using Taxonomy**

Confirm coefficient dominance matches the pre-determined stress class.

| Module | $\mathbf{\beta}$ (Excitation) | $\mathbf{\gamma}$ (Damping) | Interpretation |
| :--- | :--- | :--- | :--- |
| **Seismic** | $18.3916$ (Massive) | $0.0403$ (Tiny) | **Excitation-Limited:** Rare, massive amplification required. |
| **Finance** | $3.5605$ (Moderate) | $0.1978$ (Moderate) | **Excitation-Driven:** Volatility dominates, but liquidity provides a measurable defense. |
| **Social** | $3.8296$ (High) | $0.0495$ (Tiny) | **Excitation-Overwhelming:** Damping is structurally weak. |

---

### **11. Step 9: Package the Module**

Your module must follow this structure for integration:
/your_domain_module/ ├── signals.py ├── normalization.py ├── coefficients.json └── README.md

The `README.md` must state the domain definition, signal choices, target anchors, calibration results, and known limitations.

---

### **12. What Makes a Module Valid**

A DCII module is valid if: Signals are measurable, Targets are explicit, Calibration is reproducible, and Behavior matches domain intuition.

**Final Note:** DCII's strength is **controlled escalation detection** under uncertainty. If others can build modules using this tutorial, the framework survives.

