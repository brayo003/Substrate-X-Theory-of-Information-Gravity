import sys
import os
import time

# Ensure directory compliance
sys.path.append(os.getcwd())

from SXC_IGC.Topological_Navigation.gamma_radar_v12 import check_pole_proximity

def run_governor_loop(simulated_health_drain):
    print("SXC-V12-G: SYSTEM INITIALIZED")
    print("-" * 40)
    
    for health in simulated_health_drain:
        # 1. Radar checks the 1909 Geography
        trigger_reset, tension = check_pole_proximity(health, redline=5.0)
        
        status = "CRITICAL: TRIGGERING HYSTERESIS RESET" if trigger_reset else "NOMINAL"
        
        print(f"Substrate Health: {health:.2f} | Gamma Tension: {tension:.4f} | Status: {status}")
        
        if trigger_reset:
            print("-" * 40)
            print("FIREWALL ACTIVE: System anchored back to 0.4 baseline.")
            print("-" * 40)
            break
        time.sleep(0.1)

# Simulation: A system sliding from 2.0 (Stable) to -0.1 (Crash)
nairobi_scenario = [2.0, 1.5, 1.0, 0.5, 0.2, 0.1, 0.05, -0.01]
run_governor_loop(nairobi_scenario)
