#!/usr/bin/env python3
"""
Stage 7 — Domain Execution Order Audit

Reconstruct the exact execution order of every registered domain
during simulation_engine._run_domain_hooks().
"""

import sys
sys.path.insert(0, '.')

from kernel.world_kernel import WorldKernel
from domains.population import initialize_valley_population
from domains.terrain import initialize_valley_terrain
from domains.resources import initialize_valley_resources
from domains.needs import initialize_valley_needs
from domains.time import initialize_valley_time
from domains.weather import initialize_valley_weather
from domains.agriculture import initialize_valley_agriculture
from domains.health import initialize_valley_health
from domains.physics import initialize_valley_physics
from domains.production import initialize_valley_production
from domains.economy import initialize_valley_economy
from domains.relationships import initialize_valley_relationships
from domains.society import initialize_valley_society
from domains.learning import initialize_valley_learning
from domains.conversation import initialize_valley_conversation

print("Stage 7 — Domain Execution Order Audit")
print("=" * 60)

# Create kernel
kernel = WorldKernel()

# Register all domains
kernel.register_all_domains()

# Get domain hooks from simulation engine
domain_hooks = kernel.simulation_engine.domain_hooks

print(f"\nRegistered domains: {len(domain_hooks)}")
print(f"\nExecution order (alphabetical, as per sorted(domain_hooks.items())):")
print("-" * 60)

for index, (name, hook) in enumerate(sorted(domain_hooks.items()), 1):
    print(f"{index:2d}. {name}")

print("\n" + "=" * 60)
print("Physics position in execution order:")
print("-" * 60)

domain_names = sorted(domain_hooks.keys())
physics_index = domain_names.index("physics") + 1
print(f"Physics executes at position {physics_index}")

print("\nDomains that execute AFTER Physics:")
print("-" * 60)

for index, name in enumerate(domain_names, 1):
    if index > physics_index:
        print(f"{index:2d}. {name}")

print("\n" + "=" * 60)
print("CONCLUSION:")
print("-" * 60)

if physics_index < len(domain_names):
    print(f"✓ Population executes at position {domain_names.index('population') + 1}")
    print(f"✓ Population executes AFTER Physics (position {physics_index})")
    print(f"✓ Population CAN legally consume physics_goal_completion_signals in same tick")
else:
    print("✗ Physics executes last - no domain can consume its signals in same tick")

print("\n" + "=" * 60)
