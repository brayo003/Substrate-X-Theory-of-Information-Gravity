# METHODS: SUBSTRATE X THEORY VERIFICATION

## Mathematical Foundation
All predictions derive rigorously from the Substrate X Master Equation:

∂s/∂t + ∇·(s v_sub) = αE - β∇·(E v_sub) + γF - σ_irr

With gravitational interaction term:
F_grav = k s v_sub

## Derivation Pathway
1. **Weak-field Limit**: Substrate flow equations reduce to Newtonian gravity
2. **First-order Corrections**: Substrate curvature produces post-Newtonian terms  
3. **Specific Solutions**: Each classical test derived from fundamental equations

## Parameter Usage
- **No tuned parameters**: All calculations use standard physical constants
- **Constants Source**: CODATA 2018 recommended values
- **Orbital Parameters**: From published astronomical ephemerides
- **Uncertainty Propagation**: Standard error analysis applied

## Numerical Implementation
- **Pure Python**: No external numerical solvers beyond scipy constants
- **Explicit Formulas**: All calculations use closed-form expressions
- **Transparent**: Full code provided for independent verification
- **Regression Test**: Script produces consistent results across runs

## Verification Tests
1. **Mercury Precession**: Planetary motion in curved substrate flow
2. **Gravitational Lensing**: Light propagation in substrate medium  
3. **Binary Pulsar**: Energy loss via substrate wave emission

## Future Extensions
- Shapiro time delay calculations
- Gravitational redshift predictions  
- Strong-field regime solutions
- Cosmological applications
