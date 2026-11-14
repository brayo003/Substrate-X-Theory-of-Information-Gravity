# C2 v02 Extension Workspace

This directory is an explicitly non-frozen research branch. It exists because the
frozen C2 framework leaves the quantum--classical coupling `g` undetermined.
Nothing here changes, validates, or retroactively upgrades the frozen theory.

The branch has one objective: determine whether a quantitative bridge from C2
information variables to physical energy can be added and empirically tested
without hiding a fitted parameter inside a new definition.

## Status labels

- **Frozen input**: a result imported by reference from C2 v01.
- **Proposed extension**: a new hypothesis, never a theorem.
- **Derived conditional result**: follows only after named proposed extensions.
- **Measurement result**: must include raw data, calibration, uncertainty, and
  a preregistered competing-model comparison.

## Workstreams

1. `01_energy_bridge/`: an energy-per-information bridge `eta`, if one can be
   derived or independently measured.
2. `02_qft_matching/`: a possible microscopic/QFT matching route.
3. `03_independent_measurement/`: a protocol to estimate a bridge parameter
   independently of Ramsey-rate fitting.
4. `04_tests/`: executable no-go and consistency tests.

The starting no-go result is preserved: under `s,J -> a(s,J)` and `g -> g/a`,
all current frozen transport and dephasing observables are invariant. Therefore
v01 does not determine a numerical `g` or `k_rot`.

See [governance](00_governance/CHARTER.md) before treating any v02 expression
as physics.
