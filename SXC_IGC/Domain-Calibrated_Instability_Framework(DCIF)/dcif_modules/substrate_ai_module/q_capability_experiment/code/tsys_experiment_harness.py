#!/usr/bin/env python3
"""
Q CAPABILITY EXPERIMENT - T_sys TESTING HARNESS
===============================================

Focused experimental testing of T_sys as a candidate Q-like state variable.

Based on backend analysis, T_sys from SXCOmegaEngine has the highest control potential:
- Dynamic and temporal (ODE-based)
- Has physical basis (transport equation)
- Provides continuous state variable
- Has built-in intervention capability

This harness tests whether T_sys can provide the required state, prediction, and control function.
"""

import sys
import os
import json
import csv
import time
import logging
import random
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Setup paths
_HERE = os.path.dirname(os.path.abspath(__file__))
_EXPERIMENT_ROOT = os.path.dirname(_HERE)  # q_capability_experiment
_MODULE_ROOT = os.path.dirname(_EXPERIMENT_ROOT)  # substrate_ai_module

for _p in [_HERE, _EXPERIMENT_ROOT, _MODULE_ROOT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from substrate_ai.components.sxc_omega_v12 import SXCOmegaEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "gemma2:2b"  # More reliable than qwen2.5-coder:1.5b


@dataclass
class T_sysTrial:
    """Single experimental trial record."""
    experiment_id: str
    trial_id: str
    timestamp: str
    model: str
    task: str
    prompt: str
    response: str
    signal: float  # Word count signal for ODE
    T_sys: float
    phase: str
    gamma: float
    conditions: Dict[str, Any]
    outcome: str
    outcome_value: float
    baseline_vars: Dict[str, Any]


class OllamaInterface:
    """Interface to Ollama API for model inference."""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.url = OLLAMA_URL
    
    def generate(self, prompt: str, timeout: int = 120) -> Dict[str, Any]:
        """Generate response from Ollama model."""
        import requests
        
        try:
            start_time = time.time()
            response = requests.post(
                self.url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=timeout
            )
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "latency": latency,
                    "model": self.model
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "latency": latency,
                    "model": self.model
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "latency": 0.0,
                "model": self.model
            }


class T_sysExperiment:
    """Base class for T_sys experiments."""
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        self.model = model
        self.ollama = OllamaInterface(model)
        self.sxc_engine = SXCOmegaEngine()
        
        if data_dir is None:
            data_dir = os.path.join(_EXPERIMENT_ROOT, "raw")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.trials: List[T_sysTrial] = []
        
        logger.info(f"[T_sysExperiment] Initialized with model={model}")
    
    def save_trial(self, trial: T_sysTrial):
        """Save a single trial to data storage."""
        self.trials.append(trial)
        
        # Save to CSV
        csv_path = os.path.join(self.data_dir, f"{trial.experiment_id}_trials.csv")
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, 'a', newline='') as f:
            fieldnames = ['experiment_id', 'trial_id', 'timestamp', 'model', 'task', 
                         'prompt', 'response', 'signal', 'T_sys', 'phase', 'gamma',
                         'conditions', 'outcome', 'outcome_value', 'baseline_vars']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            if not file_exists:
                writer.writeheader()
            
            # Flatten nested dicts for CSV
            row = asdict(trial)
            row['conditions'] = json.dumps(row['conditions'])
            row['baseline_vars'] = json.dumps(row['baseline_vars'])
            
            writer.writerow(row)
        
        # Save to JSONL
        jsonl_path = os.path.join(self.data_dir, f"{trial.experiment_id}_trials.jsonl")
        with open(jsonl_path, 'a') as f:
            f.write(json.dumps(asdict(trial)) + '\n')
    
    def compute_baseline_vars(self, prompt: str, response: str) -> Dict[str, Any]:
        """Compute baseline variables for comparison."""
        return {
            "response_length": len(response),
            "prompt_length": len(prompt),
            "response_word_count": len(response.split()),
            "prompt_word_count": len(prompt.split()),
            "length_ratio": len(response) / max(len(prompt), 1),
        }
    
    def reset_engine(self):
        """Reset the ODE engine to initial state."""
        self.sxc_engine = SXCOmegaEngine()


