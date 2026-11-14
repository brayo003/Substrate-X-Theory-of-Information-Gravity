#!/usr/bin/env python3
"""
FIXED NEURAL SUBSTRATE - Addressing structural gaps
"""
import numpy as np
from collections import deque
import time

class FunctionalNeuralNetwork:
    """
    FIXED: Proper neural network that actually functions
    """
    
    def __init__(self, grid_size=32, **params):
        self.grid_size = grid_size
        
        # Neural variables
        self.V = np.zeros((grid_size, grid_size))
        self.spiking = np.zeros((grid_size, grid_size), dtype=bool)
        self.refractory = np.zeros((grid_size, grid_size))
        
        # FIXED PARAMETERS - YOUR CORRECTIONS
        self.threshold = params.get('threshold', 1.0)
        self.reset_potential = params.get('reset_potential', 0.0)
        self.resting_potential = params.get('resting_potential', -0.1)
        self.refractory_period = params.get('refractory_period', 3)  # REDUCED
        self.decay_rate = params.get('decay_rate', 0.98)  # FIXED: Much slower decay
        
        # FIXED SYNAPTIC WEIGHTS - YOUR CORRECTION
        self.W = self._initialize_proper_synaptic_weights()
        self.learning_rate = params.get('learning_rate', 0.01)
        
        # FIXED DELAY SYSTEM - YOUR CORRECTION
        self.delay_queues = [[deque() for _ in range(grid_size)] for _ in range(grid_size)]
        self.max_delay = params.get('max_delay', 8)  # INCREASED for grid size
        
        # FIXED: Recurrent connectivity for sustained activity
        self.recurrent_strength = params.get('recurrent_strength', 0.3)
        
        self.step_count = 0
        self.total_spikes = 0
        
        print("🔧 FIXED NEURAL NETWORK")
        print(f"Grid: {grid_size}x{grid_size}")
        print(f"Decay: {self.decay_rate} (slower) | Refractory: {self.refractory_period} (shorter)")
        print(f"Max delay: {self.max_delay} (longer) | Recurrent: {self.recurrent_strength}")
        print("=" * 50)
    
    def _initialize_proper_synaptic_weights(self):
        """FIXED: Stronger, structured synaptic weights"""
        W = np.zeros((self.grid_size, self.grid_size, self.grid_size, self.grid_size))
        
        # FIXED: ORDER OF MAGNITUDE STRONGER WEIGHTS
        base_strength = 0.5  # 8x stronger than before
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                for k in range(self.grid_size):
                    for l in range(self.grid_size):
                        dx, dy = k - i, l - j
                        distance = np.sqrt(dx**2 + dy**2)
                        
                        if 0 < distance <= 6:  # Wider connectivity
                            # FIXED: Strong directional bias
                            directional_bias = 1.0 + 0.8 * (max(0, dx) + 0.5 * max(0, dy))
                            W[i,j,k,l] = base_strength * directional_bias * np.exp(-distance/3)
        
        print(f"  Average synaptic weight: {np.mean(W):.3f} (8x stronger)")
        return W
    
    def apply_synaptic_inputs(self):
        """FIXED: Better synaptic input application"""
        synaptic_input = np.zeros((self.grid_size, self.grid_size))
        
        # Process all delay queues
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                queue = self.delay_queues[i][j]
                while queue and queue[0][0] <= self.step_count:
                    _, strength = queue.popleft()
                    synaptic_input[i, j] += strength
        
        # Add recurrent inputs for sustained activity - FIXED
        recurrent_input = np.zeros((self.grid_size, self.grid_size))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.spiking[i, j]:
                    # Local recurrent excitation
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            ni, nj = i + di, j + dj
                            if (0 <= ni < self.grid_size and 0 <= nj < self.grid_size 
                                and not (di == 0 and dj == 0)):
                                recurrent_input[ni, nj] += self.recurrent_strength
        
        return synaptic_input + recurrent_input
    
    def propagate_spikes(self):
        """FIXED: Better spike propagation with delays"""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.spiking[i, j]:
                    for k in range(self.grid_size):
                        for l in range(self.grid_size):
                            weight = self.W[i,j,k,l]
                            if weight > 0.1:  # Only meaningful connections
                                # FIXED: Distance-based delays
                                distance = np.sqrt((i-k)**2 + (j-l)**2)
                                delay = 1 + int(distance)  # Longer delays for distance
                                delivery_time = self.step_count + min(delay, self.max_delay)
                                
                                self.delay_queues[k][l].append((delivery_time, weight))
    
    def update_hebbian_plasticity(self):
        """FIXED: More effective plasticity"""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                for k in range(self.grid_size):
                    for l in range(self.grid_size):
                        weight = self.W[i,j,k,l]
                        if weight > 0.1:
                            pre_active = self.spiking[i, j]
                            post_active = self.spiking[k, l]
                            
                            # FIXED: Stronger Hebbian learning
                            if pre_active and post_active:
                                self.W[i,j,k,l] += self.learning_rate * 2.0
                            elif pre_active:
                                self.W[i,j,k,l] -= self.learning_rate * 0.3
                            
                            # Keep weights reasonable
                            self.W[i,j,k,l] = np.clip(self.W[i,j,k,l], 0.1, 3.0)
    
    def evolve_neural_dynamics(self, external_input=None):
        """FIXED: Proper neural dynamics with sustained activity"""
        self.spiking = np.zeros((self.grid_size, self.grid_size), dtype=bool)
        
        # FIXED: Apply synaptic inputs FIRST
        synaptic_input = self.apply_synaptic_inputs()
        
        # Update membrane potentials
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.refractory[i, j] > 0:
                    self.refractory[i, j] -= 1
                    self.V[i, j] = self.resting_potential
                else:
                    # FIXED: Stronger input integration
                    total_input = synaptic_input[i, j]
                    if external_input is not None:
                        total_input += external_input[i, j] * 2.0  # Stronger external input
                    
                    self.V[i, j] += total_input
                    
                    # FIXED: Much slower decay
                    self.V[i, j] = (self.decay_rate * self.V[i, j] + 
                                   (1 - self.decay_rate) * self.resting_potential)
                    
                    # Check threshold
                    if self.V[i, j] > self.threshold:
                        self.spiking[i, j] = True
                        self.V[i, j] = self.reset_potential
                        self.refractory[i, j] = self.refractory_period
                        self.total_spikes += 1
        
        # FIXED: Propagate spikes AFTER potential updates
        self.propagate_spikes()
        
        # Apply plasticity
        self.update_hebbian_plasticity()
        
        self.step_count += 1
    
    def stimulate_region(self, center, radius, strength=2.0):  # FIXED: Stronger default
        """FIXED: Stronger stimulation"""
        external_input = np.zeros((self.grid_size, self.grid_size))
        
        cx, cy = center
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                distance = np.sqrt((i-cx)**2 + (j-cy)**2)
                if distance <= radius:
                    external_input[i, j] = strength * (1 - distance/radius)
        
        return external_input
    
    def get_neural_statistics(self):
        """Get neural activity statistics"""
        active_neurons = np.sum(self.spiking)
        avg_potential = np.mean(self.V)
        max_potential = np.max(self.V)
        
        return {
            'step': self.step_count,
            'active_neurons': active_neurons,
            'total_spikes': self.total_spikes,
            'avg_potential': avg_potential,
            'max_potential': max_potential,
            'spike_rate': self.total_spikes / max(1, self.step_count),
            'refractory_neurons': np.sum(self.refractory > 0)
        }

