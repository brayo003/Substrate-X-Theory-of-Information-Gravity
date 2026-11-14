"""
Substrate coupling module.

This module couples the physical information density field to existing SXC-IGC substrate dynamics.

Coupling interfaces:
- Entity positions → Field sources/sinks
- Entity needs → Field perturbations
- Entity actions → Field boundary conditions
- Field state → Entity state influence
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
)
from .physical_field_dynamics import apply_perturbation


class SubstrateCoupling:
    """Coupling interface between physical field and existing substrate."""
    
    def __init__(self, field: InformationDensityField):
        self.field = field
        self.coupling_points: Dict[str, PhysicalCoordinate] = {}
        self.coupling_strengths: Dict[str, float] = {}
    
    def register_entity_coupling(
        self,
        entity_id: str,
        position: Dict[str, float],
        coupling_strength: float = 1.0,
    ) -> None:
        """Register an entity as a coupling point for the field.
        
        Args:
            entity_id: Entity identifier
            position: Entity position with x, y, z keys
            coupling_strength: Strength of coupling (0.0 to 1.0)
        """
        coord = PhysicalCoordinate(
            x=position.get("x", 0.0),
            y=position.get("y", 0.0),
            z=position.get("z", 0.0),
        )
        self.coupling_points[entity_id] = coord
        self.coupling_strengths[entity_id] = coupling_strength
    
    def couple_entity_needs_to_field(
        self,
        entity_id: str,
        needs: Dict[str, float],
    ) -> InformationDensityField:
        """Couple entity needs to field as perturbations.
        
        High needs (hunger, thirst, etc.) create field perturbations.
        
        Args:
            entity_id: Entity identifier
            needs: Dictionary of need values (0.0 to 1.0)
        
        Returns:
            Field with entity needs coupled as perturbations
        """
        if entity_id not in self.coupling_points:
            return self.field
        
        coord = self.coupling_points[entity_id]
        strength = self.coupling_strengths[entity_id]
        
        # Calculate total need intensity
        total_need = sum(needs.values()) / len(needs) if needs else 0.0
        
        # Apply perturbation proportional to need intensity
        if total_need > 0.5:  # Threshold for coupling
            perturbation_amplitude = total_need * strength
            perturbation_width = 5.0  # Fixed spatial extent
            
            self.field = apply_perturbation(
                self.field,
                coord,
                perturbation_amplitude=perturbation_amplitude,
                perturbation_width=perturbation_width,
            )
        
        return self.field
    
    def couple_field_to_entity_state(
        self,
        entity_id: str,
    ) -> Dict[str, float]:
        """Couple field state back to entity as environmental influence.
        
        Field Q values influence entity behavior parameters.
        
        Args:
            entity_id: Entity identifier
        
        Returns:
            Dictionary of field-derived influence parameters
        """
        if entity_id not in self.coupling_points:
            return {}
        
        coord = self.coupling_points[entity_id]
        
        # Get field value at entity location
        field_value = self.field.get_density_at(coord)
        
        # Calculate field-derived influences
        influences = {
            "field_intensity": float(field_value),
            "information_availability": min(1.0, field_value / 2.0),
            "environmental_pressure": max(0.0, (field_value - 1.0) / 2.0),
        }
        
        return influences
    
    def couple_entity_actions_to_field(
        self,
        entity_id: str,
        action_type: str,
        action_parameters: Dict[str, Any],
    ) -> InformationDensityField:
        """Couple entity actions to field as boundary conditions.
        
        Actions like "work", "move", "interact" create field effects.
        
        Args:
            entity_id: Entity identifier
            action_type: Type of action
            action_parameters: Action-specific parameters
        
        Returns:
            Field with action effects applied
        """
        if entity_id not in self.coupling_points:
            return self.field
        
        coord = self.coupling_points[entity_id]
        strength = self.coupling_strengths[entity_id]
        
        # Different actions create different field effects
        action_effects = {
            "work": {"amplitude": 0.5, "width": 3.0},
            "move": {"amplitude": 0.3, "width": 2.0},
            "interact": {"amplitude": 0.4, "width": 4.0},
            "rest": {"amplitude": -0.2, "width": 5.0},  # Negative for relaxation
        }
        
        effect = action_effects.get(action_type, {"amplitude": 0.0, "width": 0.0})
        
        if effect["amplitude"] != 0.0:
            perturbation_amplitude = effect["amplitude"] * strength
            perturbation_width = effect["width"]
            
            self.field = apply_perturbation(
                self.field,
                coord,
                perturbation_amplitude=perturbation_amplitude,
                perturbation_width=perturbation_width,
            )
        
        return self.field
    
    def get_field_statistics(self) -> Dict[str, float]:
        """Get field statistics for substrate integration.
        
        Returns:
            Dictionary of field statistics
        """
        field_values = self.field.state.field_values
        
        return {
            "mean_field_value": float(np.mean(field_values)),
            "std_field_value": float(np.std(field_values)),
            "max_field_value": float(np.max(field_values)),
            "min_field_value": float(np.min(field_values)),
            "total_field_energy": float(np.sum(field_values**2)),
            "field_variance": float(np.var(field_values)),
        }
    
    def synchronize_with_substrate_tick(
        self,
        substrate_state: Dict[str, Any],
    ) -> InformationDensityField:
        """Synchronize field with substrate state update.
        
        Called each substrate tick to maintain coupling.
        
        Args:
            substrate_state: Current substrate state
        
        Returns:
            Updated field
        """
        # Extract entity states from substrate
        entities = substrate_state.get("entities", {})
        
        # Couple each entity to field
        for entity_id, entity_data in entities.items():
            # Get entity position
            components = entity_data.get("components", {})
            transform = components.get("TransformComponent", {})
            position = transform.get("position", {"x": 0.0, "y": 0.0, "z": 0.0})
            
            # Register coupling if not exists
            if entity_id not in self.coupling_points:
                self.register_entity_coupling(entity_id, position)
            
            # Get entity needs
            needs = components.get("NeedsComponent", {}).get("needs", {})
            
            # Couple needs to field
            self.field = self.couple_entity_needs_to_field(entity_id, needs)
        
        return self.field
