#!/usr/bin/env python3
"""
Smart Traffic Optimization using Universal Dynamics
"""
import numpy as np
import sys
import os

# Add core engine to path
core_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core_engine', 'src')
sys.path.insert(0, core_path)

from universal_dynamics import create_engine

class SmartTrafficOptimizer:
    """
    Urban traffic flow optimization using multi-scale field theory
    
    Field Mapping:
    ρ = Vehicle density
    E = Traffic flow speed  
    F = Road infrastructure quality
    """
    
    def __init__(self, city_grid_size=32):
        self.city_grid_size = city_grid_size
        
        # Create urban-optimized engine
        self.engine = create_engine(
            domain='urban',
            grid_size=city_grid_size,
            dt=0.01,
            delta1=1.0,    # Density → Infrastructure coupling
            delta2=0.8,    # Flow speed → Infrastructure coupling
            cubic_damping=0.2,
            M_factor=5000   # Moderate stiffness for traffic jams
        )
        
        # Traffic parameters
        self.road_capacity = np.ones((city_grid_size, city_grid_size))
        self.traffic_lights = np.zeros((city_grid_size, city_grid_size))
        
        print("🏙️  Smart Traffic Optimizer initialized")
    
    def initialize_city_grid(self, highways=None, bottlenecks=None):
        """Initialize city traffic grid"""
        # Start with uniform traffic
        self.engine.initialize_gaussian(amplitude=0.3, sigma=0.2)
        
        # Add highways (higher capacity)
        if highways:
            for hw in highways:
                x1, y1, x2, y2 = hw
                self.road_capacity[x1:x2, y1:y2] = 3.0  # 3x capacity
        
        # Add bottlenecks (reduced capacity)
        if bottlenecks:
            for bn in bottlenecks:
                x, y, radius = bn
                for i in range(self.city_grid_size):
                    for j in range(self.city_grid_size):
                        distance = np.sqrt((i-x)**2 + (j-y)**2)
                        if distance < radius:
                            self.road_capacity[i,j] = 0.3  # 70% reduction
        
        print("✅ City grid initialized with infrastructure")
    
    def simulate_traffic_flow(self, steps=100, traffic_injection=0.1):
        """Simulate traffic flow with dynamic optimization"""
        congestion_alerts = []
        
        for step in range(steps):
            # Inject new traffic (simulate rush hour)
            if step % 10 == 0:
                self.engine.rho += traffic_injection * np.random.rand(*self.engine.rho.shape)
            
            # Evolve traffic dynamics
            self.engine.evolve(1)
            
            # Apply road capacity constraints
            self.engine.rho = np.minimum(self.engine.rho, self.road_capacity)
            
            # Detect congestion
            congestion_map = self.engine.rho / self.road_capacity
            severe_congestion = np.where(congestion_map > 0.8)
            
            if len(severe_congestion[0]) > 0:
                congestion_level = np.mean(congestion_map[severe_congestion])
                congestion_alerts.append({
                    'step': step,
                    'locations': list(zip(severe_congestion[0], severe_congestion[1])),
                    'severity': congestion_level
                })
        
        return congestion_alerts
    
    def optimize_traffic_lights(self):
        """Optimize traffic light timing based on field gradients"""
        # Use field gradients to identify flow directions
        rho_gradient = np.gradient(self.engine.rho)
        flow_magnitude = np.sqrt(rho_gradient[0]**2 + rho_gradient[1]**2)
        
        # High gradient areas need traffic light optimization
        optimization_needed = flow_magnitude > np.percentile(flow_magnitude, 75)
        
        optimization_suggestions = []
        for i in range(self.city_grid_size):
            for j in range(self.city_grid_size):
                if optimization_needed[i,j]:
                    # Suggest green wave in dominant flow direction
                    direction = np.arctan2(rho_gradient[1][i,j], rho_gradient[0][i,j])
                    optimization_suggestions.append({
                        'intersection': (i, j),
                        'suggested_cycle': 60 + 30 * np.sin(direction),  # Dynamic timing
                        'flow_direction': np.degrees(direction)
                    })
        
        return optimization_suggestions
    
    def generate_traffic_report(self):
        """Generate comprehensive traffic analysis report"""
        stats = self.engine.get_field_statistics()
        
        congestion_map = self.engine.rho / self.road_capacity
        congestion_level = np.mean(congestion_map)
        
        report = {
            'average_congestion': congestion_level,
            'max_congestion': np.max(congestion_map),
            'total_vehicles': np.sum(self.engine.rho),
            'infrastructure_efficiency': stats['F_rms'],  # How well infrastructure handles load
            'traffic_smoothness': 1.0 - stats['E_rms']   # Lower E_rms = smoother flow
        }
        
        return report

# Demo
if __name__ == "__main__":
    print("🏙️  Smart Traffic Optimization Demo")
    
    # Create optimizer for a 16x16 city grid
    traffic_opt = SmartTrafficOptimizer(city_grid_size=16)
    
    # Initialize with highways and bottlenecks
    highways = [(2, 0, 4, 16), (12, 0, 14, 16)]  # Vertical highways
    bottlenecks = [(8, 8, 2)]  # Center bottleneck
    
    traffic_opt.initialize_city_grid(highways=highways, bottlenecks=bottlenecks)
    
    # Simulate traffic for 50 steps
    print("Simulating traffic flow...")
    congestion_alerts = traffic_opt.simulate_traffic_flow(steps=50)
    
    # Generate reports
    traffic_report = traffic_opt.generate_traffic_report()
    light_optimizations = traffic_opt.optimize_traffic_lights()
    
    print("\n📊 Traffic Report:")
    for key, value in traffic_report.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n🚨 Congestion Alerts: {len(congestion_alerts)}")
    print(f"🚦 Traffic Light Optimizations Suggested: {len(light_optimizations)}")
    
    if light_optimizations:
        print("Top optimization suggestion:")
        print(f"  Intersection: {light_optimizations[0]['intersection']}")
        print(f"  Cycle: {light_optimizations[0]['suggested_cycle']:.1f}s")
        print(f"  Direction: {light_optimizations[0]['flow_direction']:.1f}°")
