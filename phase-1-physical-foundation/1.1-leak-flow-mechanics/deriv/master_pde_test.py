import numpy as np

nx = 400
dx = 1.0
dt = 0.002
steps = 5000

tau = 5.0
c = 1.0
v = 0.2

alpha = 0.002
E = 1.0
sigma = 0.002

s = np.zeros(nx)
s_prev = np.zeros(nx)

center = nx//2
s[center] = 1.0

for step in range(steps):

    lap = (np.roll(s,-1) - 2*s + np.roll(s,1))/dx**2
    adv = (np.roll(s,-1) - np.roll(s,1))/(2*dx)

    s_next = (
        2*s - s_prev
        + (dt**2)*(c**2)*lap
        - (dt/tau)*(s - s_prev)
        - dt*v*adv
        + dt*(alpha*E - sigma)
    )

    s_prev = s
    s = s_next

    if step % 500 == 0:
        print("step:",step)
        print("total information:",np.sum(s))
        print("max density:",np.max(s))
        print("min density:",np.min(s))
        print("-"*40)

print("\nFINAL STATE")
print("total information:",np.sum(s))
print("max density:",np.max(s))
print("min density:",np.min(s))
