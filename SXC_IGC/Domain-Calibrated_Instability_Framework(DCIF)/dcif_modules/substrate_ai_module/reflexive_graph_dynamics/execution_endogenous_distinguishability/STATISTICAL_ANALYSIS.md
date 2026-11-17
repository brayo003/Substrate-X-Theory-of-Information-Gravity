# STATISTICAL_ANALYSIS

## 1. Design and unit of analysis

- Unit: one paired seed.  All models receive the same instance, start state and
  movement uniforms for a given seed.
- n = 100 paired seeds (0–99), 100 steps each.
- Primary models A, B, C, D, CR: complete, 100/100 seeds.
- Added controls: G, H complete (100/100); CS 79/100 feasible; CT 77/100
  feasible.  Exclusions are reported, not imputed.
- No non-finite metric enters a test.  `avg_path_length` is defined for every
  D/CR run (all have a 12-node largest component); it is not used in the
  primary families.
- All tests are two-sided.  Paired differences are model-minus-control per
  seed.  Effect size is Cohen's dz = mean(d) / sd(d), with sample sd.
- 95% confidence intervals are percentile bootstrap intervals over seeds
  (10,000 resamples, RNG seed 20261115), not normal-theory intervals.
- Wilcoxon signed-rank test, `zero_method="wilcox"`, normal approximation for
  n ≥ 10.  If all differences are zero the test is undefined and p is reported
  as 1.0.
- Holm–Bonferroni correction is applied within each pre-specified family; the
  families and their sizes are listed with each table.
- The simulator is deterministic given the seed.  Seeds are the sampling unit;
  the tests describe variability across the generated instances and movement
  streams, not a population of real systems.

## 2. Family 1 — 2×2 interaction `(C−B)−(G−A)`

8 metrics, Holm over 8.

| metric | mean DiD | sd | 95% CI | dz | nonzero (+/−) | raw p | Holm p |
|---|---|---|---|---|---|---|---|
| distinct states | +3.190 | 3.535 | 2.510 to 3.890 | +0.902 | 74 (70/4) | 1.7e-12 | 1.4e-11 |
| steps traversed | +38.900 | 49.791 | 29.420 to 48.610 | +0.781 | 49 (46/3) | 1.1e-8 | 8.0e-8 |
| stall steps | −38.900 | 49.791 | −48.670 to −28.940 | −0.781 | 49 (3/46) | 1.1e-8 | 8.0e-8 |
| final blocks | −0.100 | 0.302 | −0.160 to −0.050 | −0.332 | 10 (0/10) | 1.6e-3 | 7.8e-3 |
| final gate edges | −0.060 | 0.239 | −0.110 to −0.020 | −0.251 | 6 (0/6) | 1.4e-2 | 0.043 |
| stored reach | 0.000 | 0.000 | 0.000 to 0.000 | — | 0 | — | 1.0 |
| gate reach | 0.000 | 0.000 | 0.000 to 0.000 | — | 0 | — | 1.0 |
| total splits | −0.100 | 0.302 | −0.160 to −0.050 | −0.332 | 10 (0/10) | 1.6e-3 | 7.8e-3 |

The two reachability DiDs are exactly zero for every seed, not merely
non-significant.  The final-partition and split effects are one and the same
quantity (0.1 fewer blocks/splits in C than in B/H).

## 3. Family 2 — decomposition (48 tests, Holm over 48)

Selected rows; full table in `results/analysis/table_decomposition.csv`.

| contrast | metric | mean | 95% CI | dz | Holm p |
|---|---|---|---|---|---|
| C−B | distinct states | +0.010 | −0.150 to 0.170 | +0.012 | 1.0 |
| C−B | stall steps | +12.630 | 6.780 to 19.390 | +0.387 | 2.8e-3 |
| C−B | steps traversed | −12.630 | −19.430 to −6.780 | −0.387 | 2.8e-3 |
| C−B | gate reach | 0.000 | 0.000 to 0.000 | — | 1.0 |
| G−A | distinct states | −3.180 | −3.840 to −2.530 | −0.935 | 1.8e-11 |
| G−A | stall steps | +51.530 | 41.880 to 60.760 | +1.092 | 4.2e-9 |
| C−G | stall steps | −38.900 | −48.670 to −29.210 | −0.781 | 4.1e-7 |
| C−G | gate reach | +1.860 | 1.320 to 2.450 | +0.638 | 6.8e-9 |
| H−B | stall steps | +12.630 | 6.790 to 19.370 | +0.387 | 2.8e-3 |
| C−H | stall steps | 0.000 | 0.000 to 0.000 | — | 1.0 |
| C−H | distinct states | 0.000 | 0.000 to 0.000 | — | 1.0 |
| C−H | final blocks | −0.100 | −0.160 to −0.040 | −0.332 | 0.044 |
| C−H | gate reach | 0.000 | 0.000 to 0.000 | — | 1.0 |

