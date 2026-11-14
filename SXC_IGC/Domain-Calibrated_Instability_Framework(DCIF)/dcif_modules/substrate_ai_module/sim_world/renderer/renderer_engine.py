from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


from ..core.contracts import RenderSnapshot, freeze_value
from ..core.ids import EventId, TickId, WorldId
from .render_request import RenderRequest
from .render_result import RenderResult
from .render_profiles import RenderProfile, RenderProfileRegistry
from .renderer import ASCIIRenderer, BaseRenderAdapter, DebugRenderer, JsonRenderer, RenderAdapter, TextRenderer
from .renderer_context import RendererContext

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _event_id(world_id: WorldId, event_type: str, request_id: str, index: int) -> EventId:
    seed = f"sim_world.render_event|{world_id.value}|{event_type}|{request_id}|{index}"
    # deterministic_hash returns an int; RevisionId.from_uuid() requires a valid
    # UUID string, so build a deterministic RevisionId the way core/ids.py does.
    from ..core.ids import RevisionId

    revision_id = RevisionId.deterministic("render_event", seed)
    return EventId.new(revision_id, index, {"event_type": event_type, "request_id": request_id})


def _event_timestamp(request_id: str, event_type: str) -> datetime:
    seed = f"sim_world.render_event.time|{request_id}|{event_type}"
    seed_hash = deterministic_hash(seed)
    seconds = seed_hash % 86400
    micros = (seed_hash // 86400) % 1_000_000
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)


@dataclass(frozen=True, slots=True)
class RenderEvent:
    event_id: EventId
    world_id: WorldId
    event_type: str
    timestamp: datetime
    tick_id: TickId | None
    request_id: str
    snapshot_id: str
    renderer_type: str
    result_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", str(self.event_type))
        object.__setattr__(self, "request_id", str(self.request_id))
        object.__setattr__(self, "snapshot_id", str(self.snapshot_id))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "result_id", None if self.result_id is None else str(self.result_id))
        object.__setattr__(self, "payload", freeze_value(dict(self.payload)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


from datetime import timedelta


@dataclass
class RendererEngine:
    adapters: dict[str, RenderAdapter] = field(default_factory=dict)
    profiles: RenderProfileRegistry = field(default_factory=RenderProfileRegistry)
    default_adapter_type: str = "text"
    events: list[RenderEvent] = field(default_factory=list)
    history_records: list[RenderResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.adapters:
            for adapter in (TextRenderer(), JsonRenderer(), DebugRenderer(), ASCIIRenderer()):
                self.register_adapter(adapter)
        if self.default_adapter_type not in self.adapters:
            self.default_adapter_type = next(iter(self.adapters))

    def register_adapter(self, adapter: RenderAdapter) -> RenderAdapter:
        self.adapters[str(adapter.renderer_type)] = adapter
        return adapter

    def lookup_adapter(self, adapter_type: str | None = None) -> RenderAdapter:
        if adapter_type is None:
            return self.adapters[self.default_adapter_type]
        adapter = self.adapters.get(str(adapter_type))
        if adapter is not None:
            return adapter
        return self.adapters[self.default_adapter_type]

    def lookup_profile(self, profile: RenderProfile | str | None = None, *, renderer_type: str | None = None) -> RenderProfile:
        return self.profiles.select(profile, renderer_type=renderer_type)

    def capability_report(self) -> Mapping[str, Any]:
        return freeze_value(
            {
                "default_adapter_type": self.default_adapter_type,
                "adapters": {name: adapter.capabilities() for name, adapter in sorted(self.adapters.items())},
                "profiles": self.profiles.capabilities(),
            }
        )

    def render(self, context: RendererContext) -> RenderResult:
        profile = self.lookup_profile(context.render_profile, renderer_type=context.renderer_type)
        adapter_type = context.renderer_type or profile.preferred_adapter or profile.renderer_type
        adapter = self.lookup_adapter(adapter_type)
        request = RenderRequest.create(
            world_id=context.world_id,
            snapshot=context.snapshot,
            render_profile=profile,
            renderer_type=adapter.renderer_type,
            requested_output=context.requested_output,
            configuration={**dict(profile.configuration), **dict(context.configuration)},
            metadata={
                **dict(profile.metadata),
                **dict(context.metadata),
                "correlation_id": context.correlation_id,
                "user_parameters": dict(context.user_parameters),
            },
        )
        self._emit("RenderRequested", context.world_id, request=request, snapshot=context.snapshot)
        self._emit("RenderStarted", context.world_id, request=request, snapshot=context.snapshot)
        try:
            result = adapter.render(request)
        except Exception as exc:
            self._emit("RenderFailed", context.world_id, request=request, snapshot=context.snapshot, payload={"error": str(exc)})
            raise
        self.history_records.append(result)
        self._emit("RenderCompleted", context.world_id, request=request, snapshot=context.snapshot, result=result)
        self._emit("RenderPublished", context.world_id, request=request, snapshot=context.snapshot, result=result)
        return result

    def history(self) -> tuple[RenderResult, ...]:
        return tuple(self.history_records)

    def _emit(
        self,
        event_type: str,
        world_id: WorldId,
        *,
        request: RenderRequest,
        snapshot: RenderSnapshot,
        result: RenderResult | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> RenderEvent:
        timestamp = result.generation_timestamp if result is not None else _event_timestamp(request.request_id, event_type)
        event = RenderEvent(
            event_id=_event_id(world_id, event_type, request.request_id, len(self.events) + 1),
            world_id=world_id,
            event_type=event_type,
            timestamp=timestamp,
            tick_id=snapshot.tick_id,
            request_id=request.request_id,
            snapshot_id=str(snapshot.snapshot_id.value),
            renderer_type=request.renderer_type,
            result_id=None if result is None else result.result_id,
            payload={} if payload is None else dict(payload),
            metadata={
                "profile_id": request.render_profile.profile_id,
                "profile_name": request.render_profile.name,
                "result_id": None if result is None else result.result_id,
            },
        )
        self.events.append(event)
        return event
