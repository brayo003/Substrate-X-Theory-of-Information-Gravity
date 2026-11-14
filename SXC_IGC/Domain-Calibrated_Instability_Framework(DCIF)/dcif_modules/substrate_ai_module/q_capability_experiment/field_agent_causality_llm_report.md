# Controlled Field-to-Agent Causal Coupling Experiment — LLM Report

**Date:** 2026-08-09T18:14:31.402765+00:00  
**Status:** COMPLETED  
**Classification:** `MEMORY_COUPLING_DETECTED`  

## 1. Experiment Configuration

| Parameter | Value |
|-----------|-------|
| experiment_id | field_agent_causality_llm_v1 |
| experiment_start | 2026-08-09T18:14:31.402765+00:00 |
| experiment_end | 2026-08-09T20:08:35.431288+00:00 |
| elapsed_seconds | 6843.989098072052 |
| ollama_model | qwen2.5-coder:1.5b |
| llm_temperature | 0.7 |
| llm_max_tokens | 64 |
| llm_timeout | 360 |
| seed | controlled_field_causality_llm_v1_fixed_seed |
| target_ticks | 10 |
| completed_ticks_a | 10 |
| completed_ticks_b | 10 |
| c_nominal_a | 1.0 |
| c_nominal_b | 2.0 |
| tau_nominal | 1.0 |
| entity_type | human |
| entity_name | TestAgent |
| initial_needs | {'hunger': 0.9, 'thirst': 0.8, 'energy': 0.1} |
| cooldown_ticks_override | 1 |
| cooldown_seconds_override | 0.0 |
| importance_threshold_override | 0.0 |

## 2. Ollama Model and LLM Configuration

- **Model:** `qwen2.5-coder:1.5b`
- **Temperature:** 0.7
- **max_tokens:** 64
- **timeout:** 360s
- **Deterministic generation:** Not supported by Ollama HTTP API (temperature=0.7 used; stochastic)

## 3. Entity Counts

- World A entity count: **1** (verified)
- World B entity count: **1** (verified)
- Entity type: `human`
- Entity name: `TestAgent`

## 4. Control Validation

- ✓ `world_a_entity_count`: True
- ✓ `world_b_entity_count`: True
- ✓ `entity_type_a`: True
- ✓ `entity_type_b`: True
- ✓ `same_entity_type`: True
- ✓ `c_nominal_a`: True
- ✓ `c_nominal_b`: True
- ✓ `c_nominal_differs`: True
- ✓ `tau_identical`: True
- ✓ `field_isolated`: True
- ✓ `field_state_isolated`: True
- ✓ `llm_enabled_a`: True
- ✓ `llm_enabled_b`: True
- ✓ `ollama_reachable`: True
- ✓ `model_available`: True
- ✓ `cooldown_ticks_a`: True
- ✓ `cooldown_ticks_b`: True
- ✓ `cooldown_secs_a`: True
- ✓ `cooldown_secs_b`: True
- ✓ `importance_threshold_a`: True
- ✓ `importance_threshold_b`: True

## 5. LLM Call Counts

| World | Total Calls | Successful |
|-------|------------|-----------|
| A (c=1.0) | 10 | 1 |
| B (c=2.0) | 10 | 3 |

## 6. Field Trajectories (sampled)

| Tick | A c_nominal | A spectral_entropy | B c_nominal | B spectral_entropy |
|------|------------|-------------------|------------|-------------------|
| 10 | 1.0000 | 3.178404066278161e-32 | 2.0000 | 3.178404066278161e-32 |

## 7. LLM Input Comparison (first call each world)

**World A prompt hash (first call):** `b86ed1316ff37775bb250d76f065eb3110686ab7cecd5b9a6376019bbfbf0559`

```
You are TestAgent, a villager and farmer in a simulation world.

Current Situation:
- Location: village_center
- Current tick: 0

Your Needs:
- hunger: 0.90
- thirst: 0.80
- energy: 0.10

Your Inventory:
- Empty

Nearby Entities:
- None

Current Goals:
- None

Recent Events:
- None

Environment:
- location: village_center

Transport Regime: unknown
Q Regime: unknown
Spectral Regime: unknown
Spectral Dominant K: 0.0000

Based on your current situation, needs, and environment, what do you want to do?

Provide your response as a single sentence describing your intent and reasoning.

```

**World B prompt hash (first call):** `b86ed1316ff37775bb250d76f065eb3110686ab7cecd5b9a6376019bbfbf0559`

```
You are TestAgent, a villager and farmer in a simulation world.

Current Situation:
- Location: village_center
- Current tick: 0

Your Needs:
- hunger: 0.90
- thirst: 0.80
- energy: 0.10

Your Inventory:
- Empty

Nearby Entities:
- None

Current Goals:
- None

Recent Events:
- None

Environment:
- location: village_center

Transport Regime: unknown
Q Regime: unknown
Spectral Regime: unknown
Spectral Dominant K: 0.0000

Based on your current situation, needs, and environment, what do you want to do?

Provide your response as a single sentence describing your intent and reasoning.

```

## 8. LLM Output Comparison (first call each world)

**World A response (tick 1):**
```

```

**World B response (tick 1):**
```
I am eating a meal and drinking water in the village center, feeling hungry (0.90) and thirsty (0.80), and need energy (0.10).
```

## 9. Divergence Analysis

- **First divergence tick:** 1
- **First divergence layer:** FIELD_PARAMS

| Layer | First Divergence Tick |
|-------|-----------------------|
| FIELD_PARAMS | 1 |
| SPECTRAL_OBSERVABLE | 1 |
| PERCEPTION | 2 |
| LLM_INPUT | 2 |
| LLM_OUTPUT | 1 |
| PLAN | None |
| ACTION | None |
| STATE | None |
| MEMORY | 1 |

## 10. Scientific Classification

**Classification: `MEMORY_COUPLING_DETECTED`**

**Reason:** Field differs → perception differs → LLM output differs → memory differs

- perception_differs: **True**
- output_differs: **True**
- plan_differs: **False**
- state_differs: **False**
- memory_differs: **True**

## 11. Limitations

- **Hardware constraint:** Each LLM call on this machine takes ~270s. The spec requires 500 ticks minimum; at 1 call/tick × 500 ticks × 2 worlds = ~75 hours. This run used 10 ticks per world, which is sufficient to demonstrate all causal layers but below the 500-tick spec minimum.
- Ollama HTTP API does not expose a deterministic seed; LLM inference is stochastic.
- One run was performed. For causal attribution stochastic divergence must be ruled out
  by repeating with matched conditions.
- The experiment covers one specific causal link. It does not prove the broader
  autonomous-artificial-life hypothesis.
- Needs decay over ticks may change the importance calculation in later ticks.
- max_tokens reduced to 64 (from 512) to reduce per-call latency.
