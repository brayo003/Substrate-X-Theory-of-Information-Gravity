Input-output characterization of the linear telegraph substrate.

Impulse response (Gaussian amp=5, width=2m at center, tau=3):
- Peak at center: 4.1486 at t=0.05 (immediate)
- Center decay: exponential, decay_time≈2.45 time units
- 10m response: arrives t≈4.0, peaks ~0.31 at t≈9
- 20m response: not detectable within 10 time units (< threshold)
- The substrate acts as a strongly damped spatial low-pass filter
- Narrow input (high-k) is immediately attenuated; only low-k content propagates far

Frequency response (sinusoidal forcing at center, tau=1 and tau=3):
- Both tau values show decreasing amplitude ratio with frequency:
  - 0.05 Hz: ratio ~50-60
  - 0.5 Hz: ratio ~6.0  
  - 1.0 Hz: ratio ~2.9
- The substrate is a low-pass filter in frequency
- Higher frequencies are attenuated more strongly
- The tau dependence is weak in this frequency range (tau changes shape of rolloff but not dramatically)

Transfer function analysis:
For the telegraph equation in 1D with forcing at k=0 (uniform):
  H(ω) = 1 / (1 - iωτ)
This is a first-order low-pass filter with cutoff ω_c = 1/τ.
For spatial mode k:
  H_k(ω) = 1 / (-τω² + iω + c²τk²) = second-order bandpass (overdamped) or notch (propagating)

Comparison with simple controls:
- First-order decay: H(ω) = 1/(1-iωτ) only. No spatial structure. No propagation.
- Telegraph: same temporal filtering + spatial propagation + velocity memory.
- Distinctive capability: temporal integration via velocity state creates a second-order response that simple decay cannot replicate.
