import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Grid
# -----------------------------
nx = 600
dx = 1.0
dt = 0.01
steps = 3000

# -----------------------------
# Physical parameters
# -----------------------------
c = 1.0
tau = 10.0

# -----------------------------
# Fields
# -----------------------------
s = np.zeros(nx)
s_prev = np.zeros(nx)

# Initial pulse
center = nx // 2
s[center] = 1.0

positions = []
times = []

# -----------------------------
# Simulation
# -----------------------------
for step in range(steps):

    lap = np.roll(s,-1) - 2*s + np.roll(s,1)

    s_next = (
        2*s - s_prev
        + (dt**2)*(c**2)*lap/(dx**2)
        - (dt/tau)*(s - s_prev)
    )

    s_prev = s
    s = s_next

    # detect peak position (right side)
    peak_index = np.argmax(s[center:]) + center

    positions.append(peak_index)
    times.append(step * dt)

# -----------------------------
# Measure propagation speed
# -----------------------------
positions = np.array(positions)
times = np.array(times)

distance = (positions - center) * dx

# linear fit
valid = distance > 2
coeff = np.polyfit(times[valid], distance[valid], 1)

speed = coeff[0]

print("\n===============================")
print("Measured propagation speed:", speed)
print("Expected speed:", c)
print("===============================\n")

# -----------------------------
# Plot trajectory
# -----------------------------
plt.plot(times, distance)
plt.xlabel("time")
plt.ylabel("wavefront distance")
plt.title("Wavefront propagation")
plt.show()

