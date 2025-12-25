"""
Pipeline Steps 7-9
Validation, interpretation, and packaging
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

def validate_module(self):
    """Step 7: Validate the calibrated module."""
    if not self.calibration_result:
        raise ValueError("Module must be calibrated before validation")
    
    # Generate test signals
    test_dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='B')
    n_test = len(test_dates)
    
    test_signals = {}
    for name in self.signals.keys():
        # Create test data with different characteristics
        test_signals[name] = pd.Series(
            np.random.randn(n_test) * 0.5 + 0.5,  # Different distribution
            index=test_dates
        )
    
    # Calculate DCII on test data
    dcii_values = []
    for i in range(n_test):
        daily_signals = {name: test_signals[name].iloc[i] for name in test_signals.keys()}
        dcii = self.dcii_equation.compute(daily_signals)
        dcii_values.append(dcii)
    
    # Calculate validation metrics
    dcii_series = pd.Series(dcii_values, index=test_dates)
    
    validation_metrics = {
        'test_period': {
            'start': test_dates[0].strftime('%Y-%m-%d'),
            'end': test_dates[-1].strftime('%Y-%m-%d'),
            'days': n_test
        },
        'dcii_statistics': {
            'mean': float(dcii_series.mean()),
            'std': float(dcii_series.std()),
            'min': float(dcii_series.min()),
            'max': float(dcii_series.max()),
            'in_stable_range': float((dcii_series < 0.3).mean()),
            'in_critical_range': float((dcii_series > 0.7).mean())
        },
        'stability_test': dcii_series.std() < 0.2,  # Should be stable
        'boundary_test': all(0 <= x <= 1 for x in dcii_values)
    }
    
    self.calibration_result.validation_metrics = validation_metrics
    
    print("STEP 7: MODULE VALIDATION")
    print("-"*70)
    print(f"Test period: {validation_metrics['test_period']['start']} to "
          f"{validation_metrics['test_period']['end']}")
    print(f"DCII Statistics:")
    stats = validation_metrics['dcii_statistics']
    print(f"  Mean: {stats['mean']:.3f} | Std: {stats['std']:.3f}")
    print(f"  Min: {stats['min']:.3f} | Max: {stats['max']:.3f}")
    print(f"  % in stable range: {stats['in_stable_range']*100:.1f}%")
    print(f"  % in critical range: {stats['in_critical_range']*100:.1f}%")
    print()
    print(f"✅ Stability test: {'PASS' if validation_metrics['stability_test'] else 'FAIL'}")
    print(f"✅ Boundary test: {'PASS' if validation_metrics['boundary_test'] else 'FAIL'}")
    print()
    
    return validation_metrics

def interpret_results(self):
    """Step 8: Interpret calibration results."""
    if not self.calibration_result:
        raise ValueError("Module must be calibrated before interpretation")
    
    beta = self.coefficients['beta']
    gamma = self.coefficients['gamma']
    
    interpretation = {
        'pressure_sensitivity': 'High' if beta > 2.0 else 'Medium' if beta > 1.0 else 'Low',
        'resilience_effect': 'Strong' if gamma > 2.0 else 'Moderate' if gamma > 1.0 else 'Weak',
        'market_characteristics': [],
        'recommendations': []
    }
    
    # Interpret beta (pressure coefficient)
    if beta > 1.5:
        interpretation['market_characteristics'].append('High sensitivity to stress signals')
        interpretation['recommendations'].append('Use lower thresholds for alerts')
    elif beta < 0.5:
        interpretation['market_characteristics'].append('Low sensitivity to stress signals')
        interpretation['recommendations'].append('May need additional signals')
    
    # Interpret gamma (resilience coefficient)
    if gamma > 1.5:
        interpretation['market_characteristics'].append('Strong diversification benefits')
        interpretation['recommendations'].append('Focus on correlation breakdowns')
    elif gamma < 0.5:
        interpretation['market_characteristics'].append('Weak systemic resilience')
        interpretation['recommendations'].append('Monitor connectedness metrics')
    
    # Overall classification
    stability_ratio = gamma / (beta + 1e-8)
    if stability_ratio > 1.5:
        interpretation['classification'] = 'Resilient System'
    elif stability_ratio > 0.7:
        interpretation['classification'] = 'Balanced System'
    else:
        interpretation['classification'] = 'Fragile System'
    
    print("STEP 8: RESULT INTERPRETATION")
    print("-"*70)
    print(f"System Classification: {interpretation['classification']}")
    print(f"Pressure Sensitivity: {interpretation['pressure_sensitivity']} (β={beta:.3f})")
    print(f"Resilience Effect: {interpretation['resilience_effect']} (γ={gamma:.3f})")
    print(f"Stability Ratio (γ/β): {stability_ratio:.3f}")
    print()
    print("Market Characteristics:")
    for char in interpretation['market_characteristics']:
        print(f"  • {char}")
    print()
    print("Recommendations:")
    for rec in interpretation['recommendations']:
        print(f"  • {rec}")
    print()
    
    return interpretation

def package_module(self, output_dir: Path):
    """Step 9: Package the module for deployment."""
    output_dir.mkdir(parents=True, exist_ok=True)
    module_dir = output_dir / self.name
    module_dir.mkdir(exist_ok=True)
    
    # Save coefficients
    coeff_file = module_dir / "coefficients.json"
    with open(coeff_file, 'w') as f:
        json.dump({
            'coefficients': self.coefficients,
            'calibration_result': {
                'beta': float(self.calibration_result.beta),
                'gamma': float(self.calibration_result.gamma),
                'alpha': float(self.calibration_result.alpha),
                'r_squared': float(self.calibration_result.r_squared),
                'mse': float(self.calibration_result.mse),
                'is_valid': self.calibration_result.is_valid
            },
            'metadata': self.metadata,
            'normalization_params': self.normalization_params
        }, f, indent=2)
    
    # Save signals data
    signals_data = pd.DataFrame(self.normalized_signals)
    signals_file = module_dir / "signals.csv"
    signals_data.to_csv(signals_file)
    
    # Create README
    readme_content = f"""# DCII Module: {self.name}

