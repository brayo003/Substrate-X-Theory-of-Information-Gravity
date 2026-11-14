"""
Structured LLM Context Builder for Autonomous Reasoning

This module builds structured prompts for LLM reasoning that include:
- Current world observations
- Substrate observables
- Agent state
- Available executable primitives
- Recent actions
- Relevant memory/history
- Current environmental conditions
- Consequences/results of recent actions

The LLM response must resolve into an executable structured action.
"""

from dataclasses import dataclass, field
from typing import Any, Mapping
from datetime import datetime, timezone


@dataclass
class AvailablePrimitive:
    """Information about an available primitive/capability."""
    name: str
    description: str
    preconditions: list[str]
    effects: list[str]
    energy_cost: float
    time_cost: int


@dataclass
class EnvironmentContext:
    """Current environmental conditions."""
    substrate_state: dict[str, Any]
    weather: str
    resource_availability: dict[str, float]
    safety_level: str


@dataclass
class LLMReasoningContext:
    """Complete context for LLM reasoning."""
    agent_name: str
    current_tick: int
    observation: dict[str, Any]
    memory: dict[str, Any]
    available_primitives: list[AvailablePrimitive]
    environment: EnvironmentContext
    metadata: dict[str, Any] = field(default_factory=dict)


class StructuredContextBuilder:
    """Build structured prompts for LLM reasoning."""
    
    def build_prompt(self, context: LLMReasoningContext) -> str:
        """Build a structured prompt for LLM reasoning."""
        
        prompt = f"""You are an autonomous agent named {context.agent_name} making decisions in a simulated world.

CURRENT SITUATION:
- Tick: {context.current_tick}
- Observation: {context.observation}

RECENT HISTORY:
- Memory: {context.memory}

ENVIRONMENTAL CONDITIONS:
- Environment: {context.environment}

AVAILABLE PRIMITIVES:
{self._format_primitives(context.available_primitives)}

DECISION TASK:
Based on your current state, recent history, and environmental conditions, select the most appropriate primitive to execute.

RESPONSE FORMAT:
Respond with a JSON object containing:
{{
    "primitive": "NAME_OF_PRIMITIVE",
    "parameters": {{"key": "value"}},
    "reason": "brief explanation of your decision",
    "expected_effect": "what you expect to happen"
}}

Choose only from the available primitives listed above.
"""

        return prompt
    
    def _format_primitives(self, primitives: list[AvailablePrimitive]) -> str:
        """Format available primitives as a readable string."""
        result = []
        for prim in primitives:
            result.append(f"- {prim.name}: {prim.description}")
            result.append(f"  Preconditions: {', '.join(prim.preconditions) if prim.preconditions else 'none'}")
            result.append(f"  Effects: {', '.join(prim.effects) if prim.effects else 'none'}")
            result.append(f"  Energy cost: {prim.energy_cost}, Time cost: {prim.time_cost}")
        return '\n'.join(result)


def parse_llm_response(response_text: str) -> dict[str, Any]:
    """Parse LLM response into structured action."""
    import json
    
    try:
        # Try to extract JSON from response
        if '{' in response_text and '}' in response_text:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            return json.loads(json_str)
        else:
            # Fallback: try to parse entire response as JSON
            return json.loads(response_text)
    except Exception as e:
        # If parsing fails, return a structured error
        return {
            "primitive": "WAIT",
            "parameters": {},
            "reason": f"LLM response parsing failed: {str(e)}",
            "expected_effect": "Wait for next tick",
            "error": str(e)
        }
