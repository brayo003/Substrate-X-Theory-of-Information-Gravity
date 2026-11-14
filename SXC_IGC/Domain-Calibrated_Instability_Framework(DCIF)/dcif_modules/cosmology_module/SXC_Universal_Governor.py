import numpy as np

def universal_logic(signal, v_obs, v_bar, mode="Cosmos"):
    # Phase 1: The Damping (The "Flow" for Galaxies)
    # Median Error: 16% - Good for stable substrates
    damping_factor = 0.0548 
    
    # Phase 2: The Snap (The "Conflict" for Grid/Nairobi)
    # 2.8x Factor - Good for brittle substrates
    conflict_factor = 2.8
    
    tangle_point = 0.70 # The 70% Threshold
    
    if mode == "Seismic" or mode == "Quantum":
        # These systems are highly brittle; we prioritize the Snap
        return signal * conflict_factor if signal > tangle_point else signal
    else:
        # Cosmos mode: prioritize the Sink/Damping
        overshoot = (v_bar - v_obs) / v_obs
        return -max(0.1, overshoot)
