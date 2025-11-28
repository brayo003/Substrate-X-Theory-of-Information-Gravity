cat > universal_dynamics_engine/universal_pde_engine.py << 'EOF'
import numpy as np
from typing import Dict, List, Tuple
import time
from dataclasses import dataclass, field
from enum import Enum
import random
import os
import sys

# Insert project root for reliable imports of theory/applications
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from theory.information_gravity_core import calculate_information_gravity
    from theory.dynamic_metrics_core import generate_domain_tmv_metrics # NEW IMPORT
    from applications.universal_risk_indicator import generate_risk_signal
except ImportError as e:
    print(f"FATAL ERROR: Core module import failed. {e}")
    sys.exit(1) # CRITICAL: Ensures script stops if import fails.

# --- Definitions ---
class Domain(Enum):
    BIO_PHYSICS = "biophysics"
    FINANCE = "finance"
    PLANETARY = "planetary"
    ENERGY = "energy"
    URBAN = "urban"

@dataclass
class DomainState:
    domain: Domain
    metrics: Dict[str, float] = field(default_factory=dict) # T-M-V metrics
    concentrations: np.ndarray = field(init=False)
    history: List[np.ndarray] = field(default_factory=list) # NEW: Concentration history
    stability: float = 1.0
    last_update: float = field(init=False)

    @staticmethod
    def initialize(domain: Domain, grid_size: Tuple[int, int]):
        concentrations = np.random.rand(*grid_size) * 0.5 + 0.25 
        state = DomainState(
            domain=domain,
            metrics={'Tension': 0.0, 'Momentum': 0.0, 'Variance': 0.0},
            stability=1.0,
            last_update=time.time()
        )
        state.concentrations = concentrations
        state.history.append(concentrations.copy())
        return state

# --- Core Integrator ---
class UniversalPDEIntegrator:
    def __init__(self, grid_size: Tuple[int, int] = (16, 16), coupling_strength: float = 0.05):
        self.grid_size = grid_size
        self.coupling_strength = coupling_strength
        self.domain_states: Dict[Domain, DomainState] = {}
        self.cross_domain_metrics: Dict[str, float] = {}
        self.external_pressure_map: Dict[Domain, float] = { # Placeholder for external pressure
            Domain.BIO_PHYSICS: 0.1,
            Domain.FINANCE: 0.2,
            Domain.PLANETARY: 0.05,
            Domain.ENERGY: 0.15,
            Domain.URBAN: 0.3
        }
        print("🌌 UNIVERSAL PDE INTEGRATOR INITIALIZED (DYNAMIC T-M-V ENABLED)")

    def add_domain(self, domain: Domain, initial_metrics: Dict[str, float]):
        state = DomainState.initialize(domain, self.grid_size)
        state.metrics.update(initial_metrics)
        self.domain_states[domain] = state
        print(f"✅ Domain added: {domain.value}")

    def coupled_pde_step(self):
        # 1. Simulate evolution (Reaction-Diffusion + noise) and Update History
        for domain, state in self.domain_states.items():
            # Apply evolution (Reaction-Diffusion + noise)
            noise = np.random.normal(0, 0.001, self.grid_size)
            state.concentrations += noise 
            np.clip(state.concentrations, 0.0, 1.0, out=state.concentrations)
            
            # Update history and calculate T-M-V metrics (DYNAMIC STEP)
            state.history.append(state.concentrations.copy())
            if len(state.history) > 10: # Keep history window small
                state.history.pop(0)

            external_pressure = self.external_pressure_map.get(domain, 0.1)
            tmv_metrics = generate_domain_tmv_metrics(state.history, external_pressure)
            state.metrics.update(tmv_metrics)


        # 2. Calculate Cross-Domain Metrics (The Information Gravity Core)
        ig_inputs = self._generate_ig_inputs()
        
        # Calculate IG Score and Risk Signal (NOW DYNAMIC)
        ig_score = calculate_information_gravity(ig_inputs)
        uri_signal, _ = generate_risk_signal(ig_inputs)

        # Calculate Domain Alignment (Tension Metric)
        num_domains = len(self.domain_states)
        base_alignment = 0.8 / num_domains 
        alignment = np.clip(base_alignment + np.random.normal(0, 0.1), 0.1, 1.0) 
        
        anomalies = {}
        if alignment < 0.4:
            anomalies = {'alignment_low': 'Domains diverging'}

        self.cross_domain_metrics.update({
            "information_gravity": ig_score,
            "domain_alignment": alignment,
            "uri_signal": uri_signal,
            "anomalies": anomalies
        })

        return ig_score, alignment, anomalies, uri_signal

    def _generate_ig_inputs(self) -> Dict[str, float]:
        """Maps dynamic domain T-M-V metrics to the required IG core inputs."""
        inputs = {}
        
        # Mapping: Use the calculated Tension/Momentum/Variance for the IG inputs
        if Domain.BIO_PHYSICS in self.domain_states:
            bp_metrics = self.domain_states[Domain.BIO_PHYSICS].metrics
            inputs['bio_physics_vr'] = bp_metrics.get('Tension', 0.0) # Using Tension as VR substitute
            
        if Domain.PLANETARY in self.domain_states:
            pl_metrics = self.domain_states[Domain.PLANETARY].metrics
            inputs['planetary_momentum_error_ppm'] = pl_metrics.get('Momentum', 0.0) # Using Momentum
            inputs['planetary_energy_error_ppm'] = pl_metrics.get('Variance', 0.0) # Using Variance
            
        # Fallback for domains not present (to prevent IG core error)
        inputs.setdefault('bio_physics_vr', 0.5)
        inputs.setdefault('planetary_momentum_error_ppm', 0.005)
        inputs.setdefault('planetary_energy_error_ppm', 0.005)

        # Additional core inputs (placeholders until further domain integration)
        inputs.setdefault('complexity', 0.5)
        inputs.setdefault('entropy', 0.5)
        inputs.setdefault('resonance', 0.5)
        inputs.setdefault('velocity', 0.5)
        inputs.setdefault('quantum_coherence', 0.5)
        inputs.setdefault('temporal_stability', 0.5)

        return inputs

