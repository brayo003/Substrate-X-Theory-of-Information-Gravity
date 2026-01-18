#!/usr/bin/env python3
"""
REAL-WORLD UTD VALIDATION: NYC TRAFFIC DATA
Processes actual NYC DOT traffic sensor data to validate Universal Tension Dynamics
"""
import numpy as np
import csv
from datetime import datetime
from collections import defaultdict

class NYCTrafficUTD:
    def __init__(self, grid_size=(20, 20)):
        """
        Map NYC traffic to a grid for UTD analysis
        Grid covers Manhattan approximately
        """
        self.GRID_X, self.GRID_Y = grid_size
        self.rho = np.zeros(grid_size)  # Traffic density
        self.E = np.zeros(grid_size)    # Speed variance (excitation)
        self.F = np.zeros(grid_size)    # Road capacity (inhibition)
        
        # UTD Parameters
        self.r = 1.2           # Linear growth rate
        self.a = 2.0           # Nonlinear reinforcement
        self.b = 1.5           # Saturation
        self.dt = 0.05
        self.sigma = 0.35
        
        # NYC Bounds (approximate Manhattan)
        self.lat_min, self.lat_max = 40.70, 40.88
        self.lon_min, self.lon_max = -74.02, -73.90
        
        self.tension_history = []
        self.gridlock_threshold = 0.153267  # From paper
    
    def load_nyc_traffic_csv(self, filename):
        """Load and process NYC DOT traffic CSV data"""
        print(f"📊 Loading NYC traffic data from {filename}")
        
        traffic_data = []
        speeds_by_grid = defaultdict(list)
        
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Extract coordinates from link_points
                    if 'link_points' in row and row['link_points']:
                        coords = row['link_points'].split()[0].split(',')
                        lat = float(coords[0])
                        lon = float(coords[1])
                        speed = float(row.get('speed', 0))
                        
                        # Map to grid
                        grid_x = int((lat - self.lat_min) / (self.lat_max - self.lat_min) * (self.GRID_X - 1))
                        grid_y = int((lon - self.lon_min) / (self.lon_max - self.lon_min) * (self.GRID_Y - 1))
                        
                        if 0 <= grid_x < self.GRID_X and 0 <= grid_y < self.GRID_Y:
                            speeds_by_grid[(grid_x, grid_y)].append(speed)
                            traffic_data.append({
                                'lat': lat, 'lon': lon, 'speed': speed,
                                'grid_x': grid_x, 'grid_y': grid_y,
                                'timestamp': row.get('data_as_of', 'N/A'),
                                'link_name': row.get('link_name', 'Unknown')
                            })
                except (ValueError, KeyError, IndexError):
                    continue
        
        print(f"✅ Loaded {len(traffic_data)} traffic sensor readings")
        return traffic_data, speeds_by_grid
    
    def map_traffic_to_tension(self, speeds_by_grid):
        """Convert real traffic speeds to UTD tension fields"""
        print("🗺️  Mapping traffic data to tension fields...")
        
        # Initialize fields
        self.rho = np.zeros((self.GRID_X, self.GRID_Y))
        self.E = np.zeros((self.GRID_X, self.GRID_Y))
        self.F = np.ones((self.GRID_X, self.GRID_Y)) * 0.5  # Base capacity
        
        for (gx, gy), speeds in speeds_by_grid.items():
            if len(speeds) > 0:
                avg_speed = np.mean(speeds)
                speed_var = np.var(speeds) if len(speeds) > 1 else 0
                
                # Map to UTD variables:
                # rho (density): Low speed = high density
                # Free flow ~45 mph, gridlock ~5 mph
                self.rho[gx, gy] = max(0, 1 - (avg_speed / 45.0))
                
                # E (excitation): Speed variance indicates instability
                self.E[gx, gy] = min(1, speed_var / 100.0)
                
                # F (capacity): Number of sensors = infrastructure
                self.F[gx, gy] = min(1, len(speeds) / 10.0)
        
        print(f"  Mean density (rho): {np.mean(self.rho):.3f}")
        print(f"  Mean excitation (E): {np.mean(self.E):.3f}")
        print(f"  Mean capacity (F): {np.mean(self.F):.3f}")
    
    def compute_tension(self):
        """Calculate current system tension using UTD formula"""
        # Normalize fields
        rho_norm = self.rho / (np.max(self.rho) + 1e-10)
        E_norm = self.E / (np.max(self.E) + 1e-10)
        F_norm = self.F / (np.max(self.F) + 1e-10)
        
        # UTD tension: T = r*rho + a*rho^2 - b*rho^3 + E - F
        tension = (self.r * rho_norm + 
                  self.a * rho_norm**2 - 
                  self.b * rho_norm**3 + 
                  E_norm - F_norm)
        
        return np.mean(tension), np.max(tension), tension
    
    def predict_gridlock_risk(self):
        """Assess gridlock risk based on UTD threshold"""
        mean_tension, max_tension, tension_field = self.compute_tension()
        
        risk_level = mean_tension / self.gridlock_threshold
        
        print(f"\n🎯 UTD GRIDLOCK ANALYSIS")
        print(f"{'='*50}")
        print(f"  Mean Tension: {mean_tension:.6f}")
        print(f"  Max Tension:  {max_tension:.6f}")
        print(f"  Critical Threshold: {self.gridlock_threshold:.6f}")
        print(f"  Risk Level: {risk_level:.2%} of critical threshold")
        
        if risk_level > 1.0:
            print(f"  ⚠️  WARNING: GRIDLOCK IMMINENT")
            print(f"  System has exceeded critical threshold!")
        elif risk_level > 0.8:
            print(f"  🟡 CAUTION: High congestion risk")
        elif risk_level > 0.5:
            print(f"  🟢 MODERATE: Normal traffic conditions")
        else:
            print(f"  ✅ LOW: Free-flowing traffic")
        
        return mean_tension, risk_level, tension_field
    
    def identify_critical_locations(self, tension_field, traffic_data, top_n=5):
        """Find the most critical intervention points"""
        print(f"\n🔍 TOP {top_n} CRITICAL INTERVENTION POINTS:")
        print(f"{'='*50}")
        
        # Find highest tension grid cells
        flat_tension = tension_field.flatten()
        critical_indices = np.argsort(flat_tension)[-top_n:][::-1]
        
        for rank, idx in enumerate(critical_indices, 1):
            gx = idx // self.GRID_Y
            gy = idx % self.GRID_Y
            tension = tension_field[gx, gy]
            
            # Find actual roads in this grid cell
            roads_here = [t for t in traffic_data 
                         if t['grid_x'] == gx and t['grid_y'] == gy]
            
            if roads_here:
                road_names = set(r['link_name'] for r in roads_here)
                avg_speed = np.mean([r['speed'] for r in roads_here])
                
                print(f"  #{rank}. Tension: {tension:.4f}")
                print(f"      Location: Grid({gx}, {gy})")
                print(f"      Roads: {', '.join(list(road_names)[:2])}")
                print(f"      Avg Speed: {avg_speed:.1f} mph")
                print(f"      💡 Suggested: Add lane capacity or signal optimization")
                print()
    
    def validate_predictions(self, traffic_data):
        """Compare UTD predictions with actual traffic conditions"""
        print(f"\n📈 VALIDATION: UTD vs ACTUAL CONDITIONS")
        print(f"{'='*50}")
        
        # Get actual congestion (low speeds)
        congested_roads = [t for t in traffic_data if t['speed'] < 15]
        flowing_roads = [t for t in traffic_data if t['speed'] > 35]
        
        print(f"  Actual congested roads: {len(congested_roads)}")
        print(f"  Actual free-flowing roads: {len(flowing_roads)}")
        
        # Check if UTD predicted these correctly
        mean_tension, risk_level, tension_field = self.predict_gridlock_risk()
        
        if len(congested_roads) > len(flowing_roads) and risk_level > 0.8:
            print(f"  ✅ UTD CORRECTLY predicted high congestion")
        elif len(congested_roads) < len(flowing_roads) and risk_level < 0.5:
            print(f"  ✅ UTD CORRECTLY predicted normal flow")
        else:
            print(f"  ⚠️  UTD prediction mismatch - needs calibration")
        
        return mean_tension, risk_level

