# Complete Master Equation of Substrate X Theory
**Final Corrected Form (Causal)**

The complete master equation with all dimensional corrections applied:

$$\tau \frac{\partial^2 s}{\partial t^2} + \frac{\partial s}{\partial t} = c^2 \tau \nabla^2 s - \nabla \cdot (s\mathbf{v}_{\text{sub}} + \chi s \mathbf{u}) + \alpha E + \beta \nabla \cdot (E\mathbf{v}_{\text{sub}}) + \gamma F - \sigma_{\text{irr}}$$

---

### Term-by-Term Breakdown

#### Left-Hand Side: Information Transport
1. **Time Evolution (Causal, Damped)**
   $$\tau \frac{\partial^2 s}{\partial t^2} + \frac{\partial s}{\partial t}$$
   * **s:** Information density (info/m³)
   * **τ:** Damping time constant (s)
   * **Physical meaning:** Telegrapher form with inertia and relaxation

2. **Diffusion**
   $$c^2 \tau \nabla^2 s$$
   * **c:** Speed of light (m/s)
   * **Physical meaning:** Information diffuses with effective diffusivity $D = c^2\tau$

#### Right-Hand Side: Information Transport & Sources
3. **Advection**
   $$-\nabla \cdot (s\mathbf{v}_{\text{sub}})$$
   * **v_sub:** Substrate flow velocity (m/s)
   * **Physical meaning:** Information transported by substrate motion

4. **Coherence Transport**
   $$-\nabla \cdot (\chi s \mathbf{u})$$
   * **χ:** Coherence transport coefficient (m/s)
   * **u:** Coherent propagation direction (unit vector)
   * **Physical meaning:** Directed coherent transport of information

5. **Direct Energy Coupling**
   $$+\alpha E$$
   * **α:** Information–energy coupling constant [info/(J·s)]
   * **E:** Mass–energy density [J/m³]
   * **Physical meaning:** Energy creates information

6. **Energy Flow Coupling**
   $$+\beta \nabla \cdot (E\mathbf{v}_{\text{sub}})$$
   * **β:** Energy flow coupling constant [info·s/J]
   * **Physical meaning:** Energy transport creates information

7. **Force Coupling**
   $$+\gamma F$$
   * **γ:** Force coupling constant [info/(N·s)]
   * **F:** Force density [N/m³]
   * **Physical meaning:** Forces generate information

8. **Irreversible Loss**
   $$-\sigma_{\text{irr}}$$
   * **σ_irr:** Irreversible entropy production rate [info/(m³·s)]
   * **Physical meaning:** Information loss through irreversible processes

---

### Covariant Form
$$\tau \partial_\mu \partial^\mu s + \partial_\mu J^\mu = S - \sigma_{\text{irr}}$$

**where:**
* $J^\mu = (c s, s\mathbf{v}_{\text{sub}} + \chi s \mathbf{u})$
* $S = \alpha E + \beta \nabla \cdot (E\mathbf{v}_{\text{sub}}) + \gamma F$

---

### Key Physical Constants

| Constant | Units | Physical Meaning |
| :--- | :--- | :--- |
| **α** | info/(J·s) | Information per unit energy per time |
| **β** | info·s/J | Information from energy flow |
| **γ** | info/(N·s) | Information from force |
| **χ** | m/s | Coherence speed |
| **τ** | s | Damping time constant |
| **c** | m/s | Causal propagation speed |
| **σ_irr** | info/(m³·s) | Irreversible loss |
| **D = c²τ** | m²/s | Effective diffusivity |

---

### Special Cases

* **Steady State** ($\partial s/\partial t = \partial^2 s/\partial t^2 = 0$)
  $$c^2 \tau \nabla^2 s = \nabla \cdot (s\mathbf{v}_{\text{sub}} + \chi s \mathbf{u}) - \alpha E - \beta \nabla \cdot (E\mathbf{v}_{\text{sub}}) - \gamma F + \sigma_{\text{irr}}$$

* **Weak-Field Limit** ($\nabla^2 s \to 0$, spatial variations small)
  $$\nabla \cdot (s\mathbf{v}_{\text{sub}}) \approx \alpha E$$

* **Diffusion Limit** ($\tau \to 0$)
  $$\frac{\partial s}{\partial t} = D \nabla^2 s - \nabla \cdot (s\mathbf{v}_{\text{sub}} + \chi s \mathbf{u}) + \alpha E + \beta \nabla \cdot (E\mathbf{v}_{\text{sub}}) + \gamma F - \sigma_{\text{irr}}$$
  *where $D = c^2\tau$*

---

### Regularized Forms (Point Mass)

* **Information density:**
  $$s(r) = s_0 \frac{R}{r + R_{\min}}$$

* **Substrate flow:**
  $$\mathbf{v}_{\text{flow}}(r) = -\hat{r} \frac{2GM}{(r + R_{\min})^2}$$
  *with $R_{\min} = \frac{2GM}{c^2}$*

---

### Gravitational Force Law
$$\mathbf{F}_{\text{grav}} = k s \mathbf{v}_{\text{sub}}$$
* **k:** Gravitational coupling constant [kg·m³/(info·s)]
* **k = 2.71 × 10⁻²¹** (empirical calibration)

---

### Decoherence Prediction
$$\Gamma = \Gamma_0 + \frac{k_{\text{rot}} \omega^2}{1 + (\omega/\omega_{\max})^2}$$
* **Γ₀:** Base decoherence rate (s⁻¹)
* **k_rot = 4.5 × 10⁻⁷ s**
* **ω_max ≈ 10⁶ rad/s**

---

### Complete System Summary

**Master equation:**
$$\tau \frac{\partial^2 s}{\partial t^2} + \frac{\partial s}{\partial t} = c^2 \tau \nabla^2 s - \nabla \cdot (s\mathbf{v}_{\text{sub}} + \chi s \mathbf{u}) + \alpha E + \beta \nabla \cdot (E\mathbf{v}_{\text{sub}}) + \gamma F - \sigma_{\text{irr}}$$

**Gravitational force:**
$$\mathbf{F}_{\text{grav}} = k s \mathbf{v}_{\text{sub}}$$
