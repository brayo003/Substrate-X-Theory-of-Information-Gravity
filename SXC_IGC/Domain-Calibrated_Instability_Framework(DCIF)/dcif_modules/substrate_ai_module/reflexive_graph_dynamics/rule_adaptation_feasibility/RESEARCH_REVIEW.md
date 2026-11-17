# Research Review — Endogenous Rule Adaptation for Graph Transformation

**Status of this review.** This document was written from prior knowledge of the
literature. The working environment has a hard no-network rule, so no citation
was checked against a live source at the time of writing. Citations are given at
the level of author/system and are marked **[not live-verified]**. Where a claim
is my own interpretation rather than a published result, it is marked
*[interpretation]*.

---

## 1. What the proposal actually is

The capability under test is a system whose state is

```
X_t = (G_t, R_t, H_t)
```

with `G_t` a directed graph, `R_t` a finite set of graph-transformation rules,
and `H_t` interaction history, where an operation may change both `G_t` and
`R_t`. Rules can be **created, modified, disabled, and deleted** by a fixed,
bounded set of meta-rules.

Stripped of terminology, this is:

1. a finite, parameterised rule space;
2. a bounded search over that space driven by observed failure;
3. a selection policy over the current rule set.

That decomposition matters, because each of the three components has an
established literature. The question for Gate 1 is not whether "endogenous rule
modification" has been used as a phrase, but whether the *operational content*
is already covered.

---

## 2. Established families of methods

### 2.1 Algebraic and programmed graph rewriting

- **Double-pushout (DPO) graph transformation** — Ehrig, Pfender, Schneider;
  Corradini, Montanari, Rossi, Ehrig, Heckel, Löwe **[not live-verified]**. Rules
  are spans `L <- K -> R`; rewriting is a pushout construction. Rules are
  first-class mathematical objects: they can be composed, inverted, and reasoned
  about algebraically.
- **Single-pushout and sesqui-pushout** variants extend the same idea to partial
  morphisms **[not live-verified]**.
- **Programmed graph replacement systems** — Schürr **[not live-verified]** —
  add control flow over rule applications (sequences, loops, alternatives). This
  is the direct ancestor of "which rule to apply when".
- **Graph programming languages**: PROGRES, GrGen.NET, GP 2, AGG
  **[not live-verified]**. GP 2 in particular has rule schemata with parameters
  and a compiler; rule sets are static at compile time but rule *applications*
  are searched and backtracked.

**Coverage of the proposal.** Rule *application* and rule *selection* are fully
covered. Rule *creation at run time* is not part of classical DPO. However,
DPO's rule algebra already allows rules to be derived from other rules
(composition, inverse), so "a new rule is produced from existing rules by a
fixed construction" is not novel in kind.

### 2.2 Adaptive and evolving graph grammars

- **Adaptive graph grammars / graph-grammar-based evolutionary algorithms** —
  systems in which the grammar or rule set is itself subject to variation and
  selection, e.g. graph-grammar encodings in evolutionary design
  **[not live-verified; family-level claim]**.
- **Rule evolution in learning classifier systems and Pittsburgh-style rule
  learners** — the rule set is the genotype; mutation/crossover create and
  delete rules **[not live-verified]**.
- **Grammatical evolution and grammar induction** — de la Higuera's survey of
  grammatical inference **[not live-verified]** — learns or edits a grammar from
  data.

**Coverage.** "Create/modify/delete rules under a fixed meta-level procedure" is
exactly what these systems do. The proposed mechanism is a *bounded, hand-written
variant operator over a finite rule space*, which is weaker than a general
evolutionary rule learner and does not add a new representational primitive.

### 2.3 Higher-order and reflective rewriting

- **Higher-order rewriting** — Nipkow, van Oostrom, the Terese survey
  **[not live-verified]** — rewrite rules may rewrite terms containing rules or
  abstractions.
- **Reflective towers and self-interpreters** — Smith **[not live-verified]** —
  a program can inspect and modify its own representation. This is the classical
  answer to "can a system modify its own rules": yes, by reifying rules as data
  and running a fixed meta-program over them.
- **Metaprogramming / macros** — Lisp, Racket, Template Haskell
  **[not live-verified]** — compile-time creation and transformation of rules.

**Coverage.** Reflective rewriting establishes that self-modification is
representable as ordinary computation over an enlarged state. It does *not*
establish that self-modification is advantageous. That is an empirical question,
and it is the only question this study can answer.