def main():
    print("🗽 NYC TRAFFIC - UNIVERSAL TENSION DYNAMICS VALIDATOR")
    print("="*60)
    print("Real-world test using actual NYC DOT sensor data")
    print()
    
    # Initialize UTD engine
    utd = NYCTrafficUTD(grid_size=(20, 20))
    
    # Load data
    filename = "nyc_traffic_24h.csv"
    try:
        traffic_data, speeds_by_grid = utd.load_nyc_traffic_csv(filename)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        print(f"\nPlease download the data first using:")
        print(f'curl "https://data.cityofnewyork.us/resource/i4gi-tjb9.csv?$limit=10000&$order=data_as_of DESC" -o nyc_traffic_24h.csv')
        return
    
    if not traffic_data:
        print("❌ No valid traffic data found in file")
        return
    
    # Map to tension fields
    utd.map_traffic_to_tension(speeds_by_grid)
    
    # Predict gridlock risk
    mean_tension, risk_level, tension_field = utd.predict_gridlock_risk()
    
    # Identify critical intervention points
    utd.identify_critical_locations(tension_field, traffic_data, top_n=5)
    
    # Validate predictions
    utd.validate_predictions(traffic_data)
    
    print("\n" + "="*60)
    print("🎯 REAL-WORLD VALIDATION COMPLETE")
    print("="*60)
    print(f"\nKey Finding:")
    if risk_level > 1.0:
        print(f"  UTD predicts IMMEDIATE GRIDLOCK RISK in NYC")
        print(f"  Current tension is {(risk_level-1)*100:.1f}% above critical threshold")
    else:
        print(f"  UTD shows NYC is at {risk_level:.1%} of gridlock threshold")
        print(f"  System has {(1-risk_level)*100:.1f}% safety margin")

if __name__ == "__main__":
    main()
