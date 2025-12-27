#!/usr/bin/env python3
"""
CLEAN UNIVERSAL-NEURAL INTERFACE
Keeps both systems distinct but enables powerful synergy
"""
import numpy as np
from typing import Dict, Any, Callable

class UniversalNeuralInterface:
    """
    Clean interface between universal dynamics engine and neural networks
    Maintains separation of concerns while enabling cooperation
    """
    
    def __init__(self):
        # Interface state - no internal logic, just communication
        self.interface_state = {
            'universal_to_neural': {},
            'neural_to_universal': {},
            'learning_signals': {},
            'performance_metrics': {}
        }
        
        # Callback registry - pure message passing
        self.callbacks = {
            'on_universal_update': [],
            'on_neural_decision': [],
            'on_interface_event': []
        }
        
        print("🔄 UNIVERSAL-NEURAL INTERFACE INITIALIZED")
        print("Pure message passing - No mixed logic")
        print("=" * 50)
    
    def package_universal_state(self, universal_engine) -> Dict[str, Any]:
        """
        Extract observation data from universal engine for neural network
        Pure data packaging - no logic
        """
        # Safe normalization
        rho_max = np.max(universal_engine.rho) + 1e-8
        E_max = np.max(np.abs(universal_engine.E)) + 1e-8
        F_max = np.max(np.abs(universal_engine.F)) + 1e-8
        
        return {
            'field_patterns': {
                'rho_normalized': universal_engine.rho / rho_max,
                'E_normalized': universal_engine.E / E_max,
                'F_normalized': universal_engine.F / F_max
            },
            'system_state': {
                'stress_levels': np.mean(universal_engine.stress_history) if hasattr(universal_engine, 'stress_history') else 0.0,
                'constraint_activity': np.mean(universal_engine.broken_regions) if hasattr(universal_engine, 'broken_regions') else 0.0,
                'stability_warnings': universal_engine.stability_warnings if hasattr(universal_engine, 'stability_warnings') else 0,
                'step_count': universal_engine.step_count if hasattr(universal_engine, 'step_count') else 0
            },
            'performance_metrics': {
                'dynamics_complexity': self._calculate_field_complexity(universal_engine.rho),
                'constraint_efficiency': self._calculate_constraint_efficiency(universal_engine),
                'energy_usage': np.mean(universal_engine.rho**2)  # Rough energy measure
            }
        }
    
    def _calculate_field_complexity(self, field):
        """Pure function - field complexity calculation"""
        grad_x = np.gradient(field, axis=0)
        grad_y = np.gradient(field, axis=1)
        return np.mean(grad_x**2 + grad_y**2)
    
    def _calculate_constraint_efficiency(self, engine):
        """Pure function - constraint efficiency metric"""
        if hasattr(engine, 'broken_regions') and hasattr(engine, 'stress_history'):
            active_constraints = np.mean(engine.broken_regions)
            stress_level = np.mean(engine.stress_history)
            return active_constraints / (stress_level + 1e-8)
        return 0.0
    
    def apply_neural_controls(self, universal_engine, neural_controls: Dict[str, Any]):
        """
        Apply neural network decisions to universal engine
        Pure parameter setting - no internal logic
        """
        if not neural_controls:
            return
            
        # Parameter adjustments
        if 'parameter_adjustments' in neural_controls:
            adjustments = neural_controls['parameter_adjustments']
            
            # Safe parameter updates with bounds
            if 'M_factor_adjust' in adjustments and hasattr(universal_engine, 'M_factor'):
                universal_engine.M_factor *= (1.0 + adjustments['M_factor_adjust'])
                universal_engine.M_factor = np.clip(universal_engine.M_factor, 1000, 1e6)
            
            if 'damping_adjust' in adjustments and hasattr(universal_engine, 'cubic_damping'):
                universal_engine.cubic_damping *= (1.0 + adjustments['damping_adjust'])
                universal_engine.cubic_damping = np.clip(universal_engine.cubic_damping, 0.01, 2.0)
        
        # Constraint tuning
        if 'constraint_tuning' in neural_controls:
            tuning = neural_controls['constraint_tuning']
            
            if 'threshold_adjust' in tuning and hasattr(universal_engine, 'breaking_threshold'):
                universal_engine.breaking_threshold *= (1.0 + tuning['threshold_adjust'])
                universal_engine.breaking_threshold = np.clip(universal_engine.breaking_threshold, 0.1, 5.0)
        
        # Emergency overrides
        if 'emergency_actions' in neural_controls:
            self._handle_emergency_actions(universal_engine, neural_controls['emergency_actions'])
    
    def _handle_emergency_actions(self, engine, actions):
        """Pure function - handle emergency actions"""
        if 'stabilize_system' in actions and actions['stabilize_system']:
            # Gentle stabilization
            engine.rho *= 0.9
            engine.E *= 0.8
            engine.F *= 0.8
        
        if 'reset_constraints' in actions and actions['reset_constraints']:
            if hasattr(engine, 'broken_regions'):
                engine.broken_regions = np.zeros_like(engine.broken_regions, dtype=bool)
            if hasattr(engine, 'stress_history'):
                engine.stress_history = np.zeros_like(engine.stress_history)
    
    def generate_learning_signals(self, universal_state: Dict, neural_controls: Dict) -> Dict[str, Any]:
        """
        Generate learning signals for neural network based on universal dynamics
        Pure signal generation - no learning logic
        """
        performance = universal_state['performance_metrics']
        
        # Reward signals
        rewards = {
            'stability_reward': -universal_state['system_state']['stability_warnings'] * 0.1,
            'efficiency_reward': performance['constraint_efficiency'] * 0.01,
            'complexity_reward': performance['dynamics_complexity'] * 0.001,
            'energy_penalty': -performance['energy_usage'] * 0.0001
        }
        
        # Learning guidance
        guidance = {
            'suggested_actions': self._suggest_actions(universal_state),
            'performance_feedback': {
                'current_score': sum(rewards.values()),
                'improvement_directions': self._analyze_improvement_directions(universal_state)
            }
        }
        
        return {
            'rewards': rewards,
            'guidance': guidance,
            'state_quality': self._assess_state_quality(universal_state)
        }
    
    def _suggest_actions(self, state):
        """Pure function - action suggestions based on state"""
        suggestions = []
        
        if state['system_state']['stress_levels'] > 0.8:
            suggestions.append("increase_damping")
        if state['system_state']['constraint_activity'] < 0.1:
            suggestions.append("lower_thresholds")
        if state['performance_metrics']['dynamics_complexity'] < 0.01:
            suggestions.append("encourage_activity")
            
        return suggestions
    
    def _analyze_improvement_directions(self, state):
        """Pure function - improvement direction analysis"""
        directions = {}
        
        high_stress = state['system_state']['stress_levels'] > 0.5
        low_complexity = state['performance_metrics']['dynamics_complexity'] < 0.05
        
        if high_stress and low_complexity:
            directions['primary'] = "balance_constraints"
        elif not high_stress and low_complexity:
            directions['primary'] = "stimulate_activity"
        else:
            directions['primary'] = "maintain_balance"
            
        return directions
    
    def _assess_state_quality(self, state):
        """Pure function - state quality assessment"""
        stress = state['system_state']['stress_levels']
        complexity = state['performance_metrics']['dynamics_complexity']
        efficiency = state['performance_metrics']['constraint_efficiency']
        
        # Ideal: moderate stress, high complexity, good efficiency
        quality = (complexity * 0.4 + efficiency * 0.3 + (1.0 - abs(stress - 0.5)) * 0.3)
        return quality
    
    # EVENT SYSTEM for loose coupling
    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for interface events"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def notify_callbacks(self, event_type: str, data: Dict):
        """Notify registered callbacks"""
        for callback in self.callbacks.get(event_type, []):
            callback(data)
    
    # MAIN INTERFACE CYCLE
    def interface_cycle(self, universal_engine, neural_controls: Dict = None):
        """
        Complete interface cycle: observe → control → learn
        Pure coordination - no domain logic
        """
        # 1. UNIVERSAL → NEURAL: Package current state
        universal_state = self.package_universal_state(universal_engine)
        self.interface_state['universal_to_neural'] = universal_state
        
        # Notify observers
        self.notify_callbacks('on_universal_update', universal_state)
        
        # 2. NEURAL → UNIVERSAL: Apply controls if provided
        if neural_controls:
            self.apply_neural_controls(universal_engine, neural_controls)
            self.interface_state['neural_to_universal'] = neural_controls
            self.notify_callbacks('on_neural_decision', neural_controls)
        
        # 3. Generate learning signals
        learning_signals = self.generate_learning_signals(universal_state, neural_controls or {})
        self.interface_state['learning_signals'] = learning_signals
        
        # 4. Update performance metrics
        self.interface_state['performance_metrics'] = universal_state['performance_metrics']
        
        return {
            'universal_state': universal_state,
            'learning_signals': learning_signals,
            'interface_metrics': self._get_interface_metrics()
        }
    
    def _get_interface_metrics(self):
        """Pure function - interface performance metrics"""
        return {
            'communication_volume': len(str(self.interface_state)),
            'update_frequency': self.interface_state.get('performance_metrics', {}).get('step_count', 0),
            'interface_health': 1.0  # Always healthy - pure message passing
        }


