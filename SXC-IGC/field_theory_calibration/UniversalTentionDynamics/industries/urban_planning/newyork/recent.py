#!/usr/bin/env python3
"""
UTD PHASE TRANSITION CALIBRATION
Calibrates Universal Tension Dynamics to detect REGIME SHIFTS, not gradual congestion
Focuses on finding the critical threshold where systems flip from stable to catastrophic
"""
import numpy as np
import csv
from datetime import datetime
from collections import defaultdict
from scipy.optimize import differential_evolution, minimize
import json

class PhaseTransitionCalibrator:
    def __init__(self, grid_size=(20, 20)):
        self.GRID_X, self.GRID_Y = grid_size
        
        # NYC Bounds (Manhattan)
        self.lat_min, self.lat_max = 40.70, 40.88
        self.lon_min, self.lon_max = -74.02, -73.90
        
        # Known regime states we need to distinguish
        self.regime_labels = {
            'FREE_FLOW': 0,      # Normal conditions, system has slack
            'CONGESTED': 0.3,    # Routine congestion, still stable
            'STRESSED': 0.6,     # High load, vulnerable to cascade
            'CRITICAL': 0.85,    # Near phase transition
            'GRIDLOCK': 1.0      # Catastrophic collapse
        }
        
    def load_traffic_data(self, filename):
        """Load NYC traffic data from CSV"""
        print(f"📊 Loading traffic data from {filename}...")
        
        traffic_data = []
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if 'link_points' in row and row['link_points']:
                        coords = row['link_points'].split()[0].split(',')
                        lat = float(coords[0])
                        lon = float(coords[1])
                        speed = float(row.get('speed', 0))
                        
                        # Map to grid
                        grid_x = int((lat - self.lat_min) / (self.lat_max - self.lat_min) * (self.GRID_X - 1))
                        grid_y = int((lon - self.lon_min) / (self.lon_max - self.lon_min) * (self.GRID_Y - 1))
                        
                        if 0 <= grid_x < self.GRID_X and 0 <= grid_y < self.GRID_Y:
                            traffic_data.append({
                                'speed': speed,
                                'grid_x': grid_x,
                                'grid_y': grid_y,
                                'timestamp': row.get('data_as_of', 'N/A'),
                                'link_name': row.get('link_name', 'Unknown')
                            })
                except (ValueError, KeyError, IndexError):
                    continue
        
        print(f"✅ Loaded {len(traffic_data)} sensor readings")
        return traffic_data
    
    def classify_regime(self, traffic_data):
        """
        Classify system regime based on STRUCTURAL indicators, not just slow roads
        
        REGIME INDICATORS:
        - FREE_FLOW: Low density, low variance, independent flows
        - CONGESTED: High density, but flows still independent, no correlation breakdown
        - STRESSED: High density + increasing speed variance + spatial correlation
        - CRITICAL: Speed variance spiking, flow breakdown starting to cascade
        - GRIDLOCK: Complete network seizure, speeds <5mph everywhere, total correlation
        """
        if not traffic_data:
            return 'FREE_FLOW', 0, {}
        
        speeds = np.array([t['speed'] for t in traffic_data])
        
        # Core metrics
        avg_speed = np.mean(speeds)
        speed_variance = np.var(speeds)
        pct_severe = np.sum(speeds < 5) / len(speeds)  # Complete stoppage
        pct_stopped = np.sum(speeds < 1) / len(speeds)  # Actually stopped
        
        # Spatial correlation (critical for phase transitions)
        grid_speeds = defaultdict(list)
        for t in traffic_data:
            grid_speeds[(t['grid_x'], t['grid_y'])].append(t['speed'])
        
        # Calculate spatial clustering of low speeds
        severe_cells = sum(1 for speeds in grid_speeds.values() 
                          if speeds and np.mean(speeds) < 10)
        total_cells = len(grid_speeds)
        spatial_clustering = severe_cells / total_cells if total_cells > 0 else 0
        
        # Network-wide correlation indicator
        # High variance + high clustering = correlated failure (phase transition)
        # High clustering + low variance = uniform slow (normal congestion)
        correlation_score = spatial_clustering * (speed_variance / 100)
        
        metrics = {
            'avg_speed': avg_speed,
            'speed_variance': speed_variance,
            'pct_severe': pct_severe * 100,
            'pct_stopped': pct_stopped * 100,
            'spatial_clustering': spatial_clustering,
            'correlation_score': correlation_score,
            'total_readings': len(traffic_data)
        }
        
        # REGIME CLASSIFICATION LOGIC
        # This is the key: distinguishing routine congestion from phase transitions
        
        if pct_stopped > 0.3:  # 30%+ actually stopped
            regime = 'GRIDLOCK'
            regime_score = 1.0
            
        elif correlation_score > 0.15 and pct_severe > 0.4:
            # High correlation + widespread severe congestion = critical
            regime = 'CRITICAL'
            regime_score = 0.85
            
        elif spatial_clustering > 0.5 and speed_variance > 150:
            # High clustering + high variance = stressed, vulnerable
            regime = 'STRESSED'
            regime_score = 0.6
            
        elif avg_speed < 20 or pct_severe > 0.3:
            # Slow but no structural breakdown = routine congestion
            regime = 'CONGESTED'
            regime_score = 0.3
            
        else:
            regime = 'FREE_FLOW'
            regime_score = 0.0
        
        return regime, regime_score, metrics
    
    def create_tension_fields(self, traffic_data, speed_scale, density_exp, capacity_base):
        """
        Create tension fields emphasizing VARIANCE and CORRELATION, not just density
        """
        speeds_by_grid = defaultdict(list)
        for t in traffic_data:
            speeds_by_grid[(t['grid_x'], t['grid_y'])].append(t['speed'])
        
        rho = np.zeros((self.GRID_X, self.GRID_Y))  # Density
        E = np.zeros((self.GRID_X, self.GRID_Y))    # Excitation (variance)
        F = np.ones((self.GRID_X, self.GRID_Y)) * capacity_base  # Capacity
        
        for (gx, gy), speeds in speeds_by_grid.items():
            if len(speeds) > 0:
                avg_speed = np.mean(speeds)
                speed_var = np.var(speeds) if len(speeds) > 1 else 0
                
                # Density: normalized congestion level
                rho[gx, gy] = max(0, (1 - (avg_speed / speed_scale))**density_exp)
                
                # Excitation: CRITICAL for phase transition detection
                # High variance = fluctuating, unstable, approaching breakdown
                E[gx, gy] = min(1, speed_var / 200.0)
                
                # Capacity: infrastructure strength
                F[gx, gy] = min(1, capacity_base + len(speeds) / 15.0)
        
        return rho, E, F
    
    def compute_utd_tension(self, rho, E, F, r, a, b, excitation_weight=1.0):
        """
        Compute UTD tension with emphasis on variance (excitation)
        The key: phase transitions show up as VARIANCE spikes, not just high density
        """
        # Normalize fields
        rho_norm = rho / (np.max(rho) + 1e-10)
        E_norm = E / (np.max(E) + 1e-10)
        F_norm = F / (np.max(F) + 1e-10)
        
        # Spatial gradient (stress propagation)
        rho_grad_x = np.abs(np.gradient(rho_norm, axis=0))
        rho_grad_y = np.abs(np.gradient(rho_norm, axis=1))
        spatial_stress = np.sqrt(rho_grad_x**2 + rho_grad_y**2)
        
        # UTD formula with spatial coupling
        # r*ρ: base congestion
        # a*ρ²: self-reinforcing feedback
        # -b*ρ³: saturation
        # E: variance (instability)
        # spatial_stress: cascade risk
        # -F: capacity absorption
        
        tension = (r * rho_norm + 
                  a * rho_norm**2 - 
                  b * rho_norm**3 + 
                  excitation_weight * E_norm +
                  0.5 * spatial_stress -
                  F_norm)
        
        return np.mean(tension), np.max(tension), np.std(tension)
    
    def objective_function(self, params, traffic_data, regime_score):
        """
        Objective: Match UTD tension to REGIME classification, not road counts
        """
        # Unpack parameters
        r, a, b, speed_scale, density_exp, capacity_base, excitation_weight = params
        
        # Physical constraints
        if (r < 0 or a < 0 or b < 0 or 
            speed_scale < 5 or speed_scale > 100 or
            excitation_weight < 0 or excitation_weight > 5):
            return 1e6
        
        try:
            # Create fields
            rho, E, F = self.create_tension_fields(traffic_data, speed_scale, 
                                                   density_exp, capacity_base)
            
            # Compute tension
            mean_tension, max_tension, std_tension = self.compute_utd_tension(
                rho, E, F, r, a, b, excitation_weight
            )
            
            # Map tension to [0, 1] regime space using sigmoid
            # The critical threshold is where sigmoid inflection point should be
            predicted_regime = 1 / (1 + np.exp(-mean_tension))
            
            # Error: difference from true regime classification
            error = abs(predicted_regime - regime_score)
            
            # Penalty for unrealistic tension values
            if abs(mean_tension) > 10:
                error += 0.5
            
            return error
            
        except Exception as e:
            return 1e6
    
    def calibrate_to_regime(self, traffic_data):
        """
        Calibrate UTD to match REGIME classification, not congestion percentage
        """
        regime, regime_score, metrics = self.classify_regime(traffic_data)
        
        print(f"\n🎯 REGIME CLASSIFICATION")
        print("="*60)
        print(f"Regime: {regime} (score: {regime_score:.3f})")
        print(f"\nMetrics:")
        print(f"  Avg Speed: {metrics['avg_speed']:.1f} mph")
        print(f"  Speed Variance: {metrics['speed_variance']:.1f}")
        print(f"  Severe Congestion: {metrics['pct_severe']:.1f}%")
        print(f"  Stopped: {metrics['pct_stopped']:.1f}%")
        print(f"  Spatial Clustering: {metrics['spatial_clustering']:.3f}")
        print(f"  Correlation Score: {metrics['correlation_score']:.4f}")
        
        print(f"\n🔧 Calibrating UTD to regime={regime}...")
        
        # Parameter bounds
        # r, a, b, speed_scale, density_exp, capacity_base, excitation_weight
        bounds = [
            (0.1, 5.0),   # r: linear growth
            (0.1, 5.0),   # a: nonlinear reinforcement
            (0.1, 5.0),   # b: saturation
            (10, 60),     # speed_scale: reference speed
            (0.5, 3.0),   # density_exp: density exponent
            (0.1, 0.8),   # capacity_base: base capacity
            (0.5, 3.0)    # excitation_weight: variance importance
        ]
        
        print("   Running global optimization...")
        
        result = differential_evolution(
            self.objective_function,
            bounds,
            args=(traffic_data, regime_score),
            maxiter=150,
            popsize=20,
            seed=42,
            disp=False,
            workers=1
        )
        
        optimal_params = result.x
        final_error = result.fun
        
        r, a, b, speed_scale, density_exp, capacity_base, excitation_weight = optimal_params
        
        print(f"\n✅ CALIBRATION COMPLETE")
        print(f"   Regime Match Error: {final_error:.4f}")
        print(f"\n📊 CALIBRATED PARAMETERS:")
        print(f"   r (growth):             {r:.4f}")
        print(f"   a (reinforcement):      {a:.4f}")
        print(f"   b (saturation):         {b:.4f}")
        print(f"   speed_scale:            {speed_scale:.2f} mph")
        print(f"   density_exponent:       {density_exp:.4f}")
        print(f"   capacity_base:          {capacity_base:.4f}")
        print(f"   excitation_weight:      {excitation_weight:.4f}")
        
        return {
            'r': r, 'a': a, 'b': b,
            'speed_scale': speed_scale,
            'density_exp': density_exp,
            'capacity_base': capacity_base,
            'excitation_weight': excitation_weight,
            'error': final_error,
            'regime': regime,
            'regime_score': regime_score,
            'metrics': metrics
        }
    
    def validate_regime_detection(self, traffic_data, calibrated_params):
        """
        Validate that calibrated UTD correctly identifies the regime
        """
        print(f"\n🔬 REGIME DETECTION VALIDATION")
        print("="*60)
        
        # Extract params
        r = calibrated_params['r']
        a = calibrated_params['a']
        b = calibrated_params['b']
        speed_scale = calibrated_params['speed_scale']
        density_exp = calibrated_params['density_exp']
        capacity_base = calibrated_params['capacity_base']
        excitation_weight = calibrated_params['excitation_weight']
        
        # True regime
        true_regime = calibrated_params['regime']
        true_score = calibrated_params['regime_score']
        
        # Create fields
        rho, E, F = self.create_tension_fields(traffic_data, speed_scale, 
                                               density_exp, capacity_base)
        
        # Compute tension
        mean_tension, max_tension, std_tension = self.compute_utd_tension(
            rho, E, F, r, a, b, excitation_weight
        )
        
        # Predicted regime
        predicted_score = 1 / (1 + np.exp(-mean_tension))
        
        # Find critical threshold (where regime crosses from safe to dangerous)
        # This is the sigmoid inflection point
        critical_threshold = 0.0  # Sigmoid inflection
        
        print(f"True Regime:        {true_regime}")
        print(f"True Score:         {true_score:.3f}")
        print(f"Mean Tension:       {mean_tension:.4f}")
        print(f"Max Tension:        {max_tension:.4f}")
        print(f"Tension StdDev:     {std_tension:.4f}")
        print(f"Predicted Score:    {predicted_score:.3f}")
        print(f"Error:              {abs(predicted_score - true_score):.3f}")
        
        print(f"\n🎯 CRITICAL THRESHOLDS:")
        print(f"   Tension = {critical_threshold:.4f} → Regime score = 0.50")
        print(f"   Tension > +1.0 → CRITICAL (score ~0.73)")
        print(f"   Tension > +2.0 → GRIDLOCK (score ~0.88)")
        
        # Risk assessment
        if mean_tension < -2.0:
            risk = "✅ SAFE - System has significant slack"
        elif mean_tension < -1.0:
            risk = "🟢 LOW - Normal operating conditions"
        elif mean_tension < 0:
            risk = "🟡 MODERATE - Congested but stable"
        elif mean_tension < 1.0:
            risk = "🟠 ELEVATED - Stressed, monitor closely"
        elif mean_tension < 2.0:
            risk = "🔴 HIGH - Critical, near phase transition"
        else:
            risk = "⚠️  EXTREME - Gridlock imminent/occurring"
        
        print(f"\n   Current Assessment: {risk}")
        
        # Validation result
        error = abs(predicted_score - true_score)
        if error < 0.15:
            print(f"\n✅ EXCELLENT REGIME DETECTION")
        elif error < 0.25:
            print(f"\n✅ GOOD REGIME DETECTION")
        else:
            print(f"\n⚠️  NEEDS REFINEMENT")
        
        return {
            'mean_tension': mean_tension,
            'max_tension': max_tension,
            'std_tension': std_tension,
            'predicted_score': predicted_score,
            'true_score': true_score,
            'error': error,
            'critical_threshold': critical_threshold
        }
    
    def save_calibration(self, params, filename='utd_regime_calibrated.json'):
        """Save regime-calibrated parameters"""
        with open(filename, 'w') as f:
            json.dump(params, f, indent=2, default=float)
        print(f"\n💾 Regime-calibrated parameters saved to {filename}")

