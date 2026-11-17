# Limitations

This document records what the study cannot establish, what went wrong, and the
alternative explanations that remain.

## 1. Scope limitations

1. **Synthetic graphs only.** All results are on a 24-node directed graph with
   four hand-chosen constraints. Nothing here establishes behaviour on real
   dependency graphs, program graphs, chemical graphs, or social networks. No
   real-world applicability is claimed.
2. **One task family, one budget.** The 900-op budget, three fixed disruption
   points, and the specific disruption sizes are design choices. A different
   budget or a longer horizon could change the balance between building a
   library and using one. No budget sweep was run, so the result should not be
   read as "rule creation can never pay off".
3. **Small rule space.** The complete inventory has 68 rules. Creation can only
   recover rules that already exist in a small, enumerated set. In a space too
   large to enumerate, a complete fixed baseline could not be constructed, and
   the comparison in this study would not be possible. The result is therefore
   specifically about *small, enumerable* rule spaces.
4. **Fixed disruptions.** Disruptions are seeded but not adversarial and do not
   adapt to the model. A system that exploits disruption regularities would not
   be detected here.

## 2. Literature limitations

5. **No live literature verification.** The environment forbids network access.
   `RESEARCH_REVIEW.md` is written from prior knowledge; every citation is marked
   `[not live-verified]`. A claim that a specific paper does or does not support a
   mechanism should be checked against the primary source before being relied on.
6. **No third-party baseline.** Model E1 and E2 are our implementations of
   programmed rewriting and best-improvement search on the same rule inventory.
   No published adaptive-graph-grammar system, DPO engine, or library-learning
   system was executed. **No claim of superiority over any untested system is
   made.** It is possible that a well-engineered established method would do
   better than E1/E2; that would only strengthen the negative verdict.
7. **Higher-order rewriting was not implemented.** The proposal is about
   modifying rules, not modifying the mechanism that modifies rules. A true
   higher-order or reflective rewriting baseline would test a stronger form of
   self-modification and was out of scope by the directive itself.

## 3. Design limitations

8. **The meta-rules are hand-designed and bounded.** Model D's five meta-rules
   were tuned on development cases. They may be suboptimal. In particular:
   - creation stops after six failed variants for one constraint type, which can
     prevent the one variant that would work (this is visible in cases where D
     tries six safe reachability variants while a radius-3 unsafe variant is
     needed);
   - the 20-op check interval and 3-op creation cost make creation slow relative
     to a 900-op budget.
   A stronger meta-rule set might narrow the gap to C. It would not obviously
   beat B, which already has every rule. This is an alternative explanation for
   part of D's deficit and is not fully excluded.
9. **B's priority order is tuned on development cases.** B is deliberately a
   strong baseline (safe variants first). A naive fixed order makes B much
   weaker and would have produced a misleadingly positive comparison for D. The
   cost of this choice is that B may be stronger than a "neutral" fixed baseline.
10. **E1 and B are not independent.** E1 uses B's priority order with batched
    application, so their terminal results coincide. E1 should be read as a
    control-flow variant of B, not as an independent method.
11. **Model C's deactivation is a design choice.** C can disable rules but not
    change them. Its deactivation policy (never disable while the target type is
    violated) was added during development after a deadlock was found. A
    different policy would change C's numbers.
12. **Memory measurement is weak.** `tracemalloc` was started and stopped per
    episode, but the rule-evaluation cache is process-global, so memory
    attribution across models is approximate. The library-size difference (9 vs
    68 rules) is the reliable cost signal, not the kilobyte figures.

## 4. Statistical limitations

13. **One primary comparison family, many metrics.** Eight paired comparisons
    were made per metric, Holm-corrected within each metric. The metrics are
    correlated (final violations and success are near-duplicates), so the
    correction is conservative in some directions and not a full family-wise
    guarantee across all 32 tests.
14. **AUC result is fragile.** D vs C on time-weighted violations is nominally
    significant by rank test but the bootstrap CI includes zero. It is reported
    as mixed and is not used to support any claim.
15. **Success is a hard threshold.** A model that ends one violation short is
    counted as a failure. This is why final-violation counts and AUC are
    reported alongside it.
16. **Censored recovery is charged, not modelled.** Charging the full remaining
    phase is a conservative convention; survival analysis would be more
    informative but was not used.

## 5. Failures and anomalies observed

17. **D is not merely redundant, it is worse.** 30 of 100 cases are strictly
    worse than B and 20 strictly worse than C. This is a substantive negative
    result, not noise: the paired tests are significant after correction.
18. **73% of creations had no observed effect.** Of 206 creation events, 150
    were followed by no application of the new rule within 50 ops. The
    mechanism spends operations on rules it does not use.
19. **The dominant residual is C3.** D ends with 34 mutual pairs across 100
    cases, versus 10 for C. Created safe cycle-removal rules were often
    inapplicable once the graph was already damaged, so D could not undo its own
    earlier damage.
20. **`unnecessary` is vacuous for disable events.** A disabled rule cannot be
    used afterwards, so the field is mechanically 1. Disable usefulness is not
    measured by that field and no conclusion is drawn from it.
21. **E2 is a budget artefact.** It evaluates all 68 rules per decision and
    therefore gets ~13 decisions per episode. Its poor result reflects the cost
    of exhaustive search under this budget, not a property of best-improvement
    search in general.

## 6. What would change the verdict

The verdict would need revisiting if any of the following were established:

- on a rule space too large to enumerate, a complete fixed baseline cannot exist,
  and creation becomes the only way to acquire a needed rule;
- a meta-rule set that creates the right rule in ~1 decision (rather than after
  several stalls at 3 ops per creation) closes the gap to C;
- a task with high rule reuse, where one created rule pays for itself across many
  episodes, reverses the cost/benefit balance.

None of these was tested. The verdict applies to the benchmark as specified.