Reading: C−B and H−B are the same effect (the movement gate).  C−H is zero on
all trajectory and reachability metrics.  G−A is the gating effect without
refinement.  The interaction is therefore the difference between the gating
effect with and without refinement, mediated entirely by the movement gate.

## 4. Family 3 — D versus CR (9 tests, Holm over 9)

| metric | mean D−CR | sd | 95% CI | dz | raw p | Holm p |
|---|---|---|---|---|---|---|
| final edges | −0.690 | 1.143 | −0.920 to −0.470 | −0.604 | 1.4e-7 | 1.1e-6 |
| removed edges | +0.690 | 1.143 | 0.460 to 0.910 | +0.604 | 1.4e-7 | 1.1e-6 |
| created ever traversed | −19.200 | 5.123 | −20.180 to −18.190 | −3.748 | 3.7e-18 | 3.4e-17 |
| graph stable at | +0.030 | 0.171 | 0.000 to 0.070 | +0.175 | 0.083 | 0.250 |
| partition stable at | +0.880 | 3.526 | 0.310 to 1.660 | +0.250 | 3.2e-4 | 1.6e-3 |
| distinct states | −0.100 | 0.362 | −0.170 to −0.030 | −0.276 | 7.5e-3 | 0.030 |
| stored reach | −0.110 | 1.100 | −0.330 to 0.000 | −0.100 | 0.317 | 0.635 |
| gate reach (fresh) | −0.110 | 1.100 | −0.330 to 0.000 | −0.100 | 0.317 | 0.635 |
| final gate edges (fresh) | −0.690 | 1.143 | −0.910 to −0.470 | −0.604 | 1.4e-7 | 1.1e-6 |

The significant quantities are downstream of placement:
`created_ever_effective` (source concentration), removal and final edge count
(removal of untraversed edges), and final gate size.  The two reachability
metrics are not significant (p = 0.32) and differ in only 1/100 seeds.

## 5. Family 4 — D-vs-CR topology (24 tests, Holm over 24)

Stored graph; gate graph gives the same pattern.

| metric | mean D−CR | 95% CI | dz | Holm p |
|---|---|---|---|---|
| density | −0.005 | −0.007 to −0.004 | −0.604 | 8.0e-6 |
| mean out-degree | −0.058 | −0.076 to −0.039 | −0.604 | 2.4e-6 |
| **out-degree sd** | **+2.473** | **2.380 to 2.565** | **+5.223** | **8.6e-17** |
| **max out-degree** | **+3.380** | **3.150 to 3.600** | **+2.910** | **6.2e-17** |
| **clustering** | **+0.105** | **0.093 to 0.117** | **+1.731** | **1.3e-16** |
| weak components | 0.000 | 0.000 to 0.000 | — | 1.0 |
| largest component | 0.000 | 0.000 to 0.000 | — | 1.0 |
| avg path length | −0.004 | −0.012 to 0.004 | −0.099 | 1.0 |
| quotient cross pairs | −0.690 | −0.910 to −0.470 | −0.604 | 2.4e-6 |
| quotient density | −0.005 | −0.007 to −0.004 | −0.604 | 3.7e-6 |
| consistency violations | 0.000 | 0.000 to 0.000 | — | 1.0 |
| reach from z0 | −0.110 | −0.330 to 0.000 | −0.100 | 1.0 |

The degree distribution and clustering differ strongly; connectivity, path
length and reachability do not.

## 6. Matching-control decomposition of the D topology effect

D vs CS (same count and source), feasible seeds only (n = 79), and D vs CT
(same count and quotient block-pair multiset), n = 77:

