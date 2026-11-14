import numpy as np

def audit_gravity_limit(mass_kg, radius_m):
    """
    V12 Logic: Gravitational Shatter-Point.
    NLI = (G * M) / (R * c^2) * Scaling_Constant
    """
    G = 6.674e-11
    c = 3e8
    
    # Gravitational Potential Load
    # We normalize such that NLI = 1.0 at the Schwarzschild Radius
    # NLI = (2 * G * M) / (r * c^2)
    nli = (2 * G * mass_kg) / (radius_m * c**2)
    
    print(f"⚛️ V12 GRAVITY AUDIT: SYSTEM SHATTER-POINT")
    print("-" * 45)
    print(f"Object Mass:   {mass_kg:.2e} kg")
    print(f"Object Radius: {radius_m:.2e} m")
    print(f"Normalized Gravitational Load: {nli:.4f}")
    
    if nli >= 1.0:
        print("STATUS: SHATTERED (Event Horizon Formed)")
        print("VERDICT: Substrate Interior is Offline. Data projected to Surface.")
    else:
        print("STATUS: LANDSCAPE (Stable Spacetime)")
        print(f"VERDICT: { (1.0 - nli)*100 :.2f}% Safety Margin remains.")
    print("-" * 45)

if __name__ == "__main__":
    # Test 1: The Earth (Stable)
    audit_gravity_limit(5.97e24, 6.37e6)
    print("\n")
    # Test 2: The Sun compressed to 3km (The Shatter Point)
    audit_gravity_limit(1.98e30, 3000)
