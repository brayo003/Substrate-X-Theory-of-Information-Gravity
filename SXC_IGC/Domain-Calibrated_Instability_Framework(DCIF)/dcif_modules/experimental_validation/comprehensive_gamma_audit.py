import os
import json
import numpy as np

def extract_coefficients(filepath):
    """Extract beta and gamma from any coefficient file structure"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Try different structures
    beta, gamma = None, None
    
    # Check various possible structures
    if isinstance(data, dict):
        # Direct keys
        if 'beta' in data and 'gamma' in data:
            beta = data['beta']
            gamma = data['gamma']
        # Nested in 'coefficients'
        elif 'coefficients' in data and isinstance(data['coefficients'], dict):
            coeff = data['coefficients']
            if 'beta' in coeff and 'gamma' in coeff:
                beta = coeff['beta']
                gamma = coeff['gamma']
        # Check for lowercase/uppercase variations
        elif 'Beta' in data and 'Gamma' in data:
            beta = data['Beta']
            gamma = data['Gamma']
        elif 'BETA' in data and 'GAMMA' in data:
            beta = data['BETA']
            gamma = data['GAMMA']
    
    return beta, gamma

def main():
    print("SXC-V12: COMPREHENSIVE GAMMA UNIVERSALITY AUDIT")
    print("="*70)
    
    results = []
    
    # Check all module directories
    for item in os.listdir('.'):
        if os.path.isdir(item) and not item.startswith('.'):
            coeff_file = os.path.join(item, 'coefficients.json')
            if os.path.exists(coeff_file):
                beta, gamma = extract_coefficients(coeff_file)
                if beta is not None and gamma is not None:
                    ratio = beta / gamma if gamma != 0 else float('inf')
                    results.append({
                        'module': item,
                        'beta': beta,
                        'gamma': gamma,
                        'ratio': ratio
                    })
                    print(f"{item:<30} | β={beta:>8.4f} | γ={gamma:>8.4f} | β/γ={ratio:>10.2f}")
    
    if results:
        print("\n" + "="*70)
        print("GAMMA (γ) DISTRIBUTION ANALYSIS:")
        print("-"*70)
        
        gammas = [r['gamma'] for r in results]
        betas = [r['beta'] for r in results]
        ratios = [r['ratio'] for r in results if r['ratio'] != float('inf')]
        
        # Calculate statistics
        print(f"Number of modules with valid coefficients: {len(results)}")
        print(f"γ range: {min(gammas):.6f} to {max(gammas):.6f}")
        print(f"β range: {min(betas):.6f} to {max(betas):.6f}")
        
        if ratios:
            print(f"β/γ ratio range: {min(ratios):.2f} to {max(ratios):.2f}")
        
        mean_gamma = np.mean(gammas)
        median_gamma = np.median(gammas)
        std_gamma = np.std(gammas)
        
        print(f"\nγ Statistics:")
        print(f"  Mean γ:    {mean_gamma:.6f}")
        print(f"  Median γ:  {median_gamma:.6f}")
        print(f"  Std γ:     {std_gamma:.6f}")
        print(f"  CV (%):    {(std_gamma/mean_gamma*100):.2f}%")
        
        # Check for clustering around 0.04
        print(f"\nDistance from γ = 0.04:")
        for r in results:
            diff = abs(r['gamma'] - 0.04)
            diff_pct = (diff / 0.04) * 100
            if diff_pct < 10:  # Within 10%
                print(f"  {r['module']:<30}: γ={r['gamma']:.4f} ({diff_pct:.1f}% from 0.04)")
        
        # Count how many are near 0.04
        near_004 = sum(1 for g in gammas if abs(g - 0.04) < 0.01)
        print(f"\nModules with γ ≈ 0.04 ±0.01: {near_004}/{len(results)}")
        
        if near_004 / len(results) > 0.5:
            print("⚡ STRONG EVIDENCE: γ clusters around 0.04 across domains!")
        
        # Save detailed results
        import pandas as pd
        df = pd.DataFrame(results)
        df = df.sort_values('gamma')
        df.to_csv('gamma_universality_audit.csv', index=False)
        print(f"\nDetailed results saved to: gamma_universality_audit.csv")
        
    else:
        print("No valid coefficient files found!")

if __name__ == "__main__":
    main()
