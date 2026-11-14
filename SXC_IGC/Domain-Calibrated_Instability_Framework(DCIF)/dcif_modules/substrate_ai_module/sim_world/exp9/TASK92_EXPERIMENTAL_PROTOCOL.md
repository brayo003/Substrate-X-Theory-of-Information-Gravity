# Task 9.2 — Anonymous Distributed Evidence Integration

**Status:** Protocol revision (no implementation until approved)  
**Date:** 2026-11-13  
**Hypothesis (to test, not assume):** When individually ambiguous observations are distributed across autonomous agents, **spatial nonlinear coincidence + hysteresis** produce a correct collective GO/NO-GO decision that equally constrained anonymous messaging and shared memory cannot achieve as effectively, **because of the nonlinear field’s dynamics**.

**Decisive standard:** Not “multiple deposits activate” (Task 8). The spatial relationship between fragments must be computationally relevant.

---

## 1. Task (one sentence)

Four agents each observe at most one noisy local intensity; a fragment alone is ambiguous; the collective must output **GO** only when **≥2 true fragments coincide in unmarked space** (joint sufficiency), else **NO-GO**—with no IDs, labels, or keyed stores.

---

## 2. Evidence-generation model (fully specified)

### 2.1 Geometry
- Arena \([0,L]^2\), \(L=50\) (Task 9 scale).  
- Unmarked coincidence region \(\mathcal{R}^*\): disk of radius \(R=4.0\), centre drawn uniformly (inset ≥10 from boundary) on GO trials; **agents never receive \(\mathcal{R}^*\) identity**.  
- Sensor radius \(\rho=3.5\); deposit width \(w=2.0\); deposit jitter \(\sigma_d=0.5\).  
- **Independence:** true fragments placed with pairwise distance \(\in[1.5, 2.5]\) inside \(\mathcal{R}^*\) (distinct sites; same coincidence neighbourhood for field overlap; not identical cells).  
- Distractors: ≥12 from \(\mathcal{R}^*\) centre and ≥8 from each other.

### 2.2 Intensity distributions (overlap required)
| Fragment type | Latent mean \(\mu\) | Obs noise |
|---|---|---|
| True | \(\mu_T=0.70\) | \(o=\mu+\varepsilon\), \(\varepsilon\sim\mathcal{N}(0,\sigma^2)\), \(\sigma=0.25\) |
| Distractor | \(\mu_D=0.55\) | same \(\sigma\) |

Single-observation ROC is poor by design: \(P(o>0.65\mid\mathrm{true})\approx0.58\), \(P(o>0.65\mid\mathrm{dist})\approx0.34\) (approx.). **No agent policy may use GT type.**

### 2.3 Trial classes
- **GO (50%):** \(K=3\) true fragments in \(\mathcal{R}^*\) + \(D=3\) distractors elsewhere. Joint sufficiency = spatial co-location of ≥2 true deposits.  
- **NO-GO (50%), subtype mix (fixed):**  
  - **N0 (50% of NO-GO):** \(D=6\) distractors only.  
  - **N1 (50% of NO-GO):** 1 true-like fragment (\(\mu_T\)) + 5 distractors—**individually strong possible, jointly insufficient**.  
- Fragments are **independent** draws: separate locations, independent \(\varepsilon\), no shared latent beyond GO’s common \(\mathcal{R}^*\).

### 2.4 Why space matters
Anonymous scalar count/sum can fire on many weak distractors or one strong N1 hit. **Correct GO requires co-located integration.** The substrate’s proposed role is nonlinear latch from overlapping deposits in \(\mathcal{R}^*\); restricted BB/msg lack spatial binding unless agents are physically co-located when writing (they are not required to be).

---

## 3. Information restrictions

| Allowed | Forbidden |
|---|---|
| Own pose; local intensity if fragment in \(\rho\) | Region IDs; `is_true`; class labels; \(\mathcal{R}^*\) |
| Local medium ops as defined per condition | Global field max; keyed maps; messages with pose/IDs/topics |

### 3.1 Restricted messaging (exact)
- On write: broadcast one scalar \(c\in[0,1]\) = clipped observation (or 0 if none).  
- Payload: **that scalar only**—no pose, ID, topic, timestamp beyond TTL expiry.  
- On read: agent receives the **list of live scalars** (TTL matched to field hold window budget).  
- Policy may use count, sum, max, mean of that list only.

### 3.2 Restricted blackboard (exact)
- Append-only **unordered multiset** \(M\) of scalars in \([0,1]\).  
- One append per agent max; value = clipped local observation (or 0).  
- Readers may inspect **all individual values** and compute sum, count, mean, max—**no keys, no positions, no overwrite of others’ entries**.  
- Stale window matched to msg TTL.  
- **Explicit:** BB has **no spatial structure**; any substrate win attributable to spatial organization must be stated as such in the report.

### 3.3 Substrate nl / linear (exact)
- Deposit Gaussian amplitude `DEP_AMP` (Task 9 freeze 0.45) at own pose ± jitter; one write/agent.  
- Read: local max in radius \(R_{\mathrm{read}}=5\) at **own pose only**.  
- Commit rule uses sustained local readout (hysteresis arm)—see §5.

---

## 4. Matched budgets

