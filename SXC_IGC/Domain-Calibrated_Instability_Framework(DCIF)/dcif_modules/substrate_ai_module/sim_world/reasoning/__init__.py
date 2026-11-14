"""
Reasoning Module - LLM integration for autonomous entity reasoning

This module provides:
- LLM Service: Local inference through Ollama
- Entity Context Builder: Build prompts from simulation state
- Intent Generation: LLM outputs intentions
- Intent Translation: Convert intentions to Goals
- Reasoning Coordinator: Performance optimizations and coordination
- Reasoning Cycle Tracker: Comprehensive tracking of all reasoning cycles
"""

from .llm_service import LLMService, LLMRequest, LLMResponse
from .intent_schema import Intent, IntentBatch
from .context_builder import ContextBuilder, EntityContext
from .intent_generator import IntentGenerator
from .intent_translator import IntentTranslator
from .reasoning_coordinator import ReasoningCoordinator, ReasoningCooldown
from .reasoning_cycle_tracker import ReasoningCycle, ReasoningCycleTracker

__all__ = [
    "LLMService",
    "LLMRequest",
    "LLMResponse",
    "Intent",
    "IntentBatch",
    "ContextBuilder",
    "EntityContext",
    "IntentGenerator",
    "IntentTranslator",
    "ReasoningCoordinator",
    "ReasoningCooldown",
    "ReasoningCycle",
    "ReasoningCycleTracker",
]
