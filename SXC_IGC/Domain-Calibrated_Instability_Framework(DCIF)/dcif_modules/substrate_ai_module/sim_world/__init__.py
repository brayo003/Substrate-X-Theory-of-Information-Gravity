from __future__ import annotations

import importlib
import sys


# Import submodules first before any legacy alias registration
from .core import *
from .domains import *
from .entities import *
from .governor import *
from .kernel import *
from .memory import *
from .planner import *
from .renderer import *
from .simulation import *
from .transport import *
from .utils import *
from .verifier import *


def _register_legacy_aliases() -> None:
    """
    Register legacy module aliases for backward compatibility.
    
    This is called lazily only when a legacy import is attempted,
    avoiding circular import issues during package initialization.
    """
    aliases = {
        "sim_world.action_executor": "sim_world.simulation.action_executor",
        "sim_world.action_validator": "sim_world.simulation.action_validator",
        "sim_world.agent_memory": "sim_world.memory.agent_memory",
        "sim_world.asset_memory": "sim_world.memory.asset_memory",
        "sim_world.components": "sim_world.entities.components",
        "sim_world.config": "sim_world.core.config",
        "sim_world.contracts": "sim_world.core.contracts",
        "sim_world.entity": "sim_world.entities.entity",
        "sim_world.errors": "sim_world.core.errors",
        "sim_world.events": "sim_world.core.events",
        "sim_world.goal_manager": "sim_world.planner.goal_manager",
        "sim_world.governor_context": "sim_world.governor.governor_context",
        "sim_world.governor_engine": "sim_world.governor.governor_engine",
        "sim_world.governor_history": "sim_world.governor.governor_history",
        "sim_world.governor_policy": "sim_world.governor.governor_policy",
        "sim_world.ids": "sim_world.core.ids",
        "sim_world.knowledge_memory": "sim_world.memory.knowledge_memory",
        "sim_world.plan_generator": "sim_world.planner.plan_generator",
        "sim_world.plan_scheduler": "sim_world.planner.plan_scheduler",
        "sim_world.plan_validator": "sim_world.planner.plan_validator",
        "sim_world.planner_context": "sim_world.planner.planner_context",
        "sim_world.planner_engine": "sim_world.planner.planner_engine",
        "sim_world.q_calibrator": "sim_world.transport.q_calibrator",
        "sim_world.q_metrics": "sim_world.transport.q_metrics",
        "sim_world.q_observation": "sim_world.transport.q_observation",
        "sim_world.registry": "sim_world.entities.registry",
        "sim_world.relationship_memory": "sim_world.memory.relationship_memory",
        "sim_world.relationships": "sim_world.entities.relationships",
        "sim_world.render_profiles": "sim_world.renderer.render_profiles",
        "sim_world.render_request": "sim_world.renderer.render_request",
        "sim_world.render_result": "sim_world.renderer.render_result",
        "sim_world.render_snapshot": "sim_world.renderer.render_snapshot",
        "sim_world.renderer_context": "sim_world.renderer.renderer_context",
        "sim_world.renderer_engine": "sim_world.renderer.renderer_engine",
        "sim_world.resources": "sim_world.entities.resources",
        "sim_world.revision": "sim_world.core.revision",
        "sim_world.scheduler": "sim_world.simulation.scheduler",
        "sim_world.simulation_context": "sim_world.simulation.simulation_context",
        "sim_world.simulation_engine": "sim_world.simulation.simulation_engine",
        "sim_world.snapshot": "sim_world.core.snapshot",
        "sim_world.storage": "sim_world.core.storage",
        "sim_world.temporal_memory": "sim_world.memory.temporal_memory",
        "sim_world.tick": "sim_world.core.tick",
        "sim_world.transport_context": "sim_world.transport.transport_context",
        "sim_world.transport_engine": "sim_world.transport.transport_engine",
        "sim_world.verifier_context": "sim_world.verifier.verifier_context",
        "sim_world.verifier_engine": "sim_world.verifier.verifier_engine",
        "sim_world.world_kernel": "sim_world.kernel.world_kernel",
        "sim_world.world_memory": "sim_world.memory.world_memory",
        "sim_world.world_rules": "sim_world.simulation.world_rules",
    }
    
    for alias, target in aliases.items():
        if alias not in sys.modules:
            sys.modules[alias] = importlib.import_module(target)


# Don't register legacy aliases at import time
# They will be registered on-demand if needed
