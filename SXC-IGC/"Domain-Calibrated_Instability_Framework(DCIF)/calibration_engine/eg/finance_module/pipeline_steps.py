"""
Pipeline Steps 3-6
Normalization, target states, taxonomy, and calibration
"""

import numpy as np
import pandas as pd
from scipy import optimize

def normalize_signals(self, method: str = 'zscore'):
    """Step 3: Normalize signals to [0,1] range."""
    self.normalized_signals = {}
    self.normalization_params = {}
    
    for name, series in self.signals.items():
        if method == 'zscore':
            # Z-score then sigmoid to [0,1]
            z_score = (series - series.mean()) / (series.std() + 1e-8)
            normalized = 1 / (1 + np.exp(-z_score))
            self.normalization_params[name] = {
                'method': 'zscore',
                'mean': float(series.mean()),
                'std': float(series.std())
            }
        elif method == 'minmax':
            # Min-max scaling
            min_val, max_val = series.min(), series.max()
            normalized = (series - min_val) / (max_val - min_val + 1e-8)
            self.normalization_params[name] = {
                'method': 'minmax',
                'min': float(min_val),
                'max': float(max_val)
            }
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        self.normalized_signals[name] = pd.Series(normalized, index=series.index)
    
    print("STEP 3: SIGNAL NORMALIZATION")
    print("-"*70)
    print(f"Normalization method: {method}")
    for name, series in self.normalized_signals.items():
        print(f"  {name:20} | min: {series.min():5.3f} | max: {series.max():5.3f}")
    print()
    return self.normalized_signals

def define_target_states(self):
    """Step 4: Define target DCII states for different scenarios."""
    # Define reference scenarios for calibration
    self.scenarios = {
        # Stable market conditions
        'stable': StressScenario(
            name='stable',
            signals={name: 0.2 for name in self.normalized_signals.keys()},
            target_dcii=0.2,
            weight=1.0
        ),
        # Elevated stress
        'elevated': StressScenario(
            name='elevated',
            signals={name: 0.5 for name in self.normalized_signals.keys()},
            target_dcii=0.5,
            weight=1.0
        ),
        # Crisis conditions
        'crisis': StressScenario(
            name='crisis',
            signals={name: 0.8 for name in self.normalized_signals.keys()},
            target_dcii=0.8,
            weight=2.0  # Higher weight for crisis scenarios
        ),
        # Recovery phase
        'recovery': StressScenario(
            name='recovery',
            signals={name: 0.4 for name in self.normalized_signals.keys()},
            target_dcii=0.4,
            weight=1.0
        ),
    }
    
    print("STEP 4: TARGET STATE DEFINITION")
    print("-"*70)
    for name, scenario in self.scenarios.items():
        print(f"  {name:10} | Target DCII: {scenario.target_dcii:.2f} | Weight: {scenario.weight:.1f}")
    print()
    return self.scenarios

def classify_stress_taxonomy(self):
    """Step 5: Classify stress levels based on DCII values."""
    self.stress_taxonomy = {
        'stable': {
            'range': (0.0, 0.3),
            'color': 'green',
            'actions': ['Normal monitoring', 'Regular operations']
        },
        'elevated': {
            'range': (0.3, 0.5),
            'color': 'yellow',
            'actions': ['Increase monitoring', 'Review positions']
        },
        'high': {
            'range': (0.5, 0.7),
            'color': 'orange',
            'actions': ['Prepare contingency', 'Reduce risk']
        },
        'critical': {
            'range': (0.7, 1.0),
            'color': 'red',
            'actions': ['Crisis protocols', 'Liquidate non-essential']
        }
    }
    
    print("STEP 5: STRESS TAXONOMY CLASSIFICATION")
    print("-"*70)
    for level, info in self.stress_taxonomy.items():
        low, high = info['range']
        print(f"  {level:10} | DCII: {low:.1f}-{high:.1f} | Actions: {info['actions'][0]}")
    print()
    return self.stress_taxonomy

def calibrate_coefficients(self):
    """Step 6: Calibrate α, β, γ coefficients to match target states."""
    
    def objective(params):
        """Objective function to minimize."""
        beta, gamma = params
        alpha = 0.0  # Fixed for now
        
        total_error = 0.0
        eq = DCIIEquation(alpha=alpha, beta=beta, gamma=gamma)
        
        for scenario in self.scenarios.values():
            computed = eq.compute(scenario.signals)
            error = (computed - scenario.target_dcii) ** 2
            total_error += error * scenario.weight
        
        return total_error
    
    # Initial guess and bounds
    initial_guess = [1.0, 1.0]
    bounds = [(0.1, 5.0), (0.1, 5.0)]
    
    # Optimize
    result = optimize.minimize(
        objective,
        initial_guess,
        bounds=bounds,
        method='L-BFGS-B'
    )
    
    if result.success:
        beta_opt, gamma_opt = result.x
        alpha_opt = 0.0
        
        self.coefficients = {
            'alpha': float(alpha_opt),
            'beta': float(beta_opt),
            'gamma': float(gamma_opt)
        }
        
        # Update equation
        self.dcii_equation = DCIIEquation(
            alpha=alpha_opt,
            beta=beta_opt,
            gamma=gamma_opt
        )
        
        # Calculate validation metrics
        errors = []
        for scenario in self.scenarios.values():
            computed = self.dcii_equation.compute(scenario.signals)
            errors.append(computed - scenario.target_dcii)
        
        mse = np.mean(np.array(errors) ** 2)
        r2 = 1 - mse / np.var([s.target_dcii for s in self.scenarios.values()])
        
        self.calibration_result = CalibrationResult(
            beta=beta_opt,
            gamma=gamma_opt,
            alpha=alpha_opt,
            r_squared=float(r2),
            mse=float(mse),
            is_valid=r2 > 0.8 and mse < 0.05
        )
        
        print("STEP 6: COEFFICIENT CALIBRATION")
        print("-"*70)
        print(f"✅ Calibration successful!")
        print(f"   β (pressure coefficient): {beta_opt:.4f}")
        print(f"   γ (resilience coefficient): {gamma_opt:.4f}")
        print(f"   α (gradient coefficient): {alpha_opt:.4f} (fixed)")
        print(f"   R²: {r2:.4f}")
        print(f"   MSE: {mse:.6f}")
        print(f"   Validation: {'PASS' if self.calibration_result.is_valid else 'FAIL'}")
        print()
        
        # Show scenario matches
        print("Scenario validation:")
        for name, scenario in self.scenarios.items():
            computed = self.dcii_equation.compute(scenario.signals)
            print(f"  {name:10} | Target: {scenario.target_dcii:.3f} | "
                  f"Computed: {computed:.3f} | "
                  f"Error: {abs(computed - scenario.target_dcii):.4f}")
        print()
    else:
        print("❌ Calibration failed!")
        print(result.message)
    
    return self.calibration_result
