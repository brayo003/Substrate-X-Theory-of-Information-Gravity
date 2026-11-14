# PHASE 10 FINAL ASSESSMENT
**Project:** SXC-IGC sim_world  
**Date:** 2026-11-13  
**Question:** Does meaningful spectral substrate information improve autonomous-agent performance compared with an equivalent system without that information?

---

## Classification

**Category 3 — No Demonstrated Advantage**

> The experiment does not establish a meaningful improvement in autonomous-agent performance from spectral substrate information under the conditions tested.

---

## Evidence Summary

### What the experiment found

**1. Spectral is significantly worse than baseline on the primary metric.**

In all three scenarios (stable, dynamic, disrupted), the spectral condition produced substantially higher mean final hunger than the baseline (no-substrate) condition:

- Stable: mean_diff = +0.296, Cohen's d = +10.74, p ≈ 0 (n=30 paired trials)
- Dynamic: mean_diff = +0.288, Cohen's d = +8.26, p ≈ 0
- Disrupted: mean_diff = +0.289, Cohen's d = +13.62, p ≈ 0

These are large effects in the wrong direction. The spectral condition reliably harms agents' ability to manage hunger compared with an agent that uses no substrate information at all.

**2. Spectral is not significantly different from ablation.**

The ablation condition (time-reversed spectral signals — same marginal distribution, destroyed temporal structure) produced results statistically indistinguishable from the spectral condition in all three scenarios:

- Stable: mean_diff = +0.002, d = +0.10, p = 0.585 — not significant, negligible effect
- Dynamic: mean_diff = −0.006, d = −0.31, p = 0.098 — not significant
- Disrupted: mean_diff = −0.005, d = −0.26, p = 0.165 — not significant

This directly tests H2 (information-specificity): if the spectral signal's specific temporal relationship to the environment provided meaningful information, the spectral condition should outperform an ablation that preserves the signal's marginal distribution but destroys its timing. It does not.

**3. The mechanism of harm is identified: a coordination-hunger trade-off.**

The spectral condition at tau=3.0 drives substantial coordination (31–58% of agent-ticks), which prevents adequate foraging. At tau=3.0, C_spectral ≈ +0.57, giving coordination_capacity ≈ 0.79. This exceeds the cooperation threshold for most agents most of the time, causing them to cooperate when they should be foraging.

The baseline, which never cooperates and always forages when hungry, outperforms every substrate condition on hunger management. This is not a failure of the substrate signal to work — the intervention tests confirm it is used correctly. It is a failure of the current agent decision function to appropriately balance substrate-driven coordination against need satisfaction.

**4. The tau scan reveals a regime boundary, not an optimal operating point.**

At tau ≤ 2.0, coordination_capacity is low enough that agents forage effectively: mean hunger ≈ 0.44–0.45, task success ≈ 100%. At tau ≥ 3.0, coordination dominates: mean hunger ≈ 0.74, task success ≈ 0%. The transition between these regimes occurs reproducibly across 10 independent seeds at tau ≈ 1.5–2.0.

This confirms the theoretical spectral transition at k_c = 1/(2cτ_c). What it does not confirm is that any tau value gives spectral agents a *comparative advantage* over baseline agents. At tau ≤ 2.0, the spectral agents perform similarly to baseline — but only because the overdamped substrate suppresses coordination, leaving them behaviorally equivalent to the no-substrate baseline. At tau ≥ 3.0, the coherent substrate drives coordination at the expense of need satisfaction.

**5. Legacy-Q performs no better than spectral.**

In stable and disrupted scenarios, legacy-Q is significantly worse than baseline with similar effect sizes to spectral. In dynamic, neither is distinguishable. The corrected spectral observable does not perform worse than the deprecated local-gradient observable — but neither provides a performance benefit over no substrate at all.

---

## What the substrate correctly does

The spectral substrate works as a physics engine. The following are confirmed:

- C_spectral is correctly computed from background-subtracted FFT fluctuations. It is bounded in [−1, +1] and responds predictably to tau.
- The spectral transition at τ_c ≈ 1/(2ck) is reproduced numerically within 3–10% error across modal validation tests.
- The substrate signal flows cleanly through the full pipeline: SpectralTransportObservable → SubstrateState → EntityContext → agent decision.
- The agent decision function uses the signal monotonically and correctly: at c=−1, agents never cooperate; at c=+1, they always cooperate when needs allow.
- Coordination efficiency (stress reduction per cooperate action) scales correctly with signal (0.08 at c=0, 0.12 at c=+1).

The substrate is a correct, functioning physical substrate with well-defined properties. What is not demonstrated is that an agent system benefits from using it under the current experimental conditions.

---

## Why no advantage was found

Three candidate explanations:

