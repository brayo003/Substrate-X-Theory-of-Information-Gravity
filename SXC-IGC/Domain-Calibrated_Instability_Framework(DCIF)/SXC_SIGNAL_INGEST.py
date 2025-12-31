import random
import time

class SignalIngestor:
    def __init__(self):
        self.state = {
            'market_volatility': 15.0, # Base VIX-style value
            'network_load': 0.2,       # Percentage
            'sentiment_score': 0.5     # Neutral
        }

    def fetch_live_signals(self):
        """Simulates fetching data from a live JSON API."""
        # Simulate a sudden market shock (E-spike)
        self.state['market_volatility'] += random.uniform(-1.0, 2.5)
        self.state['network_load'] = min(1.0, max(0.0, self.state['network_load'] + random.uniform(-0.05, 0.05)))
        
        # Normalize signals to Engine Excitation (E) range [0-1]
        norm_signals = {
            'finance_E': min(1.0, self.state['market_volatility'] / 40.0),
            'urban_E': self.state['network_load'],
            'social_E': 1.0 - self.state['sentiment_score'] # Inverse: lower sentiment = higher E
        }
        return norm_signals

if __name__ == "__main__":
    ingestor = SignalIngestor()
    print("INGESTOR_STREAMS_ACTIVE: Normalizing signals for SXC_CORE...")
    for _ in range(5):
        print(ingestor.fetch_live_signals())
        time.sleep(0.5)
