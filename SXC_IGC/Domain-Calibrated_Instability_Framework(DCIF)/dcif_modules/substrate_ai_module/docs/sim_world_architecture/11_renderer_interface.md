# 11. Renderer Interface

## Contract

A renderer is a replaceable actuator for representation. It receives an immutable, verified-for-release world snapshot plus a render profile; it returns a proposal and evidence. It owns no persistent world/asset memory, planning state, simulation state, or acceptance authority.

## Requests and responses

`RenderRequest` contains snapshot revision, scoped entity/scene graph, canonical asset references, relationship and continuity constraints, target modality, camera/sensor profile, quality/latency budget, safety constraints, deterministic seed where supported, and correlation ID. `RenderProposal` contains output reference, renderer/model/version, consumed request ID, extraction hints, declared limitations, generation parameters, timing, and trace evidence. The renderer may cache only ephemeral job data; durable identity always resolves through supplied asset references.

## Adapter families

| Renderer type | Proposal form |
|---|---|
| LLM | text, dialogue, structured narrative claims |
| Diffusion | image/video with conditioning and frame metadata |
| Game engine / 3D | scene/frame/telemetry output |
| Robotics | bounded physical action or sensor-actuation proposal |
| Text, audio, video | modality-native artifact plus extraction metadata |

Each adapter translates only at its edge. A multi-renderer composition has one shared target snapshot and separate proposals/reports; no renderer is privileged as source of world truth. The Kernel/Verifier/Governor pipeline handles discrepancies and acceptance.

## Public Interfaces

- Provides: render requests, renderer adapters, modality-specific proposal outputs, and traceable render evidence.
- Consumes: immutable verified snapshots, render profiles, canonical asset references, and modality constraints.
- Emits: render proposals, output artifacts, extraction hints, and declared limitations.

## Dependencies

- Depends on: verified world snapshots, asset references, and adapter-specific generation back ends.
- Does NOT depend on: world memory ownership, planning authority, simulation state, or governor truth claims.
- Must preserve: replaceability, modality independence, and ephemeral job state only.

## Acceptance Criteria

- Multiple renderer types can implement the same contract.
- The renderer owns no durable memory or authority over truth.
- The same snapshot can be rendered by different adapters without changing authoritative world state.
- Output always returns through verification before acceptance.