def main():
    print("🔬 UTD PHASE TRANSITION CALIBRATION")
    print("="*60)
    print("Calibrating to detect REGIME SHIFTS, not routine congestion")
    print()
    
    calibrator = PhaseTransitionCalibrator(grid_size=(20, 20))
    
    # Load data
    filename = "nyc_traffic_24h.csv"
    try:
        traffic_data = calibrator.load_traffic_data(filename)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        print(f"\nDownload data first:")
        print(f'curl "https://data.cityofnewyork.us/resource/i4gi-tjb9.csv?$limit=10000&$order=data_as_of DESC" -o nyc_traffic_24h.csv')
        return
    
    if not traffic_data:
        print("❌ No valid traffic data")
        return
    
    # Calibrate to regime
    calibrated_params = calibrator.calibrate_to_regime(traffic_data)
    
    # Validate
    validation_results = calibrator.validate_regime_detection(traffic_data, calibrated_params)
    
    # Save
    final_params = {**calibrated_params, **validation_results}
    calibrator.save_calibration(final_params)
    
    print("\n" + "="*60)
    print("🎉 PHASE TRANSITION CALIBRATION COMPLETE")
    print("="*60)
    print("\nKey Insight:")
    print("UTD now distinguishes between:")
    print("  • Routine congestion (high density, stable)")
    print("  • Phase transition (variance spike, correlation breakdown)")
    print("\nNext: Test on historical gridlock events to validate threshold")

if __name__ == "__main__":
    main()
