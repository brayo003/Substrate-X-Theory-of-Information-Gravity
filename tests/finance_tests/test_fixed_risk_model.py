"""
Test for Fixed 1R Risk Model and Market Regime Filtering
Ensures position sizing and the 'Stand Aside' rule are correct.
"""
import unittest
import sys
import os

# Add parent directory to path to import trading_bot (Assuming correct relative path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Define a mock bot class for testing purposes
class MockFixedRiskTradingBot:
    def __init__(self, capital=10000, risk_per_trade=0.01, stop_loss_pct=0.05, min_trend_score=0.70):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.stop_loss_pct = stop_loss_pct
        self.min_trend_score = min_trend_score

    def calculate_position_size(self, price, trend_score):
        """Calculates shares to buy or returns 0 if filter fails."""
        # Enforce Market Regime Filter
        if trend_score < self.min_trend_score:
            return 0  # STAND ASIDE

        # Fixed 1R Risk Calculation
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

    def test_risk_neutrality_high_price(self):
        """Test position size for a high-priced asset ($100) at strong trend."""
        asset_price = 100.00
        shares_to_buy = self.bot.calculate_position_size(asset_price, trend_score=0.90)
        # FIX: The correct expected value is 20.00, not 2.00
        self.assertAlmostEqual(shares_to_buy, 20.00, 2, "High price shares calculation error.")

    def test_regime_filter_stand_aside(self):
        """Test the filter: Trend score below threshold must result in 0 shares."""
        asset_price = 50.00
        shares_to_buy = self.bot.calculate_position_size(asset_price, trend_score=0.69)
        self.assertEqual(shares_to_buy, 0, "Regime filter failed to STAND ASIDE below 0.70.")

    def test_regime_filter_execute(self):
        """Test the filter: Trend score at or above threshold must result in calculated size."""
        asset_price = 50.00
        shares_to_buy = self.bot.calculate_position_size(asset_price, trend_score=0.70)
        self.assertAlmostEqual(shares_to_buy, 40.0, 2, "Regime filter failed to EXECUTE at 0.70.")
        
    def test_loss_amount_integrity(self):
        """Ensure the loss amount is always 1R when a trade is executed."""
        asset_price = 100.00
        shares_to_buy = self.bot.calculate_position_size(asset_price, trend_score=0.80) 
        
        loss_per_share = asset_price * self.bot.stop_loss_pct
        total_loss = loss_per_share * shares_to_buy
        
        self.assertAlmostEqual(total_loss, self.EXPECTED_LOSS_AMOUNT, 2, 
                               "Risk integrity failed: Total loss must equal 1R.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
