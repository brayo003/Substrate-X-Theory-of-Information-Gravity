# Experiment Results

## 0. Freeze and run record

| Item | Value |
|---|---|
| Benchmark revision | R2 (68 rules) |
| Frozen source hashes | `config/SOURCE_HASHES.txt`, verified after the run |
| Development cases | 0–39 (used for configuration; see `IMPLEMENTATION_REPORT.md §5`) |
| Validation cases | 40–59 (implementation check only) |
| Held-out evaluation | 60–159, 100 cases × 7 models = 700 episodes |
| Budget | 900 ops per episode, all evaluations and meta-actions charged |
| Evaluation runs | Once for the record, plus determinism and reproducibility re-runs; all behavioural columns identical |

The held-out split was executed after the configuration was frozen. The
determinism re-run changed no behavioural column (700/700 rows identical except
wall-clock `runtime_s`).

---

## 1. Main results (held-out, n = 100)

| Model | Success | Wilson 95% CI | Final violations mean (SD) | Total violations | Recovery ops (mean) | AUC violations | Ops (mean) | Library size |
|---|---|---|---|---|---|---|---|---|
| A — fixed, 7 rules | 22% | 15.0–31.1 | 3.55 (5.44) | 355 | 132.0 | 1.52 | 827 | 7 |
| B — fixed, 68 rules | **96%** | 90.2–98.4 | **0.26 (2.30)** | **26** | **48.4** | 0.25 | 766 | 68 |
| C — adaptive selection | 82% | 73.3–88.3 | 0.40 (2.31) | 40 | 94.0 | 0.70 | 779 | 68 |
| D — endogenous modification | 68% | 58.3–76.3 | 0.65 (2.37) | 65 | 106.0 | 0.68 | 786 | 9.0 |
| Dc — creation-only ablation | 70% | 60.4–78.1 | 0.64 (2.38) | 64 | 103.8 | 0.64 | 773 | 9.0 |
| E1 — programmed rewriting | **96%** | 90.2–98.4 | **0.26 (2.30)** | **26** | 49.0 | **0.14** | 770 | 68 |
| E2 — best-improvement search | 8% | 4.1–15.0 | 2.89 (1.78) | 289 | 189.8 | 2.46 | 914 | 68 |

`AUC violations` is the time-weighted violation exposure; lower is better.

**Immediate reading.** Every model that is given the complete library and a
working selection rule (B, C, E1) outperforms the model that must build its
library at run time (D). D does improve substantially over the incomplete fixed
baseline A, so rule creation *does* something — but it lands closer to A than to
B.

### Residual violations by constraint type (sum over 100 cases)

| Model | C1 unreachable | C2 degree | C3 mutual pair | C4 required missing |
|---|---|---|---|---|
| A | 307 | 2 | 46 | 0 |
| B | 26 | 0 | 0 | 0 |
| C | 29 | 0 | 10 | 1 |
| D | 31 | 0 | 34 | 0 |
| E1 | 26 | 0 | 0 | 0 |
| E2 | 18 | 58 | 142 | 71 |

D's residual error is dominated by C3 (mutual pairs): 34 of its 65 total
violations. C, with the full inventory, leaves 10. Creation of safe `CYCLE`
variants was frequent but often too late or not applicable.

---

## 2. Paired statistics (held-out, n = 100 pairs)

Paired differences are `first model − second model`; negative favours the first
model for violation metrics. CIs are 10,000-resample percentile bootstrap.
p-values are Wilcoxon signed-rank (continuous) or exact McNemar (success), with
Holm correction across the eight comparisons in each metric family.

