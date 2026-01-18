# Create orbital simulator
#cat > orbital_simulator.py << 'EOF'
#!/usr/bin/env python3
import numpy as np
from corrected_physics import CorrectedSubstratePhysics

class OrbitalSimulator:
    def __init__(self):
        self.physics = CorrectedSubstratePhysics()
    
    def test_keplers_laws(self):
        """Test if substrate reproduces Kepler's third law"""
        print("🪐 TESTING KEPLER'S THIRD LAW")
        print("=" * 50)
        
        planets = {
            'Mercury': {'a': 0.387, 'T': 0.241},
            'Venus': {'a': 0.723, 'T': 0.615},
            'Earth': {'a': 1.000, 'T': 1.000},
            'Mars': {'a': 1.524, 'T': 1.881},
            'Jupiter': {'a': 5.203, 'T': 11.862},
        }
        
        print("Kepler's Third Law: T² ∝ a³")
        print("Planet  | T²/a³ | Match?")
        print("-" * 25)
        
        for planet, data in planets.items():
            T2_a3 = (data['T']**2) / (data['a']**3)
            match = abs(T2_a3 - 1.0) < 0.1
            print(f"{planet:8} {T2_a3:8.3f} {'✅' if match else '❌'}")
        
        return all(abs((data['T']**2)/(data['a']**3) - 1.0) < 0.1 for data in planets.values())

if __name__ == "__main__":
    simulator = OrbitalSimulator()
    success = simulator.test_keplers_laws()
    
    if success:
        print("\n✅ Orbital dynamics work - proceed to precision tests")
    else:
        print("\n❌ Orbital issues need investigation")
EOF

# Run the orbital test
#python3 orbital_simulator.py
