#!/usr/bin/env python3
"""
ADVANCED NEURAL CONTROLLER
Real neural network that can learn to control universal dynamics
"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class AdvancedNeuralController(nn.Module):
    """
    Real neural network with learning capabilities
    Can be trained to optimize universal dynamics
    """
    
    def __init__(self, state_size=None, action_size=6, hidden_size=128):
        super(AdvancedNeuralController, self).__init__()
        
        self.state_size = state_size
        self.action_size = action_size
        self.hidden_size = hidden_size
        
        # Network will be created when we know the state size
        self.network = None
        
        # Training setup
        self.optimizer = None
        self.criterion = nn.MSELoss()
        
        # Experience replay
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        
        # Control parameters
        self.control_ranges = {
            'M_factor': (1000, 100000),
            'damping': (0.01, 2.0),
            'threshold': (0.1, 5.0),
            'excitation': (0.1, 3.0),
            'inhibition': (0.1, 2.0),
            'recovery': (0.001, 0.1)
        }
        
        print("🧠 ADVANCED NEURAL CONTROLLER INITIALIZED")
        print(f"State size: {state_size}, Actions: {action_size}, Hidden: {hidden_size}")
        print("=" * 50)
    
    def _build_network(self, state_size):
        """Build the network when state size is known"""
        self.state_size = state_size
        self.network = nn.Sequential(
            nn.Linear(state_size, self.hidden_size),
            nn.ReLU(),
            nn.Linear(self.hidden_size, self.hidden_size),
            nn.ReLU(), 
            nn.Linear(self.hidden_size, self.hidden_size//2),
            nn.ReLU(),
            nn.Linear(self.hidden_size//2, self.action_size),
            nn.Tanh()  # Outputs between -1 and 1
        )
        
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)
    
    def forward(self, state):
        if self.network is None:
            self._build_network(state.shape[1])
        return self.network(state)
    
    def preprocess_state(self, universal_state):
        """
        Convert universal engine state to neural network input
        """
        field_patterns = universal_state['field_patterns']
        system_state = universal_state['system_state']
        performance = universal_state['performance_metrics']
        
        # Flatten and normalize field patterns
        rho_flat = field_patterns['rho_normalized'].flatten()
        E_flat = field_patterns['E_normalized'].flatten() 
        F_flat = field_patterns['F_normalized'].flatten()
        
        # Combine all features
        features = np.concatenate([
            rho_flat,
            E_flat,
            F_flat,
            [system_state['stress_levels']],
            [system_state['constraint_activity']],
            [system_state['stability_warnings'] / 10.0],  # Normalize
            [performance['dynamics_complexity']],
            [performance['constraint_efficiency']],
            [performance['energy_usage']]
        ])
        
        return torch.FloatTensor(features).unsqueeze(0)  # Add batch dimension
    
    def compute_controls(self, universal_state):
        """
        Compute control actions based on current state
        """
        # Preprocess state
        state_tensor = self.preprocess_state(universal_state)
        
        # Get neural network output
        with torch.no_grad():
            if self.network is None:
                self._build_network(state_tensor.shape[1])
            raw_actions = self.forward(state_tensor).numpy()[0]  # Remove batch dimension
        
        # Convert to actual parameter adjustments
        controls = self._raw_actions_to_controls(raw_actions)
        return controls
    
    def _raw_actions_to_controls(self, raw_actions):
        """
        Convert neural network outputs to meaningful control actions
        """
        # Map each output dimension to a specific control
        controls = {
            'parameter_adjustments': {
                'M_factor_adjust': raw_actions[0] * 0.2,  # ±20% adjustment
                'damping_adjust': raw_actions[1] * 0.3,   # ±30% adjustment
                'excitation_adjust': raw_actions[2] * 0.4, # ±40% adjustment
                'inhibition_adjust': raw_actions[3] * 0.3, # ±30% adjustment
            },
            'constraint_tuning': {
                'threshold_adjust': raw_actions[4] * 0.2,  # ±20% adjustment
                'recovery_adjust': raw_actions[5] * 0.5,   # ±50% adjustment
            }
        }
        
        return controls
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """Train on past experiences"""
        if len(self.memory) < self.batch_size:
            return
        
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Handle network initialization
        if self.network is None and len(states) > 0:
            sample_state = self.preprocess_state(states[0])
            self._build_network(sample_state.shape[1])
        
        states = torch.cat([self.preprocess_state(s) for s in states])
        next_states = torch.cat([self.preprocess_state(s) for s in next_states])
        rewards = torch.FloatTensor(rewards)
        actions = torch.FloatTensor(actions)
        dones = torch.BoolTensor(dones)
        
        # Simple training: predict actions that lead to high rewards
        current_q = self.forward(states)
        target_q = current_q.clone()
        
        # Update Q-values based on rewards
        for i in range(self.batch_size):
            if dones[i]:
                target_q[i] = rewards[i]
            else:
                # Simple TD learning
                target_q[i] = rewards[i] + 0.95 * torch.max(self.forward(next_states[i:i+1]))
        
        # Train network
        self.optimizer.zero_grad()
        loss = self.criterion(current_q, target_q)
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

# Simple test function
def test_neural_controller():
    """Test the neural controller standalone"""
    print("🧠 TESTING NEURAL CONTROLLER STANDALONE")
    
    # Create mock universal state
    mock_state = {
        'field_patterns': {
            'rho_normalized': np.random.random((8, 8)),
            'E_normalized': np.random.random((8, 8)),
            'F_normalized': np.random.random((8, 8))
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
    
    # Test controller
    controller = AdvancedNeuralController()
    controls = controller.compute_controls(mock_state)
    
    print("✅ Neural controls computed successfully:")
    for control_type, adjustments in controls.items():
        print(f"   {control_type}: {adjustments}")
    
    return controls

if __name__ == "__main__":
    test_neural_controller()
