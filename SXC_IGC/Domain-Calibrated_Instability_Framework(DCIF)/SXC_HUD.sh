#!/bin/bash
# SXC-IGC Live Stream HUD (Direct Docker Socket)

echo "Attaching to SXC-Active-Node Stream..."
docker logs -f sxc-active-node 2>&1 | awk -F'|' '
/TIMESTAMP/ || /---/ { print; next }
{
    if (NF >= 4) {
        t = $2; phase = $3; vix = $4;
        
        # Color Logic
        color="\033[0;32m"; # Nominal - Green
        if (phase ~ "PREDICTIVE") color="\033[0;33m"; # Predictive - Yellow
        if (phase ~ "FIREWALL") color="\033[0;31m";   # Firewall - Red
        
        printf "%s | Tension:%s | %sPhase:%s\033[0m | VIX:%s\n", $1, t, color, phase, vix
    }
}'
