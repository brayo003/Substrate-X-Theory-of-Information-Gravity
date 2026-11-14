import numpy as np

# ---- signal ----
signals = [30]*200 + [35]*200 + [40]*200 + [45]*200 + [50]*200

# ---- baseline 1: raw threshold ----
raw_alert = None
for i, s in enumerate(signals):
    if s >= 45:
        raw_alert = i
        break

# ---- baseline 2: EWMA ----
alpha = 0.05
ewma = 0.0
ewma_alert = None
for i, s in enumerate(signals):
    ewma = alpha*s + (1-alpha)*ewma
    if ewma > 42:
        ewma_alert = i
        break

# ---- engine-inspired observer ----
T = 0.5
M = 0.0
z = 1.0

beta_base = 3.5
gamma_base = 0.8
dt = 0.05
kappa = 0.05
alpha_m = 0.6
lam = 0.3

engine_alert = None

for i, s in enumerate(signals):
    radius = 1.0 / z
    beta = beta_base * (1.0 / radius**0.5)
    gamma = gamma_base * radius

    E = 1 - np.exp(-s / 40.0)
    inflow = E * beta
    outflow = gamma * T

    T += (inflow - outflow) * dt
    M += (alpha_m*T - lam*M) * dt
    z += kappa * (M / (1+M)) * dt

    # engine alert condition (slope-based, not threshold)
    if i > 5 and (T - prev_T) > 0.15:
        engine_alert = i
        break

    prev_T = T

print("ALERT TIMES (lower = earlier)")
print("Raw threshold:", raw_alert)
print("EWMA:", ewma_alert)
print("Engine:", engine_alert)
