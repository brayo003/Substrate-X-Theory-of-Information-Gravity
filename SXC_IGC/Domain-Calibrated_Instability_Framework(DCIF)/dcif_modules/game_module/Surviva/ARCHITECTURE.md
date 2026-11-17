ARCHITECTURE.md

Purpose
-------
This document describes the authoritative runtime architecture for the V12 / "Tension" systems in src/. It records ownership, update ordering, the event bus contract, and controller responsibilities so future changes (refactors, features, tuning) can be made safely.

High-level summary
------------------
- Single authoritative PlayerState per player, created and owned by `SystemManager`.
- Deterministic update pipeline executed by `SystemManager` on `RunService.Heartbeat` in a fixed order.
- Lightweight `EventBus` to decouple controllers and signal state changes (metrics and rupture/consequence events).
- Controllers are passive consumers of `PlayerState` (they must not create their own MemoryField/PredictionField/TensionEngine instances).

Key components
--------------
1) PlayerState (src/shared/PlayerState.lua)
- Per-player authoritative container that owns the player's sub-systems:
  - `MemoryField` (grid of memory values)
  - `PredictionField` (gaze/predictability grid)
  - `TensionEngine` (HorizonEngine instance: tension dynamics, damage, rupture)
  - `ArtifactState`, `BookState`, `SanctuaryState` (behavioral/collection state)
  - `Derived` (DerivedMetrics instance) and `Consequences` (ConsequenceModel instance)
  - `Metrics` table (mutable snapshot values: Tension, Predictability, AverageMemory, IdentityDrift)
  - `Runtime` table (transient runtime inputs like EventStress)
- Responsibility: own precise instances and expose read/write helpers (getters) for controllers.

2) SystemManager (src/server/SystemManager.lua)
- Single runtime manager: creates/destroys PlayerState for players, runs the deterministic update loop.
- Update pipeline order (executed each heartbeat):
  1. MemoryField update
  2. PredictionField update
  3. TensionEngine.step (applies signals -> may rupture)
  4. Derived metrics recompute (IdentityDrift, Predictability, AverageMemory)
  5. Consequence evaluation (ConsequenceModel functions evaluate probabilistic outcomes)
  6. Event emission: TensionChanged, PredictionChanged, MemoryChanged, RuptureOccurred, SanctuaryBreachImminent, PlayerStateCreated/Destroy
  7. Controllers subscribe to events and perform side-effects and client sync
- Responsibility: ensure ordering, own lifecycle, and keep the pipeline deterministic.

3) EventBus (src/shared/EventBus.lua)
- Simple pub/sub: `subscribe(eventName, fn)` and `emit(eventName, ...)`.
- Emitted (canonical) events from SystemManager:
  - `PlayerStateCreated` (ps)
  - `PlayerStateDestroy` (ps)
  - `RuptureOccurred` (ps)
  - `SanctuaryBreachImminent` (ps)
  - `TensionChanged` (ps, value)
  - `PredictionChanged` (ps, value)
  - `MemoryChanged` (ps, value)
- Controllers should use `EventBus:subscribe` to react to these signals rather than polling.

Controller pattern and responsibilities
---------------------------------------
- Controllers are responsible for domain subsystems (SanctuaryController, ResourceDepletion, StillnessTrapController, StalkerSuperposition, ArtifactManager, BookController, BookMutations, SanctuaryDegradation, etc.).
- Contract for controllers:
  - Constructor signature: new(player, playerState, [otherDeps])
  - Do not create or own MemoryField/PredictionField/TensionEngine instances.
  - Use `playerState.MemoryField`, `playerState.PredictionField`, `playerState.TensionEngine` for reads/writes.
  - Subscribe to `SystemManager.Bus` for metric/rupture events (e.g., `TensionChanged`) and to `PlayerState` lifecycle events (`PlayerStateCreated` / `PlayerStateDestroy`).
  - Sync clients via existing RemoteEvents (e.g., `V12_Sync`) but avoid client-only services on server modules.
  - Clean up on `:destroy()` when PlayerStateDestroy or when the player leaves.

Ownership graph (short)
-----------------------
- SystemManager
  - creates PlayerState
    - PlayerState owns MemoryField, PredictionField, TensionEngine
    - DerivedMetrics and ConsequenceModel are instantiated and attached to PlayerState by SystemManager
  - SystemManager runs the heartbeat pipeline and emits events via EventBus
