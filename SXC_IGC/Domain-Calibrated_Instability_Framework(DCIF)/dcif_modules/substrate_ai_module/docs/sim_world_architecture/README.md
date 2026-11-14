# SimWorld Architecture Set

This is the architecture specification for **SimWorld**, a persistent AI simulation operating system. It is deliberately renderer-neutral: a renderer may be an LLM, diffusion model, game engine, robotics stack, or any combination, but none may become authoritative.

## Design commitments

- The World Kernel is the sole authority for committed world state.
- Simulation determines what becomes true; planning only proposes intentions.
- A renderer proposes an observation of the world; it never creates reality.
- Q is a read-only transport observable. It observes state transitions and informs the Governor; it never plans, stores memory, renders, or mutates state.
- Verification compares a rendered observation against an authoritative snapshot.
- The Governor decides control actions only: accept, reject, retry, slow down, branch, or rollback.
- Every subsystem has one responsibility and communicates through versioned contracts.

## Documents

1. [World Kernel Architecture](01_world_kernel_architecture.md)
2. [Repository Design](02_repository_design.md)
3. [World Kernel](03_world_kernel.md)
4. [Entity System](04_entity_system.md)
5. [Simulation Engine](05_simulation_engine.md)
6. [Planner](06_planner.md)
7. [Memory](07_memory.md)
8. [Transport Q](08_transport.md)
9. [Verifier](09_verifier.md)
10. [Governor](10_governor.md)
11. [Renderer Interface](11_renderer_interface.md)
12. [Implementation Roadmap](12_implementation_roadmap.md)

The design incorporates the central distinction established in `cchekki.txt`: persistent world state says an object exists, whereas asset memory says which specific object it is. It also preserves the AI-3 finding that Q has observational value independently of intervention; operational thresholds must therefore be calibrated per domain and reported with their provenance.

## Contract format

Each architecture document is treated as a frozen implementation contract and should expose the same three sections:

- `Public Interfaces`
- `Dependencies`
- `Acceptance Criteria`

When a subsystem changes, the contract changes first, then implementation follows the updated contract. This keeps the architecture documents authoritative and makes implementation layers independently verifiable.
