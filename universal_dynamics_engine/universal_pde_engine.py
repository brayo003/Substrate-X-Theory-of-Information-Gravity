import numpy as np
from typing import Dict, List, Tuple
import time
from dataclasses import dataclass
from enum import Enum

class Domain(Enum):
    BIO_PHYSICS = "biophysics"
    FINANCE = "finance" 
    PLANETARY = "planetary"
    ENERGY = "energy"
    URBAN = "urban"

@dataclass
class DomainState:
    domain: Domain
    metrics: Dict[str, float]
    concentrations: np.ndarray
    stability: float
    last_update: float
    
class UniversalAnomalyDetector:
    def detect_anomalies(self, domains, cross_metrics):
        anomalies = {}
        avg_stability = np.mean([state.stability for state in domains.values()])
        
        if avg_stability < 0.3:
            anomalies['stability_critical'] = f"Global stability too low: {avg_stability:.3f}"
        if cross_metrics.get('domain_alignment', 1) < 0.5:
            anomalies['alignment_low'] = "Domains diverging"
            
        return anomalies

class UniversalPDEIntegrator:
    def __init__(self, grid_size: Tuple[int, int] = (64, 64)):
        self.grid_size = grid_size
        self.domains = {}
        self.global_time = 0.0
        self.global_dt = 0.001
        self.coupling_strength = 0.1
        
        self.cross_domain_metrics = {}
        self.validation_history = []
        self.anomaly_detector = UniversalAnomalyDetector()
        
        print("🌌 UNIVERSAL PDE ENGINE INITIALIZED")
        print("   True cross-domain coupling enabled")
        
    def add_domain(self, domain: Domain, initial_state: Dict):
        self.domains[domain] = DomainState(
            domain=domain,
            metrics=initial_state,
            concentrations=np.random.normal(0, 0.1, self.grid_size),
            stability=1.0,
            last_update=self.global_time
        )
        print(f"✅ Domain added: {domain.value}")
        
    def compute_cross_domain_diagnostics(self) -> Dict:
        diagnostics = {}
        
        if len(self.domains) >= 2:
            domain_stabilities = [state.stability for state in self.domains.values()]
            diagnostics['information_gravity'] = np.mean(domain_stabilities)
            
            correlations = self._compute_domain_correlations()
            diagnostics['domain_alignment'] = np.mean(np.abs(correlations))
            
            diagnostics['uri_signal'] = self._compute_universal_risk()
            
        diagnostics['mass_conservation'] = self._validate_conservation_laws()
        
        return diagnostics
    
    def _compute_domain_correlations(self) -> np.ndarray:
        n_domains = len(self.domains)
        correlation_matrix = np.zeros((n_domains, n_domains))
        
        domains_list = list(self.domains.values())
        for i in range(n_domains):
            for j in range(i, n_domains):
                if i == j:
                    correlation_matrix[i,j] = 1.0
                else:
                    corr = np.corrcoef(
                        domains_list[i].concentrations.flatten(),
                        domains_list[j].concentrations.flatten()
                    )[0,1]
                    correlation_matrix[i,j] = corr
                    correlation_matrix[j,i] = corr
                    
        return correlation_matrix
    
    def _compute_universal_risk(self) -> str:
        avg_stability = np.mean([state.stability for state in self.domains.values()])
        domain_alignment = self.cross_domain_metrics.get('domain_alignment', 0)
        
        risk_score = (1 - avg_stability) * (1 - domain_alignment)
        
        if risk_score < 0.1:
            return "EXECUTE/EXPAND"
        elif risk_score < 0.3:
            return "MONITOR/CONFIRM" 
        else:
            return "CONTRACT/STAND_ASIDE"
    
    def _validate_conservation_laws(self) -> float:
        total_mass = 0.0
        for state in self.domains.values():
            total_mass += np.sum(np.abs(state.concentrations))
        return abs(total_mass - len(self.domains))
    
    def coupled_pde_step(self):
        previous_states = {
            domain: state.concentrations.copy() 
            for domain, state in self.domains.items()
        }
        
        for domain, state in self.domains.items():
            domain_evolution = self._domain_pde_step(domain, state)
            coupling_terms = self._compute_coupling_terms(domain, state)
            
            total_update = domain_evolution + self.coupling_strength * coupling_terms
            state.concentrations += self.global_dt * total_update
            state.last_update = self.global_time
            
            state.metrics = self._update_domain_metrics(domain, state)
            state.stability = self._compute_domain_stability(state, previous_states[domain])
        
        self.global_time += self.global_dt
        self._continuous_validation()
        
    def _domain_pde_step(self, domain: Domain, state: DomainState) -> np.ndarray:
        if domain == Domain.BIO_PHYSICS:
            return self._biophysics_pde(state)
        elif domain == Domain.FINANCE:
            return self._finance_pde(state)
        else:
            return self._diffusion_pde(state.concentrations)
    
    def _diffusion_pde(self, u: np.ndarray) -> np.ndarray:
        laplacian = np.zeros_like(u)
        laplacian[1:-1, 1:-1] = (
            (u[1:-1, 2:] - 2*u[1:-1, 1:-1] + u[1:-1, 0:-2]) +
            (u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[0:-2, 1:-1])
        )
        return 0.1 * laplacian
    
    def _biophysics_pde(self, state: DomainState) -> np.ndarray:
        u = state.concentrations
        reaction = 0.1 - u + u**2 * np.roll(u, 1, axis=0)
        diffusion = self._diffusion_pde(u)
        return diffusion + reaction
    
    def _finance_pde(self, state: DomainState) -> np.ndarray:
        u = state.concentrations
        reaction = 0.05 * (0.5 - u) + 0.1 * np.gradient(u)[0]
        diffusion = self._diffusion_pde(u)
        return diffusion + reaction
    
    def _compute_coupling_terms(self, target_domain: Domain, target_state: DomainState) -> np.ndarray:
        coupling = np.zeros(self.grid_size)
        
        for domain, state in self.domains.items():
            if domain != target_domain:
                if target_domain == Domain.FINANCE and domain == Domain.BIO_PHYSICS:
                    coupling += 0.1 * np.gradient(state.concentrations)[0]
                elif target_domain == Domain.BIO_PHYSICS and domain == Domain.FINANCE:
                    coupling += 0.05 * state.concentrations
                    
        return coupling
    
    def _update_domain_metrics(self, domain: Domain, state: DomainState) -> Dict:
        metrics = {
            'variance': np.var(state.concentrations),
            'mean': np.mean(state.concentrations),
            'gradient': np.mean(np.abs(np.gradient(state.concentrations)))
        }
        
        if domain == Domain.FINANCE:
            metrics['volatility'] = np.std(state.concentrations)
        elif domain == Domain.BIO_PHYSICS:
            metrics['pattern_strength'] = np.var(state.concentrations)
            
        return metrics
    
    def _compute_domain_stability(self, state: DomainState, previous_state: np.ndarray) -> float:
        change = np.mean(np.abs(state.concentrations - previous_state))
        return 1.0 / (1.0 + change)
    
    def _continuous_validation(self):
        self.cross_domain_metrics = self.compute_cross_domain_diagnostics()
        
        anomalies = self.anomaly_detector.detect_anomalies(
            self.domains, 
            self.cross_domain_metrics
        )
        
        validation_snapshot = {
            'time': self.global_time,
            'cross_domain_metrics': self.cross_domain_metrics.copy(),
            'domain_states': {
                domain.value: {
                    'stability': state.stability,
                    'metrics': state.metrics.copy()
                } for domain, state in self.domains.items()
            },
            'anomalies': anomalies
        }
        self.validation_history.append(validation_snapshot)
        
        if anomalies:
            print(f"🚨 ANOMALIES DETECTED: {anomalies}")