- Controllers (one instance per player) reference PlayerState and subscribe to EventBus

State flow and update ordering (deterministic pipeline)
-------------------------------------------------------
1) Input collection: controllers and client signals can append transient inputs into `playerState.Runtime` (EventStress, signal buffers). This is *not* a direct state mutation of M/P/T — it's a transient buffer consumed by SystemManager.
2) Memory update: `playerState.MemoryField:update(dt)` updates M grid based on recent player actions and signals.
3) Prediction update: `playerState.PredictionField:update(dt)` updates P grid (gaze/intent model).
4) Tension step: `playerState.TensionEngine:step(signal)` consumes runtime signals and updated M/P proxies, computes T_sys, and may return rupture
5) Derived metrics: recompute IdentityDrift, AverageMemory, Predictability from M/P/T
6) ConsequenceModel evaluation: evaluate probabilities of world reactions (doors, walls, sanctuary breach) — these are pure functions of metrics
7) Event emission: SystemManager emits metric changes & rupture/consequence events
8) Controller response: controllers subscribed to those events perform side-effects (spawn stalker, apply world changes), and issue client syncs

Event flow examples
-------------------
- Rupture flow:
  1) TensionEngine.step returns ruptured=true for PlayerState A
  2) SystemManager detects ruptured and emits `RuptureOccurred`(ps)
  3) ArtifactManager, BookMutations, StalkerSuperposition subscribe and react (ArtifactManager may drop an artifact; StalkerSuperposition may spawn a visible stalker; BookMutations uses T to enable mutations)
  4) Controllers may call `playerState.TensionEngine:addArtifactTension(-x)` to apply artifact effects (safe because PlayerState owns the engine)

- Sanctuary breach flow:
  1) Derived metrics and ConsequenceModel compute a `SanctuaryBreachProbability`
  2) If high, SystemManager emits `SanctuaryBreachImminent`(ps)
  3) SanctuaryController and SanctuaryDegradation react (visuals, spawn circling stalker, update memory in sanctuary)

Lifecycle notes
---------------
- Player joining: SystemManager:onPlayerAdded -> create PlayerState -> attach Derived/Consequences -> emit `PlayerStateCreated`
- Player leaving: SystemManager:onPlayerRemoving -> emit `PlayerStateDestroy` -> call `ps:destroy()` -> cleanup

Migration notes / checklist for remaining refactors
--------------------------------------------------
- All modules must follow constructor pattern `new(player, playerState, ...)`.
- Replace any `require("MemoryField").new()` / `TensionEngine.new()` call sites with `playerState.MemoryField` and `playerState.TensionEngine` usage.
- Convert controller factories in `James.server.lua` into ModuleScripts under `src/server/controllers/` and instantiate them from Phase controllers or SystemManager (recommended).
- Replace direct controller-to-controller calls with EventBus events.

Safety & staging plan (how to roll changes incrementally)
---------------------------------------------------------
1. Add defensive guards: wherever a controller expects `playerState`, guard against nil (early return) so the server doesn't crash if a player joins before wiring completes.
2. Migrate each controller one at a time and run local smoke checks. Prefer to migrate low-impact controllers first (ResourceDepletion, BookMutations) before high-impact systems (ShatterController, StalkerSuperposition).
3. Move James factories to modules and wire them to SystemManager; keep old factories as shims for a short period (deprecated wrappers) to support staged switchovers.

Open questions / TODOs
---------------------
- Which controllers still rely on client-only services (e.g., UserInputService) while being server modules? These must be audited and split.
- Controllers should subscribe to `SystemManager.Bus` (or be passed the Bus) — currently EventBus is created inside SystemManager and not globally exported. Suggestion: export SystemManager.Bus (already done as SystemManager.Bus) and pass it to controllers on init.
- Add unit tests / smoke harness to simulate PlayerState lifecycle and run SystemManager:update(dt) to validate pipeline order.

Appendix: canonical event names
-------------------------------
- `PlayerStateCreated` (ps)
- `PlayerStateDestroy` (ps)
- `RuptureOccurred` (ps)
- `SanctuaryBreachImminent` (ps)
- `TensionChanged` (ps, value)
- `PredictionChanged` (ps, value)
- `MemoryChanged` (ps, value)

End of document