# Example neural controller
class ExampleNeuralController:
    """
    Example neural network controller that uses the interface
    Completely separate from universal engine logic
    """
    
    def __init__(self):
        self.learning_rate = 0.01
        self.control_policy = {}
    
    def make_decision(self, universal_state: Dict) -> Dict[str, Any]:
        """
        Neural network decision making
        Pure neural logic - no universal engine knowledge
        """
        # Extract relevant features
        stress = universal_state['system_state']['stress_levels']
        complexity = universal_state['performance_metrics']['dynamics_complexity']
        
        # Simple policy (replace with actual neural network)
        controls = {}
        
        if stress > 0.7:
            controls['parameter_adjustments'] = {
                'M_factor_adjust': -0.1,  # Reduce stiffness
                'damping_adjust': 0.05    # Increase damping
            }
        elif complexity < 0.1:
            controls['parameter_adjustments'] = {
                'M_factor_adjust': 0.05,  # Slightly increase stiffness
                'damping_adjust': -0.1    # Reduce damping
            }
        
        return controls


# Demonstration
if __name__ == "__main__":
    print("🔄 DEMONSTRATING CLEAN UNIVERSAL-NEURAL INTERFACE")
    print("=" * 60)
    
    # Create systems independently
    neural_controller = ExampleNeuralController()
    interface = UniversalNeuralInterface()
    
    print("✅ Systems created independently:")
    print("   - Neural Controller: Decision making specialist") 
    print("   - Interface: Pure communication channel")
    print("   - Universal Engine: Will be connected separately")
    print()
    
    # Demonstrate interface without universal engine (proving independence)
    print("🔄 Testing interface without universal engine...")
    
    # Create a mock universal state to demonstrate the interface works standalone
    mock_universal_state = {
        'field_patterns': {
            'rho_normalized': np.random.random((16, 16)),
            'E_normalized': np.random.random((16, 16)),
            'F_normalized': np.random.random((16, 16))
        },
        'system_state': {
            'stress_levels': 0.3,
            'constraint_activity': 0.2,
            'stability_warnings': 0,
            'step_count': 100
        },
        'performance_metrics': {
            'dynamics_complexity': 0.15,
            'constraint_efficiency': 0.8,
            'energy_usage': 0.5
        }
    }
    
    # Show neural controller making decisions
    neural_controls = neural_controller.make_decision(mock_universal_state)
    print(f"Neural controls generated: {neural_controls}")
    
    # Show interface generating learning signals
    learning_signals = interface.generate_learning_signals(mock_universal_state, neural_controls)
    print(f"Learning signals: {learning_signals['rewards']}")
    
    print(f"\n🎯 INTERFACE DEMONSTRATION COMPLETE")
    print("Systems remain pure and distinct")
    print("Interface works without universal engine present")
    print("Each system focuses on its strengths")
    print("=" * 60)