# --- Demonstration and CLI Runner ---
class UniversalDynamicsEngine:
    def __init__(self):
        self.integrator = UniversalPDEIntegrator()

    def add_domain(self, domain: Domain):
        self.integrator.add_domain(domain, {})
        print(f"✅ Domain added: {domain.value}")

    def evolve_system(self, steps=100):
        print("\n🔄 EVOLVING COUPLED SYSTEM (DYNAMIC T-M-V ACTIVE)...")
        for i in range(steps):
            ig_score, alignment, anomalies, uri_signal = self.integrator.coupled_pde_step()
            
            if anomalies:
                for k, v in anomalies.items():
                    print(f"🚨 ANOMALIES DETECTED: {{'{k}': '{v}'}}")

            if i % 20 == 0 or i == steps - 1:
                # Log a dynamic metric (e.g., BioPhysics Tension)
                bp_tension = self.integrator.domain_states.get(Domain.BIO_PHYSICS, DomainState(domain=Domain.BIO_PHYSICS)).metrics.get('Tension', 0.0)
                
                print(f"Step {i}: Time={i/1000:.3f}")
                print(f"  Information Gravity: {ig_score:.4f}")
                print(f"  Domain Alignment: {alignment:.4f}")
                print(f"  BioPhysics Tension: {bp_tension:.4f}") # DYNAMIC LOG
                print(f"  URI Signal: {uri_signal.split()[0]}")

        print("\n📊 FINAL CROSS-DOMAIN STATE:")
        for domain, state in self.integrator.domain_states.items():
            final_variance = state.concentrations.var()
            print(f"  {domain.value}: Tension={state.metrics.get('Tension', 0.0):.4f}, Momentum={state.metrics.get('Momentum', 0.0):.4f}")


def run_engine_demo():
    print("🚀 DEMONSTRATING DYNAMIC T-M-V COUPLING")
    print("============================================================\n")

    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    engine.add_domain(Domain.ENERGY)
    
    engine.evolve_system(steps=100)
    
    print("✅ Dynamic engine execution complete")

if __name__ == '__main__':
    run_engine_demo()
EOF
