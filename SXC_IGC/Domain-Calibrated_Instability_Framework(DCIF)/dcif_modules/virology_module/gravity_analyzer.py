import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

def calculate_gravity():
    print("--- Substrate-X: Gravitational Mass Comparison [Fixed] ---")
    
    try:
        covid = pd.read_csv("covid_data_raw.csv")
        flu = pd.read_csv("flu_data_raw.csv")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Dynamic Column Detection for Flu
    # The engine looks for common epidemiological headers
    flu_candidates = ['value', 'Incident Hospitalizations', 'cases', 'Daily cases']
    flu_col = next((c for c in flu_candidates if c in flu.columns), None)
    
    if not flu_col:
        # Fallback: Use the last numeric column if specific headers fail
        flu_col = flu.select_dtypes(include=[np.number]).columns[-1]
        print(f"Notice: Using fallback column '{flu_col}' for Flu Excitation.")

    # 2. Extract High-Tension Anchors
    c_excitation = covid['new_cases_per_million'].dropna().mean()
    c_tension = covid['new_deaths_per_million'].dropna().mean()
    
    f_excitation = flu[flu_col].dropna().mean() 
    f_tension = f_excitation * 0.001 # Baseline dissipation constant

    # 3. Calculate Beta (Information Mass)
    # This measures the curvature of the impact on the substrate
    beta_covid = np.log10(c_tension + 1) / np.log10(c_excitation + 1)
    beta_flu = np.log10(f_tension + 1) / np.log10(f_excitation + 1)

    print(f"\n[PHYSICAL QUANTIFICATION]")
    print(f"COVID-19 Particle Mass (Beta): {beta_covid:.6f}")
    print(f"Influenza Particle Mass (Beta): {beta_flu:.6f}")
    
    # 4. Relative Gravity
    ratio = beta_covid / beta_flu
    print(f"\nRelative Information Gravity: {ratio:.2f}x")
    
    print("\n--- Substrate Diagnostics ---")
    if ratio > 1:
        print(f"COVID-19 is {ratio:.1f}x more likely to warp the healthcare substrate.")
        
    # Calibration to the 4.19 Singularity
    # K represents the systemic curvature
    k_factor = (beta_covid / 0.5) * 4.19
    print(f"Current Systemic Curvature (K): {k_factor:.4f}")

    if k_factor >= 4.19:
        print("WARNING: K >= 4.19. Substrate is in a state of pre-Snap Tension.")
    else:
        print("STATUS: Substrate is currently Elastic.")

if __name__ == "__main__":
    calculate_gravity()