| metric | D−CS | 95% CI | D−CT | 95% CI |
|---|---|---|---|---|
| out-degree sd | 0.000 | 0 to 0 | 0.000 | 0 to 0 |
| max out-degree | 0.000 | 0 to 0 | 0.000 | 0 to 0 |
| clustering | 0.000 | 0 to 0 | 0.000 | 0 to 0 |
| weak components | 0.000 | 0 to 0 | 0.000 | 0 to 0 |
| largest component | 0.000 | 0 to 0 | 0.000 | 0 to 0 |
| avg path length | 0.000 | 0 to 0 | 0.000 | 0 to 0 |
| density | 0.000 | 0 to 0 | 0.000 | 0 to 0 |
| final edges | 0.000 | 0 to 0 | 0.000 | 0 to 0 |
| created ever traversed | 0.000 | 0 to 0 | +0.091 | −0.013 to 0.208 |

The entire D-vs-CR topological difference is reproduced by matching the source
of created edges (CS) or the quotient-level edge types (CT).  It is not a
partition-conditioned effect.

## 7. Exact counts of qualitative outcomes

| check | count |
|---|---|
| D/CR created counts equal | 100/100 |
| D/CR final graph identical | 0/100 |
| D/CR trajectory identical | 0/100 |
| D/CR final partition identical | 100/100 |
| D/CR stored reach identical | 99/100 |
| D/CR gate reach identical (fresh gate) | 99/100 |
| D/CR gate reach identical (as stored by `one.py`) | 100/100 |
| A/B trajectory identical | 100/100 |
| B/H final partition identical | 100/100 |
| C/B final partition identical | 90/100 |
| C/H trajectory identical | 94/100 |
| C/H final partition identical | 90/100 |
| C/H gate reach identical | 100/100 |
| C runs ending stalled | 13/100 |
| C runs with absorbing stall | 12/100 |
| G runs ending stalled | 55/100 |
| G runs with absorbing stall | 55/100 |
| CS feasible / same final graph as D | 79/79 |
| CT feasible / same final graph as D | 77/77 |

## 8. Censoring, missingness and non-finite values

| model | partition stable mean (max) | graph stable censored at 100 | final blocks (mean) |
|---|---|---|---|
| A | 0.00 (0) | 0/100 | 3.00 |
| B | 2.05 (3) | 0/100 | 11.88 |
| G | 0.00 (0) | 0/100 | 3.00 |
| H | 2.05 (3) | 0/100 | 11.88 |
| C | 2.30 (4) | 0/100 | 11.78 |
| D | 3.24 (34) | **99/100** | 12.00 |
| CR | 2.36 (8) | **96/100** | 12.00 |
| CS | 3.25 (34) | 78/79 | 12.00 |
| CT | 3.04 (34) | 77/77 | 12.00 |

Graph stabilisation is **not observed**.  `graph_stable_at = 100` means the
graph signature still changed at the final recorded transition.  Only 1/100 D
runs and 4/100 CR runs have a change-free final step, and even those have
`graph_stable_at = 99`, i.e. one step of stability.  No run has a stable graph
regime of meaningful length.  All statements about graph stabilisation are
therefore censored at 100 steps.

Missingness: A/B/C/D/CR/G/H 100/100; CS 21 excluded; CT 23 excluded.  The
exclusions are not random with respect to the treatment (they occur when the
control's trajectory diverges and the matched count becomes infeasible), so
CS/CT results are reported on the feasible subset only and are not used in
any headline test.  No value was imputed.

## 9. What the statistics do and do not support

Supported by the data:

- A non-additive interaction of gating and refinement on stalls, traversals
  and distinct states, with tight CIs and large paired effect sizes.
- Exact equality of D/CR counts (by construction) and final partitions
  (empirically 100/100).
- Strong D/CR differences in degree distribution and clustering, fully
  accounted for by the source of created edges.

Not supported by the data:

- Any difference in stored or gate reachability between C and B, or between
  D and CR.
- Any persistent partition-size effect of coupling beyond 0.1 blocks.
- Any D/CR effect that survives count+source or count+topology matching.
- Any claim that 100/100 graph or trajectory differences are evidence of
  coupling: they are guaranteed by the design.

Statistical caveat: because the simulator is deterministic, "p-values" here
summarise separation across generated seeds, not sampling from a real
population.  The CIs are bootstrap intervals over seeds and should be read as
stability intervals, not as population confidence intervals.
