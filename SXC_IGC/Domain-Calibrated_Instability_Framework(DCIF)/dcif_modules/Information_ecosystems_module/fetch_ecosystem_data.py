import numpy as np

class EcosystemDataFetcher:
    def __init__(self, mode="BURSTY"):
        self.mode = mode
        self.step_count = 0

    def fetch_latest_tension_signal(self):
        self.step_count += 1
        t = self.step_count
        
        if self.mode == "OSCILLATORY":
            # Normal variance: Swings between 30 and 50
            return 40 + 10 * np.sin(t * 0.1)
            
        elif self.mode == "DECAYING":
            # Dying rumor: Starts high, cools down
            return 60 * np.exp(-t * 0.01)
            
        elif self.mode == "BURSTY":
            # The Singularity: Sudden spike to 75
            return 30 if t < 20 else 75
            
        return 52.5 # Default V12 Calibration
