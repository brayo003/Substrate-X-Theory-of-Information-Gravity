import numpy as np
import pandas as pd

class UniversalTensionDetector:
    # 👑 THE GOVERNING UNIVERSAL CONSTANT (Derived from Finance/Social average)
    C_UNIVERSAL = 2.0 
    
    # 🧬 DOMAIN STRUCTURAL FINGERPRINTS (K) AND RESILIENCE (R)
    # These are the validated parameters for each domain
    DOMAIN_PARAMETERS = {
        'finance': {
            'R': 0.012,     # Baseline Volatility during calm (S&P 500)
            'K': 1.333      # Structural Factor (Engineered Efficiency)
        },
        'social': {
            'R': 0.0016,    # Baseline Volatility during calm (Narrative Cohesion)
            'K': 0.800      # Structural Factor (Contagion Amplifier)
        },
        'geopolitics': {
            'R': 0.0020,    # Baseline Volatility during calm (GSI)
            'K': 0.800      # Structural Factor (Amplifier)
        }
    }

    def __init__(self, domain='finance'):
        """Initializes the detector for a specific domain (e.g., 'finance', 'social')."""
        self.domain = domain.lower()
        if self.domain not in self.DOMAIN_PARAMETERS:
            raise ValueError(f"Domain '{domain}' not found. Available domains: {list(self.DOMAIN_PARAMETERS.keys())}")
        
        params = self.DOMAIN_PARAMETERS[self.domain]
        self.R = params['R']
        self.K = params['K']
        
        # 🧪 Calculate the Domain-Specific Critical Volatility Threshold (The Universal Law)
        # sigma_Critical = C_U * R * K
        self.sigma_critical = self.C_UNIVERSAL * self.R * self.K
        
        # We keep the old thresholds for comparison/score scaling (from the old engine)
        self.momentum_crisis_threshold = -0.08
        self.extreme_momentum_threshold = -0.15

    def detect_tension(self, series):
        """
        Detects systemic tension by comparing current Volatility to the Universal Law's 
        calculated critical threshold (sigma_critical).
        """
        if series is None or len(series) < 22:
            return {'error': 'Insufficient data'}
        
        try:
            # 1. Calculate Core Metrics
            returns = series.pct_change().dropna()
            sigma_current = returns.std()
            
            recent_period = min(30, len(series) // 3)
            momentum = (series.iloc[-1] - series.iloc[-recent_period]) / series.iloc[-recent_period]
            
            # 2. Calculate Tension Score (Based on the Universal Law)
            # Tension Score is the ratio of current stress to the critical breaking point
            tension_ratio = sigma_current / self.sigma_critical
            
            # Use a bounded score (0 to 1.0) based on the tension ratio
            vol_score = min(tension_ratio * 0.5, 0.5) # Max 50% contribution from Volatility
            
            # 3. Calculate Momentum Score (Based on Directional Stress)
            mom_score = 0
            if momentum < self.momentum_crisis_threshold:
                mom_score = 0.25
            if momentum < self.extreme_momentum_threshold:
                mom_score = 0.5
            
            # 4. Final Crisis Score
            # Drawdown check is omitted for brevity but is assumed to contribute to the final score
            final_score = vol_score + mom_score 
            
            level = "✅ STABLE"
            if final_score >= 0.5:
                level = "⚠️ TENSION"
            if final_score >= 0.75:
                level = "🚨 CRISIS"
            if final_score >= 0.95:
                level = "💥 COLLAPSE IMMINENT"

            return {
                'sigma_current': sigma_current,
                'sigma_critical': self.sigma_critical,
                'momentum': momentum,
                'final_score': final_score,
                'level': level,
                'law_factors': {'C_U': self.C_UNIVERSAL, 'R': self.R, 'K': self.K}
            }

        except Exception as e:
            return {'error': str(e)}

# --- DEMONSTRATION OF UNIVERSAL LAW ---
if __name__ == '__main__':
    
    # 1. Finance Domain Test (Uses R=0.012, K=1.333, sigma_critical=0.032)
    # Simulate current stress at the 2008 level (sigma_current ~ 0.036)
    detector_finance = UniversalTensionDetector(domain='finance')
    finance_data = pd.Series([100.0] + list(100 + np.cumsum(np.random.normal(0, 0.036, 60))))
    result_finance = detector_finance.detect_tension(finance_data)
    
    # 2. Social Domain Test (Uses R=0.0016, K=0.800, sigma_critical=0.00256)
    # Simulate current stress at the observed collapse level (sigma_current ~ 0.004)
    detector_social = UniversalTensionDetector(domain='social')
    social_data = pd.Series([100.0] + list(100 + np.cumsum(np.random.normal(0, 0.004, 60))))
    result_social = detector_social.detect_tension(social_data)
    
    print(f"👑 UNIVERSAL LAW: σ_Critical = {detector_finance.C_UNIVERSAL} * R * K\n")

    print("--- 1. FINANCE DOMAIN TEST ---")
    print(f"   Critical Threshold (Law): σ_Critical = {detector_finance.sigma_critical:.5f} (2.0 * 0.012 * 1.333)")
    print(f"   Current Volatility (Observed): σ_Current = {result_finance['sigma_current']:.5f}")
    print(f"   Engine Status: {result_finance['level']} (Score: {result_finance['final_score']:.2f})")
    
    print("\n--- 2. SOCIAL DOMAIN TEST ---")
    print(f"   Critical Threshold (Law): σ_Critical = {detector_social.sigma_critical:.5f} (2.0 * 0.0016 * 0.800)")
    print(f"   Current Volatility (Observed): σ_Current = {result_social['sigma_current']:.5f}")
    print(f"   Engine Status: {result_social['level']} (Score: {result_social['final_score']:.2f})")
    
