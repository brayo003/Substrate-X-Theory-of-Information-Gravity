#!/usr/bin/env python3
"""
Q CAPABILITY EXPERIMENT - STATE VARIABLE ANALYSIS
================================================

Phase 1: Backend State Variable Investigation

This script analyzes the existing backend to identify all available state variables
that could potentially serve as Q-like control signals for autonomous AI.
"""

import sys
import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Setup paths
_HERE = os.path.dirname(os.path.abspath(__file__))
_EXPERIMENT_ROOT = os.path.dirname(_HERE)  # q_capability_experiment
_MODULE_ROOT = os.path.dirname(_EXPERIMENT_ROOT)  # substrate_ai_module

for _p in [_HERE, _EXPERIMENT_ROOT, _MODULE_ROOT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class StateVariableDescription:
    """Description of a candidate state variable."""
    name: str
    source: str  # Which component produces it
    type: str    # Type of variable (continuous, discrete, categorical)
    range: str  # Expected range
    update_frequency: str  # When it updates
    theoretical_meaning: str  # What it theoretically represents
    actual_meaning: str  # What it actually computes
    control_potential: str  # High/Medium/Low based on analysis


class BackendStateAnalyzer:
    """Analyze the backend to identify available state variables."""
    
    def __init__(self):
        self.variables: List[StateVariableDescription] = []
        self.analysis_results: Dict[str, Any] = {}
        
    def analyze_component(self, component_name: str, file_path: str) -> Dict[str, Any]:
        """Analyze a specific component file for state variables."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for key patterns
            variables = []
            
            # Check for Q-related variables
            if 'Q' in content or 'q_field' in content:
                variables.append({
                    'name': 'Q',
                    'source': component_name,
                    'type': 'continuous',
                    'theoretical_meaning': 'Transport regime classifier Q = 4c²τ²|∇ln s|² - 1',
                    'control_potential': 'Unknown'
                })
            
            # Check for tension-related variables
            if 'tension' in content:
                variables.append({
                    'name': 'tension',
                    'source': component_name,
                    'type': 'continuous',
                    'theoretical_meaning': 'Problem difficulty/complexity metric',
                    'control_potential': 'Medium'
                })
            
            # Check for regime-related variables
            if 'regime' in content:
                variables.append({
                    'name': 'regime',
                    'source': component_name,
                    'type': 'categorical',
                    'theoretical_meaning': 'Operating regime classification',
                    'control_potential': 'Medium'
                })
            
            # Check for T_sys
            if 'T_sys' in content:
                variables.append({
                    'name': 'T_sys',
                    'source': component_name,
                    'type': 'continuous',
                    'theoretical_meaning': 'System temperature from V12 ODE',
                    'control_potential': 'High'
                })
            
            return {
                'component': component_name,
                'variables_found': len(variables),
                'variables': variables
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {component_name}: {e}")
            return {
                'component': component_name,
                'variables_found': 0,
                'variables': [],
                'error': str(e)
            }
    
    def scan_backend(self) -> Dict[str, Any]:
        """Scan the entire backend for state variables."""
        logger.info("[BackendAnalyzer] Scanning backend for state variables...")
        
        # Key components to analyze
        components_to_analyze = [
            ('unified_governor', 'substrate_ai/components/unified_governor.py'),
            ('cognitive_governor', 'cognitive_governor.py'),
            ('problem_analyzer', 'problem_analyzer.py'),
            ('substrate_core', 'substrate_core.py'),
            ('substrate_ai', 'substrate_ai.py'),
            ('adaptive_thinker', 'adaptive_thinker.py'),
            ('q_field', 'substrate_ai/components/q_field.py'),
        ]
        
        results = {}
        for name, path in components_to_analyze:
            full_path = os.path.join(_MODULE_ROOT, path)
            if os.path.exists(full_path):
                logger.info(f"[BackendAnalyzer] Analyzing {name}...")
                results[name] = self.analyze_component(name, full_path)
            else:
                logger.warning(f"[BackendAnalyzer] {name} not found at {full_path}")
                results[name] = {
                    'component': name,
                    'variables_found': 0,
                    'variables': [],
                    'error': 'File not found'
                }
        
        return results
    
    def identify_candidate_q_variables(self) -> List[StateVariableDescription]:
        """Identify which variables could serve as Q-like control signals."""
        logger.info("[BackendAnalyzer] Identifying candidate Q-like variables...")
        
        candidates = []
        
        # Based on theoretical requirements, Q-like variables should:
        # 1. Be continuous or at least ordinal
        # 2. Have some relationship to system state/dynamics
        # 3. Potentially have predictive/control value
        
        # Candidate 1: Q from QField
        candidates.append(StateVariableDescription(
            name="Q_from_QField",
            source="QField",
            type="continuous",
            range="[-1, 3] (theoretical) or varies (implementation)",
            update_frequency="Per inference cycle",
            theoretical_meaning="Transport regime classifier Q = 4c²τ²|∇ln s|² - 1",
            actual_meaning="Semantic distance between text embeddings (proven by previous audit)",
            control_potential="Low - proven to be semantic distance, not transport dynamics"
        ))
        
        # Candidate 2: T_sys from SXCOmegaEngine
        candidates.append(StateVariableDescription(
            name="T_sys",
            source="SXCOmegaEngine",
            type="continuous",
            range="[0, 1] (normalized)",
            update_frequency="Per ODE timestep",
            theoretical_meaning="System temperature from V12 transport equation",
            actual_meaning="Dynamic state variable from ODE system",
            control_potential="High - dynamic, temporal, has physical basis"
        ))
        
        # Candidate 3: Tension from ProblemAnalyzer
        candidates.append(StateVariableDescription(
            name="tension",
            source="ProblemAnalyzer",
            type="continuous",
            range="[0, 1] (normalized)",
            update_frequency="Per query",
            theoretical_meaning="Problem difficulty/complexity metric",
            actual_meaning="Heuristic based on keyword detection and feature extraction",
            control_potential="Medium - heuristic but potentially useful"
        ))
        
        # Candidate 4: Regime from SubstrateDynamics
        candidates.append(StateVariableDescription(
            name="regime",
            source="SubstrateDynamics",
            type="categorical",
            range="{'narrative_ok', 'transitional', 'formal_required'}",
            update_frequency="Per query",
            theoretical_meaning="Operating regime classification",
            actual_meaning="Threshold-based classification on tension",
            control_potential="Medium - categorical but potentially useful"
        ))
        
        # Candidate 5: Synthetic Q from multiple signals
        candidates.append(StateVariableDescription(
            name="Q_synthetic",
            source="UnifiedGovernor (potential)",
            type="continuous",
            range="To be determined",
            update_frequency="Per inference cycle",
            theoretical_meaning="Composite state variable combining multiple signals",
            actual_meaning="Could combine T_sys, tension, Q from QField",
            control_potential="High - could leverage multiple information sources"
        ))
        
        self.variables = candidates
        return candidates
    
    def generate_analysis_report(self) -> str:
        """Generate a comprehensive analysis report."""
        report = []
        report.append("=" * 80)
        report.append("BACKEND STATE VARIABLE ANALYSIS")
        report.append("=" * 80)
        report.append("")
        
        # Backend scan results
        report.append("## BACKEND COMPONENT SCAN")
        report.append("")
        scan_results = self.scan_backend()
        
        for component, result in scan_results.items():
            report.append(f"### {component}")
            report.append(f"Variables found: {result['variables_found']}")
            if result.get('error'):
                report.append(f"Error: {result['error']}")
            for var in result.get('variables', []):
                report.append(f"- {var['name']}: {var.get('theoretical_meaning', 'N/A')}")
            report.append("")
        
        # Candidate Q variables
        report.append("## CANDIDATE Q-LIKE VARIABLES")
        report.append("")
        candidates = self.identify_candidate_q_variables()
        
        for i, candidate in enumerate(candidates, 1):
            report.append(f"### Candidate {i}: {candidate.name}")
            report.append(f"Source: {candidate.source}")
            report.append(f"Type: {candidate.type}")
            report.append(f"Range: {candidate.range}")
            report.append(f"Update Frequency: {candidate.update_frequency}")
            report.append(f"Theoretical Meaning: {candidate.theoretical_meaning}")
            report.append(f"Actual Meaning: {candidate.actual_meaning}")
            report.append(f"Control Potential: {candidate.control_potential}")
            report.append("")
        
        # Preliminary assessment
        report.append("## PRELIMINARY ASSESSMENT")
        report.append("")
        
        high_potential = [v for v in candidates if "High" in v.control_potential]
        medium_potential = [v for v in candidates if "Medium" in v.control_potential]
        low_potential = [v for v in candidates if "Low" in v.control_potential]
        
        report.append(f"High Control Potential: {len(high_potential)}")
        for v in high_potential:
            report.append(f"  - {v.name} ({v.source})")
        report.append("")
        
        report.append(f"Medium Control Potential: {len(medium_potential)}")
        for v in medium_potential:
            report.append(f"  - {v.name} ({v.source})")
        report.append("")
        
        report.append(f"Low Control Potential: {len(low_potential)}")
        for v in low_potential:
            report.append(f"  - {v.name} ({v.source})")
        report.append("")
        
        # Recommendations
        report.append("## PRELIMINARY RECOMMENDATIONS")
        report.append("")
        
        if high_potential:
            report.append("PRIORITY: Test high-control-potential variables first:")
            for v in high_potential:
                report.append(f"  - {v.name}: Focus experimental effort here")
            report.append("")
        
        if medium_potential:
            report.append("SECONDARY: Test medium-control-potential variables:")
            for v in medium_potential:
                report.append(f"  - {v.name}: Test if high-potential variables fail")
            report.append("")
        
        if low_potential:
            report.append("DEPRIORATE: Low-control-potential variables:")
            report.append("  - These are unlikely to provide the required autonomous control function")
            report.append("  - Only test if all higher-potential options fail")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, output_path: str):
        """Save the analysis report."""
        report = self.generate_analysis_report()
        with open(output_path, 'w') as f:
            f.write(report)
        logger.info(f"[BackendAnalyzer] Report saved to {output_path}")


def main():
    analyzer = BackendStateAnalyzer()
    
    # Generate and save report
    report_path = os.path.join(_HERE, "BACKEND_STATE_ANALYSIS.md")
    analyzer.save_report(report_path)
    
    # Print report to console
    print(analyzer.generate_analysis_report())


if __name__ == "__main__":
    main()
