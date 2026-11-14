"""
Legacy Q isolation module.

This module isolates legacy/proxy Q implementations from the theoretical Q implementation
to prevent confusion and ensure clear separation between engineered proxies and theoretical Q.

Legacy implementations:
- substrate_ai/components/q_field.py: Cosine-distance based Q (engineered proxy)
- Feature-space Q: Feature-gradient based Q (engineered proxy)
- Transport engine Q: Structural change metrics (unrelated metric)

Theoretical implementation:
- physical_field domain: Theoretical Q with physical field dynamics
"""

from typing import Dict, Any, Literal

# Legacy Q types
LEGACY_COSINE_Q = "legacy_cosine_q"
LEGACY_FEATURE_Q = "legacy_feature_q"
LEGACY_TRANSPORT_Q = "legacy_transport_q"

# Theoretical Q type
THEORETICAL_PHYSICAL_Q = "theoretical_physical_q"


class LegacyQIsolation:
    """Isolates legacy Q implementations from theoretical Q."""
    
    @staticmethod
    def classify_q_implementation(
        implementation_type: str,
        equation: str,
        domain: str,
        parameters: Dict[str, Any],
    ) -> Literal["theoretical", "proxy", "unrelated"]:
        """Classify a Q implementation as theoretical, proxy, or unrelated."""
        
        # Theoretical Q classification
        if implementation_type == THEORETICAL_PHYSICAL_Q:
            if equation == "4c²τ²|∇ln s|² - 1":
                if domain == "physical_space":
                    if parameters.get("c_measured", 0) > 0 and parameters.get("tau_measured", 0) > 0:
                        return "theoretical"
                    else:
                        return "proxy"  # Uses nominal parameters, not measured
                else:
                    return "proxy"  # Wrong domain
            else:
                return "proxy"  # Wrong equation
        
        # Legacy proxy classifications
        if implementation_type == LEGACY_COSINE_Q:
            if "cosine" in equation.lower():
                return "proxy"
        
        if implementation_type == LEGACY_FEATURE_Q:
            if "feature" in equation.lower() or "gradient" in equation.lower():
                return "proxy"
        
        if implementation_type == LEGACY_TRANSPORT_Q:
            if "structural" in equation.lower() or "topology" in equation.lower():
                return "unrelated"
        
        # Default to proxy for unknown implementations
        return "proxy"
    
    @staticmethod
    def get_legacy_q_metadata(
        implementation_type: str,
    ) -> Dict[str, Any]:
        """Get metadata for legacy Q implementations."""
        
        metadata = {
            LEGACY_COSINE_Q: {
                "file": "substrate_ai/components/q_field.py",
                "equation": "4c²τ²(cosine_distance)² - 1",
                "domain": "embedding_space",
                "parameters": {"c": 1.0, "tau": 0.5},
                "physical_meaning": "Semantic distance classification",
                "status": "engineered_proxy",
                "relation_to_theoretical": "Same mathematical form, different objects",
            },
            LEGACY_FEATURE_Q: {
                "file": "q_capability_experiment/code/phase2_q_calculation.py",
                "equation": "4c²τ²(feature_gradient)² - 1",
                "domain": "feature_space",
                "parameters": {"c": 1.0, "tau": 0.5},
                "physical_meaning": "Feature change classification",
                "status": "engineered_proxy",
                "relation_to_theoretical": "Same mathematical form, different objects",
            },
            LEGACY_TRANSPORT_Q: {
                "file": "sim_world/transport/transport_engine.py",
                "equation": "Not theoretical Q form",
                "domain": "entity_state_space",
                "parameters": "None",
                "physical_meaning": "Structural change classification",
                "status": "unrelated_metric",
                "relation_to_theoretical": "Different mathematical form and purpose",
            },
        }
        
        return metadata.get(implementation_type, {})
    
    @staticmethod
    def validate_separation(
        theoretical_q: Dict[str, Any],
        legacy_q: Dict[str, Any],
    ) -> bool:
        """Validate that theoretical and legacy Q are properly separated."""
        
        # Check that they have different domains
        if theoretical_q.get("domain") == legacy_q.get("domain"):
            return False
        
        # Check that they have different equations
        if theoretical_q.get("equation") == legacy_q.get("equation"):
            return False
        
        # Check that theoretical Q uses measured parameters
        if theoretical_q.get("parameters", {}).get("c_measured", 0) == 0:
            return False
        
        if theoretical_q.get("parameters", {}).get("tau_measured", 0) == 0:
            return False
        
        return True
