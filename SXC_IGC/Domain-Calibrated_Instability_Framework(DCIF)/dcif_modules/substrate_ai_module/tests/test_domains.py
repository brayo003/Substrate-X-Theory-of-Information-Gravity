import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim_world import SimulationContext, SimulationEngine, TickContext, TickId, WorldId
from sim_world.domains.physics import register as register_physics


def test_domains_can_register_with_simulation_engine() -> None:
    engine = SimulationEngine()
    register_physics(engine)

    world_id = WorldId.new("domain-test")
    context = SimulationContext(
        world_id=world_id,
        tick_context=TickContext(
            world_id=world_id,
            tick_id=TickId.new(world_id, 1),
            state_revision=None,
            parent_revision=None,
            timestamp=datetime.now(timezone.utc),
            correlation_id="domain-test",
        ),
        tick_number=1,
        world_state={"entities": {}},
        committed_revision=None,
    )

    result = engine.advance(context)

    assert result.proposals
    assert any(proposal.subject == "domain.physics" for proposal in result.proposals)
