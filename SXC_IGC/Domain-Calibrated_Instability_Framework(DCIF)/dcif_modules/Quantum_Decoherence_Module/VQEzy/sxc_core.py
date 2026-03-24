import numpy as np
import h5py

class SXCSentinel:
    """
    Substrate-X Theory of Information Gravity: Core Sentinel
    Calibrated for IBMQ Toronto (V12)
    """
    def __init__(self, beta_threshold=7.0):
        self.beta_limit = beta_threshold
        self.t_sys = 0.0
        self.phase = 'NOMINAL'
        self.gamma_nominal = 0.8
        self.gamma_firewall = 5.0
        self.dt = 0.05
        
    def calculate_substrate_drag(self, param_history):
        """Calculates the Information Gravity (Variance) of parameters."""
        return np.var(param_history, axis=0)

    def evaluate_node_stress(self, tension_value, gate_density_beta):
        """
        Updates the System Stress (T_sys) based on localized tension 
        and the algorithm's Beta (Gate Density).
        """
        # Excitation Flux: E = 1 - exp(-T * 2)
        excitation = 1 - np.exp(-tension_value * 2.0)
        
        # Apply Phase-aware dampening (The Firewall)
        current_gamma = self.gamma_firewall if self.phase == 'FIREWALL' else self.gamma_nominal
        
        # Differential Change: (Inflow - Outflow) * dt
        inflow = excitation * gate_density_beta
        outflow = current_gamma * self.t_sys
        self.t_sys += (inflow - outflow) * self.dt
        
        # State Transition
        if self.t_sys > 1.0:
            self.phase = 'FIREWALL'
        elif self.t_sys < 0.2:
            self.phase = 'NOMINAL'
            
        return self.t_sys, self.phase

    def get_stability_report(self, drag_tensor):
        """Pinpoints 'Fracture' points in the ansatz footprint."""
        mean_drag = np.mean(drag_tensor)
        max_jitter = np.max(drag_tensor)
        status = "CRITICAL" if mean_drag > 1.5 or max_jitter > 3.0 else "STABLE"
        
        return {
            "mean_gravity": mean_drag,
            "peak_jitter": max_jitter,
            "status": status,
            "firewall_active": self.phase == 'FIREWALL'
        }
