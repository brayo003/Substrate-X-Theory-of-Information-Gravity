Systematic comparison between the documented original theory and the Python implementation. Sources found in the repository:

1. SXC-IGC canonical equation (authoritative_core/governing_equations.md): dx/dt = rx + ax² - bx³. Scalar nonlinear instability normal form. NOT IMPLEMENTED in Python.

2. Three-field substrate theory (field_theory_calibration/substrate_x_results/20251126_180749/theory_definition.json):
  - ∂ρ/∂t = α∇²ρ + βρ(1-ρ) + γEρ + κFρ
  - ∂E/∂t = δ₁ρ - ∇²E + F_coupling - E/τ_E
  - ∂F/∂t = δ₂E - ∇²F - 0.2F³ - F/τ_F
  - Closed feedback: ρ → E → F → ρ
  NOT IMPLEMENTED in Python.

3. Python implementation: τ∂²s/∂t² + ∂s/∂t = c²τ∇²s. Linear. Two variables (s, v=∂s/∂t). No auxiliary fields. No nonlinearity.

Comparison table:
| Mechanism | Theory spec | Python | Status |
|---|---|---|---|
| Substrate field | ρ (nonlinear reaction-diffusion) | s (linear telegraph) | DIFFERENT |
| E-field | ∂E/∂t = δ₁ρ - ∇²E + F_coupling - E/τ_E | Not implemented | MISSING |
| F-field | ∂F/∂t = δ₂E - ∇²F - 0.2F³ - F/τ_F | Not implemented | MISSING |
| Feedback loop | ρ→E→F→ρ | s→v→s (linear) | REDUCED |
| Nonlinearity | βρ(1-ρ), κFρ, -0.2F³ | None | ABSENT |
| SXC-IGC eq | dx/dt = rx+ax²-bx³ | Not implemented | NOT IMPLEMENTED |
| Modal discriminant | Not in original theory | D(k)=4c²τ²k²-1, C_spectral | EXTENSION (not from original) |
| Memory mechanism | Multi-field slow relaxation | Velocity state | DIFFERENT |
| BCs | Neumann (from solver code) | Zero-Laplacian artifact | INCONSISTENT |
| Bistability | Possible (nonlinear system) | Impossible (linear) | ABSENT |

Conclusion: The Python implementation is a linear prototype that captures only the wave-propagation aspect of the original theory. The nonlinear coupling (logistic saturation, field feedback) and the two auxiliary fields (E, F) that enable the multi-timescale memory and potential bistability are not implemented.
