import numpy as np
import pandas as pd

class UniversalTensionDetector:
    # 👑 THE GOVERNING UNIVERSAL CONSTANT
    C_UNIVERSAL = 2.0 
    
    # 🧬 DOMAIN STRUCTURAL FINGERPRINTS (K), RESILIENCE (R), AND MAX LOSS (MMaxLoss)
    DOMAIN_PARAMETERS = {
        'finance': {
            'R': 0.012,        # Baseline Volatility during calm
            'K': 1.333,        # Structural Factor
            'MMaxLoss': -0.22  # Maximum loss threshold for capitulation entry
        },
        'social': {
            'R': 0.0016,       # Baseline Volatility during calm
            'K': 0.800,        # Structural Factor  
            'MMaxLoss': -0.18  # Maximum narrative collapse threshold
        },
        'geopolitics': {
            'R': 0.0020,       # Baseline Volatility during calm
            'K': 0.800,        # Structural Factor
            'MMaxLoss': -0.25  # Maximum geopolitical stress threshold
        }
    }

    def __init__(self, domain='finance'):
        self.domain = domain.lower()
        if self.domain not in self.DOMAIN_PARAMETERS:
            raise ValueError(f"Domain '{domain}' not found. Available: {list(self.DOMAIN_PARAMETERS.keys())}")
        
        params = self.DOMAIN_PARAMETERS[self.domain]
        self.R = params['R']
        self.K = params['K']
        self.MMaxLoss = params['MMaxLoss']
        
        # Calculate Domain-Specific Critical Volatility Threshold
        self.sigma_critical = self.C_UNIVERSAL * self.R * self.K
        
        # Momentum thresholds
        self.momentum_crisis_threshold = -0.08
        self.extreme_momentum_threshold = -0.15

    def detect_tension(self, series):
        """Main Engine: Defensive tension detection"""
        if series is None or len(series) < 22:
            return {'error': 'Insufficient data'}
        
        try:
            returns = series.pct_change().dropna()
            sigma_current = returns.std()
            
            recent_period = min(30, len(series) // 3)
            momentum = (series.iloc[-1] - series.iloc[-recent_period]) / series.iloc[-recent_period]
            
            # Tension Ratio (Universal Law)
            tension_ratio = sigma_current / self.sigma_critical
            vol_score = min(tension_ratio * 0.5, 0.5)
            
            # Momentum Score
            mom_score = 0
            if momentum < self.momentum_crisis_threshold:
                mom_score = 0.25
            if momentum < self.extreme_momentum_threshold:
                mom_score = 0.5
            
            final_score = vol_score + mom_score 
            
            level = "✅ STABLE"
            if final_score >= 0.5:
                level = "⚠️ TENSION"
            if final_score >= 0.75:
                level = "🚨 CRISIS"
            if final_score >= 0.95:
                level = "💥 COLLAPSE IMMINENT"

            return {
                'sigma_current': round(sigma_current, 5),
                'sigma_critical': round(self.sigma_critical, 5),
                'momentum': round(momentum, 3),
                'final_score': round(final_score, 2),
                'level': level,
                'tension_ratio': round(tension_ratio, 2)
            }

        except Exception as e:
            return {'error': str(e)}

    def detect_capitulation(self, series):
        """Inverse Engine: Offensive opportunity detection"""
        tension_result = self.detect_tension(series)
        
        if 'error' in tension_result:
            return {'error': tension_result['error']}
        
        TR = tension_result['tension_ratio']
        momentum = tension_result['momentum']
        
        # 🎯 CAPITULATION ENTRY LOGIC
        if TR > 1.0 and momentum <= self.MMaxLoss:
            signal = '⚔️ CAPITULATION ENTRY - Maximum inefficiency point reached'
            confidence = min(0.95, (TR - 1.0) * 2 + abs(momentum - self.MMaxLoss) * 3)
        else:
            signal = '🛡️ NO ENTRY - Awaiting capitulation conditions'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': round(confidence, 2),
            'conditions_met': {
                'tension_ratio_above_critical': TR > 1.0,
                'momentum_at_max_loss': momentum <= self.MMaxLoss,
                'tension_ratio': round(TR, 2),
                'momentum': round(momentum, 3),
                'MMaxLoss_threshold': self.MMaxLoss
            },
            'defensive_status': tension_result
        }

# Test the dual-engine system
if __name__ == '__main__':
    print("🧪 TESTING DUAL-ENGINE UNIVERSAL TENSION SYSTEM")
    print("=" * 60)
    
    # Simulate crisis data
    crisis_data = pd.Series([100.0] + list(100 + np.cumsum(np.random.normal(0, 0.040, 60))))
    
    detector = UniversalTensionDetector(domain='finance')
    
    print("1. MAIN ENGINE (Defensive):")
    defense = detector.detect_tension(crisis_data)
    for key, value in defense.items():
        print(f"   {key}: {value}")
    
    print("\n2. INVERSE ENGINE (Offensive):")
    offense = detector.detect_capitulation(crisis_data)
    for key, value in offense.items():
        print(f"   {key}: {value}")
