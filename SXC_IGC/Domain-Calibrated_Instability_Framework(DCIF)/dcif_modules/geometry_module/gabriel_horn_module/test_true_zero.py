import numpy as np

class SXCIgcFromZero:
    def __init__(self, r=0.153267):
        self.r = r
        self.a = 1.0
        self.b = 1.0
        self.dt = 0.05
        self.x = 0.001  # Start NEAR zero (not 0.5!)
    
    def drift(self, x):
        return self.r * x + self.a * (x**2) - self.b * (x**3)
    
    def simulate(self, steps=1000):
        history = []
        for _ in range(steps):
            dx = self.drift(self.x) * self.dt
            noise = 0.001 * np.random.randn() * self.dt
            self.x += dx + noise
            self.x = max(self.x, 0.0)  # No negative tension
            history.append(self.x)
        return history

gamma = 0.0548
r_values = [0.001, 0.01, 0.03, 0.05, 0.153267]

print("STARTING FROM NEAR ZERO (x=0.001)")
print("γ = 0.0548")
print("=" * 60)

for r in r_values:
    engine = SXCIgcFromZero(r=r)
    history = engine.simulate(5000)
    final_x = history[-1]
    max_x = max(history)
    
    status = "BELOW γ" if r < gamma else "ABOVE γ"
    
    print(f"r = {r:.6f} ({status})")
    print(f"  Final x: {final_x:.6f}")
    print(f"  Max x: {max_x:.6f}")
    print(f"  Growth factor: {final_x/0.001:.1f}x")
    print(f"  Stable? {'YES' if abs(final_x - max_x) < 0.01 else 'NO'}")
    print()
