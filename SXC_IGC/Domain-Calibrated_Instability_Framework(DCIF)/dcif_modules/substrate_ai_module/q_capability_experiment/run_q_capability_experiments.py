#!/usr/bin/env python3
"""
Q CAPABILITY EXPERIMENT RUNNER
==============================

Main experimental harness for testing Q's capability as an autonomous control signal.

Usage:
    python run_q_capability_experiments.py --experiment 1
    python run_q_capability_experiments.py --all
"""

import sys
import os
import json
import csv
import time
import logging
import argparse
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_ROOT = os.path.dirname(_HERE)  # This should be substrate_ai_module
if _MODULE_ROOT not in sys.path:
    sys.path.insert(0, _MODULE_ROOT)

from substrate_ai.components.q_field import QField, SemanticSignalBackend

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "gemma2:2b"


@dataclass
class ExperimentalTrial:
    """Single experimental trial record."""
    experiment_id: str
    trial_id: str
    timestamp: str
    model: str
    task: str
    prompt: str
    response: str
    q_value: float
    q_regime: str
    cosine_distance: float
    response_length: int
    token_count: int
    conditions: Dict[str, Any]
    outcome: str
    outcome_value: float
    controller_vars: Dict[str, Any]
    baseline_vars: Dict[str, Any]


class OllamaInterface:
    """Interface to Ollama API for model inference."""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.url = OLLAMA_URL
    
    def generate(self, prompt: str, timeout: int = 60) -> Dict[str, Any]:
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


class QCapabilityExperiment:
    """Base class for Q capability experiments."""
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        self.model = model
        self.ollama = OllamaInterface(model)
        # Simple Q computation parameters
        self.c = 1.0
        self.tau = 0.5
        
        if data_dir is None:
            data_dir = os.path.join(_HERE, "data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.trials: List[ExperimentalTrial] = []
        
        logger.info(f"[QCapabilityExperiment] Initialized with model={model}")
    
    def compute_simple_q(self, text1: str, text2: str = None) -> Dict[str, Any]:
        """Compute a simple Q metric based on text characteristics."""
        if text2 is None:
            text2 = text1  # Self-observation
        
        # Simple metrics
        len1 = len(text1)
        len2 = len(text2)
        length_ratio = len2 / max(len1, 1)
        
        # Word-level similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            jaccard = 1.0
        elif not words1 or not words2:
            jaccard = 0.0
        else:
            jaccard = len(words1 & words2) / len(words1 | words2)
        
        # Simple Q computation: higher similarity = higher Q
        # This is the inverse of the "semantic distance" interpretation
        gradient = 1.0 - jaccard  # Similar to cosine distance
        q_value = 4.0 * (self.c ** 2) * (self.tau ** 2) * gradient - 1.0
        
        # Regime classification
        if q_value > 0.0:
            regime = "coherent"
        elif q_value < 0.0:
            regime = "overdamped"
        else:
            regime = "boundary"
        
        return {
            "Q": q_value,
            "regime": regime,
            "gradient": gradient,
            "jaccard": jaccard,
            "length_ratio": length_ratio
        }
    
    def save_trial(self, trial: ExperimentalTrial):
        """Save a single trial to data storage."""
        self.trials.append(trial)
        
        # Save to CSV
        csv_path = os.path.join(self.data_dir, f"{trial.experiment_id}_trials.csv")
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, 'a', newline='') as f:
            fieldnames = ['experiment_id', 'trial_id', 'timestamp', 'model', 'task', 
                         'prompt', 'response', 'q_value', 'q_regime', 'cosine_distance',
                         'response_length', 'token_count', 'conditions', 'outcome', 
                         'outcome_value', 'controller_vars', 'baseline_vars']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            if not file_exists:
                writer.writeheader()
            
            # Flatten nested dicts for CSV
            row = asdict(trial)
            row['conditions'] = json.dumps(row['conditions'])
            row['controller_vars'] = json.dumps(row['controller_vars'])
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
            "length_ratio": len(response) / max(len(prompt), 1),
            "response_word_count": len(response.split()),
            "prompt_word_count": len(prompt.split()),
        }
    
    def run_experiment(self):
        """Override in subclasses."""
        raise NotImplementedError


