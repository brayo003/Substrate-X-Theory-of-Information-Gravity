import pandas as pd
import numpy as np

def generate_matrix():
    # Load the 34-domain substrate data
    df = pd.read_csv('domain_scales.csv')
    domains = df['domain'].tolist()
    gammas = df['gamma'].tolist()
    betas = df['beta'].tolist()
    
    n = len(domains)
    matrix = np.zeros((n, n))
    
    # The Universal Conflict Constant
    CONFLICT_FACTOR = 2.8
    
    print("SXC-V12: INTER-DOMAIN INTERFERENCE MATRIX (IDIM)")
    print("="*80)
    print("Target: Identifying Impedance Mismatch (Instant -> Slow Pressure)")
    print("-" * 80)
    
    results = []
    for i in range(n):
        for j in range(n):
            if i == j: continue
            
            # Impedance Mismatch Logic:
            # If Source (i) is FASTER than Target (j), pressure accumulates.
            # Pressure = (Gamma_Source / Gamma_Target) * Conflict_Factor
            if gammas[i] > gammas[j]:
                interference = (gammas[i] / gammas[j]) * CONFLICT_FACTOR
                matrix[i, j] = interference
                
                if interference > 10.0: # High Risk Threshold
                    results.append({
                        'Source': domains[i],
                        'Target': domains[j],
                        'Interference': interference,
                        'Window_Collapse': 1.20397 / gammas[j]
                    })

    # Display Top 10 Critical Vulnerabilities
    rdf = pd.DataFrame(results).sort_values(by='Interference', ascending=False)
    print(rdf.head(10).to_string(index=False))
    
    print("\n" + "="*80)
    print("DEDUCTION: These pairs represent 'Ghost Snap' priorities.")
    print("High interference means the Source overwhelms the Target's leak rate.")

if __name__ == "__main__":
    generate_matrix()
