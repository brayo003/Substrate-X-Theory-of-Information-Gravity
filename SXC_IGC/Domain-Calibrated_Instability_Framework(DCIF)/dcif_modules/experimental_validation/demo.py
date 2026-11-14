import math

def run_rigorous_logic():
    print("--- SXC REGIME TRANSITION: RIGOROUS COUPLING (V12.5) ---")
    print("Formula: T = Flux / (gamma_src * gamma_tgt)")
    print("-" * 52)

    try:
        g_src = float(input("Source Gamma (Recovery Rate, e.g., 0.9): ") or 0.9)
        g_tgt = float(input("Target Gamma (Recovery Rate, e.g., 0.002): ") or 0.002)
        flux  = float(input("Raw Flux (Signal Density, e.g., 0.01): ") or 0.01)

        # The Rigorous Tension: No cancellation possible.
        # If either side slows down, Tension MUST rise.
        tension = flux / (g_src * g_tgt)

        print(f"\n[RESULTS]")
        print(f"Substrate Product: {g_src * g_tgt:.6f}")
        print(f"Final Tension:     {tension:.4f}")

        print("\n[REGIME STATUS]")
        if tension > 1.0:
            print("❌ SHATTER: The target substrate has collapsed.")
        elif tension > 0.7:
            print("⚠️ TANGLE: Critical bottleneck detected.")
        else:
            print("🟢 STABLE: Dissipation keeps pace with load.")

    except ValueError:
        print("Input error.")

if __name__ == "__main__":
    run_rigorous_logic()
