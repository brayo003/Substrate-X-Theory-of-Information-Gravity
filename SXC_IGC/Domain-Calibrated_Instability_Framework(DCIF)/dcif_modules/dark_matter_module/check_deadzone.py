import numpy as np
from astroquery.jplhorizons import Horizons

# Target: Saturn (699) relative to Sun (500@10)
obj = Horizons(id='699', location='500@10', epochs=2451545.0)
v = obj.vectors()

x, y, z = v['x'][0], v['y'][0], v['z'][0]
r_au = np.sqrt(x**2 + y**2 + z**2)
r_meters = r_au * 1.496e11

print(f"--- SOLAR SYSTEM DEAD ZONE DATA ---")
print(f"Saturn Distance: {r_au:.4f} AU")
print(f"Saturn Distance: {r_meters:.4e} meters")