| Resource | Cap |
|---|---|
| \(N_a=4\), \(T_{\max}\), speed, \(\rho\) | Identical all conditions |
| Writes / msgs / BB appends | 1 each per agent |
| `DEP_AMP`, \(w\), \((r,a,b,\tau,c,\Delta t)\) | Frozen Task 7–8 / Task 9 freeze; **no retune** |

Pilot may adjust **only** \(\mu_T,\mu_D,\sigma,R\), placement distances to avoid floor/ceiling—then freeze before confirmatory.

---

## 5. Conditions and ablations

**Primary conditions (4):** (1) nonlinear substrate (2) linear substrate (3) restricted BB (4) restricted msg.

**Mechanism ablations (nonlinear seed-matched):**

| Arm | Definition |
|---|---|
| NL + hysteresis | Full reaction; commit requires local readout \(\ge\theta=0.85\) for \(H=20\) consecutive ticks after evolution (Task 9 hold). |
| NL, hysteresis disabled | Same reaction and \(\theta\); commit on first tick with readout \(\ge\theta\) (**\(H=1\)**). *Interpretation:* removes sustained-persistence requirement; if advantage vanishes only here, persistence/hold—not coincidence alone—drove it. |
| Linear | \(r=a=b=0\); same \(H=20\), \(\theta\), deposits. |
| Deposit disabled | No field writes; otherwise identical to NL+hysteresis. |

Optional smoke (non-primary): 2 controlled deposits in \(\mathcal{R}^*\) → nl latch, linear not.

**Note:** If \(H=1\) is judged too weak as “hysteresis off,” confirmatory report must also state that a stronger intervention (e.g. force non-persistent readout of instantaneous deposit sum without bistable evolution) was out of scope unless pre-registered in freeze JSON.

---

## 6. Decision rule and primary metric (single procedure)

- Each agent outputs \(\{\mathrm{GO},\,\mathrm{NO\text{-}GO},\,\mathrm{ABSTAIN}\}\).  
- **Collective decision:** if ≥3 agents agree on GO or on NO-GO, that is the decision; otherwise **UNDECIDED**.  
- UNDECIDED is **incorrect** for accuracy (never scored as match to \(Y\)).  
- **Primary metric:** balanced accuracy  
  \(\mathrm{BA}=\tfrac12(\mathrm{TPR}+\mathrm{TNR})\)  
  with TPR/TNR computed on trials where \(Y\) is GO/NO-GO; UNDECIDED counts as error for both.  
- **Secondary (report only):** coverage = fraction of trials with a decided collective output; mean latency; write counts.  
- **No** majority-of-2; **no** mean-commit shortcut.

---

## 7. Experimental units and statistics

### 7.1 Unit structure
- **Seed** \(s\): draws shared geometry/noise RNG stream.  
- Per seed: **\(T=10\) trials** (5 GO + 5 NO-GO; NO-GO split 2–3 / 3–2 alternating by seed parity into N0/N1).  
- All four primary conditions + ablations see **identical trial instances** (same fragments/noise) for that seed.  
- **Seed-level paired observation:** mean BA (or mean trial-correct) over the 10 trials within seed, per condition.  
- Confirmatory: **\(N=24\) seeds** (e.g. 500–523) → 24 paired units (not 240 independent unless GEE/cluster-robust is pre-registered; default = seed-level pairs).

### 7.2 Tests (preregistered)
- Paired permutation (or Wilcoxon) on seed-level BA.  
- α=0.05.  
- **Multiple comparisons m=4**, Bonferroni:  
  1. NL vs restricted BB  
  2. NL vs restricted msg  
  3. NL vs linear  
  4. NL vs NL-hysteresis-off  
- **Best-baseline rule (operationalized):** advantage criterion uses \(\max(\mathrm{BA}_{BB},\mathrm{BA}_{msg})\), but **both** BB and msg contrasts are tested; pass requires NL BA − max(BB,msg) ≥ **0.15** **and** adjusted significance on the contrast vs that max baseline (if BB is max, test 1 must reject; if msg is max, test 2).

### 7.3 Pass / STOP
**PASS** (all required):
1. Capability: NL seed-mean BA ≥ **0.65**  
2. Advantage: NL − max(BB, msg) ≥ **0.15** absolute, with Bonferroni-significant contrast vs that baseline  
3. Mechanism: (NL − linear) ≥ **0.15** and (NL − hyst-off) ≥ **0.15**, each Bonferroni-significant  

**STOP:** any confirmatory failure → **retire** this architectural hypothesis. No extra agents, rescoring, hybrids, or level frameworks.  
**PASS follow-up:** one replication cohort (new seeds) before treating as a Substrate AI component.

---

## 8. Explicit non-goals

Propagation necessity claims; hybrids; acceptance ladders; retuning \((r,a,b)\); field-only publication as fulfilment of Substrate AI; beating unconstrained (keyed) BB.

---

## 9. Freeze checklist (before confirmatory)

- [ ] Evidence parameters frozen after ≤8-seed pilot  
- [ ] BB/msg information models implemented exactly as §3  
- [ ] Single collective decision rule §6  
- [ ] Seed×10 trial unit locked  
- [ ] Stop thresholds unchanged after seeing confirmatory data  
