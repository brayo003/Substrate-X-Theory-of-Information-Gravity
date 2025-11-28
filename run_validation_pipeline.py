# run_validation_pipeline.py

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# 1. IMPORT CORE COMPONENTS
# Add parent directory to path to allow import of core/ and domains/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.universal_stable_core import UniversalDynamicsEngine
from domains.urban_config import get_urban_parameters

# Define directories for output
ANALYSIS_DIR = 'analysis'
LATEST_DATA_DIR = os.path.join(ANALYSIS_DIR, 'latest_data')
PLOTS_DIR = os.path.join(ANALYSIS_DIR, 'real_time_plots')

# Ensure output directories exist
os.makedirs(LATEST_DATA_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

def run_urban_validation_pipeline(num_steps=100):
    """
    Executes a complete validation run for the Urban Dynamics domain.
    """
    print("\n--- 🏙️ Starting Urban Validation Pipeline ---")
    
    # --- STEP 1: LOAD CONFIGURATION ---
    try:
        params, initial_fields = get_urban_parameters()
    except Exception as e:
        print(f"ERROR: Failed to load urban parameters: {e}")
        return

    print(f"Parameters loaded: R={params['R']}, D={params['D']}, Grid={params['GRID_RES']}")
    
    # --- STEP 2: INITIALIZE AND RUN ENGINE ---
    
    # Initialize the Universal Engine
    engine = UniversalDynamicsEngine(params)
    
    # Set initial conditions from config
    engine.set_initial_conditions(
        rho_initial=initial_fields['rho'], 
        E_initial=initial_fields['E'], 
        F_initial=initial_fields['F']
    )
    
    print(f"Engine initialized. Running simulation for {num_steps} time steps...")
    
    # Run the core simulation
    final_fields, final_metrics = engine.run_simulation(num_steps)
    
    if not final_metrics.get('stability_flag', False):
        print("🚨 WARNING: Simulation reported instability!")

    # --- STEP 3: ANALYSIS AND OUTPUT ---
    
    # 3a. Save Raw Data
    rho_final = final_fields['rho']
    data_path = os.path.join(LATEST_DATA_DIR, 'urban_final_rho.npz')
    np.savez_compressed(data_path, rho=rho_final)
    print(f"✅ Final density field saved to: {data_path}")

    # 3b. Generate and Save Plot (Heatmap of final Rho field)
    try:
        plt.figure(figsize=(8, 8))
        # Assuming the field is 2D, squeeze to remove the Z-axis dimension
        rho_2d = np.squeeze(rho_final) 
        plt.imshow(rho_2d, cmap='viridis', origin='lower')
        plt.colorbar(label='Information Mass Density (rho)')
        plt.title(f"Urban Final Density Field (Variance: {final_metrics['final_variance']:.4f})")
        
        plot_path = os.path.join(PLOTS_DIR, 'urban_density_heatmap.png')
        plt.savefig(plot_path)
        plt.close()
        print(f"✅ Final heatmap plot saved to: {plot_path}")
    
    except Exception as e:
        print(f"ERROR: Failed to generate or save plot: {e}")
        
    print("--- Pipeline Complete. Check analysis/ folder. ---")


if __name__ == '__main__':
    run_urban_validation_pipeline(num_steps=200)

