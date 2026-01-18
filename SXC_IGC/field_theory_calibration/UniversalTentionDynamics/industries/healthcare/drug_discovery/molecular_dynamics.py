#!/usr/bin/env python3
"""
Molecular Dynamics for Drug Discovery using Universal Dynamics
"""
import numpy as np
import sys
import os

core_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core_engine', 'src')
sys.path.insert(0, core_path)

from universal_dynamics import create_engine

class DrugDiscoverySimulator:
    """
    Molecular dynamics simulator for drug-target interactions
    
    Field Mapping:
    ρ = Molecular density/concentration
    E = Binding energy/affinity  
    F = Protein structure flexibility
    """
    
    def __init__(self, simulation_size=32):
        self.sim_size = simulation_size
        
        self.engine = create_engine(
            domain='healthcare',
            grid_size=simulation_size,
            dt=0.005,
            delta1=0.8,    # Concentration → Flexibility coupling
            delta2=1.2,    # Binding energy → Flexibility coupling  
            cubic_damping=0.1,
            M_factor=20000  # High stiffness for molecular binding
        )
        
        self.target_protein = None
        self.drug_molecules = None
        
        print("🧬 Drug Discovery Simulator initialized")
    
    def setup_protein_target(self, binding_sites=None, active_sites=None):
        """Setup protein target structure"""
        # Initialize protein as Gaussian density
        self.engine.initialize_gaussian(amplitude=0.5, sigma=0.15)
        self.target_protein = self.engine.rho.copy()
        
        # Enhance binding sites
        if binding_sites:
            for site in binding_sites:
                x, y, strength = site
                radius = 3
                for i in range(max(0, x-radius), min(self.sim_size, x+radius)):
                    for j in range(max(0, y-radius), min(self.sim_size, y+radius)):
                        distance = np.sqrt((i-x)**2 + (j-y)**2)
                        if distance < radius:
                            self.target_protein[i,j] += strength * np.exp(-distance**2)
        
        print("✅ Protein target configured")
    
    def introduce_drug_candidate(self, molecular_structure, concentration=0.3):
        """Introduce drug candidate into simulation"""
        self.drug_molecules = np.zeros((self.sim_size, self.sim_size))
        
        # Place drug molecules (simplified)
        for i in range(self.sim_size):
            for j in range(self.sim_size):
                if molecular_structure[i,j] > 0:
                    self.drug_molecules[i,j] = concentration * molecular_structure[i,j]
        
        # Update engine fields
        self.engine.rho = self.target_protein + self.drug_molecules
        self.engine.E = np.zeros((self.sim_size, self.sim_size))  # Reset energy
        self.engine.F = np.ones((self.sim_size, self.sim_size))   # Flexible initial state
        
        print("💊 Drug candidate introduced")
    
    def simulate_binding(self, steps=200):
        """Simulate drug-target binding dynamics"""
        binding_events = []
        affinity_scores = []
        
        for step in range(steps):
            self.engine.evolve(1)
            
            # Calculate binding affinity (correlation between drug and protein)
            if self.drug_molecules is not None:
                affinity = np.corrcoef(self.drug_molecules.flatten(), 
                                     self.engine.rho.flatten())[0,1]
                affinity_scores.append(affinity)
                
                # Detect strong binding events
                if affinity > 0.7 and step > 10:
                    binding_events.append({
                        'step': step,
                        'affinity': affinity,
                        'binding_strength': np.mean(self.engine.E)  # Energy field
                    })
        
        return binding_events, affinity_scores
    
    def analyze_drug_efficacy(self):
        """Analyze drug efficacy based on simulation results"""
        stats = self.engine.get_field_statistics()
        
        # Efficacy metrics
        binding_stability = 1.0 - stats['E_rms']  # Lower energy fluctuation = more stable
        specificity = stats['F_rms']  # Field F indicates binding specificity
        
        # Calculate binding pockets
        high_affinity_regions = self.engine.rho > np.percentile(self.engine.rho, 80)
        binding_pockets = np.sum(high_affinity_regions)
        
        efficacy_report = {
            'binding_affinity_score': np.mean(self.engine.E) if hasattr(self, 'affinity_scores') else 0,
            'binding_stability': binding_stability,
            'binding_specificity': specificity,
            'binding_pockets_detected': binding_pockets,
            'drug_target_engagement': stats['rho_max']  # Maximum interaction
        }
        
        return efficacy_report

# Demo
if __name__ == "__main__":
    print("🧬 Drug Discovery Simulation Demo")
    
    # Create simulator
    drug_sim = DrugDiscoverySimulator(simulation_size=24)
    
    # Setup protein with binding sites
    binding_sites = [(8, 8, 0.5), (16, 16, 0.7), (12, 4, 0.3)]
    drug_sim.setup_protein_target(binding_sites=binding_sites)
    
    # Create simple drug molecule structure
    drug_structure = np.zeros((24, 24))
    drug_structure[10:14, 10:14] = 1.0  # Simple square molecule
    
    # Introduce drug
    drug_sim.introduce_drug_candidate(drug_structure, concentration=0.4)
    
    # Simulate binding
    print("Simulating drug-target binding...")
    binding_events, affinity_scores = drug_sim.simulate_binding(steps=100)
    
    # Analyze results
    efficacy = drug_sim.analyze_drug_efficacy()
    
    print("\n💊 Drug Efficacy Report:")
    for key, value in efficacy.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n🔗 Binding Events Detected: {len(binding_events)}")
    if binding_events:
        print(f"Strongest Binding: affinity={binding_events[0]['affinity']:.3f}")
    
    if affinity_scores:
        print(f"Final Affinity Score: {affinity_scores[-1]:.3f}")