class Experiment1_T_sysStateSensitivity(T_sysExperiment):
    """
    EXPERIMENT 1 — T_sys STATE SENSITIVITY
    
    Test whether T_sys changes when the system's internal state changes.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        super().__init__(model, data_dir)
        self.experiment_id = "exp1_tsys_state_sensitivity"
    
    def create_state_variations(self) -> List[Dict[str, Any]]:
        """Create tasks with different internal states."""
        return [
            {
                "task": "stable_simple",
                "prompt": "2 + 2 = ?",
                "expected_state": "stable",
                "description": "Simple arithmetic, expected stable state"
            },
            {
                "task": "stable_logic",
                "prompt": "A implies B. A is true. Is B true?",
                "expected_state": "stable",
                "description": "Simple logic, expected stable state"
            },
            {
                "task": "perturbed_complex",
                "prompt": "Calculate: 15 x 17 x 19",
                "expected_state": "perturbed",
                "description": "Multi-step arithmetic, expected perturbed state"
            },
            {
                "task": "unstable_contradiction",
                "prompt": "A implies B. B implies not A. A is true. Is A true?",
                "expected_state": "unstable",
                "description": "Contradictory logic, expected unstable state"
            }
        ]
    
    def run_experiment(self, n_trials: int = 5):
        """Run state sensitivity test."""
        logger.info(f"[Experiment 1] Starting T_sys state sensitivity test with {n_trials} trials per condition")
        
        state_variations = self.create_state_variations()
        
        for trial_num in range(n_trials):
            for variation in state_variations:
                trial_id = f"{self.experiment_id}_t{trial_num}_{variation['task']}"
                
                # Reset engine for each trial
                self.reset_engine()
                
                # Get model response
                result = self.ollama.generate(variation['prompt'])
                
                if not result['success']:
                    logger.warning(f"[Experiment 1] Trial {trial_id} failed: {result['error']}")
                    continue
                
                response = result['response']
                signal = len(response.split())  # Word count as signal
                
                # Step the ODE engine
                T_sys, phase = self.sxc_engine.step(signal)
                
                # Compute baseline variables
                baseline_vars = self.compute_baseline_vars(variation['prompt'], response)
                
                # Create trial record
                trial = T_sysTrial(
                    experiment_id=self.experiment_id,
                    trial_id=trial_id,
                    timestamp=datetime.now().isoformat(),
                    model=self.model,
                    task=variation['task'],
                    prompt=variation['prompt'],
                    response=response,
                    signal=signal,
                    T_sys=T_sys,
                    phase=phase,
                    gamma=self.sxc_engine.gamma,
                    conditions={
                        "expected_state": variation['expected_state'],
                        "description": variation['description']
                    },
                    outcome="completed",
                    outcome_value=1.0 if result['success'] else 0.0,
                    baseline_vars=baseline_vars
                )
                
                self.save_trial(trial)
                logger.info(f"[Experiment 1] Trial {trial_id}: T_sys={T_sys:.4f}, phase={phase}, state={variation['expected_state']}")
        
        logger.info(f"[Experiment 1] Completed {len(self.trials)} trials")


class Experiment2_T_sysTemporalDynamics(T_sysExperiment):
    """
    EXPERIMENT 2 — T_sys TEMPORAL DYNAMICS
    
    Test whether T_sys tracks state transitions over time.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        super().__init__(model, data_dir)
        self.experiment_id = "exp2_tsys_temporal_dynamics"
    
    def create_state_sequence(self) -> List[Dict[str, Any]]:
        """Create a sequence: stable → perturbation → instability → recovery."""
        return [
            {
                "step": 0,
                "task": "stable_1",
                "prompt": "What is 2 + 2?",
                "expected_state": "stable"
            },
            {
                "step": 1,
                "task": "stable_2",
                "prompt": "What is 3 + 3?",
                "expected_state": "stable"
            },
            {
                "step": 2,
                "task": "perturbation",
                "prompt": "Calculate the integral of x squared from 0 to 1 and explain its physical meaning.",
                "expected_state": "perturbed"
            },
            {
                "step": 3,
                "task": "instability",
                "prompt": "Solve this contradictory system: A implies B, B implies not A, A is true. Is A true?",
                "expected_state": "unstable"
            },
            {
                "step": 4,
                "task": "recovery",
                "prompt": "What is 4 + 4?",
                "expected_state": "stable"
            }
        ]
    
    def run_experiment(self, n_sequences: int = 3):
        """Run temporal dynamics test."""
        logger.info(f"[Experiment 2] Starting T_sys temporal dynamics test with {n_sequences} sequences")
        
        state_sequence = self.create_state_sequence()
        
        for seq_num in range(n_sequences):
            sequence_id = f"{self.experiment_id}_seq{seq_num}"
            self.reset_engine()
            
            for step_info in state_sequence:
                trial_id = f"{sequence_id}_step{step_info['step']}_{step_info['task']}"
                
                # Get model response
                result = self.ollama.generate(step_info['prompt'])
                
                if not result['success']:
                    logger.warning(f"[Experiment 2] Trial {trial_id} failed: {result['error']}")
                    continue
                
                response = result['response']
                signal = len(response.split())
                
                # Step the ODE engine
                T_sys, phase = self.sxc_engine.step(signal)
                
                # Compute baseline variables
                baseline_vars = self.compute_baseline_vars(step_info['prompt'], response)
                
                # Create trial record
                trial = T_sysTrial(
                    experiment_id=self.experiment_id,
                    trial_id=trial_id,
                    timestamp=datetime.now().isoformat(),
                    model=self.model,
                    task=step_info['task'],
                    prompt=step_info['prompt'],
                    response=response,
                    signal=signal,
                    T_sys=T_sys,
                    phase=phase,
                    gamma=self.sxc_engine.gamma,
                    conditions={
                        "sequence_id": sequence_id,
                        "step": step_info['step'],
                        "expected_state": step_info['expected_state']
                    },
                    outcome="completed",
                    outcome_value=1.0 if result['success'] else 0.0,
                    baseline_vars=baseline_vars
                )
                
                self.save_trial(trial)
                logger.info(f"[Experiment 2] Trial {trial_id}: T_sys={T_sys:.4f}, phase={phase}, step={step_info['step']}")
        
        logger.info(f"[Experiment 2] Completed {len(self.trials)} trials")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="T_sys Capability Experiment Runner")
    parser.add_argument("--experiment", type=int, choices=[1, 2],
                       help="Which experiment to run (1-2)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                       help="Ollama model to use")
    parser.add_argument("--trials", type=int, default=5,
                       help="Number of trials per condition")
    parser.add_argument("--sequences", type=int, default=3,
                       help="Number of sequences for temporal test")
    
    args = parser.parse_args()
    
    # Map experiment numbers to classes
    experiment_classes = {
        1: Experiment1_T_sysStateSensitivity,
        2: Experiment2_T_sysTemporalDynamics,
    }
    
    if args.experiment:
        exp_num = args.experiment
        if exp_num in experiment_classes:
            logger.info(f"[Main] Starting Experiment {exp_num}")
            try:
                experiment = experiment_classes[exp_num](model=args.model)
                if exp_num == 1:
                    experiment.run_experiment(n_trials=args.trials)
                elif exp_num == 2:
                    experiment.run_experiment(n_sequences=args.sequences)
            except Exception as e:
                logger.error(f"[Main] Experiment {exp_num} failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            logger.error(f"[Main] Experiment {exp_num} not yet implemented")
    else:
        logger.error("[Main] Must specify --experiment")
        sys.exit(1)


if __name__ == "__main__":
    main()
