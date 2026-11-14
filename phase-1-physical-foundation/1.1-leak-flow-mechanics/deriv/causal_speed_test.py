import numpy as np

nx = 600
dx = 1.0
dt = 0.001
steps = 12000

tau = 5.0
c = 1.0
sigma = 0.001
b = 0.001

s = np.zeros(nx)
s_prev = np.zeros(nx)
s_prev2 = np.zeros(nx)

start = nx//4
s[start:start+5] = [0.2,0.6,1.0,0.6,0.2]

s_prev = s.copy()
s_prev2 = s.copy()

print("\nTracking right-moving wave\n")

positions = []
times = []

for step in range(steps):

    laplacian = (np.roll(s,-1)+np.roll(s,1)-2*s)/dx**2

    damping = sigma*s
    saturation = b*s**3

    if step == 0:
        d2s = 0
    else:
        d2s = (s - 2*s_prev + s_prev2)/dt**2

    rhs = (c**2 * tau * laplacian) - damping - saturation

    if step == 0:
        s_next = s + dt*rhs
    else:
        s_next = 2*s - s_prev + dt**2*(rhs - d2s)

    s_prev2 = s_prev.copy()
    s_prev = s.copy()
    s = s_next

    if step % 400 == 0:

        region = s[nx//4:]
        peak = np.argmax(region) + nx//4

        time = step*dt

        positions.append(peak)
        times.append(time)

        print("time:",round(time,3),"peak:",peak)

times = np.array(times)
positions = np.array(positions)

coef = np.polyfit(times,positions,1)

speed = coef[0]*dx

print("\n==============================")
print("Measured propagation speed:",speed)
print("Expected wave speed:",c)
print("==============================")
