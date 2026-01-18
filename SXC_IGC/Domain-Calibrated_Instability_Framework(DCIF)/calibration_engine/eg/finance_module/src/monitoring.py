"""
Real-time Monitoring and Utilities
"""

import math
from datetime import datetime
from typing import Dict, Any

def monitor_real_time(self, current_signals: Dict[str, float]) -> Dict[str, Any]:
    """
    Monitor real-time market conditions using calibrated DCII module.
    
    Parameters:
    -----------
    current_signals : Dict[str, float]
        Current values of all defined signals
        
    Returns:
    --------
    Dict containing:
        - dcii_index: Current DCII stress level (0-1)
        - stress_level: Classification (Stable/Elevated/High/Critical)
        - contributing_factors: Which signals are driving stress
        - recommendation: Suggested actions
    """
    # Normalize current signals
    normalized = {}
    signal_contributions = {}
    
    for signal_name, value in current_signals.items():
        if signal_name in self.normalization_params:
            params = self.normalization_params[signal_name]
            
            if params['method'] == 'zscore':
                z_score = (value - params['mean']) / (params['std'] + 1e-8)
                norm_value = 1 / (1 + math.exp(-z_score))
            elif params['method'] == 'minmax':
                norm_value = (value - params['min']) / (params['max'] - params['min'] + 1e-8)
            else:
                norm_value = value
            
            normalized[signal_name] = norm_value
            # Contribution is normalized value times beta
            signal_contributions[signal_name] = norm_value * self.coefficients.get('beta', 1.0)
    
    # Calculate DCII
    dcii = self.dcii_equation.compute(normalized)
    
    # Classify stress level
    if dcii < 0.3:
        stress_level = "Stable"
        recommendation = "Normal operations"
    elif dcii < 0.5:
        stress_level = "Elevated"
        recommendation = "Increase monitoring, review positions"
    elif dcii < 0.7:
        stress_level = "High"
        recommendation = "Prepare contingency plans, reduce risk exposure"
    else:
        stress_level = "Critical"
        recommendation = "Activate crisis protocols, consider liquidation"
    
    # Identify top contributors
    sorted_contributors = sorted(
        signal_contributions.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    return {
        'dcii_index': float(dcii),
        'stress_level': stress_level,
        'contributing_factors': dict(sorted_contributors),
        'recommendation': recommendation,
        'timestamp': datetime.now().isoformat(),
        'normalized_signals': normalized
    }

def run_full_pipeline(self, output_dir: Path = None) -> Dict[str, any]:
    """
    Run the complete 9-step DCII pipeline.
    """
    if output_dir is None:
        output_dir = Path.cwd() / "output"
    
    print("="*70)
    print("DCII FRAMEWORK: COMPLETE FINANCE MODULE EXAMPLE")
    print("="*70)
    print()
    
    # Update calibration date
    self.metadata['calibration_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Execute all steps
    self.define_domain()
    self.define_signals()
    self.normalize_signals()
    self.define_target_states()
    self.classify_stress_taxonomy()
    self.calibrate_coefficients()
    
    if self.calibration_result and self.calibration_result.is_valid:
        validation_metrics = self.validate_module()
        interpretation = self.interpret_results()
        module_path = self.package_module(output_dir)
    else:
        print("❌ Calibration failed. Cannot proceed with validation.")
        return {}
    
    # Summary
    print("="*70)
    print("PIPELINE COMPLETE: MODULE READY FOR USE")
    print("="*70)
    print(f"Module: {self.name}")
    print(f"Location: {module_path}")
    print(f"Coefficients: β={self.coefficients['beta']:.4f}, γ={self.coefficients['gamma']:.4f}")
    if interpretation:
        print(f"Classification: {interpretation.get('classification', 'N/A')}")
    print(f"Validation: {'PASSED' if self.calibration_result.is_valid else 'WARNINGS'}")
    print()
    print("Next: Replace simulated signals with real market data.")
    print("      Test module on historical crisis periods.")
    print()
    
    return {
        "module": self,
        "coefficients": self.coefficients,
        "validation": validation_metrics,
        "interpretation": interpretation,
        "output_path": module_path
    }
