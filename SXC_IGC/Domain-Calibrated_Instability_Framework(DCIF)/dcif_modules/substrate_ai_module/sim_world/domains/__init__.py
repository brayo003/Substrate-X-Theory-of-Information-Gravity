from __future__ import annotations

from typing import Any

# Only import from domains that actually have domain files
from .weather import register as register_weather
from .needs import register as register_needs
from .health import register as register_health
from .society import register as register_society

# Domains with domain files but missing imports
from .resources import register as register_resources, initialize_valley_resources
from .agriculture import register as register_agriculture, initialize_valley_agriculture
from .production import register as register_production, initialize_valley_production
from .learning import register as register_learning, initialize_valley_learning
from .economy import register as register_economy, initialize_valley_economy
from .relationships import register as register_relationships, initialize_valley_relationships
from .conversation import register as register_conversation, initialize_valley_conversations

# Population domain (uses __init__.py instead of domain file)
from .population import register as register_population, initialize_valley_population

# Terrain domain (uses __init__.py instead of domain file)
from .terrain import register as register_terrain, initialize_valley_terrain

# Time domain (uses __init__.py; produces world.time.hour per PROTOCOL.md)
from .time import register as register_time

# Physical field domain (theoretical Q substrate)
from .physical_field import register as register_physical_field, initialize_physical_field


def register_all(engine: object) -> None:
    """Register all available domains with the simulation engine."""
    # PROGRESSIVE INTEGRATION: Add domains one by one
    register_weather(engine)
    register_time(engine)
    register_physical_field(engine)  # NEW: Theoretical Q physical substrate
    # register_needs(engine)
    # register_health(engine)
    # register_society(engine)
    # register_resources(engine)
    # register_agriculture(engine)
    # register_production(engine)
    # register_learning(engine)
    # register_economy(engine)
    # register_relationships(engine)
    # register_conversation(engine)
    register_population(engine)
    # register_terrain(engine)


def bootstrap_all(kernel: object) -> None:
    """Bootstrap the initial world by calling all domain initialization functions."""
    # PROGRESSIVE INTEGRATION: All bootstraps
    initialize_valley_population(kernel)
    initialize_valley_terrain(kernel)
    initialize_valley_resources(kernel)
    initialize_valley_agriculture(kernel)
    initialize_valley_production(kernel)
    initialize_valley_learning(kernel)
    initialize_valley_economy(kernel)
    initialize_valley_relationships(kernel)
    initialize_valley_conversations(kernel)
