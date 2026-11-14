# Flux-to-Energy Units Guardrail

## Why `eta` is not automatically `g`

The proposed energy-per-information bridge has units

`[eta] = J / info`.

The frozen interaction coefficient has units

`[g] = J m^2 s / info`.

They are therefore not the same quantity. The difference is exactly one area
times one time:

`[g] = [eta] [area] [time]`.

This is unavoidable because the substrate variable `J` is a flux,
`info / (m^2 s)`, whereas `eta` maps an *information count* to energy.

## Operational calibration equation

For a known, approximately uniform flux through an explicitly defined sampling
area `A_eff` during a specified interaction window `T_eff`, define the sampled
information count

`Delta I = J A_eff T_eff`.

If a v02 bridge hypothesis asserts `Delta E = eta Delta I`, then

`Delta E = (eta A_eff T_eff) J`.

Matching this to the frozen longitudinal interaction gives, up to the stated
energy-gap convention,

`g = eta A_eff T_eff`.

For `H_int = g J sigma_z`, the two energy eigenvalues shift by `+gJ` and
`-gJ`; hence the energy *splitting* shifts by

`Delta E_gap = 2 g J`,

and the angular-frequency shift is

`Delta omega_q = 2 g J / hbar`.

## Consequences

1. A spectroscopy measurement of `Delta omega_q` versus an absolutely
   calibrated `J` estimates `g` directly from its slope. It does not require
   Ramsey decay data.
2. It does **not** by itself derive `eta`: extracting `eta` additionally
   requires independently justified, operational measurements of `A_eff` and
   `T_eff`.
3. Calling `g = eta / J_abs` is dimensionally incorrect and must not appear in
   v02.
4. A candidate bridge must state why `A_eff` and `T_eff` are physical,
   independently measured quantities rather than new hidden fit parameters.

## Status

This is a dimensional clarification of the frozen interaction equation. It is
not a bridge hypothesis and does not determine `g` or `eta`.