| Comparison | Metric | Mean diff | 95% CI | p (Holm) | Effect size |
|---|---|---|---|---|---|
| D − A | final violations | −2.90 | [−3.89, −2.03] | <1e−6 (<1e−6) | rank-biserial −0.97 |
| D − A | success | +0.46 | — | <1e−6 (<1e−6) | risk diff +0.46 |
| D − B | final violations | +0.39 | [+0.26, +0.53] | 1e−6 (6e−6) | +0.94 |
| D − B | success | −0.28 | — | <1e−6 (<1e−6) | −0.28 |
| D − B | recovery ops | +57.6 | [+46.2, +70.3] | <1e−6 (<1e−6) | +0.96 |
| D − B | AUC violations | +0.425 | [+0.341, +0.525] | <1e−6 (<1e−6) | +0.93 |
| D − C | final violations | +0.25 | [+0.14, +0.38] | 1.8e−4 (5.5e−4) | +0.83 |
| D − C | success | −0.14 | — | 1.3e−3 (3.9e−3) | −0.14 |
| D − C | recovery ops | +12.0 | [+2.9, +22.1] | 0.87 (0.97) | +0.02 |
| D − C | AUC violations | −0.022 | [−0.098, +0.069] | 5.7e−5 (1.7e−4) | −0.46 |
| D − E1 | final violations | +0.39 | [+0.26, +0.53] | 1e−6 (6e−6) | +0.94 |
| D − E1 | success | −0.28 | — | <1e−6 (<1e−6) | −0.28 |
| D − E1 | AUC violations | +0.540 | [+0.456, +0.639] | <1e−6 (<1e−6) | +0.97 |
| D − E2 | final violations | −2.24 | [−2.75, −1.61] | <1e−6 (<1e−6) | −0.95 |
| D − E2 | success | +0.60 | — | <1e−6 (<1e−6) | +0.60 |
| Dc − C | final violations | +0.24 | [+0.11, +0.38] | 7.8e−4 (1.6e−3) | +0.73 |
| Dc − C | success | −0.12 | — | 7.5e−3 (1.5e−2) | −0.12 |
| D − Dc | final violations | +0.01 | [−0.07, +0.09] | 0.67 (0.67) | +0.33 |
| D − Dc | success | −0.02 | — | 0.63 (0.63) | −0.02 |

Note on the one mixed result: D − C on `auc_violations` is −0.022, but the
bootstrap CI includes zero while the rank-based test is significant. This is a
large number of very small paired differences, not a meaningful advantage. D − C
on `recovery_ops` is also non-significant. The terminal metrics are unambiguous:
D succeeds less often and ends with more violations than C.

### Case-level win/tie/loss (final violations, lower is better)

| Comparison | D better | tie | D worse |
|---|---|---|---|
| D vs A | 71 | 28 | 1 |
| D vs B | 1 | 69 | 30 |
| D vs C | 2 | 78 | 20 |
| D vs E1 | 1 | 69 | 30 |
| D vs E2 | 95 | 4 | 1 |

On success (higher is better), D vs C is: D worse 16, tie 82, D better 2.

---

## 3. Critical tests

### Test 1 — Does rule modification matter? (D vs B)

**No advantage.** B is significantly better on every primary metric: 96% vs 68%
success (McNemar p < 1e−6), 0.26 vs 0.65 mean final violations, 48 vs 106
recovery ops, 0.25 vs 0.68 time-weighted violations. D wins on only 1 of 100
cases and loses on 30.

The gain D does achieve over A comes from acquiring rules that B already has.
Once B has them from the start, D's creation machinery is a net cost.

### Test 2 — Does modification outperform selection? (D vs C)

**No.** C, which can only select and disable rules from the complete library,
beats D on success (82% vs 68%, Holm p = 3.9e−3) and on final violations
(0.40 vs 0.65, Holm p = 5.5e−4, rank-biserial 0.83). D is marginally better on
time-weighted AUC in a statistically fragile way and not different on recovery
time.

The creation-only ablation Dc does not rescue this: Dc is also worse than C
(success 70% vs 82%, final violations p = 1.6e−3). Disabling and modifying rules
are not the cause; *creation itself* does not pay for itself at this budget.

### Test 3 — Does it outperform established methods? (D vs E)

**No.** E1 (programmed rewriting, complete library) matches B exactly on
terminal outcomes: 96% success, 26 total violations, and lower time-weighted
exposure (0.14 vs 0.68). D is worse on every primary metric (all Holm
p ≤ 6e−6).

E2 (exhaustive best-improvement search) is much worse than D, but it is also
much worse than every other baseline: its per-decision cost (68 evaluations)
exhausts the budget after ~13 decisions. D beats E2 on all four primary metrics.
This is the one comparison D wins, and it does not indicate a capability
advantage — it indicates that exhaustive search is infeasible under this budget.

### Test 4 — Is adaptation stable?

**Partially, and not cheaply.** Over 100 cases D performed:

| Action | Count | Per case |
|---|---|---|
| create | 206 | 2.06 |
| modify | 13 | 0.13 |
| disable | 192 | 1.92 |
| delete | 3 | 0.03 |
| total | 414 | 4.14 |

- **Convergence:** 68 cases ended with zero violations; 78 cases performed at
  least one meta-action, of which 46 (59%) succeeded. All 22 cases that needed no
  meta-action succeeded.
- **Uncontrolled growth:** no. The library stayed bounded (max 19 rules, mean
  9.0, against a soft limit of 18).