**Explanation A — Metric mismatch.** The agent decision function is designed to increase coordination when the substrate is coherent. Coordination is beneficial for stress reduction, not hunger management. The primary metric is mean_final_hunger. At tau=3.0, coordination increases sufficiently to prevent adequate foraging, penalising spectral agents on the metric we chose. If the metric were mean_final_stress, spectral would likely score better than baseline (spectral reduces stress more). This is a real trade-off, not a failure of the substrate — but it means the substrate does not help agents on the specific task we measured.

**Explanation B — Miscalibrated threshold function.** The cooperation threshold `0.3 + 0.4*(hunger+stress)/2` rises with need pressure, but not fast enough. At tau=3.0, C_spectral ≈ +0.57 gives coordination_capacity ≈ 0.79, which exceeds the threshold for agents with moderate hunger. The agent cooperates when it should forage. A higher base threshold or steeper need-pressure scaling would change this. However, changing the threshold to improve spectral's performance would be engineering the result rather than measuring it.

**Explanation C — The substrate does not carry task-relevant information at tau=3.0.** At tau=3.0, the substrate is persistently coherent (C_spectral stays near +0.57 throughout the run). There is no temporal variation in the signal that could distinguish "good time to coordinate" from "bad time to coordinate." A constantly-high coordination signal is equivalent to a constant bias toward cooperation. The ablation result supports this: shuffling the signal does not change outcomes because the signal is nearly constant anyway.

The most honest interpretation is a combination of all three: the substrate drives coordination appropriately given its signal, but the task does not reward coordination at the expense of foraging, and the signal is too constant to provide useful timing information.

---

## What would need to change to test the hypothesis fairly

The current experiment tests whether a *persistently coherent* substrate benefits agents on a *hunger-management task*. This is not the most informative test of the hypothesis.

A stronger test would require:

1. **A task that explicitly rewards coordination.** If agents cannot complete their primary goal without coordinating — for example, if resources require joint action to harvest — then a substrate that enables coordination at the right time would have a direct effect on task success.

2. **A dynamically varying substrate.** A substrate that alternates between coherent and overdamped regimes would give the spectral signal genuine temporal information: agents should cooperate during coherent windows and forage during overdamped windows. The ablation would then genuinely perform worse because it delivers the wrong signal at the wrong time.

3. **A calibrated tau value near the transition zone (τ ≈ 1.5–2.0).** At these values, the substrate is not permanently coherent — it fluctuates. The spectral signal would carry real information about whether the current moment supports coordination.

4. **A richer agent decision function that explicitly optimises for joint objectives.** The current function uses coordination only to reduce stress. A function where coordination produces shared resources or collective achievements would make coordination genuinely valuable.

None of these changes are implemented. The experiment that was run answers the question that was asked, but that question may be insufficiently demanding to detect a genuine substrate advantage.

---

## Classification rationale

The classification is Category 3 (No Demonstrated Advantage) rather than Category 4 (Inconclusive) because:

- The experiment has adequate statistical power (30 paired trials per condition, large effect sizes in the wrong direction).
- The null result on spectral vs ablation is replicated across three independent scenarios.
- The mechanism of the negative result is identified and interpretable.
- The result is reproducible (tau scan shows consistent transition across 10 independent seeds).

The null result is not due to insufficient sample size or random variability. It is a stable, large-effect finding: spectral agents at tau=3.0 coordinate too much and forage too little, and this is true regardless of whether their coordination signal is real or shuffled.

---

## What Phase 10 established

| Claim | Status |
|-------|--------|
| The spectral substrate physics is correct | Established (6/6 modal tests, closed-form agreement) |
| C_spectral is computed correctly | Established |
| The substrate signal flows to agents | Established |
| The agent decision function uses the signal | Established (9/9 intervention tests) |
| The spectral transition near τ_c is reproducible | Established (10 seeds per tau value) |
| The spectral condition outperforms baseline | **Not established — opposite found** |
| The spectral condition outperforms ablation | **Not established** |
| The spectral signal provides task-relevant information | **Not established under current task design** |
| The substrate advantage is scenario-independent | Not tested (would require different task) |

---

## Recommended next steps (not part of Phase 10)

1. Design a task that requires coordination to succeed, not merely one where coordination is possible.
2. Run the experiment with a dynamically switching substrate (alternating tau values).
3. Rerun with tau ≈ 1.5–2.0 and measure whether agents time their coordination to spectral coherence windows.
4. Test the LLM path with Ollama when available; LLMs may use the substrate context differently than the deterministic rule system.

---

## Final statement

The spectral substrate is a physically correct, mathematically well-defined system. The signal pipeline is functioning. The agent uses the signal. Under the conditions tested — a persistently coherent substrate (τ=3.0), a hunger-management primary task, and rule-based agents that use coordination signal strength to decide cooperation timing — the spectral substrate does not improve agent performance. It makes it worse, by systematically promoting coordination over foraging.

This is a meaningful result. It precisely characterises the conditions under which the substrate does not help, and it identifies what would need to change for a fair test of the hypothesis.

The spectral substrate advantage remains a hypothesis. It is not demonstrated here, and it is not refuted in principle. It is unresolved pending a more demanding experiment.