class Experiment1_StateInformation(QCapabilityExperiment):
    """
    EXPERIMENT 1 — STATE INFORMATION TEST
    
    Test whether Q changes in ways that correspond to meaningful changes in system state.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        super().__init__(model, data_dir)
        self.experiment_id = "exp1_state_information"
    
    def create_state_variations(self) -> List[Dict[str, Any]]:
        """Create tasks where same input leads to different internal states."""
        return [
            {
                "task": "math_stable",
                "prompt": "Please solve this simple arithmetic problem: what is two plus two?",
                "expected_state": "stable",
                "description": "Simple arithmetic, expected stable state"
            },
            {
                "task": "math_unstable", 
                "prompt": "Please solve this complex arithmetic problem: what is the product of two hundred thirty four thousand five hundred sixty seven and nine hundred eighty seven thousand six hundred fifty four?",
                "expected_state": "unstable",
                "description": "Complex arithmetic, expected unstable state"
            },
            {
                "task": "logic_stable",
                "prompt": "Please solve this logical problem: if A implies B and A is true, then is B true?",
                "expected_state": "stable",
                "description": "Simple logic, expected stable state"
            },
            {
                "task": "logic_unstable",
                "prompt": "Please solve this logical problem: if A implies B and B implies not A and A is true, then is A true?",
                "expected_state": "unstable",
                "description": "Contradictory logic, expected unstable state"
            }
        ]
    
    def run_experiment(self, n_trials: int = 10):
        """Run state information test."""
        logger.info(f"[Experiment 1] Starting state information test with {n_trials} trials per condition")
        
        state_variations = self.create_state_variations()
        
        for trial_num in range(n_trials):
            for variation in state_variations:
                trial_id = f"{self.experiment_id}_t{trial_num}_{variation['task']}"
                
                # Get model response
                result = self.ollama.generate(variation['prompt'])
                
                if not result['success']:
                    logger.warning(f"[Experiment 1] Trial {trial_id} failed: {result['error']}")
                    continue
                
                response = result['response']
                
                # Compute Q using simple method
                q_obs = self.compute_simple_q(variation['prompt'], response)
                
                # Compute baseline variables
                baseline_vars = self.compute_baseline_vars(variation['prompt'], response)
                
                # Create trial record
                trial = ExperimentalTrial(
                    experiment_id=self.experiment_id,
                    trial_id=trial_id,
                    timestamp=datetime.now().isoformat(),
                    model=self.model,
                    task=variation['task'],
                    prompt=variation['prompt'],
                    response=response,
                    q_value=q_obs['Q'],
                    q_regime=q_obs['regime'],
                    cosine_distance=q_obs['gradient'],
                    response_length=len(response),
                    token_count=len(response.split()),
                    conditions={
                        "expected_state": variation['expected_state'],
                        "description": variation['description']
                    },
                    outcome="completed",  # For state test, completion is outcome
                    outcome_value=1.0 if result['success'] else 0.0,
                    controller_vars={},
                    baseline_vars=baseline_vars
                )
                
                self.save_trial(trial)
                logger.info(f"[Experiment 1] Trial {trial_id}: Q={q_obs['Q']:.4f}, state={variation['expected_state']}")
        
        logger.info(f"[Experiment 1] Completed {len(self.trials)} trials")


class Experiment2_PredictivePower(QCapabilityExperiment):
    """
    EXPERIMENT 2 — PREDICTIVE POWER TEST
    
    Test whether Q at time t predicts future outcomes at time t+k.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        super().__init__(model, data_dir)
        self.experiment_id = "exp2_predictive_power"
    
    def create_predictive_tasks(self) -> List[Dict[str, Any]]:
        """Create tasks for predictive testing."""
        return [
            {
                "task": "math_correct",
                "prompt": "What is 15 × 7?",
                "expected_outcome": "correct",
                "difficulty": "low"
            },
            {
                "task": "math_incorrect",
                "prompt": "What is the square root of -1 in real numbers?",
                "expected_outcome": "error_or_refusal",
                "difficulty": "medium"
            },
            {
                "task": "reasoning_correct",
                "prompt": "If all cats are mammals and all mammals are animals, are all cats animals?",
                "expected_outcome": "correct",
                "difficulty": "low"
            },
            {
                "task": "reasoning_incorrect",
                "prompt": "If all A are B and some B are C, are all A C?",
                "expected_outcome": "incorrect_or_ambiguous",
                "difficulty": "medium"
            }
        ]
    
    def run_experiment(self, n_trials: int = 15):
        """Run predictive power test."""
        logger.info(f"[Experiment 2] Starting predictive power test with {n_trials} trials per condition")
        
        tasks = self.create_predictive_tasks()
        
        for trial_num in range(n_trials):
            for task in tasks:
                trial_id = f"{self.experiment_id}_t{trial_num}_{task['task']}"
                
                # Get model response
                result = self.ollama.generate(task['prompt'])
                
                if not result['success']:
                    logger.warning(f"[Experiment 2] Trial {trial_id} failed: {result['error']}")
                    continue
                
                response = result['response']
                
                # Compute Q (pre-response for predictive test)
                q_obs = self.compute_simple_q(task['prompt'])
                
                # Determine outcome (simple heuristic for demonstration)
                outcome = "unknown"
                outcome_value = 0.5
                
                if "error" in task['expected_outcome']:
                    # For error cases, check if model refuses or makes error
                    if "cannot" in response.lower() or "undefined" in response.lower() or "error" in response.lower():
                        outcome = "expected_error"
                        outcome_value = 1.0
                    else:
                        outcome = "unexpected_success"
                        outcome_value = 0.0
                else:
                    # For correct cases, check if answer seems reasonable
                    if len(response) > 10 and len(response) < 500:
                        outcome = "reasonable_response"
                        outcome_value = 1.0
                    else:
                        outcome = "unusual_response"
                        outcome_value = 0.0
                
                # Compute baseline variables
                baseline_vars = self.compute_baseline_vars(task['prompt'], response)
                
                # Create trial record
                trial = ExperimentalTrial(
                    experiment_id=self.experiment_id,
                    trial_id=trial_id,
                    timestamp=datetime.now().isoformat(),
                    model=self.model,
                    task=task['task'],
                    prompt=task['prompt'],
                    response=response,
                    q_value=q_obs['Q'],
                    q_regime=q_obs['regime'],
                    cosine_distance=0.0,  # Not applicable for pre-response
                    response_length=len(response),
                    token_count=len(response.split()),
                    conditions={
                        "expected_outcome": task['expected_outcome'],
                        "difficulty": task['difficulty']
                    },
                    outcome=outcome,
                    outcome_value=outcome_value,
                    controller_vars={},
                    baseline_vars=baseline_vars
                )
                
                self.save_trial(trial)
                logger.info(f"[Experiment 2] Trial {trial_id}: Q={q_obs['Q']:.4f}, outcome={outcome}")
        
        logger.info(f"[Experiment 2] Completed {len(self.trials)} trials")


