import numpy as np

def v12_step(x, r, a, b, dt):
    return x + (r*x + a*x**2 - b*x**3) * dt

def run_test():
    print("--- [VALIDATION] Testing Step Sensitivity (dt) ---")
    x_init = 0.1
    r, a, b = 0.15, 1.0, 1.0
    steps_total_time = 10.0
    
    # Compare standard dt to ultra-fine dt
    for dt in [0.05, 0.01, 0.001]:
        x = x_init
        for _ in range(int(steps_total_time/dt)):
            x = v12_step(x, r, a, b, dt)
        print(f"dt={dt:.3f} | Final x after {steps_total_time}s: {x:.6f}")

if __name__ == "__main__":
    run_test()
