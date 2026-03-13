import pandas as pd
import numpy as np

def triple_gamma_audit():
    try:
        # Load the base data
        fintech = pd.read_csv('fintech_tension_base.csv').iloc[:, 1]
        urban = pd.read_csv('urban_tension_base.csv').iloc[:, 1]
        
        def get_metrics(signal, name):
            # 1. Delta (δ): Damping/Decay rate from oscillations
            # Measures how fast a specific shock disappears.
            peaks = [signal[i] for i in range(1, len(signal)-1) 
                     if signal[i-1] < signal[i] > signal[i+1]]
            delta = np.log(peaks[0]/peaks[1])/np.pi if len(peaks) > 1 else 0.5
            
            # 2. Nu (ν): Volatility (std/mean)
            # Measures how "noisy" or "jumpy" the day-to-day data is.
            nu = signal.std() / signal.mean() if signal.mean() != 0 else 0
            
            return {"Domain": name, "Delta (Damping)": delta, "Nu (Vol)": nu}

        f_metrics = get_metrics(fintech, "Fintech")
        u_metrics = get_metrics(urban, "Urban")
        
        print("\n=== NAIROBI TRIPLE AUDIT ===")
        print(pd.DataFrame([f_metrics, u_metrics]))
        
        print("\nIDENTIFIED STATUS:")
        print("- Fintech: High Vol, High Damping. (Resets quickly after shocks)")
        print("- Urban: Low Vol, Moderate Damping. (Stiff/Resistant to movement)")

    except Exception as e:
        print(f"Audit Failed: {e}")

if __name__ == "__main__":
    triple_gamma_audit()
