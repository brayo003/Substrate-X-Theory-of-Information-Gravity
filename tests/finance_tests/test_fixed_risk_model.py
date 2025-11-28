"""
Test for Integrated UDE Stability Filter (Pattern Metrics for Regime Detection).
Ensures the 'Stand Aside' rule is now governed by the Bio-Physics Variance Ratio.
"""
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Define a mock bot class for testing purposes
class MockFixedRiskTradingBot:
    # We now use a high Variance Ratio (V_R) as the threshold for 'Strong Trend'
    MIN_VARIANCE_RATIO_EXECUTE = 10000.0 

    def __init__(self, capital=10000, risk_per_trade=0.01, stop_loss_pct=0.05):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.stop_loss_pct = stop_loss_pct

    def calculate_position_size(self, price, u_variance_ratio):
        """Calculates shares using UDE Variance Ratio for filtering."""
        
        # UDE Stability Filter: EXECUTE only if the UDE shows a strong, emergent pattern
        if u_variance_ratio < self.MIN_VARIANCE_RATIO_EXECUTE:
            return 0  # STAND ASIDE (Low V_R = Range-bound/Unclear Regime)
        
        # Fixed 1R Risk Calculation (Executed only for high V_R)
        risk_amount = self.capital * self.risk_per_trade
        loss_per_share = price * self.stop_loss_pct
        
        if loss_per_share == 0:
            return 0
            
        return risk_amount / loss_per_share

class TestFixedRiskModel(unittest.TestCase):
    
    def setUp(self):
        self.initial_capital = 10000.00
        self.bot = MockFixedRiskTradingBot(capital=self.initial_capital)
        self.EXPECTED_LOSS_AMOUNT = self.initial_capital * self.bot.risk_per_trade # $100.00
        self.EXECUTE_SHARES_100 = 20.0 # $100 / ($100 * 0.05)

    def test_risk_neutrality_high_price(self):
        """Test position size for a high-priced asset ($100) at high V_R."""
        asset_price = 100.00
        # High V_R (Strong Pattern) should allow trade
        shares_to_buy = self.bot.calculate_position_size(asset_price, u_variance_ratio=12000.0)
        self.assertAlmostEqual(shares_to_buy, self.EXECUTE_SHARES_100, 2, "High V_R shares calculation error.")

    def test_regime_filter_stand_aside_low_vr(self):
        """Test the filter: V_R below threshold must result in 0 shares (STAND ASIDE)."""
        asset_price = 50.00
        # Low V_R (Range-bound/Homogeneous)
        shares_to_buy = self.bot.calculate_position_size(asset_price, u_variance_ratio=9999.0)
        self.assertEqual(shares_to_buy, 0, "Regime filter failed to STAND ASIDE below 10,000x.")

    def test_regime_filter_execute_high_vr(self):
        """Test the filter: V_R at or above threshold must result in calculated size."""
        asset_price = 50.00
        shares_to_buy = self.bot.calculate_position_size(asset_price, u_variance_ratio=10000.0)
        
        # Expected shares: $100 / ($50 * 0.05) = 40.0 shares
        self.assertAlmostEqual(shares_to_buy, 40.0, 2, "Regime filter failed to EXECUTE at 10,000x.")
        
    def test_loss_amount_integrity(self):
        """Ensure the loss amount is always 1R when a trade is executed."""
        asset_price = 100.00
        shares_to_buy = self.bot.calculate_position_size(asset_price, u_variance_ratio=15000.0) 
        
        loss_per_share = asset_price * self.bot.stop_loss_pct
        total_loss = loss_per_share * shares_to_buy
        
        self.assertAlmostEqual(total_loss, self.EXPECTED_LOSS_AMOUNT, 2, 
                               "Risk integrity failed: Total loss must equal 1R.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
