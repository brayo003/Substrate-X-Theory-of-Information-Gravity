from scipy import stats
import pandas as pd

# Data from previous run
total_events = 117288
extreme_events = 102
# Expected rate if events were distributed normally (uniform noise)
expected_extreme = total_events * (1 / 1000) # Assuming 1 in 1000 chance for noise

p_value = 1 - stats.poisson.cdf(extreme_events, expected_extreme)
print(f"⚛️ V12 STATISTICAL SIGNIFICANCE")
print("-" * 30)
print(f"Extreme Events Observed: {extreme_events}")
print(f"Expected (Noise): {expected_extreme:.2f}")
print(f"P-Value: {p_value:.2e}")

if p_value < 0.01:
    print("VERDICT: [STATISTICAL CERTAINTY]")
    print("These 102 events are NOT random noise. They are logically significant.")
