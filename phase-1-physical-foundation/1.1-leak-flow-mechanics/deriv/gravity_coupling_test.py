import numpy as np
import matplotlib.pyplot as plt

# radial distance
r = np.linspace(1,100,500)

# assume source strength
Q = 1.0

# predicted flux
flux = Q/(r**2)

# log-log slope
logr = np.log(r)
logf = np.log(flux)

coeff = np.polyfit(logr,logf,1)

print("\n==============================")
print("Measured power-law slope:",coeff[0])
print("Expected slope: -2")
print("==============================\n")

plt.loglog(r,flux)
plt.xlabel("r")
plt.ylabel("flux")
plt.title("Inverse square scaling")
plt.show()
