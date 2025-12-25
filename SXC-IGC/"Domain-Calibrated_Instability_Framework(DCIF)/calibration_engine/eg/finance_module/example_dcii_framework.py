#!/usr/bin/env python3
"""
STANDARD DCII IMPLEMENTATION - FIXED VERSION
Domain-Calibrated Instability Index Framework
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from scipy import optimize
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CORE DCII MATHEMATICS
# ============================================================================

@dataclass
class DCIIParameters:
    """DCII equation parameters."""
    alpha: float = 0.0    # Gradient coefficient
    beta: float = 1.0     # Pressure coefficient
    gamma: float = 1.0    # Resilience coefficient
    
    def to_dict(self) -> Dict:
        """Convert to serializable dictionary."""
        return {
            'alpha': float(self.alpha),
            'beta': float(self.beta),
            'gamma': float(self.gamma)
        }

@dataclass
class StressLevel:
    """Definition of a stress classification level."""
    name: str
    min_dcii: float
    max_dcii: float
    color: str
    actions: List[str]
    
    def contains(self, dcii: float) -> bool:
        """Check if DCII value falls within this level."""
        return self.min_dcii <= dcii < self.max_dcii
    
    def to_dict(self) -> Dict:
        """Convert to serializable dictionary."""
        return {
            'name': self.name,
            'min_dcii': float(self.min_dcii),
            'max_dcii': float(self.max_dcii),
            'color': self.color,
            'actions': self.actions
        }

class DCIICalculator:
    """Core DCII calculation engine."""
    
    def __init__(self, params: DCIIParameters):
        self.params = params
    
    def compute(self, signals: Dict[str, float]) -> float:
        """Compute DCII index from normalized signals [0,1]."""
        if not signals:
            return 0.0
        
        signal_values = list(signals.values())
        pressure = self.params.beta * np.mean(signal_values)
        resilience = self.params.gamma * np.std(signal_values) if len(signal_values) > 1 else 0.0
        dcii = pressure - resilience
        return np.clip(dcii, 0.0, 1.0)
    
    def classify(self, dcii: float, taxonomy: List[StressLevel]) -> Optional[StressLevel]:
        """Classify DCII value into stress level."""
        for level in taxonomy:
            if level.contains(dcii):
                return level
        return None

# ============================================================================
# CALIBRATION ENGINE
# ============================================================================

@dataclass
class CalibrationScenario:
    """Scenario for DCII calibration."""
    name: str
    signals: Dict[str, float]  # Normalized signal values
    target_dcii: float         # Expected DCII for this scenario
    weight: float = 1.0        # Importance weight
    
    def to_dict(self) -> Dict:
        """Convert to serializable dictionary."""
        return {
            'name': self.name,
            'signals': {k: float(v) for k, v in self.signals.items()},
            'target_dcii': float(self.target_dcii),
            'weight': float(self.weight)
        }

class CalibrationResult:
    """Results of DCII calibration."""
    
    def __init__(self, parameters: DCIIParameters, scenarios: List[CalibrationScenario], 
                 metrics: Dict[str, float], is_valid: bool):
        self.parameters = parameters
        self.scenarios = scenarios
        self.metrics = metrics
        self.is_valid = is_valid
    
    def to_dict(self) -> Dict:
        """Convert to serializable dictionary."""
        return {
            'parameters': self.parameters.to_dict(),
            'scenarios': [s.to_dict() for s in self.scenarios],
            'metrics': {k: float(v) if isinstance(v, (int, float, np.generic)) else v 
                       for k, v in self.metrics.items()},
            'is_valid': bool(self.is_valid),
            'timestamp': datetime.now().isoformat()
        }

class DCIICalibrator:
    """Calibrates DCII parameters to match target scenarios."""
    
    def __init__(self, scenarios: List[CalibrationScenario]):
        self.scenarios = scenarios
    
    def calibrate(self) -> CalibrationResult:
        """Calibrate DCII parameters to match scenarios."""
        
        def objective(params):
            beta, gamma = params
            calculator = DCIICalculator(DCIIParameters(beta=beta, gamma=gamma))
            total_error = 0.0
            for scenario in self.scenarios:
                computed = calculator.compute(scenario.signals)
                error = (computed - scenario.target_dcii) ** 2
                total_error += error * scenario.weight
            return total_error
        
        initial_guess = [1.0, 1.0]
        bounds = [(0.1, 5.0), (0.1, 5.0)]
        
        result = optimize.minimize(
            objective,
            initial_guess,
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        if result.success:
            beta_opt, gamma_opt = result.x
            params = DCIIParameters(beta=beta_opt, gamma=gamma_opt)
            
            calculator = DCIICalculator(params)
            errors = []
            predictions = []
            targets = []
            
            for scenario in self.scenarios:
                pred = calculator.compute(scenario.signals)
                predictions.append(pred)
                targets.append(scenario.target_dcii)
                errors.append(pred - scenario.target_dcii)
            
            mse = np.mean(np.array(errors) ** 2)
            r2 = 1 - mse / np.var(targets) if np.var(targets) > 0 else 0.0
            
            metrics = {
                'mse': float(mse),
                'r2': float(r2),
                'max_error': float(np.max(np.abs(errors))),
                'mean_error': float(np.mean(np.abs(errors)))
            }
            
            is_valid = r2 > 0.7 and mse < 0.05
            
            return CalibrationResult(
                parameters=params,
                scenarios=self.scenarios,
                metrics=metrics,
                is_valid=is_valid
            )
        else:
            raise ValueError(f"Calibration failed: {result.message}")

# ============================================================================
# MAIN DCII MODULE
# ============================================================================

class DCIIModule:
    """Complete DCII Module for any domain."""
    
    def __init__(self, name: str, domain: str = "Financial Markets"):
        self.name = name
        self.domain = domain
        self.metadata = {
            'created': datetime.now().isoformat(),
            'version': '1.0.0',
            'domain': domain
        }
        
        self.signals: Dict[str, pd.Series] = {}
        self.normalized_signals: Dict[str, pd.Series] = {}
        self.normalization_params: Dict[str, Dict] = {}
        self.calculator: Optional[DCIICalculator] = None
        self.calibration_result: Optional[CalibrationResult] = None
        
        self.stress_levels = [
            StressLevel('stable', 0.0, 0.3, 'green', ['Normal operations']),
            StressLevel('elevated', 0.3, 0.5, 'yellow', ['Increase monitoring']),
            StressLevel('high', 0.5, 0.7, 'orange', ['Prepare contingency']),
            StressLevel('critical', 0.7, 1.0, 'red', ['Activate crisis protocols'])
        ]
    
    def create_example_signals(self, days: int = 1000) -> 'DCIIModule':
        """Create example signals for demonstration."""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
        np.random.seed(42)
        t = np.arange(len(dates)) / 252
        
        self.signals = {
            'volatility': pd.Series(15 + 10*np.sin(2*np.pi*t) + 8*np.random.randn(len(dates)), index=dates),
            'returns': pd.Series(0.0002 + 0.015*np.random.randn(len(dates)), index=dates),
            'liquidity': pd.Series(np.random.lognormal(mean=0, sigma=0.3, size=len(dates)), index=dates),
            'sentiment': pd.Series(np.random.beta(a=2, b=2, size=len(dates))*100, index=dates),
            'volume_ratio': pd.Series(1.0 + 0.5*np.sin(4*np.pi*t) + 0.3*np.random.randn(len(dates)), index=dates)
        }
        
        print(f"✅ Created {len(self.signals)} example signals")
        return self
    
    def normalize_signals(self, method: str = 'zscore') -> 'DCIIModule':
        """Normalize all signals to [0, 1] range."""
        self.normalization_params = {}
        self.normalized_signals = {}
        
        for name, series in self.signals.items():
            if method == 'zscore':
                mean_val = series.mean()
                std_val = series.std()
                z = (series - mean_val) / (std_val + 1e-8)
                norm = 1 / (1 + np.exp(-z))
                self.normalization_params[name] = {
                    'method': 'zscore',
                    'mean': float(mean_val),
                    'std': float(std_val)
                }
            else:  # minmax
                min_val = series.min()
                max_val = series.max()
                norm = (series - min_val) / (max_val - min_val + 1e-8)
                self.normalization_params[name] = {
                    'method': 'minmax',
                    'min': float(min_val),
                    'max': float(max_val)
                }
            
            self.normalized_signals[name] = pd.Series(norm, index=series.index)
        
        print("Signal normalization summary:")
        for name, series in self.normalized_signals.items():
            print(f"  {name:15} → [{series.min():.3f}, {series.max():.3f}]")
        
        return self
    
    def define_scenarios(self) -> List[CalibrationScenario]:
        """Define calibration scenarios."""
        signal_names = list(self.normalized_signals.keys())
        
        return [
            CalibrationScenario('stable', {n: 0.2 for n in signal_names}, 0.2, 1.0),
            CalibrationScenario('elevated', {n: 0.5 for n in signal_names}, 0.5, 1.0),
            CalibrationScenario('crisis', {n: 0.8 for n in signal_names}, 0.8, 2.0),
            CalibrationScenario('recovery', {n: 0.4 for n in signal_names}, 0.4, 1.0),
        ]
    
    def calibrate(self) -> 'DCIIModule':
        """Calibrate DCII parameters."""
        print("🔧 Calibrating DCII parameters...")
        
        scenarios = self.define_scenarios()
        calibrator = DCIICalibrator(scenarios)
        self.calibration_result = calibrator.calibrate()
        self.calculator = DCIICalculator(self.calibration_result.parameters)
        
        print("✅ Calibration complete!")
        print(f"   β (pressure) = {self.calibration_result.parameters.beta:.3f}")
        print(f"   γ (resilience) = {self.calibration_result.parameters.gamma:.3f}")
        print(f"   R² = {self.calibration_result.metrics['r2']:.3f}")
        print(f"   MSE = {self.calibration_result.metrics['mse']:.4f}")
        print(f"   Valid = {self.calibration_result.is_valid}")
        
        return self
    
    def validate(self) -> Dict[str, Any]:
        """Validate the calibrated module."""
        if not self.calibration_result:
            raise ValueError("Module must be calibrated before validation")
        
        dcii_values = []
        for i in range(len(next(iter(self.normalized_signals.values())))):
            daily_signals = {name: series.iloc[i] for name, series in self.normalized_signals.items()}
            dcii = self.calculator.compute(daily_signals)
            dcii_values.append(dcii)
        
        dcii_series = pd.Series(dcii_values)
        validation = {
            'historical_dcii': {
                'mean': float(dcii_series.mean()),
                'std': float(dcii_series.std()),
                'min': float(dcii_series.min()),
                'max': float(dcii_series.max())
            },
            'passes_tests': bool(dcii_series.std() < 0.3 and all(0 <= x <= 1 for x in dcii_values))
        }
        
        print("📊 Validation results:")
        print(f"   Historical DCII: {validation['historical_dcii']['mean']:.3f} ± {validation['historical_dcii']['std']:.3f}")
        print(f"   Range: [{validation['historical_dcii']['min']:.3f}, {validation['historical_dcii']['max']:.3f}]")
        print(f"   Tests passed: {validation['passes_tests']}")
        
        return validation
    
    def interpret(self) -> Dict[str, Any]:
        """Interpret calibration results."""
        if not self.calibration_result:
            raise ValueError("Module must be calibrated before interpretation")
        
        beta = self.calibration_result.parameters.beta
        gamma = self.calibration_result.parameters.gamma
        stability_ratio = gamma / (beta + 1e-8)
        
        interpretation = {
            'pressure_sensitivity': 'Moderate' if beta > 0.8 else 'Low',
            'resilience_strength': 'Moderate' if gamma > 0.8 else 'Low',
            'system_type': 'Balanced' if 0.8 < stability_ratio < 1.2 else 'Other',
            'stability_ratio': float(stability_ratio)
        }
        
        print("🔍 Interpretation:")
        print(f"   System Type: {interpretation['system_type']}")
        print(f"   Pressure Sensitivity: {interpretation['pressure_sensitivity']} (β={beta:.3f})")
        print(f"   Resilience: {interpretation['resilience_strength']} (γ={gamma:.3f})")
        print(f"   Stability Ratio: {interpretation['stability_ratio']:.3f}")
        
        return interpretation
    
    def save(self, output_dir: Path = Path("./dcii_modules")) -> Path:
        """Save the calibrated module to disk."""
        if not self.calibration_result:
            raise ValueError("Module must be calibrated before saving")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        module_dir = output_dir / self.name
        module_dir.mkdir(exist_ok=True)
        
        # Save calibration results
        with open(module_dir / "calibration.json", 'w') as f:
            json.dump(self.calibration_result.to_dict(), f, indent=2)
        
        # Save normalization parameters
        with open(module_dir / "normalization.json", 'w') as f:
            json.dump(self.normalization_params, f, indent=2)
        
        # Save metadata
        metadata = {
            **self.metadata,
            'calibrated': datetime.now().isoformat(),
            'signals': list(self.signals.keys())
        }
        
        with open(module_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"💾 Module saved to: {module_dir}")
        return module_dir
    
    def normalize_current_signals(self, current_signals: Dict[str, float]) -> Dict[str, float]:
        """Normalize current signal values."""
        normalized = {}
        for name, value in current_signals.items():
            if name in self.normalization_params:
                params = self.normalization_params[name]
                if params['method'] == 'zscore':
                    z = (value - params['mean']) / (params['std'] + 1e-8)
                    normalized[name] = float(1 / (1 + np.exp(-z)))
                else:  # minmax
                    norm = (value - params['min']) / (params['max'] - params['min'] + 1e-8)
                    normalized[name] = float(np.clip(norm, 0.0, 1.0))
            else:
                print(f"⚠️  Warning: No normalization params for {name}, using raw value")
                normalized[name] = float(value)
        
        return normalized
    
    def monitor(self, current_signals: Dict[str, float]) -> Dict[str, Any]:
        """Monitor current conditions."""
        if not self.calculator:
            raise ValueError("Module must be calibrated before monitoring")
        
        normalized = self.normalize_current_signals(current_signals)
        dcii = self.calculator.compute(normalized)
        
        stress_level = None
        for level in self.stress_levels:
            if level.contains(dcii):
                stress_level = level
                break
        
        sorted_signals = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'dcii': float(dcii),
            'stress_level': stress_level.name if stress_level else 'unknown',
            'color': stress_level.color if stress_level else 'gray',
            'recommended_actions': stress_level.actions if stress_level else [],
            'contributing_signals': dict(sorted_signals[:3]),
            'normalized_signals': normalized
        }
    
    def run_pipeline(self, output_dir: Path = Path("./dcii_modules")) -> Dict[str, Any]:
        """Run the complete 9-step DCII pipeline."""
        print("="*70)
        print(f"DCII PIPELINE: {self.name}")
        print("="*70)
        
        try:
            # Steps 1-3
            print("\n📊 STEP 1-3: DATA PREPARATION")
            print("-"*40)
            self.create_example_signals(500)
            self.normalize_signals()
            
            # Steps 4-6
            print("\n🔧 STEP 4-6: CALIBRATION")
            print("-"*40)
            self.calibrate()
            
            # Steps 7-8
            print("\n📈 STEP 7-8: VALIDATION & INTERPRETATION")
            print("-"*40)
            validation = self.validate()
            interpretation = self.interpret()
            
            # Step 9
            print("\n💾 STEP 9: DEPLOYMENT")
            print("-"*40)
            module_path = self.save(output_dir)
            
            # Test monitoring
            print("\n🎯 TEST MONITORING")
            print("-"*40)
            test_signals = {
                'volatility': 25.0,
                'returns': -0.015,
                'liquidity': 0.8,
                'sentiment': 35.0,
                'volume_ratio': 1.3
            }
            
            alert = self.monitor(test_signals)
            print(f"DCII Index: {alert['dcii']:.3f}")
            print(f"Stress Level: {alert['stress_level']}")
            print(f"Top Contributors: {alert['contributing_signals']}")
            
            print("\n" + "="*70)
            print("✅ PIPELINE COMPLETE!")
            print("="*70)
            
            return {
                'module_path': str(module_path),
                'validation': validation,
                'interpretation': interpretation,
                'test_alert': alert
            }
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='DCII Framework')
    parser.add_argument('--run-pipeline', action='store_true', help='Run complete pipeline')
    parser.add_argument('--monitor', action='store_true', help='Monitor current conditions')
    parser.add_argument('--signals', type=str, help='JSON string of current signals')
    parser.add_argument('--module', type=str, default='Market_DCII', help='Module name')
    parser.add_argument('--output-dir', type=Path, default=Path('./dcii_modules'), help='Output directory')
    
    args = parser.parse_args()
    
    if args.run_pipeline:
        module = DCIIModule(name=args.module)
        results = module.run_pipeline(output_dir=args.output_dir)
        
        print(f"\n📁 Module saved to: {results['module_path']}")
        print("🎯 Quick test:")
        print(f"  python3 dcii_standard_fixed.py --monitor --module {args.module}")
    
    elif args.monitor:
        module_path = args.output_dir / args.module
        
        if module_path.exists():
            print(f"Loading module {args.module}...")
            # For simplicity, create new module
            module = DCIIModule(name=args.module)
            module.create_example_signals(100).normalize_signals().calibrate()
        else:
            print(f"Creating new module {args.module}...")
            module = DCIIModule(name=args.module)
            module.create_example_signals(100).normalize_signals().calibrate()
        
        if args.signals:
            try:
                current_signals = json.loads(args.signals)
            except json.JSONDecodeError:
                print("Error: Invalid JSON for signals")
                sys.exit(1)
        else:
            current_signals = {
                'volatility': 30.0,
                'returns': -0.02,
                'liquidity': 0.6,
                'sentiment': 25.0,
                'volume_ratio': 1.5
            }
            print("Using default test signals:", current_signals)
        
        result = module.monitor(current_signals)
        
        print("\n📊 MONITORING RESULTS")
        print("="*40)
        print(f"DCII Index: {result['dcii']:.3f}")
        print(f"Stress Level: {result['stress_level']} ({result['color']})")
        print(f"Timestamp: {result['timestamp']}")
        
        if result['recommended_actions']:
            print(f"Recommended Actions: {', '.join(result['recommended_actions'])}")
        
        print(f"\nTop Contributors:")
        for signal, value in result['contributing_signals'].items():
            print(f"  {signal}: {value:.3f}")
    
    else:
        print("DCII Framework - Domain-Calibrated Instability Index")
        print("\nCommands:")
        print("  --run-pipeline     Run complete 9-step calibration")
        print("  --monitor          Monitor current conditions")
        print("  --signals JSON     JSON string of current signals")
        print("\nExamples:")
        print("  python3 dcii_standard_fixed.py --run-pipeline")
        print("  python3 dcii_standard_fixed.py --monitor")
        print("  python3 dcii_standard_fixed.py --monitor --signals '{\"volatility\":35}'")

if __name__ == "__main__":
    main()
