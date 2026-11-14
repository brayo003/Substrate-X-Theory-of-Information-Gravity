Precise characterization of the information processing limits.

Supported operations (verified):
1. Linear superposition: f(aA+bB) = af(A)+bf(B), error <10⁻¹⁴
2. Spatial low-pass filtering: high-k content decays faster at boundary
3. Temporal low-pass filtering: high-frequency forcing attenuated (ratio∘2.9 at 1Hz vs 60 at 0.05Hz)
4. Spatial memory: 9 spatially distinct histories distinguishable at t=5 (all tested N pass)
5. Mode-selective observation: C_spectral classifies global modal energy fractions
6. Temporal integration: velocity accumulates s changes over history

Unsupported operations (mathematically proven):
1. Nonlinear classification: impossible (superposition holds to 10⁻¹⁵)
2. Bistable storage: impossible (unique equilibrium per IC, proven)
3. Amplitude discrimination: two perturbations of same spatial pattern but different amplitudes produce identical normalized responses
4. Spatial classification via global C_spectral: C_diff=0 for different spatial locations (demonstrated)
5. Gain>1: all modes decay, no amplification
6. Content-addressable retrieval: no attractor network
7. Autonomous transitions: no internal mechanism to produce state jumps without external forcing

Mathematical reason for each limitation:
- (1,2,3) follow from linearity
- (4) follows from C_spectral being a global (spatially averaged) observable
- (5) follows from energy dissipation (γ>0 for all modes)
- (6,7) require multiple stable equilibria, which require nonlinearity

Capacity bounds:
- Spatial memory capacity: ~225 independent positions on 30×30 grid with width-2m perturbations
- Temporal depth: ~4.5 time units (s-dist half-life at tau=3)
- Observable dimension: C_spectral is 1 scalar. Full state is 1800 numbers (s+v for 900 nodes).
- Information bottleneck: compressing 1800 dimensions to 1 scalar loses all spatial information
