# Gate 1 — missing parameters

The supplied PDF does not provide raw numerical datasets for Figure 4 or Figure
5. The following quantities are required for a fully predictive simulation but
are absent, underspecified, or only implicit in the paper.

| Needed quantity | Status in supplied paper | Consequence |
|---|---|---|
| Raw Figure 4/5 coordinates and per-point errors | Not supplied as a table | digitization required for quantitative comparison |
| Exact microwave carrier frequency/detuning | No value for the reported run | cannot predict Rabi phase/contrast from first principles |
| Microwave field amplitude and phase at the NV | Not supplied | only reported Rabi frequency can constrain a pulse model |
| Individual pulse lengths/calibrations for Figure 5 | Not supplied | ideal-pulse model only until supplied |
| Figure 5 starting rotation phase `phi0` | Not supplied numerically | must be fitted to digitized data or retained as unknown |
| Full stationary carbon-13 bath model | Not supplied | stationary echo curve cannot be derived uniquely |
| `T2` envelope functional form and exact value for Fig. 5 | Only approximate `T2 ~ 350 us` | an envelope model cannot be uniquely fixed |
| Exact field vector / `B0` for Fig. 5 | 6.2 G typical, but run-specific vector not tabulated | misalignment inference cannot be independently recomputed |
| Fluorescence count windows and normalization formula | Qualitative description only | absolute contrast cannot be predicted |
| Rotation phase jitter/wobble time series | Only bounds/qualitative report | no faithful mechanical-noise simulation |
| Spin-1 parameters beyond zero-field splitting | Not tabulated for this run | full spin-1 Hamiltonian is not fully specified |

## Gate consequence

The paper is sufficient for a conventional **shape and phase-accumulation**
model of Figure 5, and for a frequency check of Figure 4. It is insufficient
for a parameter-free reconstruction of contrast, the stationary carbon-13
curve, or uncertainty bars. Those limits must appear in later validation and
certification documents.