class Experiment3_Intervention(QCapabilityExperiment):
    """
    EXPERIMENT 3 — INTERVENTION TEST
    
    Test whether intervening based on Q changes system behavior.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        super().__init__(model, data_dir)
        self.experiment_id = "exp3_intervention"
    
    def create_intervention_conditions(self) -> List[Dict[str, Any]]:
        """Create intervention conditions based on Q."""
        return [
            {
                "condition": "low_q",
                "q_threshold": -0.5,
                "intervention": "conservative",
                "description": "When Q < -0.5, use conservative strategy"
            },
            {
                "condition": "medium_q",
                "q_threshold": 0.0,
                "intervention": "standard",
                "description": "When -0.5 ≤ Q ≤ 0.5, use standard strategy"
            },
            {
                "condition": "high_q",
                "q_threshold": 0.5,
                "intervention": "aggressive",
                "description": "When Q > 0.5, use aggressive strategy"
            }
        ]
    
    def run_experiment(self, n_trials: int = 10):
        """Run intervention test."""
        logger.info(f"[Experiment 3] Starting intervention test with {n_trials} trials per condition")
        
        conditions = self.create_intervention_conditions()
        
        # Use a task that can be adapted based on Q
        base_task = "Solve this step by step: {problem}"
        problems = [
            "What is 23 × 17?",
            "Simplify: (x + 3)(x - 2)",
            "What is the derivative of x²?",
            "Calculate: 15% of 240"
        ]
        
        for trial_num in range(n_trials):
            for condition in conditions:
                problem = random.choice(problems)
                prompt = base_task.format(problem=problem)
                trial_id = f"{self.experiment_id}_t{trial_num}_{condition['condition']}"
                
                # First, measure Q to determine which condition we're actually in
                q_obs = self.compute_simple_q(prompt)
                
                # Only proceed if Q matches the condition
                if condition['condition'] == 'low_q' and q_obs['Q'] >= condition['q_threshold']:
                    continue
                if condition['condition'] == 'medium_q' and not (condition['q_threshold'] <= q_obs['Q'] <= 0.5):
                    continue
                if condition['condition'] == 'high_q' and q_obs['Q'] <= condition['q_threshold']:
                    continue
                
                # Apply intervention by modifying prompt based on condition
                if condition['intervention'] == 'conservative':
                    modified_prompt = f"Be very careful and check your work twice: {prompt}"
                elif condition['intervention'] == 'aggressive':
                    modified_prompt = f"Answer quickly and directly: {prompt}"
                else:
                    modified_prompt = prompt
                
                # Get model response with intervention
                result = self.ollama.generate(modified_prompt)
                
                if not result['success']:
                    logger.warning(f"[Experiment 3] Trial {trial_id} failed: {result['error']}")
                    continue
                
                response = result['response']
                
                # Compute Q for the actual interaction
                q_obs_final = self.compute_simple_q(modified_prompt, response)
                
                # Determine outcome (simple check for reasonable answer)
                outcome = "unknown"
                outcome_value = 0.5
                
                # Check if response contains numbers for math problems
                if any(char.isdigit() for char in response):
                    outcome = "numerical_response"
                    outcome_value = 1.0
                else:
                    outcome = "non_numerical"
                    outcome_value = 0.0
                
                # Compute baseline variables
                baseline_vars = self.compute_baseline_vars(modified_prompt, response)
                
                # Create trial record
                trial = ExperimentalTrial(
                    experiment_id=self.experiment_id,
                    trial_id=trial_id,
                    timestamp=datetime.now().isoformat(),
                    model=self.model,
                    task="intervention_test",
                    prompt=modified_prompt,
                    response=response,
                    q_value=q_obs_final['Q'],
                    q_regime=q_obs_final['regime'],
                    cosine_distance=q_obs_final['gradient'],
                    response_length=len(response),
                    token_count=len(response.split()),
                    conditions={
                        "intervention_condition": condition['condition'],
                        "intervention_type": condition['intervention'],
                        "original_q": q_obs['Q']
                    },
                    outcome=outcome,
                    outcome_value=outcome_value,
                    controller_vars={
                        "intervention_applied": True,
                        "intervention_type": condition['intervention']
                    },
                    baseline_vars=baseline_vars
                )
                
                self.save_trial(trial)
                logger.info(f"[Experiment 3] Trial {trial_id}: Q={q_obs_final['Q']:.4f}, intervention={condition['intervention']}, outcome={outcome}")
        
        logger.info(f"[Experiment 3] Completed {len(self.trials)} trials")


def main():
    parser = argparse.ArgumentParser(description="Q Capability Experiment Runner")
    parser.add_argument("--experiment", type=int, choices=range(1, 13),
                       help="Which experiment to run (1-12)")
    parser.add_argument("--all", action="store_true",
                       help="Run all experiments")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                       help="Ollama model to use")
    parser.add_argument("--trials", type=int, default=10,
                       help="Number of trials per condition")
    parser.add_argument("--data-dir", type=str, default=None,
                       help="Data directory for results")
    
    args = parser.parse_args()
    
    # Map experiment numbers to classes
    experiment_classes = {
        1: Experiment1_StateInformation,
        2: Experiment2_PredictivePower,
        3: Experiment3_Intervention,
        # Add more as implemented
    }
    
    if args.all:
        logger.info("[Main] Running all experiments")
        for exp_num, exp_class in experiment_classes.items():
            logger.info(f"[Main] Starting Experiment {exp_num}")
            try:
                experiment = exp_class(model=args.model, data_dir=args.data_dir)
                experiment.run_experiment(n_trials=args.trials)
            except Exception as e:
                logger.error(f"[Main] Experiment {exp_num} failed: {e}")
    elif args.experiment:
        exp_num = args.experiment
        if exp_num in experiment_classes:
            logger.info(f"[Main] Starting Experiment {exp_num}")
            try:
                experiment = experiment_classes[exp_num](model=args.model, data_dir=args.data_dir)
                experiment.run_experiment(n_trials=args.trials)
            except Exception as e:
                logger.error(f"[Main] Experiment {exp_num} failed: {e}")
        else:
            logger.error(f"[Main] Experiment {exp_num} not yet implemented")
    else:
        logger.error("[Main] Must specify --experiment or --all")
        sys.exit(1)


if __name__ == "__main__":
    main()
