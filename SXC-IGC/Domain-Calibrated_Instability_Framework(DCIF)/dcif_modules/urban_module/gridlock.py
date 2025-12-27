#!/usr/bin/env python3
"""
COMPLETE UTD GRIDLOCK DETECTION TEST
Downloads multiple traffic snapshots and validates UTD can distinguish regimes
NO MANUAL EDITING REQUIRED - fully automated
"""
import numpy as np
import csv
import json
import subprocess
import os
from collections import defaultdict
from datetime import datetime

class CompleteUTDTest:
    def __init__(self):
        self.GRID_X, self.GRID_Y = 20, 20
        self.lat_min, self.lat_max = 40.70, 40.88
        self.lon_min, self.lon_max = -74.02, -73.90
        
    def download_snapshots(self):
        """Download multiple traffic snapshots from different times"""
        print("="*70)
        print("STEP 1: DOWNLOADING TRAFFIC DATA FROM DIFFERENT TIMES")
        print("="*70)
        
        base_url = "https://data.cityofnewyork.us/resource/i4gi-tjb9.csv"
        
        snapshots = [
            {'name': 'Most Recent', 'offset': 0, 'filename': 'snap_0.csv'},
            {'name': 'Earlier-1', 'offset': 40000, 'filename': 'snap_1.csv'},
            {'name': 'Earlier-2', 'offset': 80000, 'filename': 'snap_2.csv'},
            {'name': 'Earlier-3', 'offset': 120000, 'filename': 'snap_3.csv'},
            {'name': 'Earlier-4', 'offset': 160000, 'filename': 'snap_4.csv'},
        ]
        
        downloaded = []
        
        for i, snap in enumerate(snapshots, 1):
            print(f"\n[{i}/{len(snapshots)}] Downloading: {snap['name']}")
            
            # Construct URL properly
            url = f"{base_url}?$limit=8000&$offset={snap['offset']}&$order=data_as_of%20DESC"
            
            try:
                # Use subprocess with proper shell escaping
                result = subprocess.run(
                    ['curl', '-s', url, '-o', snap['filename']],
                    capture_output=True,
                    timeout=90
                )
                
                if result.returncode == 0 and os.path.exists(snap['filename']):
                    # Check file size
                    size = os.path.getsize(snap['filename'])
                    if size > 1000:
                        with open(snap['filename'], 'r') as f:
                            lines = len(f.readlines())
                            if lines > 100:
                                print(f"   ✅ Downloaded {lines-1} records ({size//1024}KB)")
                                downloaded.append(snap)
                            else:
                                print(f"   ⚠️  File too small ({lines} lines)")
                    else:
                        print(f"   ⚠️  Download failed or empty")
                else:
                    print(f"   ❌ Download error")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n✅ Successfully downloaded {len(downloaded)} snapshots")
        return downloaded
    
    def analyze_snapshot(self, filename):
        """Analyze traffic conditions in a snapshot"""
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
                        timestamp = row.get('data_as_of', 'N/A')
                        
                        grid_x = int((lat - self.lat_min) / (self.lat_max - self.lat_min) * (self.GRID_X - 1))
                        grid_y = int((lon - self.lon_min) / (self.lon_max - self.lon_min) * (self.GRID_Y - 1))
                        
                        if 0 <= grid_x < self.GRID_X and 0 <= grid_y < self.GRID_Y:
                            traffic_data.append({
                                'speed': speed,
                                'grid_x': grid_x,
                                'grid_y': grid_y,
                                'timestamp': timestamp
                            })
                except (ValueError, KeyError, IndexError):
                    continue
        
        if not traffic_data:
            return None
        
        # Get timestamp
        timestamps = [t['timestamp'] for t in traffic_data if t['timestamp'] != 'N/A']
        timestamp = timestamps[0] if timestamps else 'Unknown'
        
        # Calculate metrics
        speeds = np.array([t['speed'] for t in traffic_data])
        
        metrics = {
            'timestamp': timestamp,
            'total_readings': len(speeds),
            'mean_speed': float(np.mean(speeds)),
            'median_speed': float(np.median(speeds)),
            'std_speed': float(np.std(speeds)),
            'pct_stopped': float(np.sum(speeds < 1) / len(speeds) * 100),
            'pct_crawl': float(np.sum((speeds >= 1) & (speeds < 5)) / len(speeds) * 100),
            'pct_severe': float(np.sum((speeds >= 5) & (speeds < 15)) / len(speeds) * 100),
            'pct_congested': float(np.sum((speeds >= 15) & (speeds < 25)) / len(speeds) * 100),
            'pct_moving': float(np.sum(speeds >= 25) / len(speeds) * 100),
        }
        
        # Classify severity (CORRECTED THRESHOLDS)
        if metrics['pct_stopped'] > 60 and metrics['mean_speed'] < 8:
            severity = 'GRIDLOCK'
            severity_score = 1.0
        elif metrics['pct_stopped'] > 45 and metrics['mean_speed'] < 12:
            severity = 'CRITICAL'
            severity_score = 0.85
        elif metrics['pct_stopped'] > 35 and metrics['mean_speed'] < 18:
            severity = 'STRESSED'
            severity_score = 0.6
        elif metrics['mean_speed'] < 25:
            severity = 'CONGESTED'
            severity_score = 0.4
        else:
            severity = 'FREE_FLOW'
            severity_score = 0.1
        
        metrics['severity'] = severity
        metrics['severity_score'] = severity_score
        
        return traffic_data, metrics
    
    def compute_utd_tension(self, traffic_data):
        """Compute UTD tension for traffic data"""
        # Create tension fields
        speeds_by_grid = defaultdict(list)
        for t in traffic_data:
            speeds_by_grid[(t['grid_x'], t['grid_y'])].append(t['speed'])
        
        rho = np.zeros((self.GRID_X, self.GRID_Y))
        E = np.zeros((self.GRID_X, self.GRID_Y))
        F = np.ones((self.GRID_X, self.GRID_Y)) * 0.3
        
        # Simple but reasonable parameters
        speed_scale = 35.0  # NYC typical free-flow
        density_exp = 1.5
        
        for (gx, gy), speeds in speeds_by_grid.items():
            if len(speeds) > 0:
                avg_speed = np.mean(speeds)
                speed_var = np.var(speeds) if len(speeds) > 1 else 0
                
                # Density
                rho[gx, gy] = max(0, min(1, (1 - (avg_speed / speed_scale))**density_exp))
                
                # Excitation (variance = instability)
                E[gx, gy] = min(1, speed_var / 150.0)
                
                # Capacity
                F[gx, gy] = min(1, 0.3 + len(speeds) / 20.0)
        
        # Normalize
        rho_norm = rho / (np.max(rho) + 1e-10)
        E_norm = E / (np.max(E) + 1e-10)
        F_norm = F / (np.max(F) + 1e-10)
        
        # Spatial gradients (stress propagation)
        rho_grad_x = np.abs(np.gradient(rho_norm, axis=0))
        rho_grad_y = np.abs(np.gradient(rho_norm, axis=1))
        spatial_stress = np.sqrt(rho_grad_x**2 + rho_grad_y**2)
        
        # UTD formula
        # Emphasis on variance (E) for phase transition detection
        r, a, b = 1.5, 2.0, 1.5
        excitation_weight = 2.0
        
        tension = (r * rho_norm + 
                  a * rho_norm**2 - 
                  b * rho_norm**3 + 
                  excitation_weight * E_norm +
                  0.8 * spatial_stress -
                  F_norm)
        
        mean_tension = np.mean(tension)
        max_tension = np.max(tension)
        std_tension = np.std(tension)
        
        return mean_tension, max_tension, std_tension
    
    def run_complete_test(self):
        """Run complete UTD validation test"""
        print("\n" + "="*70)
        print("UTD COMPLETE GRIDLOCK DETECTION TEST")
        print("="*70)
        print("This will:")
        print("1. Download traffic data from multiple times")
        print("2. Analyze actual traffic conditions")
        print("3. Compute UTD tension for each")
        print("4. Validate if UTD correctly ranks severity")
        print()
        input("Press Enter to start...")
        
        # Download data
        snapshots = self.download_snapshots()
        
        if len(snapshots) < 2:
            print("\n❌ Need at least 2 snapshots for comparison")
            return
        
        # Analyze each snapshot
        print("\n" + "="*70)
        print("STEP 2: ANALYZING TRAFFIC CONDITIONS")
        print("="*70)
        
        results = []
        
        for i, snap in enumerate(snapshots, 1):
            print(f"\n[{i}/{len(snapshots)}] Analyzing: {snap['name']}")
            print("-" * 60)
            
            analysis = self.analyze_snapshot(snap['filename'])
            
            if analysis is None:
                print("   ⚠️  No valid data")
                continue
            
            traffic_data, metrics = analysis
            
            print(f"   Timestamp: {metrics['timestamp']}")
            print(f"   Total Readings: {metrics['total_readings']}")
            print(f"   Mean Speed: {metrics['mean_speed']:.1f} mph")
            print(f"   Stopped (0-1mph): {metrics['pct_stopped']:.1f}%")
            print(f"   Moving (25+mph): {metrics['pct_moving']:.1f}%")
            print(f"   Severity: {metrics['severity']} (score: {metrics['severity_score']:.2f})")
            
            results.append({
                'name': snap['name'],
                'filename': snap['filename'],
                'traffic_data': traffic_data,
                'metrics': metrics
            })
        
        if len(results) < 2:
            print("\n❌ Need at least 2 valid snapshots")
            return
        
        # Compute UTD tension
        print("\n" + "="*70)
        print("STEP 3: COMPUTING UTD TENSION")
        print("="*70)
        
        for i, result in enumerate(results, 1):
            print(f"\n[{i}/{len(results)}] {result['name']}")
            
            mean_t, max_t, std_t = self.compute_utd_tension(result['traffic_data'])
            
            result['utd_tension'] = mean_t
            result['utd_max'] = max_t
            result['utd_std'] = std_t
            
            print(f"   UTD Mean Tension: {mean_t:.4f}")
            print(f"   UTD Max Tension: {max_t:.4f}")
            print(f"   UTD Std Dev: {std_t:.4f}")
        
        # Validation
        print("\n" + "="*70)
        print("STEP 4: VALIDATION - DOES UTD CORRECTLY RANK SEVERITY?")
        print("="*70)
        
        # Sort by actual severity
        results_by_severity = sorted(results, key=lambda x: x['metrics']['severity_score'])
        
        # Sort by UTD tension
        results_by_utd = sorted(results, key=lambda x: x['utd_tension'])
        
        print("\n📊 RANKING BY ACTUAL SEVERITY:")
        for i, r in enumerate(results_by_severity, 1):
            print(f"   {i}. {r['name']}: {r['metrics']['severity']} "
                  f"(speed: {r['metrics']['mean_speed']:.1f} mph, "
                  f"stopped: {r['metrics']['pct_stopped']:.1f}%)")
        
        print("\n🎯 RANKING BY UTD TENSION:")
        for i, r in enumerate(results_by_utd, 1):
            print(f"   {i}. {r['name']}: Tension = {r['utd_tension']:.4f}")
        
        # Check correlation
        print("\n" + "="*70)
        print("VALIDATION RESULTS")
        print("="*70)
        
        severity_ranks = [results_by_severity.index(r) for r in results]
        utd_ranks = [results_by_utd.index(r) for r in results]
        
        # Spearman correlation
        from scipy.stats import spearmanr
        try:
            correlation, p_value = spearmanr(severity_ranks, utd_ranks)
            
            print(f"\n📈 Correlation between UTD and Actual Severity:")
            print(f"   Spearman ρ = {correlation:.3f}")
            print(f"   p-value = {p_value:.4f}")
            
            if correlation > 0.8:
                print("\n✅ EXCELLENT - UTD strongly correlates with actual conditions")
            elif correlation > 0.6:
                print("\n✅ GOOD - UTD generally tracks severity correctly")
            elif correlation > 0.4:
                print("\n⚠️  MODERATE - UTD shows some predictive power")
            else:
                print("\n❌ POOR - UTD does not correlate with severity")
                
        except:
            # If scipy not available, do simple comparison
            print("\n📈 Ranking Comparison:")
            matches = sum(1 for i in range(len(results)) 
                         if abs(severity_ranks[i] - utd_ranks[i]) <= 1)
            accuracy = matches / len(results) * 100
            
            print(f"   Rankings match or ±1: {matches}/{len(results)} = {accuracy:.1f}%")
            
            if accuracy > 70:
                print("\n✅ GOOD - UTD ranking mostly matches reality")
            elif accuracy > 50:
                print("\n⚠️  MODERATE - UTD has some predictive power")
            else:
                print("\n❌ POOR - UTD ranking does not match reality")
        
        # Summary table
        print("\n" + "="*70)
        print("DETAILED COMPARISON TABLE")
        print("="*70)
        print(f"\n{'Snapshot':<15} {'Severity':<12} {'Mean Speed':<12} {'UTD Tension':<12}")
        print("-" * 60)
        for r in sorted(results, key=lambda x: x['utd_tension']):
            print(f"{r['name']:<15} {r['metrics']['severity']:<12} "
                  f"{r['metrics']['mean_speed']:>6.1f} mph   "
                  f"{r['utd_tension']:>8.4f}")
        
        # Save results
        output = {
            'test_timestamp': datetime.now().isoformat(),
            'snapshots_tested': len(results),
            'results': [{
                'name': r['name'],
                'severity': r['metrics']['severity'],
                'severity_score': r['metrics']['severity_score'],
                'mean_speed': r['metrics']['mean_speed'],
                'pct_stopped': r['metrics']['pct_stopped'],
                'pct_moving': r['metrics']['pct_moving'],
                'utd_tension': r['utd_tension'],
                'timestamp': r['metrics']['timestamp']
            } for r in results]
        }
        
        with open('utd_test_results.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print("\n💾 Results saved to utd_test_results.json")
        
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)

if __name__ == "__main__":
    tester = CompleteUTDTest()
    tester.run_complete_test()