- **Oscillation:** 22 oscillation steps across 100 cases, comparable to C (23).
  No runaway oscillation was observed after the development-phase fixes.
- **Destructive interactions:** present. The dominant residual is C3 (34 mutual
  pairs), i.e. created cycle-removal rules were often not applicable when the
  graph was already damaged.
- **Ineffective rules:** 150 of 206 creations (73%) produced no observed
  behaviour change within 50 ops (`unnecessary = 1`). Only 53 creations (26%)
  were followed by an improving application. Almost all of the benefit came
  from two rule forms: `REACH_CAP|avoid_cycle=True,radius=3,policy=min_out`
  (42 improving creations) and `CYCLE|policy=min_id,safe=True` (11).

Rule churn is therefore real but bounded: the system does not blow up, it simply
spends operations creating variants that do not help.

*Note on the `unnecessary` field for disable events:* a disabled rule cannot be
used afterwards, so the field is 1 by construction for disables and is not used
as evidence in this report. Creation and modification events are annotated
against the following 50 operations and are meaningful.

### Test 5 — Does it generalise?

**The mechanism generalises; the advantage does not exist to generalise.**

| Split | n | A | B | C | D | Dc | E1 |
|---|---|---|---|---|---|---|---|
| Development | 40 | 10 | 38 | 34 | 31 | 31 | 38 |
| Validation | 20 | 5 | 18 | 13 | 14 | 14 | 18 |
| Held-out | 100 | 22 | 96 | 82 | 68 | 70 | 96 |

Success rates: D 77.5% (dev), 70% (val), 68% (eval). There is no degradation on
unseen configurations, and the rules D creates most often (safe radius-3
reachability, safe cycle removal) are generic, not case-specific. D is not
memorising particular graphs.

But generalisation is only meaningful if there is something to generalise. D's
created rules are exactly rules that B already contains, so the "generalisation"
is recovery of a known inventory, not discovery of a new one.

### Test 6 — Is the advantage worth its complexity?

**No.** The cost/benefit ledger:

| Quantity | B (fixed, complete) | C (selection) | D (modification) |
|---|---|---|---|
| Success | 96% | 82% | 68% |
| Ops per success | 798 | 950 | 1,157 |
| Mean library size | 68 | 68 | 9.0 |
| Peak traced memory (mean, unreliable attribution — see LIMITATIONS §12) | 468 KB | 525 KB | 341 KB |
| Mean runtime per case | 0.022 s | 0.055 s | 0.041 s |
| Implementation complexity | none | selection + deactivation | selection + 5 meta-rules + event log |

D's only advantage is a smaller library (9 vs 68 rules), which is a real but
modest engineering benefit. The traced-memory figures are directionally
consistent with it but are not reliable enough to quantify (the annotation cache
is process-global and later-run models show lower peaks; see `LIMITATIONS.md
§12`). That benefit costs 28 percentage points of success, 359 extra operations
per success, and a substantially more complex implementation with a
history-dependent failure surface. On this benchmark the trade is clearly bad.

The ablation confirms that the cost is inherent to creation, not to pruning:
Dc (creation only) has the same success rate as D and still loses to C.

---

## 4. Secondary observations

- **Evaluation cost dominates.** Across the 100 cases, Model A performs 23,914
  rule evaluations because its 7 rules rarely match and it rescans the list;
  B needs 5,017 because its first applicable rule is usually early in the
  priority order. Model D spends 17,332 evaluations to find and try rules, then
  has to create more. Selection is expensive when the library is incomplete.
- **E1 and B produce identical graph trajectories.** E1 batches up to six
  applications per control step, so it reports fewer control steps and lower
  time-weighted exposure, but the same terminal states. E1 is best read as
  "B with batched control", not as an independent algorithm.
- **E2's failure is a budget artefact, not a capability result.** Exhaustive
  evaluation of 68 rules per decision consumes the budget in ~13 decisions. It
  is a legitimate baseline under equal cost, and it loses.
- **Censoring.** Recovery phases not completed within their phase: A 182, B 45,
  C 60, D 78, Dc 70, E1 46, E2 226 (out of 300 phases). Censored phases are
  charged their full length and retained.

---

## 5. Bottom line

Rule creation measurably improves an incomplete fixed library (A 22% → D 68%
success) but is dominated by a complete fixed library (B 96%), by adaptive
selection over that library (C 82%), and by programmed rewriting (E1 96%). The
capability is implementable and stable enough to run, but it buys nothing that
ordinary rule inventory plus selection does not already provide, at a higher
operation cost and much higher implementation complexity.