### 2.4 Library learning and program synthesis

- **DreamCoder** — Ellis et al. **[not live-verified]** — learns reusable
  abstractions ("library learning") from solved tasks and uses them to solve new
  tasks. This is the closest published analogue of "create a new rule because
  the current library cannot express the solution compactly".
- **Stitch / Babble** — Bowers et al., Cao et al. **[not live-verified]** —
  compression-driven abstraction invention.
- **Meta-rule learning / rule induction** — inductive logic programming
  (Muggleton, Cropper) **[not live-verified]**.

**Coverage.** These systems demonstrate that inventing new reusable rules can
improve search. Crucially, they also show the typical failure mode: invented
abstractions cost search time and can be useless or harmful. The correct control
is therefore a **complete fixed library** that already contains the abstractions,
which is exactly Model B in this study.

### 2.5 Adaptive algorithm selection and online control

- **Per-instance algorithm selection** — Rice's selector framework
  **[not live-verified]**.
- **Multi-armed bandits / UCB** — Auer et al. **[not live-verified]** — the
  selection rule used by Models C and D.
- **Meta-learning for solver selection** **[not live-verified]**.

**Coverage.** Selecting among existing rules, with exploration and deactivation,
is standard. The proposal's Model C is therefore not novel, and is the correct
control for "is it modification or just selection?".

---

## 3. What is *not* already established

Three things are genuinely not settled by the literature above:

1. **Quantitative comparison under an equal operation budget.** Published systems
   rarely report "rule creation vs. complete fixed library" at matched cost on
   the same task. This is an empirical gap, not a conceptual one.
2. **Stability of local rule edits.** Whether bounded create/disable/modify
   actions converge, oscillate, or accumulate dead rules on a given task class is
   not predictable from theory.
3. **Cost/benefit of the meta-level.** Library learning shows abstraction
   invention can pay off *when search is expensive and reuse is high*. Here the
   rule space is small (68 rules) and reuse is low, so the cost/benefit balance
   is an open empirical question.

Note what is *not* claimed: no new mathematical foundation, no new form of
computation, no escape from ordinary transition systems. A system with state
`(G_t, R_t)` is a transition system over the product state space. This study
tests only whether the extra state component earns its cost.

---

## 4. Gate 1 assessment

| Question | Assessment |
|---|---|
| Is the capability substantially covered by established methods? | **Yes, in kind.** Rule selection, rule composition, and rule-set evolution all exist. Creating rules by a bounded variant operator over a finite space is a special case of evolutionary/adaptive grammar methods. |
| Is there a meaningful difference that can be tested? | **Yes, but narrow.** The testable difference is *operational*: given an equal operation budget, does run-time rule creation beat (a) a complete fixed library and (b) adaptive selection over it? |
| Is there an appropriate benchmark? | **Yes, with caveats.** A synthetic online constraint-maintenance task on directed graphs is objective, reproducible, and has a known complete rule inventory. It is not a real-world workload. |
| Can the comparison be made fairly? | **Yes, if** Model B receives the complete rule inventory from the start, all models share one operation budget, and Model D's meta-actions are charged as operations. All three are implemented. |

**Gate 1 conclusion:** proceed, but frame the contribution as a *bounded
feasibility test of a special case*, not as a new capability class. The
literature gives no reason to expect a large advantage; the experiment is
designed to detect one if it exists and to report its absence otherwise.

---

## 5. Choice of established baseline (Model E)

The directive requires an established graph-rewriting baseline. Two were
implemented, both using the same 68-rule inventory:

- **E1 — programmed rewriting.** A deterministic, priority-ordered rewrite
  system in the style of programmed graph replacement (Schürr) / DPO rule
  application: scan rules in a fixed order, apply the first applicable rule, and
  batch up to six applications per control step.
- **E2 — best-improvement repair search.** Exhaustive evaluation of every
  enabled rule at every step, applying the highest-gain edit. This is the
  "obvious" search baseline and represents an expensive but simple adaptive
  rewriting strategy.

**Limitation.** Neither is a third-party implementation. A full DPO engine with
explicit pushouts, or a published adaptive graph-grammar system, was not
available in this repository and could not be downloaded under the no-network
rule. E1 and E2 are faithful *operational* baselines on this benchmark, not
brand-name systems. This is recorded in `LIMITATIONS.md` and no claim of
superiority over untested systems is made.
