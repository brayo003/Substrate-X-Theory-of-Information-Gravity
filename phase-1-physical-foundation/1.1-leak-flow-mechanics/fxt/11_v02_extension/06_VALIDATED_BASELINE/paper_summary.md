# Gate 1 — paper extraction

## Scope

This is a conventional-physics reproduction of the supplied Wood *et al.*
paper only. It does not test C2/H01 and does not infer a substrate mechanism.

## Experimental objective

The paper demonstrates preparation, microwave control, optical readout, and
spin-echo sensing of one NV electronic spin while its diamond host rotates at
up to 3.33 kHz (200,000 rpm). Its Figure 5 signal is attributed by the paper
to the time-varying projection of a stationary magnetic field onto the rotating
NV axis.

## Apparatus

- High-purity single-crystal CVD diamond, (100) cut, with a 50 micrometre
  layer of 99.8% carbon-12 and nitrogen concentration below 10 ppb.
- Single NV centres approximately 3 micrometres below the surface. The
  selected centre NV1 is about 10 micrometres from the rotation axis; NV1 and
  NV2 are separated by 3.6 micrometres.
- Diamond mounted on a Celeroton CM-2-500 high-speed motor. Rotation axis is
  denoted `z`; reported operating point is 3.33 kHz, so `Trot = 300 us`.
- A 0.95 NA confocal objective focuses 532 nm light to a reported 600 nm
  1/e^2 diameter spot. Fluorescence is collected through the objective onto an
  APD and time-tagged/processed by an FPGA.
- A 20 micrometre copper microwave wire is 100 micrometres above the diamond.
  Coils along x, y, z apply the bias field. Pulse timing is triggered from the
  motor phase synchronisation signal.
- Typical bias field is 6.2 G along `z`; reported NV coherence time is about
  350 us and is attributed to the carbon-13 bath.

## Hamiltonian and conventional rotation model

The paper does not print a full matrix Hamiltonian. It explicitly specifies a
two-level transition `mS=0 <-> mS=-1` and a zero-field splitting
`Dzfs = 2.87 GHz`. Its Figure 5 model is the following equation, retained in
the paper's notation:

\[
B_{\rm eff}(t)=B_0\sin\theta_{\rm NV}\sin\theta_B
\cos(2\pi f_{\rm rot}t+\phi_0). \tag{1}
\]

Here `B0` is the total field, `frot` the rotation frequency, `phi0` the initial
rotation phase, `thetaB` the angle between the rotation axis and magnetic
field, and `thetaNV = 54.7 deg` the angle between rotation and NV axes. The
published explanation is a time-dependent Zeeman shift caused by this field
projection. A later simulator may use an effective two-level Hamiltonian only
as an implementation of this stated transition and field model; it must record
that this matrix form is not printed in the paper.

## Pulse sequences

### Optical preparation and readout

The NV is optically pumped and read out with 532 nm light. Readout compares
fluorescence after microwave manipulation with fluorescence on the next
rotation period without microwave control. The light pulse both reads and
repumps the NV to the bright `mS=0` state. A 2 us pulse at 3.33 kHz subtends
2.4 degrees. Stationary continuous fluorescence is `Ns = 1e5 counts/s` at
2.6 mW; rotating counts are expected near 700 counts/s before the Gaussian
transit correction and reported around 350 counts/s.

### Rabi control (Figure 4)

Figure 4A: vary a resonant microwave-pulse duration and measure normalized
fluorescence. The paper reports Rabi frequency `3.6(2) MHz`.

Figure 4B: apply a pi pulse at `t=0`, then a variable-duration pulse at
`t=Trot/2 = 150 us`; the centre has moved 20 micrometres and the NV axis has
rotated 180 degrees. The figure tests control after this transport.

### Spin echo (Figure 5)

The diagram shows a pi/2 pulse, free precession for `tau/2`, a pi pulse,
another `tau/2`, and final pi/2 projection. For Figure 5 the paper restricts
to `tau < 60 us`; after the last microwave pulse it waits `Trot - tau` for the
centre to return to the optical readout region. The plotted signal is normalized
contrast versus total spin-echo time `tau`.

## Fluorescence model and reported uncertainty

The paper states fluorescence has a truncated Gaussian time dependence because
the centre crosses the laser beam. Initial dark-state fluorescence is about
20–30% lower than after repumping. Figure 4 error bars are standard errors in
computed fluorescence ratios from more than `1e5` repetitions. Figure 5 error
bars are standard errors in fluorescence ratios averaged over three runs of
about `1e6` repetitions.

## Data products and figure roles

| Figure | Content | Reproduction role |
|---|---|---|
| 1 | apparatus and timing | geometry/timing source |
| 2 | stroboscopic confocal images | not a first simulation target |
| 3 | moving-NV fluorescence traces | readout context; insufficient numerical trace data |
| 4 | Rabi oscillations during rotation | Gate 4 control validation |
| 5 | stationary and rotating spin echo | Gate 5 primary benchmark |

## Reported numerical parameters used by this project

| Quantity | Value in paper |
|---|---:|
| Rotation frequency | 3.33 kHz |
| Rotation period | 300 us |
| Bias field | 6.2 G, nominally along z |
| NV/rotation angle | 54.7 deg |
| NV radius | about 10 um |
| NV depth | 3 um |
| Rabi frequency | 3.6(2) MHz |
| Echo coherence time | about 350 us |
| Figure 5 eAC field amplitude | 88 +/- 29 mG |
| Inferred field misalignment | 1.0 +/- 0.3 deg |
| Carbon-13 gyromagnetic ratio | 1.075 kHz/G (paper notation) |

## Explicit boundary

The 88 mG Figure 5 amplitude is a fitted conventional effective-field result
reported by the authors, not a prediction to be reused as an unconstrained
fit parameter in a validation claim. It may be used in a clearly labelled
"published-parameter forward model". Any independent fit to digitized points
must separately report its parameters and uncertainty.