def run_cross_domain_demo():
    print("🚀 DEMONSTRATING TRUE CROSS-DOMAIN COUPLING")
    print("=" * 60)
    
    engine = UniversalPDEIntegrator(grid_size=(32, 32))
    
    # Add multiple domains
    engine.add_domain(Domain.BIO_PHYSICS, {'initial_energy': 1.0})
    engine.add_domain(Domain.FINANCE, {'initial_capital': 1.0})
    engine.add_domain(Domain.ENERGY, {'initial_power': 1.0})
    
    print("\n🔄 EVOLVING COUPLED SYSTEM...")
    
    for step in range(100):
        engine.coupled_pde_step()
        
        if step % 20 == 0:
            metrics = engine.cross_domain_metrics
            print(f"Step {step}: Time={engine.global_time:.3f}")
            print(f"  Information Gravity: {metrics.get('information_gravity', 0):.3f}")
            print(f"  Domain Alignment: {metrics.get('domain_alignment', 0):.3f}")
            print(f"  URI Signal: {metrics.get('uri_signal', 'UNKNOWN')}")
            print(f"  Mass Conservation: {metrics.get('mass_conservation', 0):.6f}")
            print()
    
    print("📊 FINAL CROSS-DOMAIN STATE:")
    for domain, state in engine.domains.items():
        print(f"  {domain.value}: stability={state.stability:.3f}, variance={state.metrics['variance']:.6f}")
    
    return engine

if __name__ == "__main__":
    engine = run_cross_domain_demo()
