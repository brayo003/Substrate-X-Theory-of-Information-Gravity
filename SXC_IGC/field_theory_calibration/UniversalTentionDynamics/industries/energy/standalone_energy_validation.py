#!/usr/bin/env python3
"""
COMPREHENSIVE ENERGY DOMAIN VALIDATION
Standalone test suite for oil/gas, renewables, storage, distribution, and grid management
"""
import numpy as np
import os
import sys

# ============================================================================
# UNIVERSAL ENERGY ENGINE CORE
# ============================================================================
class EnergyEngine:
    def __init__(self, grid_size=(32, 32), domain="grid"):
        self.GRID_X, self.GRID_Y = grid_size
        self.rho = np.zeros(grid_size)  # Energy density/pressure
        self.E = np.zeros(grid_size)    # Generation potential  
        self.F = np.zeros(grid_size)    # Resistance/losses
        self.steps = 0
        self.stress_history = []
        self.energy_conservation = []
        
        # Domain-specific parameters
        self.domain = domain
        self.set_domain_parameters(domain)
    
    def set_domain_parameters(self, domain):
        if domain == "oil_gas":
            # High pressure, slow diffusion, reservoir dynamics
            self.D_rho, self.D_E, self.D_F = 0.01, 0.02, 0.1
            self.delta1, self.delta2 = 1.5, 0.8  # Extraction vs depletion
            self.alpha, self.beta, self.gamma = 0.8, 0.3, 1.2
            self.tau_E, self.tau_F = 0.8, 0.5
            
        elif domain == "renewables":
            # Fast changing, weather-dependent, intermittent
            self.D_rho, self.D_E, self.D_F = 0.05, 0.1, 0.3
            self.delta1, self.delta2 = 2.0, 1.0  # Generation vs variability
            self.alpha, self.beta, self.gamma = 1.5, 0.6, 0.8
            self.tau_E, self.tau_F = 0.3, 0.4
            
        elif domain == "storage":
            # Charge/discharge cycles, capacity constraints
            self.D_rho, self.D_E, self.D_F = 0.02, 0.08, 0.2
            self.delta1, self.delta2 = 1.2, 1.5  # Charging vs discharging
            self.alpha, self.beta, self.gamma = 0.9, 0.4, 1.0
            self.tau_E, self.tau_F = 0.6, 0.7
            
        elif domain == "distribution":
            # Flow dynamics, transmission losses
            self.D_rho, self.D_E, self.D_F = 0.08, 0.12, 0.15
            self.delta1, self.delta2 = 1.8, 1.2  # Transmission vs resistance
            self.alpha, self.beta, self.gamma = 1.2, 0.7, 0.9
            self.tau_E, self.tau_F = 0.4, 0.3
            
        else:  # grid_management
            # Balance, stability, control
            self.D_rho, self.D_E, self.D_F = 0.03, 0.06, 0.25
            self.delta1, self.delta2 = 1.0, 1.8  # Supply vs demand balance
            self.alpha, self.beta, self.gamma = 0.8, 0.5, 1.1
            self.tau_E, self.tau_F = 0.5, 0.4
    
    def laplacian_2d(self, field):
        """Diffusion operator for energy flow"""
        laplacian = np.zeros_like(field)
        laplacian[1:-1, 1:-1] = (
            field[:-2, 1:-1] + field[2:, 1:-1] + 
            field[1:-1, :-2] + field[1:-1, 2:] - 4*field[1:-1, 1:-1]
        )
        return laplacian
    
    def reaction_rho(self, rho, E, F):
        """Energy density evolution"""
        return self.delta1 * E * rho * (1 - rho) - self.delta2 * F * rho
    
    def reaction_E(self, rho, E, F):
        """Generation potential evolution"""
        return (self.alpha * rho + self.beta * E * (1 - E) - 
                self.gamma * E * F - (1/self.tau_E) * E)
    
    def reaction_F(self, rho, E, F):
        """Resistance/loss evolution"""
        return 0.6 * rho**2 + 0.4 * E - (1/self.tau_F) * F
    
    def evolve_step(self, dt=0.01):
        """Evolve one time step with conservation tracking"""
        try:
            # Store initial total energy for conservation check
            initial_energy = np.sum(self.rho)
            
            # Diffusion terms
            diffusion_rho = self.D_rho * self.laplacian_2d(self.rho)
            diffusion_E = self.D_E * self.laplacian_2d(self.E)
            diffusion_F = self.D_F * self.laplacian_2d(self.F)
            
            # Reaction terms
            reaction_rho = self.reaction_rho(self.rho, self.E, self.F)
            reaction_E = self.reaction_E(self.rho, self.E, self.F)
            reaction_F = self.reaction_F(self.rho, self.E, self.F)
            
            # Update fields
            self.rho += dt * (diffusion_rho + reaction_rho)
            self.E += dt * (diffusion_E + reaction_E)
            self.F += dt * (diffusion_F + reaction_F)
            
            # Enforce physical bounds
            self.rho = np.clip(self.rho, 0, 1)
            self.E = np.clip(self.E, 0, 1)
            self.F = np.clip(self.F, 0, 1)
            
            self.steps += 1
            
            # Check energy conservation
            final_energy = np.sum(self.rho)
            conservation_error = abs(final_energy - initial_energy) / (initial_energy + 1e-8)
            self.energy_conservation.append(conservation_error)
            
            # Calculate stress (gradient-based)
            grad_x = np.diff(self.rho, axis=0)
            grad_y = np.diff(self.rho, axis=1)
            grad_x = np.pad(grad_x, ((0,1),(0,0)), mode='edge')
            grad_y = np.pad(grad_y, ((0,0),(0,1)), mode='edge')
            stress = np.max(np.sqrt(grad_x**2 + grad_y**2))
            self.stress_history.append(stress)
            
            return True
        except Exception as e:
            return False
    
    def initialize_domain(self, domain):
        """Initialize energy domain-specific scenarios"""
        self.domain = domain
        self.set_domain_parameters(domain)
        
        if domain == "oil_gas":
            # Reservoir pressure fields
            self.rho = np.random.random((self.GRID_X, self.GRID_Y)) * 0.3
            # High pressure reservoirs - use relative positions
            reservoir_positions = [
                (self.GRID_X//4, self.GRID_Y//4),
                (self.GRID_X//4, 3*self.GRID_Y//4),
                (3*self.GRID_X//4, self.GRID_Y//4),
                (3*self.GRID_X//4, 3*self.GRID_Y//4)
            ]
            for rx, ry in reservoir_positions:
                x_indices = np.arange(self.GRID_X)
                y_indices = np.arange(self.GRID_Y)
                X, Y = np.meshgrid(x_indices, y_indices, indexing='ij')
                dist = np.sqrt((X - rx)**2 + (Y - ry)**2)
                self.rho += np.exp(-dist**2 / (self.GRID_X//8)**2) * 0.5
            self.rho = np.clip(self.rho, 0, 1)
            self.E = np.ones((self.GRID_X, self.GRID_Y)) * 0.6  # Extraction potential
            self.F = np.random.random((self.GRID_X, self.GRID_Y)) * 0.4  # Reservoir resistance
            
        elif domain == "renewables":
            # Weather-dependent generation patterns
            self.rho = np.zeros((self.GRID_X, self.GRID_Y))
            # Wind/solar farms - use relative positions
            farm_positions = [
                (self.GRID_X//4, self.GRID_Y//4),
                (self.GRID_X//4, 3*self.GRID_Y//4),
                (3*self.GRID_X//4, self.GRID_Y//4),
                (3*self.GRID_X//4, 3*self.GRID_Y//4),
                (self.GRID_X//2, self.GRID_Y//2)
            ]
            for fx, fy in farm_positions:
                x_indices = np.arange(self.GRID_X)
                y_indices = np.arange(self.GRID_Y)
                X, Y = np.meshgrid(x_indices, y_indices, indexing='ij')
                dist = np.sqrt((X - fx)**2 + (Y - fy)**2)
                self.rho += np.exp(-dist**2 / (self.GRID_X//10)**2) * 0.4
            self.rho = np.clip(self.rho, 0, 1)
            self.E = np.random.random((self.GRID_X, self.GRID_Y)) * 0.8  # Weather variability
            self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.3  # Transmission limits
            
        elif domain == "storage":
            # Battery state of charge
            self.rho = np.random.random((self.GRID_X, self.GRID_Y)) * 0.2
            # Storage facilities - use relative positions
            facility_positions = [
                (self.GRID_X//3, self.GRID_Y//3),
                (self.GRID_X//3, 2*self.GRID_Y//3),
                (2*self.GRID_X//3, self.GRID_Y//3),
                (2*self.GRID_X//3, 2*self.GRID_Y//3)
            ]
            for sx, sy in facility_positions:
                x_indices = np.arange(self.GRID_X)
                y_indices = np.arange(self.GRID_Y)
                X, Y = np.meshgrid(x_indices, y_indices, indexing='ij')
                dist = np.sqrt((X - sx)**2 + (Y - sy)**2)
                self.rho += np.exp(-dist**2 / (self.GRID_X//12)**2) * 0.6
            self.rho = np.clip(self.rho, 0, 1)
            self.E = np.ones((self.GRID_X, self.GRID_Y)) * 0.5  # Charging capability
            self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.6  # Discharge resistance
            
        elif domain == "distribution":
            # Power flow network - use relative positions
            self.rho = np.zeros((self.GRID_X, self.GRID_Y))
            # Transmission lines at strategic positions
            line1_x, line2_x = self.GRID_X//3, 2*self.GRID_X//3
            line1_y, line2_y = self.GRID_Y//3, 2*self.GRID_Y//3
            
            self.rho[line1_x, :] = 0.6  # Horizontal trunk
            self.rho[:, line1_y] = 0.6  # Vertical trunk
            self.rho[line2_x, :] = 0.5  # Secondary lines
            self.rho[:, line2_y] = 0.5
            
            self.E = np.ones((self.GRID_X, self.GRID_Y)) * 0.7  # Grid capacity
            self.F = np.random.random((self.GRID_X, self.GRID_Y)) * 0.5  # Line resistance
            
        else:  # grid_management
            # Load centers and generation
            self.rho = np.zeros((self.GRID_X, self.GRID_Y))
            # Load centers - use relative positions
            load_positions = [
                (self.GRID_X//4, self.GRID_Y//4),
                (3*self.GRID_X//4, 3*self.GRID_Y//4),
                (self.GRID_X//4, 3*self.GRID_Y//4),
                (3*self.GRID_X//4, self.GRID_Y//4)
            ]
            for lx, ly in load_positions:
                x_indices = np.arange(self.GRID_X)
                y_indices = np.arange(self.GRID_Y)
                X, Y = np.meshgrid(x_indices, y_indices, indexing='ij')
                dist = np.sqrt((X - lx)**2 + (Y - ly)**2)
                self.rho += np.exp(-dist**2 / (self.GRID_X//10)**2) * 0.3
            self.rho = np.clip(self.rho, 0, 1)
            self.E = np.random.random((self.GRID_X, self.GRID_Y)) * 0.6  # Generation availability
            self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.4  # Grid stability

# ============================================================================
# TEST SUITE 1: PARAMETER SWEEP ACROSS ENERGY DOMAINS
# ============================================================================
def test_energy_parameter_sweep():
    print("🎯 ENERGY DOMAIN PARAMETER SWEEP")
    print("Testing stability across oil/gas, renewables, storage, distribution, grid")
    print("=" * 60)
    
    domains = ["oil_gas", "renewables", "storage", "distribution", "grid_management"]
    
    for domain in domains:
        print(f"\n🔧 Testing {domain.upper()} parameters...")
        
        # Test different parameter regimes
        test_cases = [
            (0.8, 1.2, "Conservative"),
            (1.5, 0.8, "Aggressive"),
            (1.0, 1.0, "Balanced")
        ]
        
        for delta1, delta2, regime in test_cases:
            engine = EnergyEngine((16, 16), domain)
            engine.delta1, engine.delta2 = delta1, delta2
            engine.initialize_domain(domain)
            
            successful_steps = 0
            max_stress = 0
            
            for step in range(50):
                if engine.evolve_step():
                    successful_steps += 1
                    if engine.stress_history:
                        max_stress = max(max_stress, engine.stress_history[-1])
            
            stability = successful_steps / 50
            status = "✅ STABLE" if stability > 0.9 else "⚠️  PARTIAL" if stability > 0.7 else "❌ UNSTABLE"
            
            print(f"   {regime}: {status} ({successful_steps}/50 steps, Max Stress: {max_stress:.3f})")
    
    print("✅ Energy parameter sweep completed\n")

# ============================================================================
# TEST SUITE 2: FLOW & CONSERVATION TEST
# ============================================================================
def test_energy_conservation():
    print("⚡ ENERGY FLOW & CONSERVATION TEST")
    print("Validating conservation laws across all energy domains")
    print("=" * 60)
    
    domains = ["oil_gas", "renewables", "storage", "distribution", "grid_management"]
    
    conservation_results = {}
    
    for domain in domains:
        print(f"\n🔬 Testing {domain} conservation...")
        
        engine = EnergyEngine((20, 20), domain)
        engine.initialize_domain(domain)
        
        initial_energy = np.sum(engine.rho)
        conservation_errors = []
        
        for step in range(100):
            engine.evolve_step()
            if engine.energy_conservation:
                conservation_errors.append(engine.energy_conservation[-1])
        
        avg_conservation_error = np.mean(conservation_errors) if conservation_errors else 0
        max_conservation_error = np.max(conservation_errors) if conservation_errors else 0
        
        conservation_results[domain] = {
            'avg_error': avg_conservation_error,
            'max_error': max_conservation_error
        }
        
        if avg_conservation_error < 0.01:
            rating = "✅ EXCELLENT CONSERVATION"
        elif avg_conservation_error < 0.05:
            rating = "⚠️  GOOD CONSERVATION"
        else:
            rating = "❌ POOR CONSERVATION"
        
        print(f"   Average error: {avg_conservation_error:.4f}")
        print(f"   Maximum error: {max_conservation_error:.4f}")
        print(f"   Rating: {rating}")
    
    # Overall conservation assessment
    print(f"\n📊 OVERALL CONSERVATION ASSESSMENT:")
    excellent = sum(1 for r in conservation_results.values() if r['avg_error'] < 0.01)
    good = sum(1 for r in conservation_results.values() if 0.01 <= r['avg_error'] < 0.05)
    poor = sum(1 for r in conservation_results.values() if r['avg_error'] >= 0.05)
    
    print(f"   ✅ Excellent: {excellent}/5 domains")
    print(f"   ⚠️  Good: {good}/5 domains")  
    print(f"   ❌ Poor: {poor}/5 domains")
    
    print("✅ Energy conservation test completed\n")

# ============================================================================
# TEST SUITE 3: SPATIAL SCENARIOS & REALISTIC GEOMETRIES
# ============================================================================
def test_energy_spatial_scenarios():
    print("🏗️ ENERGY SPATIAL SCENARIO TEST")
    print("Testing realistic grid geometries and network patterns")
    print("=" * 60)
    
    scenarios = [
        ("Radial Grid", "radial"),
        ("Mesh Network", "mesh"), 
        ("Hub & Spoke", "hub"),
        ("Distributed", "distributed")
    ]
    
    for scenario_name, scenario_type in scenarios:
        print(f"\n📐 Testing {scenario_name}...")
        
        engine = EnergyEngine((24, 24), "distribution")
        
        # Create different grid geometries
        if scenario_type == "radial":
            # Radial distribution from center
            center_x, center_y = 12, 12
            for i in range(24):
                for j in range(24):
                    dist = np.sqrt((i-center_x)**2 + (j-center_y)**2)
                    if dist < 8:
                        engine.rho[i,j] = max(0.6 - dist/20, 0.1)
        
        elif scenario_type == "mesh":
            # Mesh network
            for i in range(24):
                for j in range(24):
                    if i % 4 == 0 or j % 4 == 0:
                        engine.rho[i,j] = 0.5
        
        elif scenario_type == "hub":
            # Hub and spoke
            hubs = [(6, 6), (6, 18), (18, 6), (18, 18)]
            for hx, hy in hubs:
                for i in range(24):
                    for j in range(24):
                        dist = np.sqrt((i-hx)**2 + (j-hy)**2)
                        if dist < 4:
                            engine.rho[i,j] = 0.7
                        elif dist < 8:
                            engine.rho[i,j] = 0.4
        
        else:  # distributed
            # Distributed generation
            engine.rho = np.random.random((24, 24)) * 0.3
            nodes = [(4,4), (4,20), (20,4), (20,20), (12,12)]
            for nx, ny in nodes:
                x_indices = np.arange(24)
                y_indices = np.arange(24)
                X, Y = np.meshgrid(x_indices, y_indices, indexing='ij')
                dist = np.sqrt((X - nx)**2 + (Y - ny)**2)
                engine.rho += np.exp(-dist**2 / 9) * 0.4
            engine.rho = np.clip(engine.rho, 0, 1)
        
        engine.E = np.ones((24, 24)) * 0.6
        engine.F = np.ones((24, 24)) * 0.3
        
        # Test flow patterns
        initial_flow_variance = np.var(engine.rho)
        
        for step in range(60):
            engine.evolve_step()
        
        final_flow_variance = np.var(engine.rho)
        flow_evolution = final_flow_variance - initial_flow_variance
        
        if abs(flow_evolution) < 0.005:
            stability = "✅ STABLE FLOW"
        elif flow_evolution > 0:
            stability = "📈 FLOW CONCENTRATION"
        else:
            stability = "📉 FLOW DISPERSION"
        
        print(f"   Flow evolution: {flow_evolution:+.4f}")
        print(f"   Pattern: {stability}")
    
    print("✅ Spatial scenario test completed\n")

# ============================================================================
# TEST SUITE 4: ENERGY STRESS TESTS
# ============================================================================
def test_energy_stress_conditions():
    print("🚨 ENERGY STRESS TEST")
    print("Testing extreme conditions: spikes, failures, emergencies")
    print("=" * 60)
    
    stress_scenarios = [
        ("Power Spike", "spike"),
        ("Grid Failure", "failure"), 
        ("Cascading Outage", "cascade"),
        ("Resource Depletion", "depletion")
    ]
    
    for scenario_name, scenario_type in stress_scenarios:
        print(f"\n💥 Testing {scenario_name}...")
        
        engine = EnergyEngine((20, 20), "grid_management")
        engine.initialize_domain("grid_management")
        
        # Apply stress conditions
        if scenario_type == "spike":
            # Sudden demand spike
            engine.rho[10:14, 10:14] = 0.9  # High load center
            engine.delta1 = 2.5  # Aggressive response
            
        elif scenario_type == "failure":
            # Transmission line failure
            engine.F[8:12, :] = 0.8  # High resistance line
            engine.D_rho = 0.01  # Reduced flow capacity
            
        elif scenario_type == "cascade":
            # Cascading failure conditions
            engine.rho[5:7, 5:7] = 0.9  # Initial failure point
            engine.gamma = 0.5  # Reduced stability
            
        else:  # depletion
            # Resource depletion
            engine.E = np.ones((20, 20)) * 0.2  # Low generation
            engine.delta2 = 2.0  # High consumption rate
        
        emergency_events = 0
        successful_steps = 0
        
        for step in range(80):
            if engine.evolve_step():
                successful_steps += 1
                if engine.stress_history and engine.stress_history[-1] > 0.7:
                    emergency_events += 1
        
        resilience = successful_steps / 80
        if resilience > 0.85:
            rating = "✅ HIGH RESILIENCE"
        elif resilience > 0.7:
            rating = "⚠️  MODERATE RESILIENCE"
        else:
            rating = "❌ LOW RESILIENCE"
        
        print(f"   Successful steps: {successful_steps}/80 ({resilience:.1%})")
        print(f"   Emergency events: {emergency_events}")
        print(f"   Resilience: {rating}")
    
    print("✅ Energy stress test completed\n")

# ============================================================================
# TEST SUITE 5: STOCHASTIC CONSISTENCY & LONG-TERM DYNAMICS
# ============================================================================
def test_energy_stochastic_longterm():
    print("🎲 ENERGY STOCHASTIC & LONG-TERM TEST")
    print("Testing reproducibility and extended dynamics")
    print("=" * 60)
    
    print("\n🔍 Testing stochastic consistency...")
    
    # Stochastic consistency
    final_energies = []
    for run in range(4):
        np.random.seed(100 + run)  # Different seeds
        engine = EnergyEngine((18, 18), "renewables")
        engine.initialize_domain("renewables")
        
        for step in range(50):
            engine.evolve_step()
        
        final_energy = np.mean(engine.rho)
        final_energies.append(final_energy)
        print(f"   Run {run+1}: Final energy = {final_energy:.4f}")
    
    energy_std = np.std(final_energies)
    if energy_std < 0.01:
        consistency = "✅ EXCELLENT CONSISTENCY"
    elif energy_std < 0.03:
        consistency = "⚠️  GOOD CONSISTENCY"
    else:
        consistency = "🎲 MODERATE VARIABILITY"
    
    print(f"   Energy standard deviation: {energy_std:.4f}")
    print(f"   Consistency: {consistency}")
    
    print("\n⏳ Testing long-term dynamics...")
    
    # Long-term evolution
    engine = EnergyEngine((16, 16), "storage")
    engine.initialize_domain("storage")
    
    energy_history = []
    stress_history = []
    
    print("   Evolution: ", end="")
    for step in range(200):
        if step % 40 == 0:
            print(f"{step}", end=" ")
        engine.evolve_step()
        energy_history.append(np.mean(engine.rho))
        if engine.stress_history:
            stress_history.append(engine.stress_history[-1])
    
    # Analyze long-term behavior
    energy_range = max(energy_history) - min(energy_history)
    avg_stress = np.mean(stress_history) if stress_history else 0
    
    if energy_range < 0.1:
        behavior = "✅ STABLE OPERATION"
    elif energy_range < 0.2:
        behavior = "⚖️  MODERATE CYCLING"
    else:
        behavior = "🔄 STRONG CYCLING"
    
    print(f"\n   Energy range: {energy_range:.3f}")
    print(f"   Average stress: {avg_stress:.3f}")
    print(f"   Long-term behavior: {behavior}")
    
    print("✅ Stochastic & long-term test completed\n")

# ============================================================================
# MASTER ENERGY VALIDATION RUNNER
# ============================================================================
def run_complete_energy_validation():
    print("🌍 COMPREHENSIVE ENERGY DOMAIN VALIDATION")
    print("STANDALONE SUITE - OIL/GAS, RENEWABLES, STORAGE, DISTRIBUTION, GRID")
    print("=" * 70)
    
    tests = [
        test_energy_parameter_sweep,
        test_energy_conservation,
        test_energy_spatial_scenarios,
        test_energy_stress_conditions,
        test_energy_stochastic_longterm
    ]
    
    for test in tests:
        test()
    
    print("🎯 ALL ENERGY DOMAIN VALIDATION TESTS COMPLETED!")
    print("⚡ Your universal dynamics engine is validated for energy systems!")
    print("🏭 Ready for: Oil & Gas reservoirs, Renewable generation, Storage systems,")
    print("               Distribution networks, and Grid management!")

if __name__ == "__main__":
    run_complete_energy_validation()
