#!/bin/bash
echo "Quick Test of Substrate X Theory"
echo "--------------------------------"
python3 -c "
import numpy as np
m_S = 2e-10  # eV
alpha_S = 5e-21
F_contact = alpha_S / (4 * np.pi * 6.67e-11 * (2.435e18)**2)
print(f'Contact force ratio: {F_contact:.3e}')
print(f'Force range (1/m_S): {1/(m_S * 5.06e6):.2f} mm'
print('')
print('At key distances:')
for r_mm in [0.1, 0.5, 1.0, 2.0]:
    r = r_mm * 1e-3
    r_eV = r / 1.97327e-7
    yukawa = np.exp(-m_S * r_eV)
    ratio = F_contact * yukawa
    print(f'  {r_mm:4.1f} mm: {ratio:.3e} (Yukawa factor: {yukawa:.3e})')
"