## Overview
Domain-Calibrated Instability Index module for {self.name}.

## Calibration Results
- β (pressure coefficient): {self.coefficients['beta']:.4f}
- γ (resilience coefficient): {self.coefficients['gamma']:.4f}
- α (gradient coefficient): {self.coefficients['alpha']:.4f}
- R²: {self.calibration_result.r_squared:.4f}
- MSE: {self.calibration_result.mse:.6f}
- Validated: {self.calibration_result.is_valid}

## Signals
{', '.join(self.signals.keys())}

## Usage
```python
from enhanced_dcii_solver import FinanceDCIIModule

# Load your module
module = FinanceDCIIModule()
# Load your real data here
# module.signals = your_real_data
# module.normalize_signals()

# Monitor current conditions
current = {{'vix': 25.0, 'equity_returns': -0.01, ...}}
result = module.monitor_real_time(current)
Limitations

    Simulated signals for demonstration; replace with real market data

    α fixed at 0.0; gradient term |∇ρ| not used in current calibration

    Calibration sensitive to anchor scenario definitions

Generated by DCII Framework v1.0 on {self.metadata['calibration_date'] or datetime.now().strftime('%Y-%m-%d')}
"""
text

with open(module_dir / "README.md", 'w') as f:
    f.write(readme_content)

print("STEP 9: MODULE PACKAGING")
print("-"*70)
print(f"✅ Module packaged at: {module_dir}")
print(f"  - coefficients.json: Calibration results")
print(f"  - signals.csv: Raw and normalized signals")
print(f"  - README.md: Complete documentation")
print()

return module_dir

