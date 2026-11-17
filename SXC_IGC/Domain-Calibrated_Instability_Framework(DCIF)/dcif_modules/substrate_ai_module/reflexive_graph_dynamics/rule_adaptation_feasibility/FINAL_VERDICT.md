# Final Verdict

## Verdict: **B — REDUNDANT**

Endogenous modification of graph-transformation rules, as specified and tested
here, produces no capability that is not already provided by a complete fixed
rule library with adaptive selection. Its measurable gains are reproduced — and
exceeded — by baselines that never modify a rule.

---

## 1. What was demonstrated

A system that creates, modifies, disables, and deletes its own graph-rewriting
rules was implemented and run on 100 held-out cases under a 900-operation budget
shared with every baseline.

| Claim | Evidence | Outcome |
|---|---|---|
| Rule modification is *possible* | 206 creations, 13 modifications, 192 disables, 3 deletions executed and logged; library stayed bounded (max 19 rules) | **Yes** |
| Modification changes behaviour | Created rules were applied and improved the graph in 53 of 206 creations (26%) | **Yes, but rarely** |
| It beats an incomplete fixed library | D 68% vs A 22% success, Holm p < 1e−6, rank-biserial −0.97 | **Yes** |
| It beats a complete fixed library | D 68% vs B 96% success, Holm p < 1e−6; B better on all four primary metrics | **No** |
| It beats adaptive selection | D 68% vs C 82% success, Holm p = 3.9e−3; C better on final violations too | **No** |
| It beats an established rewriting baseline | D 68% vs E1 96% success, Holm p < 1e−6; E1 better on all four primary metrics | **No** |
| It is stable enough to use | 22 oscillation steps, bounded library, no runaway growth; but 73% of creations had no effect and C3 residuals doubled versus C | **Marginally** |
| It generalises to unseen cases | Dev 77.5%, validation 70%, held-out 68% success — no degradation | **Yes, but it generalises toward rules B already has** |
| Its advantage justifies its cost | 1,157 ops per success vs 798 (B) and 950 (C); 28 points lower success; far higher implementation complexity | **No** |

**Precisely what was demonstrated:** a bounded create/modify/disable/delete
mechanism over a finite 68-rule space can partially reconstruct a rule library
from an incomplete seed library, improving constraint maintenance from 22% to
68% success on this benchmark. The reconstruction is slow, spends 73% of its
creation budget on rules it never uses, and stops well short of the performance
obtained by simply starting with the complete library.

## 2. Why "REDUNDANT" rather than "NOT USEFUL"

Both labels are defensible, so the choice is stated explicitly.

- **REDUNDANT** — the observed behaviour is adequately reproduced by a fixed
  rule library or by adaptive selection. This is literally what happened: the
  rules that D created (safe radius-3 reachability, safe cycle removal) are
  rules that B already contains, and every case D solved is also solved by B.
  The benefit of "creating" a rule is the benefit of *having* that rule, which
  an ordinary library provides for free.
- **NOT USEFUL** — modification is possible, but its cost does not justify it.
  This is also true, but it describes a cost verdict rather than the mechanism's
  status.

**REDUNDANT** is chosen because the decisive observation is functional coverage,
not merely poor economics: the mechanism's entire positive effect is accounted
for by inventory plus selection. The cost analysis reinforces the verdict but is
not what makes it.

## 3. Tests 1–6, answered directly

1. **Does rule modification matter? (D vs B)** — No. B is significantly better on
   success (96% vs 68%), final violations, recovery time, and time-weighted
   violations. D wins 1 case in 100 and loses 30. The gain over A comes from
   acquiring rules B already has.
2. **Does modification outperform selection? (D vs C)** — No. C is better on
   success (82% vs 68%) and final violations; D's apparent advantage on
   time-weighted AUC has a CI spanning zero and is not relied on. The
   creation-only ablation Dc does not close the gap, so the deficit is caused by
   creation, not by pruning.
3. **Does it outperform established methods? (D vs E)** — No. E1 matches the
   complete-library baseline (96%, 26 total violations) and beats D on every
   primary metric. D beats only E2, whose exhaustive search is infeasible under
   the budget.
4. **Is adaptation stable?** — Bounded but wasteful. The library stays ≤ 19
   rules and oscillation is comparable to C, but 73% of creations are never
   used, and destructive interactions leave twice as many mutual-pair violations
   as C.
5. **Does it generalise?** — The mechanism generalises across seeds with no
   dev-to-eval degradation, but what it generalises to is recovering a known
   inventory, not discovering a new one.
6. **Is the advantage worth its complexity?** — No. D costs 45% more operations
   per success than B, succeeds 28 points less often, and adds five meta-rules,
   an event log, and history-dependent failure modes. Its only benefit is a
   smaller library (9 vs 68 rules); traced memory was also lower, but that
   measurement is unreliable here (`LIMITATIONS.md §12`).

## 4. Conditions attached to this verdict

This verdict is bounded by the experiment, not by the idea in general:

- It applies to **small, enumerable rule spaces** (68 rules) where a complete
  fixed baseline can be constructed. In a space too large to enumerate, the
  comparison would not be possible and the conclusion would not follow.
- It applies to **this bounded meta-rule set** at **this budget** (900 ops,
  creation charged 3 ops). A meta-mechanism that identified the needed rule in
  one step could narrow the gap; it would still have to beat a library that
  already contains that rule.
- **No claim is made about untested systems.** E1 and E2 are our own baselines,
  not third-party implementations. The verdict is that modification is redundant
  *relative to the baselines actually tested*, and that the published mechanisms
  reviewed in `RESEARCH_REVIEW.md` already cover the capability in kind.
- The benchmark is synthetic. No claim about real-world graphs is made or
  implied.

## 5. Recommendation

**Stop this line of development as a distinct capability.**

If the goal is to maintain structural constraints on graphs under change, the
evidence says: build the best rule inventory you can and invest in selecting
among rules. Run-time rule creation added nothing here that inventory and
selection did not already provide, and it cost more.

If the question is ever reopened, the only configuration that could plausibly
change the answer is a rule space too large to enumerate, where a complete fixed
baseline cannot exist. That is a different experiment with a different
benchmark, and it should be pre-registered as such.

## 6. Reproduction

```
cd /home/lenovo/Projects/GI/rule_adaptation_feasibility
bash reproduce.sh
```

The script re-runs development, validation, and held-out splits, regenerates
every table, verifies the frozen source hashes, and prints the verdict inputs.
All source, configuration, seeds, logs, and raw per-case results are included.
