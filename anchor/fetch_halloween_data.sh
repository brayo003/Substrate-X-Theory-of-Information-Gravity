#!/bin/bash
# GPS Week 1242, Day 3 = October 29, 2003 (Halloween Storm Peak)

echo "=========================================================="
echo "SXC DATA ACQUISITION: HALLOWEEN STORM 2003"
echo "=========================================================="

# Target Files from IGS Archive
# igs12423.clk: High-rate clock residuals
# igs12423.sp3: Precise satellite orbits (to calculate local rho)

SERVER="https://cddis.nasa.gov/archive/gnss/products/1242/"
FILES=("igs12423.clk.Z" "igs12423.sp3.Z")

echo "[*] Target: $SERVER"
echo "[!] REQUIREMENT: You must have a .netrc file with NASA Earthdata credentials."
echo "[!] To get data: 'wget --auth-no-challenge -i list.txt'"
echo "----------------------------------------------------------"
echo "PREPARING LOCAL DATA MANIFEST..."

for FILE in "${FILES[@]}"; do
    echo "$SERVER$FILE" >> halloween_manifest.txt
    echo "[+] Added $FILE to manifest."
done

echo "[*] DONE. Manifest saved to halloween_manifest.txt"
echo "=========================================================="
