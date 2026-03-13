import time
import os

class GravityDashboard:
    def __init__(self):
        self.width = 50

    def draw(self, tension, regime, strategy):
        os.system('clear')
        print("="*self.width)
        print(" SUBSTRATE REASONING DASHBOARD (V12 DYNAMICS)")
        print("="*self.width)
        
        # Tension Bar
        filled = int(tension * self.width)
        bar = "█" * filled + "-" * (self.width - filled)
        print(f"\nGRAVITY: [{bar}] {tension:.2f}")
        
        # Status
        status_color = "\033[92m" if tension < 0.4 else "\033[91m"
        print(f"REGIME:  {regime.upper()}")
        print(f"STRATEGY: {status_color}{strategy}\033[0m")
        print("\n" + "="*self.width)

if __name__ == "__main__":
    # Test visualization
    dash = GravityDashboard()
    dash.draw(0.85, "High Tension", "ACTUATOR_SHIFT")
