[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18055025.svg)](https://doi.org/10.5281/zenodo.18055025)

SXC-IGC: System Excitation Coordinate – Instability Growth Class
Overview

The SXC-IGC Engine is a deterministic computational framework designed to model complex system dynamics through a non-linear instability law. The framework identifies emergent scaling patterns across physical and biological domains, providing a quantitative metric for system resilience.

Core Discovery: α-Scaling

Validation confirms two distinct scaling regimes, revealing that biological systems possess significantly higher resilience to substrate-induced instability.
Domain	Exponent (α)	Evidence Base	Result
Physical	1.254±0.002	Spacecraft Telemetry (Pioneer/Ulysses)	Anomalous Drift
Biological	0.453±0.015	Lifespan/Stress Dynamics	Enhanced Resilience
Note: Biological systems demonstrate 2.77× greater structural integrity than inanimate physical systems.
Mathematical Foundation (V12)

All validated domains reduce to the core instability equation with a universal saturation bound:
dtdx​=rx+ax2−bx3

Constraints: x≤1.5

  Physical Scaling: α≈1.254

  Biological Scaling: α≈0.453
Repository Structure

  /src/core/: Validated V12 engine implementation.

  /validation/: Cross-domain test results (α logs).

  /docs/: Technical specs and architecture.

  /theoretical/: Unvalidated extensions (Phase 2-7).

Citation & License

MIT License. Citation: Brian K. (brayo003). "SXC-IGC Engine: Universal α-Scaling Framework." 2025. GitHub: https://github.com/brayo003/Substrate-X-Theory-of-Information-Gravity DOI: 10.5281/zenodo.18055025
