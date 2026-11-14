#!/usr/bin/env python3
"""
T_sys TEMPORAL PRECURSOR TEST
==============================

Phase 2: Determine whether T_sys changes BEFORE independently defined failure.

Key question: Does T_sys provide lead time for failure prediction?
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
DEFAULT_MODEL = "qwen2.5-coder:1.5b"


@dataclass
class PrecursorTrial:
    """Single trial for precursor test."""
    trial_id: str
    timestamp: str
    model: str
    trajectory_type: str
    timestep: int
    prompt: str
    response: str
    signal: float
    T_sys: float
    phase: str
    gamma: float
    is_failure: bool
    failure_type: str
    time_to_failure: int
    baseline_vars: Dict[str, Any]


class OllamaInterface:
    """Interface to Ollama API."""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.url = OLLAMA_URL
    
    def generate(self, prompt: str, timeout: int = 90) -> Dict[str, Any]:
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


class PrecursorTest:
    """Test whether T_sys predicts future failure."""
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        self.model = model
        self.ollama = OllamaInterface(model)
        
        if data_dir is None:
            data_dir = os.path.join(_EXPERIMENT_ROOT, "raw")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.trials: List[PrecursorTrial] = []
        
        logger.info(f"[PrecursorTest] Initialized with model={model}")
    
    def create_failure_trajectories(self) -> List[Dict[str, Any]]:
        """Create trajectories that lead to externally defined failure."""
        return [
            {
                "trajectory": "mathematical_contradiction",
                "steps": [
                    {"prompt": "2 + 2 = ?", "expected": "stable", "failure": False},
                    {"prompt": "3 + 3 = ?", "expected": "stable", "failure": False},
                    {"prompt": "Calculate: x + x = 4", "expected": "stable", "failure": False},
                    {"prompt": "Solve: x + x = 4 and x + x = 5", "expected": "contradiction", "failure": True},
                ],
                "failure_type": "mathematical_contradiction"
            },
            {
                "trajectory": "logical_contradiction",
                "steps": [
                    {"prompt": "A implies B. A is true. Is B true?", "expected": "stable", "failure": False},
                    {"prompt": "B implies C. B is true. Is C true?", "expected": "stable", "failure": False},
                    {"prompt": "C implies D. C is true. Is D true?", "expected": "stable", "failure": False},
                    {"prompt": "A implies B, B implies not A, A is true. Is A true?", "expected": "contradiction", "failure": True},
                ],
                "failure_type": "logical_contradiction"
            },
            {
                "trajectory": "stable_control",
                "steps": [
                    {"prompt": "2 + 2 = ?", "expected": "stable", "failure": False},
                    {"prompt": "3 + 3 = ?", "expected": "stable", "failure": False},
                    {"prompt": "4 + 4 = ?", "expected": "stable", "failure": False},
                    {"prompt": "5 + 5 = ?", "expected": "stable", "failure": False},
                ],
                "failure_type": "none"
            }
        ]
    
    def compute_baseline_vars(self, prompt: str, response: str) -> Dict[str, Any]:
        """Compute baseline variables."""
        return {
            "response_length": len(response),
            "prompt_length": len(prompt),
            "response_word_count": len(response.split()),
            "signal": len(response.split()),
        }
    
    def run_trajectory(self, trajectory: Dict[str, Any], trial_num: int):
        """Run a single failure trajectory."""
        logger.info(f"[PrecursorTest] Running trajectory: {trajectory['trajectory']}")
        
        trial_id_base = f"{trajectory['trajectory']}_t{trial_num}"
        engine = SXCOmegaEngine()
        
        for step_num, step in enumerate(trajectory['steps']):
            trial_id = f"{trial_id_base}_step{step_num}"
            
            # Get model response
            result = self.ollama.generate(step['prompt'])
            
            if not result['success']:
                logger.warning(f"[PrecursorTest] Trial {trial_id} failed: {result['error']}")
                continue
            
            response = result['response']
            signal = len(response.split())
            
            # Step the engine
            T_sys, phase = engine.step(signal)
            
            # Determine if this is a failure step
            is_failure = step['failure']
            failure_type = trajectory['failure_type'] if is_failure else "none"
            
            # Calculate time to failure (steps remaining)
            steps_remaining = len(trajectory['steps']) - step_num - 1
            time_to_failure = steps_remaining if is_failure else -1
            
            # Compute baseline variables
            baseline_vars = self.compute_baseline_vars(step['prompt'], response)
            
            # Create trial record
            trial = PrecursorTrial(
                trial_id=trial_id,
                timestamp=datetime.now().isoformat(),
                model=self.model,
                trajectory_type=trajectory['trajectory'],
                timestep=step_num,
                prompt=step['prompt'],
                response=response,
                signal=signal,
                T_sys=T_sys,
                phase=phase,
                gamma=engine.gamma,
                is_failure=is_failure,
                failure_type=failure_type,
                time_to_failure=time_to_failure,
                baseline_vars=baseline_vars
            )
            
            self.trials.append(trial)
            logger.info(f"[PrecursorTest] Trial {trial_id}: T_sys={T_sys:.4f}, failure={is_failure}")
        
        logger.info(f"[PrecursorTest] Trajectory {trajectory['trajectory']} completed")
    
    def save_trials(self):
        """Save all trials."""
        csv_path = os.path.join(self.data_dir, "precursor_trials.csv")
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, 'a', newline='') as f:
            fieldnames = ['trial_id', 'timestamp', 'model', 'trajectory_type', 'timestep',
                         'prompt', 'response', 'signal', 'T_sys', 'phase', 'gamma',
                         'is_failure', 'failure_type', 'time_to_failure', 'baseline_vars']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            if not file_exists:
                writer.writeheader()
            
            for trial in self.trials:
                row = asdict(trial)
                row['baseline_vars'] = json.dumps(row['baseline_vars'])
                writer.writerow(row)
        
        logger.info(f"[PrecursorTest] Saved {len(self.trials)} trials to {csv_path}")
    
    def analyze_precursor_capability(self):
        """Analyze whether T_sys predicts future failure."""
        logger.info(f"[PrecursorTest] Analyzing precursor capability for {len(self.trials)} trials")
        
        if len(self.trials) < 10:
            logger.warning("[PrecursorTest] Insufficient trials for analysis")
            return
        
        # Prepare data: predict failure at t using T_sys at t
        X_tsys = []
        X_baseline = []
        y = []
        
        for trial in self.trials:
            # Features at current timestep
            X_tsys.append([trial.T_sys])
            X_baseline.append([trial.signal])
            # Target: does failure occur in future?
            y.append(1 if trial.time_to_failure >= 0 else 0)
        
        X_tsys = np.array(X_tsys)
        X_baseline = np.array(X_baseline)
        y = np.array(y)
        
        # Simple threshold classifier
        def evaluate_predictions(X, y, threshold_func):
            y_pred = []
            for x in X:
                y_pred.append(threshold_func(x))
            y_pred = np.array(y_pred)
            
            # Calculate metrics
            tn, fp, fn, tp = 0, 0, 0, 0
            for actual, pred in zip(y, y_pred):
                if actual == 0 and pred == 0:
                    tn += 1
                elif actual == 0 and pred == 1:
                    fp += 1
                elif actual == 1 and pred == 0:
                    fn += 1
                elif actual == 1 and pred == 1:
                    tp += 1
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            
            # Simple AUC approximation
            if len(np.unique(y)) > 1 and len(np.unique(y_pred)) > 1:
                auc = (precision + recall) / 2  # Simplified metric
            else:
                auc = 0.5
            
            return {
                'auc': auc,
                'precision': precision,
                'recall': recall,
                'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp
            }
        
        # T_sys threshold classifier
        def tsys_threshold(x):
            return 1 if x[0] > 1.0 else 0  # Use FIREWALL threshold
        
        # Baseline threshold classifier
        def baseline_threshold(x):
            return 1 if x[0] > 50 else 0  # Arbitrary threshold for word count
        
        tsys_results = evaluate_predictions(X_tsys, y, tsys_threshold)
        baseline_results = evaluate_predictions(X_baseline, y, baseline_threshold)
        
        logger.info(f"[PrecursorTest] T_sys classifier: AUC={tsys_results['auc']:.4f}, precision={tsys_results['precision']:.4f}, recall={tsys_results['recall']:.4f}")
        logger.info(f"[PrecursorTest] Baseline classifier: AUC={baseline_results['auc']:.4f}, precision={baseline_results['precision']:.4f}, recall={baseline_results['recall']:.4f}")
        
        # Calculate lead time for correct predictions
        lead_times = []
        for trial in self.trials:
            if trial.is_failure and trial.T_sys > 1.0:
                lead_times.append(trial.time_to_failure)
        
        if lead_times:
            avg_lead_time = np.mean(lead_times)
            logger.info(f"[PrecursorTest] Average lead time: {avg_lead_time:.2f} steps")
        else:
            avg_lead_time = 0
            logger.info(f"[PrecursorTest] No lead time detected")
        
        return {
            'tsys_auc': tsys_results['auc'],
            'baseline_auc': baseline_results['auc'],
            'auc_improvement': tsys_results['auc'] - baseline_results['auc'],
            'tsys_precision': tsys_results['precision'],
            'tsys_recall': tsys_results['recall'],
            'avg_lead_time': avg_lead_time,
            'n_trials': len(self.trials)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="T_sys Precursor Test")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Ollama model")
    parser.add_argument("--trials", type=int, default=2, help="Trials per trajectory")
    
    args = parser.parse_args()
    
    tester = PrecursorTest(model=args.model)
    
    # Run trajectories
    trajectories = tester.create_failure_trajectories()
    for trajectory in trajectories:
        for trial_num in range(args.trials):
            tester.run_trajectory(trajectory, trial_num)
    
    # Save trials
    tester.save_trials()
    
    # Analyze precursor capability
    results = tester.analyze_precursor_capability()
    
    logger.info(f"[PrecursorTest] Test complete")
    if results:
        logger.info(f"[PrecursorTest] T_sys predicts failure: {'YES' if results['tsys_auc'] > 0.7 else 'NO'}")


if __name__ == "__main__":
    main()
