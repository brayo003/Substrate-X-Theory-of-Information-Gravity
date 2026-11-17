# Surviva — Substrate Survival

A Roblox survival-horror game built on the SXC-IGC tension engine. The world is a living substrate that remembers where you go, predicts where you'll be, and hunts you with what it learns.

**Engine:** Roblox (Luau)
**Build tool:** Rojo 7.4.1
**Theory:** [Substrate X — Theory of Information Gravity](https://github.com/brayo003/Substrate-X-Theory-of-Information-Gravity)

---

## The core idea

You are not trying to survive. You are trying to stay unknown.

The world tracks three spatial fields about you:

- **Tension T(x,t)** — where fear concentrates. The stalker spawns where T is high.
- **Memory M(x,t)** — where you have been. The stalker learns where M is dense.
- **Prediction P(x,t)** — where the system expects you to go. The stalker waits where P is high.

Low tension is not safety. Predictability is the real danger. If you repeat patterns, the substrate learns them. If you stay still, it closes in. Chaos is your only defense.

## The tension engine

The HorizonEngine implements the SXC-IGC drift equation:

```
f(T) = c + r*T + a*T² - b*T³
```

Parameters (locked, verified):

| Param | Value |
|-------|-------|
| c | 0.20 |
| r | -2.20 |
| a | 4.80 |
| b | 2.40 |
| forcing_scale | 27.0 |
| noise_sigma | 0.012 |
| rupture_t | 1.15 |
| cooldown_duration | 12.0 |

Geometric landmarks: Low = 0.121, Barrier = 0.500, High = 1.379.

Behavioral guarantees: idle input produces zero ruptures. Moderate activity builds tension slowly. Sustained chaos produces rupture after 40-90 seconds. Recovery always returns to baseline.

## Tension states

| Range | State | What happens |
|-------|-------|---------------|
| 0.0 - 0.4 | CALM | Resources abundant. Stalker lurks far. Sanctuary safe. |
| 0.4 - 0.7 | WARY | Resources thinner. Stalker watches. Sanctuary flickers. |
| 0.7 - 0.9 | ANGRY | Resources scarce. Stalker hunts. Sanctuary creaks. |
| 0.9 - 1.2 | HUNTED | Visual distortion. Stalker chases. Sanctuary unsafe. |
| 1.2 - 1.5 | SHATTER | Screen distorts. Stalker sprints. Sanctuary has shadows. |

## The stalker

Not scripted. It learns from your behavior:

- Where you go → ambushes on frequent routes
- When you go → appears at times you're usually outside
- What you collect → guards resources you take most
- How you escape → cuts off escape routes you use
- Where you hide → checks sanctuaries you frequent

The stalker is not a monster. It is the substrate's memory of everyone who came before. When it follows, you are walking their path. When it screams, you are hearing their last moment.

## Project structure

```
Difficulty_Governor_plugin/
├── default.project.json      Rojo project config (maps src/ to Roblox)
├── ARCHITECTURE.md            Runtime architecture: update pipeline, event bus, controller contracts
├── README.md                  This file
│
├── src/                       Active game code
│   ├── server/                Server-side systems (18 scripts)
│   ├── client/                Client-side effects and UI (8 scripts)
│   ├── shared/                Shared modules (7 modules)
│   └── obj.json               Game design state (phases, tasks, tests)
│
├── projects/Surviva/          Design documents
│   ├── gameplay.txt           Core game design: tension states, stalker, resources, sanctuary, day cycle
│   ├── gameplayv2.txt         Revised design: three-field separation, core loop, minimal system spec
│   ├── field_mech.txt         Field mechanics: how each action writes into T, M, P
│   ├── tension_predictability.md  The core inversion: low tension is not safe, predictability is danger
│   ├── system.txt             Coupled adaptive loop: player fields, substrate fields, coupling equation
│   ├── lore.txt               World lore: the Memoria, the Stalker, the artifacts, the sanctuary
│   ├── lore_technical.txt     Technical lore for implementation: stalker as compressed file, artifacts as tools
│   ├── Book_of_Substrate.txt  The Book mechanic: tracks state, unlocks entries, mutates text, predicts player
│   ├── map.txt                Map design: sanctuary, forest, ruins, origin, layers
│   ├── milestone.txt          Development milestones and phases
│   ├── progress.txt           Progress tracking
│   ├── shatter_mechanics      Shatter state mechanics
│   ├── stalker_state_machine.txt  Stalker AI states and transitions
│   ├── stillness_trap         Stillness trap mechanic
│   ├── survival_logic.txt     Survival logic rules
│   ├── artifact              Artifact definitions (Shattered Mirror, Burnt Journal, etc.)
│   ├── additives.txt          Additive design notes
│   └── assets.txt             Asset requirements (audio, visual, models)
│
├── analysis/
│   └── scripts/
│       └── tension_audit.py   Plot tension over a game session
│
└── archive/                   Non-active files (see ARCHIVE_INDEX.md)
    ├── binaries/              Roblox Studio, Rojo binary and zip
    ├── economy_whale/         Separate tycoon game concept (not Surviva)
    ├── game.rbxlx             Roblox place file
    └── surviva_research/       Java references, tuning experiments, early prototypes, dumps
```

## Server scripts

| Script | Purpose |
|--------|---------|
| SystemManager.lua | Runtime manager: creates PlayerState, runs heartbeat update pipeline, emits events |
| James.server.lua | Main integration script |
| PredictionField.server.lua | Tracks player gaze, predicts movement, writes to P grid |
| StalkerSuperposition.server.lua | Stalker AI: spawning, movement, learning from M and P fields |
| SanctuaryController.server.lua | Sanctuary zone: tension decay, safety state |
| SanctuaryDegradation.server.lua | Sanctuary decay under high memory/predictability |
| StillnessTrapController.server.lua | Punishes standing still >30s |
| ResourceDepletion.server.lua | Overharvesting creates memory scars |
| BookController.server.lua | Book of Substrate: entry unlock, display |
| BookMutations.server.lua | Book text mutation at high tension |
| ArtifactManager.server.lua | Artifact spawning and effects |
| ShatterController.server.lua | Shatter state at T > 1.2 |
| MemoryFlooding.server.lua | Memory field flooding mechanic |
| AnimalController.server.lua | Animal behavior driven by tension |
| BlendMP.server.lua | M and P field blending |
| Phase1Controller.server.lua | Phase 1 game state |
| Phase2Controller.server.lua | Phase 2 game state |
| GazeRouter.server.lua | Routes gaze data from client |
| StateLogger.server.lua | Logs state for analysis |

## Shared modules

| Module | Purpose |
|--------|---------|
| PlayerState.lua | Per-player authoritative container: owns MemoryField, PredictionField, TensionEngine |
| TensionEngine.lua | HorizonEngine: drift ODE, rupture, cooldown, momentum |
| MemoryField.lua | Grid of memory values: where the player has been |
| DerivedMetrics.lua | IdentityDrift, Predictability, AverageMemory from M/P/T |
| ConsequenceModel.lua | Probabilistic world reactions from metrics |
| EventBus.lua | Pub/sub for controller decoupling |
| FieldHandler.lua | (empty placeholder) |

## Client scripts

| Script | Purpose |
|--------|---------|
| TensionEffects.client.lua | Visual effects: ColorCorrection, FOV, saturation based on T |
| StillnessEffects.client.lua | Effects when standing still too long |
| SanctuaryEffects.client.lua | Sanctuary visual state |
| SanctuaryDegradationEffects.client.lua | Sanctuary decay visuals |
| BookUI.client.lua | Book of Substrate UI |
| BookMutationEffects.client.lua | Book mutation visual feedback |
| Bartholomew.client.lua | Companion/NPC client logic |
| GazeReporter.client.lua | Reports player gaze direction to server |

## How to run

```bash
# Install Rojo (if not already installed)
# Download from https://github.com/rojo-rbx/rojo/releases

# Start the Rojo server
./rojo serve default.project.json

# Open Roblox Studio, connect to Rojo
# Studio plugin: Rojo 7.x plugin required
```

## Development phases

Per `obj.json`, the game is in Phase 1 (core loop):

- [x] Grid memory M
- [x] Stalker spawns from M
- [x] Basic tension T
- [x] Tension engine tuning
- [ ] Sanctuary zone
- [ ] Stillness trap
- [ ] Resource depletion

## Related projects

- **UTD Mod** (`~/Git/new_world`): The production implementation of the same SXC-IGC theory as a Minecraft Fabric mod. More advanced, with 6 coupled field variables, per-chunk spatial transport, persistence, simulation lab, and validation pipeline.
- **SXC-IGC Theory** (`~/Git/Substrate_X_Theory_of_Information_Gravity`): The theoretical framework underlying both implementations.
- **`archive/surviva_research/`**: Early Java prototypes (ChunkTensionManager, TensionManager), Python parameter tuning sweeps, R-based early-warning-signal analysis, and early Lua prototypes from which the current code evolved.
