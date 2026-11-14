#!/usr/bin/env python3
"""
UTD PHASE TRANSITION VALIDATOR
Tests if calibrated UTD can distinguish between different traffic regimes
Focuses on detecting STRUCTURAL COLLAPSE, not counting slow roads
"""
import numpy as np
import csv
import json
import subprocess
from datetime import datetime
from collections import defaultdict

class PhaseTransitionValidator:
    def __init__(self):
        self.snapshots = []
        self.GRID_X, self.GRID_Y = 20, 20
        self.lat_min, self.lat_max = 40.70, 40.88
        self.lon_min, self.lon_max = -74.02, -73.90
        
        # Known historical events to test (if data available)
        self.target_events = {
            'normal_morning': {'time': '6am-8am', 'expected': 'FREE_FLOW'},
            'rush_hour': {'time': '8am-10am', 'expected': 'CONGESTED'},
            'midday': {'time': '12pm-2pm', 'expected': 'CONGESTED'},
            'evening_rush': {'time': '5pm-7pm', 'expected': 'STRESSED'},
            'night': {'time': '10pm-12am', 'expected': 'FREE_FLOW'}
        }
    
    def download_time_series(self):
        """
        Download traffic data from different times to capture regime diversity
        """
        print("📥 DOWNLOADING TIME-SERIES TRAFFIC DATA")
        print("="*60)
        print("Goal: Capture different traffic regimes for validation")
        print()
        
        # Try to get data from different time periods
        # Note: NYC Open Data might not have precise time filtering
        # We'll get multiple samples and analyze their regimes
        
        snapshots = [
            {
                'name': 'Most Recent',
                'query': '$limit=8000&$order=data_as_of DESC',
                'filename': 'regime_test_recent.csv',
            },
            {
                'name': 'Offset 10k (Earlier)',
                'query': '$limit=8000&$offset=10000&$order=data_as_of DESC',
                'filename': 'regime_test_earlier.csv',
            },
            {
                'name': 'Offset 20k (Even Earlier)',
                'query': '$limit=8000&$offset=20000&$order=data_as_of DESC',
                'filename': 'regime_test_older.csv',
            },
            {
                'name': 'Offset 30k (Historical)',
                'query': '$limit=8000&$offset=30000&$order=data_as_of DESC',
                'filename': 'regime_test_historical.csv',
            }
        ]
        
        base_url = "https://data.cityofnewyork.us/resource/i4gi-tjb9.csv"
        
        downloaded = []
        for i, snap in enumerate(snapshots, 1):
            print(f"📡 [{i}/{len(snapshots)}] Downloading: {snap['name']}")
            url = f"{base_url}?{snap['query']}"
            filename = snap['filename']
            
            try:
                cmd = f'curl -s "{url}" -o {filename}'
                result = subprocess.run(cmd, shell=True, capture_output=True, timeout=90)
                
                if result.returncode == 0:
                    try:
                        with open(filename, 'r') as f:
                            lines = f.readlines()
                            if len(lines) > 100:
                                print(f"   ✅ {len(lines)-1} records")
                                snap['records'] = len(lines) - 1
                                downloaded.append(snap)
                            else:
                                print(f"   ⚠️  Insufficient data ({len(lines)} lines)")
                    except:
                        print(f"   ❌ Read error")
                else:
                    print(f"   ❌ Download failed")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n✅ Downloaded {len(downloaded)} snapshots")
        return downloaded
    
    def load_snapshot(self, filename):
        """Load traffic snapshot"""
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
                        
                        grid_x = int((lat - self.lat_min) / (self.lat_max - self.lat_min) * (self.GRID_X - 1))
                        grid_y = int((lon - self.lon_min) / (self.lon_max - self.lon_min) * (self.GRID_Y - 1))
                        
                        if 0 <= grid_x < self.GRID_X and 0 <= grid_y < self.GRID_Y:
                            traffic_data.append({
                                'speed': speed,
                                'grid_x': grid_x,
                                'grid_y': grid_y
                            })
                except (ValueError, KeyError, IndexError):
                    continue
        return traffic_data
    
    def classify_regime(self, traffic_data):
        """
        Classify regime based on PHASE TRANSITION indicators
        """
        if not traffic_data:
            return 'UNKNOWN', 0, {}
        
        speeds = np.array([t['speed'] for t in traffic_data])
        
        avg_speed = np.mean(speeds)
        speed_variance = np.var(speeds)
        pct_severe = np.sum(speeds < 5) / len(speeds)
        pct_stopped = np.sum(speeds < 1) / len(speeds)
        
        # Spatial correlation
        grid_speeds = defaultdict(list)
        for t in traffic_data:
            grid_speeds[(t['grid_x'], t['grid_y'])].append(t['speed'])
        
        severe_cells = sum(1 for speeds in grid_speeds.values() 
                          if speeds and np.mean(speeds) < 10)
        total_cells = len(grid_speeds)
        spatial_clustering = severe_cells / total_cells if total_cells > 0 else 0
        
        # Correlation score: high variance + high clustering = phase transition
        correlation_score = spatial_clustering * (speed_variance / 100)
        
        metrics = {
            'avg_speed': avg_speed,
            'speed_variance': speed_variance,
            'pct_severe': pct_severe * 100,
            'pct_stopped': pct_stopped * 100,
            'spatial_clustering': spatial_clustering,
            'correlation_score': correlation_score,
        }
        
        # Regime classification
        if pct_stopped > 0.3:
            regime = 'GRIDLOCK'
            regime_score = 1.0
        elif correlation_score > 0.15 and pct_severe > 0.4:
            regime = 'CRITICAL'
            regime_score = 0.85
        elif spatial_clustering > 0.5 and speed_variance > 150:
            regime = 'STRESSED'
            regime_score = 0.6
        elif avg_speed < 20 or pct_severe > 0.3:
            regime = 'CONGESTED'
            regime_score = 0.3
        else:
            regime = 'FREE_FLOW'
            regime_score = 0.0
        
        return regime, regime_score, metrics
    
    def create_tension_fields(self, traffic_data, params):
        """Create tension fields using calibrated parameters"""
        speeds_by_grid = defaultdict(list)
        for t in traffic_data:
            speeds_by_grid[(t['grid_x'], t['grid_y'])].append(t['speed'])
        
        rho = np.zeros((self.GRID_X, self.GRID_Y))
        E = np.zeros((self.GRID_X, self.GRID_Y))
        F = np.ones((self.GRID_X, self.GRID_Y)) * params['capacity_base']
        
        for (gx, gy), speeds in speeds_by_grid.items():
            if len(speeds) > 0:
                avg_speed = np.mean(speeds)
                speed_var = np.var(speeds) if len(speeds) > 1 else 0
                
                rho[gx, gy] = max(0, (1 - (avg_speed / params['speed_scale']))**params['density_exp'])
                E[gx, gy] = min(1, speed_var / 200.0)
                F[gx, gy] = min(1, params['capacity_base'] + len(speeds) / 15.0)
        
        return rho, E, F
    
    def predict_with_utd(self, traffic_data, params):
        """Predict regime using calibrated UTD"""
        rho, E, F = self.create_tension_fields(traffic_data, params)
        
        # Normalize
        rho_norm = rho / (np.max(rho) + 1e-10)
        E_norm = E / (np.max(E) + 1e-10)
        F_norm = F / (np.max(F) + 1e-10)
        
        # Spatial stress
        rho_grad_x = np.abs(np.gradient(rho_norm, axis=0))
        rho_grad_y = np.abs(np.gradient(rho_norm, axis=1))
        spatial_stress = np.sqrt(rho_grad_x**2 + rho_grad_y**2)
        
        # Compute tension with excitation weight
        excitation_weight = params.get('excitation_weight', 1.0)
        tension = (params['r'] * rho_norm + 
                  params['a'] * rho_norm**2 - 
                  params['b'] * rho_norm**3 + 
                  excitation_weight * E_norm +
                  0.5 * spatial_stress -
                  F_norm)
        
        mean_tension = np.mean(tension)
        max_tension = np.max(tension)
        std_tension = np.std(tension)
        
        # Map to regime score
        predicted_score = 1 / (1 + np.exp(-mean_tension))
        
        return predicted_score, mean_tension, max_tension, std_tension
    
    def validate_regime_separation(self, calibrated_params):
        """
        Test if UTD correctly separates different regimes
        """
        print("\n🔬 REGIME SEPARATION VALIDATION")
        print("="*60)
        print("Testing if UTD can distinguish between traffic regimes")
        print()
        
        results = []
        regime_counts = defaultdict(int)
        
        for i, snap in enumerate(self.snapshots, 1):
            print(f"📊 Snapshot {i}/{len(self.snapshots)}: {snap['name']}")
            print("-" * 50)
            
            traffic_data = self.load_snapshot(snap['filename'])
            
            if not traffic_data or len(traffic_data) < 100:
                print("   ⚠️  Insufficient data - skipping\n")
                continue
            
            # Ground truth regime
            true_regime, true_score, metrics = self.classify_regime(traffic_data)
            regime_counts[true_regime] += 1
            
            # UTD prediction
            pred_score, mean_t, max_t, std_t = self.predict_with_utd(traffic_data, calibrated_params)
            
            # Calculate error
            error = abs(pred_score - true_score)
            
            print(f"   True Regime: {true_regime} (score: {true_score:.3f})")
            print(f"   UTD Tension: {mean_t:.4f}")
            print(f"   UTD Score: {pred_score:.3f}")
            print(f"   Error: {error:.3f}")
            print(f"   Metrics:")
            print(f"     Avg Speed: {metrics['avg_speed']:.1f} mph")
            print(f"     Variance: {metrics['speed_variance']:.1f}")
            print(f"     Correlation: {metrics['correlation_score']:.4f}")
            
            # Assess prediction
            if error < 0.15:
                status = "✅ EXCELLENT"
            elif error < 0.25:
                status = "✅ GOOD"
            elif error < 0.35:
                status = "⚠️  ACCEPTABLE"
            else:
                status = "❌ POOR"
            
            print(f"   Assessment: {status}\n")
            
            results.append({
                'snapshot': snap['name'],
                'true_regime': true_regime,
                'true_score': true_score,
                'predicted_score': pred_score,
                'mean_tension': mean_t,
                'error': error,
                'metrics': metrics
            })
        
        return results, regime_counts
    
    def generate_report(self, results, regime_counts, params):
        """Generate regime detection validation report"""
        print("\n" + "="*60)
        print("📈 PHASE TRANSITION DETECTION REPORT")
        print("="*60)
        
        if not results:
            print("❌ No results to report")
            return
        
        errors = [r['error'] for r in results]
        
        print(f"\n📊 REGIME DIVERSITY:")
        for regime, count in sorted(regime_counts.items()):
            print(f"   {regime}: {count} snapshot(s)")
        
        print(f"\n📊 DETECTION PERFORMANCE:")
        print(f"   Snapshots tested: {len(results)}")
        print(f"   Mean Absolute Error: {np.mean(errors):.3f}")
        print(f"   Std Dev: {np.std(errors):.3f}")
        print(f"   Best Error: {np.min(errors):.3f}")
        print(f"   Worst Error: {np.max(errors):.3f}")
        
        # Accuracy by threshold
        excellent = sum(1 for e in errors if e < 0.15)
        good = sum(1 for e in errors if e < 0.25)
        acceptable = sum(1 for e in errors if e < 0.35)
        
        print(f"\n🎯 ACCURACY BREAKDOWN:")
        print(f"   Excellent (<15% error): {excellent}/{len(results)} = {100*excellent/len(results):.1f}%")
        print(f"   Good (<25% error): {good}/{len(results)} = {100*good/len(results):.1f}%")
        print(f"   Acceptable (<35% error): {acceptable}/{len(results)} = {100*acceptable/len(results):.1f}%")
        
        # Overall assessment
        if np.mean(errors) < 0.20:
            verdict = "✅ EXCELLENT - UTD reliably detects regime transitions"
        elif np.mean(errors) < 0.30:
            verdict = "✅ GOOD - UTD distinguishes regimes effectively"
        elif np.mean(errors) < 0.40:
            verdict = "⚠️  MODERATE - Some regime confusion, refinement needed"
        else:
            verdict = "❌ POOR - Significant calibration issues"
        
        print(f"\n{verdict}")
        
        # Critical thresholds
        print(f"\n🎯 CALIBRATED TENSION THRESHOLDS:")
        print(f"   < -2.0: FREE_FLOW (system has slack)")
        print(f"   -2.0 to -1.0: LOW RISK (normal conditions)")
        print(f"   -1.0 to 0.0: CONGESTED (stable but loaded)")
        print(f"   0.0 to +1.0: STRESSED (vulnerable)")
        print(f"   +1.0 to +2.0: CRITICAL (phase transition imminent)")
        print(f"   > +2.0: GRIDLOCK (catastrophic collapse)")
        
        # Save detailed report
        report = {
            'summary': {
                'snapshots_tested': len(results),
                'mean_error': float(np.mean(errors)),
                'std_error': float(np.std(errors)),
                'regime_counts': dict(regime_counts)
            },
            'calibrated_params': params,
            'results': results
        }
        
        with open('regime_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=float)
        
        print(f"\n💾 Detailed report saved to regime_validation_report.json")

def main():
    print("🔬 UTD PHASE TRANSITION VALIDATION")
    print("="*60)
    print("Testing calibrated UTD on diverse traffic regimes")
    print()
    
    # Load calibrated parameters
    try:
        with open('utd_regime_calibrated.json', 'r') as f:
            calibrated_params = json.load(f)
        print("✅ Loaded regime-calibrated parameters")
        print(f"   r={calibrated_params['r']:.4f}, excitation_weight={calibrated_params.get('excitation_weight', 1.0):.4f}")
    except FileNotFoundError:
        print("❌ No calibrated parameters found!")
        print("   Please run regime calibration first:")
        print("   python3 phase_transition_calibration.py")
        return
    
    validator = PhaseTransitionValidator()
    
    # Download multiple snapshots
    validator.snapshots = validator.download_time_series()
    
    if len(validator.snapshots) < 2:
        print("❌ Insufficient snapshots for validation")
        return
    
    # Validate regime separation
    results, regime_counts = validator.validate_regime_separation(calibrated_params)
    
    # Generate report
    validator.generate_report(results, regime_counts, calibrated_params)
    
    print("\n" + "="*60)
    print("✅ REGIME VALIDATION COMPLETE")
    print("="*60)
    print("\nNext Step: Test on known historical gridlock events")
    print("(e.g., Hurricane Sandy, Pope visit, snowstorms)")

if __name__ == "__main__":
    main()
