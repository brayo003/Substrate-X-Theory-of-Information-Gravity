from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim_world import SimulationContext, SimulationEngine, TickContext, TickId, WorldId
from sim_world.domains import register_all


def test_domain_registry_builds_a_village_world() -> None:
    engine = SimulationEngine()
    register_all(engine)

    world_id = WorldId.new("village-seed")
    context = SimulationContext(
        world_id=world_id,
        tick_context=TickContext(
            world_id=world_id,
            tick_id=TickId.new(world_id, 1),
            state_revision=None,
            parent_revision=None,
            timestamp=datetime.now(timezone.utc),
            correlation_id="village-seed",
        ),
        tick_number=1,
        world_state={"entities": {}},
        committed_revision=None,
    )

    result = engine.advance(context)

    assert result.proposals
    assert any(proposal.subject == "domain.time" for proposal in result.proposals)
    assert any(proposal.subject == "domain.weather" for proposal in result.proposals)
    assert any(proposal.subject == "domain.terrain" for proposal in result.proposals)
    assert any(proposal.subject == "domain.population" for proposal in result.proposals)