# Test the FIXED neural network
if __name__ == "__main__":
    print("🔧 TESTING FIXED NEURAL NETWORK")
    print("Addressing: Weak inputs, tiny weights, short delays, fast decay")
    print("=" * 60)
    
    # Test 1: Sustained activity
    print("\n🔬 TEST 1: Sustained Activity")
    net1 = FunctionalNeuralNetwork(grid_size=24)  # Smaller for testing
    
    # FIXED: Stronger, longer stimulation
    stimulus = net1.stimulate_region((6, 6), radius=4, strength=3.0)
    
    activity_history = []
    for step in range(100):
        # FIXED: Ongoing input for first 20 steps
        current_stimulus = stimulus if step < 20 else None
        net1.evolve_neural_dynamics(current_stimulus)
        
        stats = net1.get_neural_statistics()
        activity_history.append(stats['active_neurons'])
        
        if step % 15 == 0 or stats['active_neurons'] > 5:
            print(f"  Step {step:3d}: Active: {stats['active_neurons']:2d}, "
                  f"Spikes: {stats['total_spikes']:3d}, "
                  f"Max V: {stats['max_potential']:5.2f}")
    
    sustained_activity = sum(activity_history[30:]) > 0  # Activity after stimulus stops
    print(f"  Sustained activity after stimulus: {sustained_activity}")
    
    # Test 2: Actual propagation
    print("\n🔬 TEST 2: Signal Propagation")
    net2 = FunctionalNeuralNetwork(grid_size=32)
    
    # Stimulate left side strongly
    left_stimulus = np.zeros((32, 32))
    left_stimulus[:, :6] = 2.5  # FIXED: Stronger stimulation
    
    propagation_data = []
    for step in range(150):
        net2.evolve_neural_dynamics(left_stimulus if step < 25 else None)
        
        # Measure activity across the grid
        layers = [
            np.sum(net2.spiking[:, :8]),    # Far left
            np.sum(net2.spiking[:, 8:16]),  # Left middle
            np.sum(net2.spiking[:, 16:24]), # Right middle  
            np.sum(net2.spiking[:, 24:])    # Far right
        ]
        propagation_data.append(layers)
        
        if step % 25 == 0:
            print(f"  Step {step:3d}: Layer activity: {layers}")
    
    # Check if signal reached right side
    signal_propagated = any(propagation_data[-1][3] > 0 for data in propagation_data[-20:])
    print(f"  Signal reached right side: {signal_propagated}")
    
    # Test 3: Meaningful plasticity
    print("\n🔬 TEST 3: Actual Learning")
    net3 = FunctionalNeuralNetwork(grid_size=20, learning_rate=0.03)
    
    # Train on specific pattern
    pattern = net3.stimulate_region((5, 5), radius=3, strength=2.5)
    
    initial_weights = net3.W.copy()
    for step in range(300):
        net3.evolve_neural_dynamics(pattern if step % 50 < 25 else None)
        
        if step % 75 == 0:
            current_weights = net3.W
            weight_change = np.mean(current_weights) - np.mean(initial_weights)
            print(f"  Step {step:3d}: Weight change: {weight_change:+.4f}")
    
    final_weight_change = np.mean(net3.W) - np.mean(initial_weights)
    print(f"  Final weight change: {final_weight_change:+.4f}")
    print(f"  Learning occurred: {abs(final_weight_change) > 0.01}")
    
    print(f"\n📊 FIXED NETWORK RESULTS:")
    print(f"  Test 1 - Sustained activity: {sustained_activity}")
    print(f"  Test 2 - Signal propagation: {signal_propagated}")  
    print(f"  Test 3 - Meaningful learning: {abs(final_weight_change) > 0.01}")
    
    success_count = sum([sustained_activity, signal_propagated, abs(final_weight_change) > 0.01])
    print(f"\n🎯 FIXES EFFECTIVE: {success_count}/3 tests passed")
    print("=" * 60)
