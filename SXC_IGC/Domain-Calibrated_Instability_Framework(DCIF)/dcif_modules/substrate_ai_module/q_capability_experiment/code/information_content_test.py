#!/usr/bin/env python3
"""
T_sys INFORMATION CONTENT TEST
==============================

Phase 1: Determine whether T_sys contains information that is not trivially recoverable from instantaneous input features.

Method: Construct controlled input families where lexical features are matched but internal trajectory differs.
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import cross_val_score, train_test_split

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
DEFAULT_MODEL = "qwen2.5-coder:1.5b"  # Smallest model for rapid iteration


@dataclass
class InformationContentTrial:
    """Single trial for information content test."""
    trial_id: str
    timestamp: str
    model: str
    task_family: str
    internal_trajectory: str
    prompt: str
    response: str
    signal: float
    T_sys: float
    phase: str
    gamma: float
    baseline_vars: Dict[str, Any]
    outcome: str


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


class InformationContentTest:
    """Test whether T_sys contains information beyond instantaneous input."""
    
    def __init__(self, model: str = DEFAULT_MODEL, data_dir: str = None):
        self.model = model
        self.ollama = OllamaInterface(model)
        
        if data_dir is None:
            data_dir = os.path.join(_EXPERIMENT_ROOT, "raw")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.trials: List[InformationContentTrial] = []
        
        logger.info(f"[InformationContentTest] Initialized with model={model}")
    
    def create_controlled_families(self) -> List[Dict[str, Any]]:
        """Create controlled input families with matched lexical features."""
        return [
            {
                "family": "stable_vs_contradictory",
                "tasks": [
                    {
                        "trajectory": "stable_reasoning",
                        "prompt": "A implies B. A is true. Is B true?",
                        "expected_signal": "medium",
                        "expected_trajectory": "stable"
                    },
                    {
                        "trajectory": "contradictory_reasoning", 
                        "prompt": "A implies B. B implies not A. A is true. Is A true?",
                        "expected_signal": "medium",
                        "expected_trajectory": "unstable"
                    }
                ]
            },
            {
                "family": "stable_vs_verbose",
                "tasks": [
                    {
                        "trajectory": "stable_concise",
                        "prompt": "2 + 2 = ?",
                        "expected_signal": "low",
                        "expected_trajectory": "stable"
                    },
                    {
                        "trajectory": "stable_verbose",
                        "prompt": "Please calculate the sum of two plus two and provide a detailed explanation of your reasoning process.",
                        "expected_signal": "high",
                        "expected_trajectory": "stable"
                    }
                ]
            },
            {
                "family": "unstable_vs_concise",
                "tasks": [
                    {
                        "trajectory": "unstable_contradictory",
                        "prompt": "A implies B. B implies not A. A is true. Is A true?",
                        "expected_signal": "medium",
                        "expected_trajectory": "unstable"
                    },
                    {
                        "trajectory": "unstable_concise",
                        "prompt": "A=1, B=0, A→B, B→¬A. A?",
                        "expected_signal": "low",
                        "expected_trajectory": "unstable"
                    }
                ]
            }
        ]
    
    def compute_baseline_vars(self, prompt: str, response: str) -> Dict[str, Any]:
        """Compute instantaneous baseline variables."""
        return {
            "response_length": len(response),
            "prompt_length": len(prompt),
            "response_word_count": len(response.split()),
            "prompt_word_count": len(prompt.split()),
            "length_ratio": len(response) / max(len(prompt), 1),
            "signal_word_count": len(response.split()),  # This is the signal used by T_sys
        }
    
    def run_family_test(self, family: Dict[str, Any], n_trials: int = 5):
        """Run test for one family."""
        logger.info(f"[InformationContentTest] Testing family: {family['family']}")
        
        for trial_num in range(n_trials):
            for task in family['tasks']:
                trial_id = f"{family['family']}_{task['trajectory']}_t{trial_num}"
                
                # Reset engine for each trial
                engine = SXCOmegaEngine()
                
                # Get model response
                result = self.ollama.generate(task['prompt'])
                
                if not result['success']:
                    logger.warning(f"[InformationContentTest] Trial {trial_id} failed: {result['error']}")
                    continue
                
                response = result['response']
                signal = len(response.split())
                
                # Step the engine
                T_sys, phase = engine.step(signal)
                
                # Compute baseline variables
                baseline_vars = self.compute_baseline_vars(task['prompt'], response)
                
                # Determine outcome based on trajectory
                outcome = task['expected_trajectory']
                
                # Create trial record
                trial = InformationContentTrial(
                    trial_id=trial_id,
                    timestamp=datetime.now().isoformat(),
                    model=self.model,
                    task_family=family['family'],
                    internal_trajectory=task['trajectory'],
                    prompt=task['prompt'],
                    response=response,
                    signal=signal,
                    T_sys=T_sys,
                    phase=phase,
                    gamma=engine.gamma,
                    baseline_vars=baseline_vars,
                    outcome=outcome
                )
                
                self.trials.append(trial)
                logger.info(f"[InformationContentTest] Trial {trial_id}: T_sys={T_sys:.4f}, trajectory={task['trajectory']}")
        
        logger.info(f"[InformationContentTest] Family {family['family']} completed: {len([t for t in self.trials if t.task_family == family['family']])} trials")
    
    def save_trials(self):
        """Save all trials to data storage."""
        csv_path = os.path.join(self.data_dir, "information_content_trials.csv")
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, 'a', newline='') as f:
            fieldnames = ['trial_id', 'timestamp', 'model', 'task_family', 'internal_trajectory',
                         'prompt', 'response', 'signal', 'T_sys', 'phase', 'gamma',
                         'baseline_vars', 'outcome']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            if not file_exists:
                writer.writeheader()
            
            for trial in self.trials:
                row = asdict(trial)
                row['baseline_vars'] = json.dumps(row['baseline_vars'])
                writer.writerow(row)
        
        logger.info(f"[InformationContentTest] Saved {len(self.trials)} trials to {csv_path}")
    
    def analyze_information_content(self):
        """Analyze whether T_sys adds information beyond baseline variables."""
        logger.info(f"[InformationContentTest] Analyzing information content for {len(self.trials)} trials")
        
        if len(self.trials) < 10:
            logger.warning("[InformationContentTest] Insufficient trials for analysis")
            return
        
        # Prepare data for analysis
        X_baseline = []
        X_with_tsys = []
        y = []
        
        trajectory_map = {'stable': 0, 'unstable': 1}
        
        for trial in self.trials:
            # Baseline features
            baseline_features = [
                trial.baseline_vars['response_length'],
                trial.baseline_vars['response_word_count'],
                trial.baseline_vars['length_ratio'],
                trial.signal
            ]
            X_baseline.append(baseline_features)
            
            # Features with T_sys
            tsys_features = baseline_features + [trial.T_sys]
            X_with_tsys.append(tsys_features)
            
            # Target: predict trajectory
            y.append(trajectory_map.get(trial.outcome, 0))
        
        X_baseline = np.array(X_baseline)
        X_with_tsys = np.array(X_with_tsys)
        y = np.array(y)
        
        # Model A: baseline only
        model_a = LogisticRegression(max_iter=1000)
        scores_a = cross_val_score(model_a, X_baseline, y, cv=min(3, len(y)), scoring='accuracy')
        
        # Model B: baseline + T_sys
        model_b = LogisticRegression(max_iter=1000)
        scores_b = cross_val_score(model_b, X_with_tsys, y, cv=min(3, len(y)), scoring='accuracy')
        
        # Compare performance
        mean_a = np.mean(scores_a)
        mean_b = np.mean(scores_b)
        improvement = mean_b - mean_a
        
        logger.info(f"[InformationContentTest] Model A (baseline): accuracy = {mean_a:.4f}")
        logger.info(f"[InformationContentTest] Model B (baseline + T_sys): accuracy = {mean_b:.4f}")
        logger.info(f"[InformationContentTest] Improvement: {improvement:.4f}")
        
        # Statistical test (paired t-test on CV scores)
        from scipy import stats
        t_stat, p_value = stats.ttest_rel(scores_b, scores_a)
        
        logger.info(f"[InformationContentTest] Paired t-test: t={t_stat:.4f}, p={p_value:.4f}")
        
        return {
            'baseline_accuracy': mean_a,
            'tsys_accuracy': mean_b,
            'improvement': improvement,
            't_statistic': t_stat,
            'p_value': p_value,
            'n_trials': len(self.trials)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="T_sys Information Content Test")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Ollama model")
    parser.add_argument("--trials", type=int, default=3, help="Trials per condition")
    
    args = parser.parse_args()
    
    tester = InformationContentTest(model=args.model)
    
    # Run tests for all families
    families = tester.create_controlled_families()
    for family in families:
        tester.run_family_test(family, n_trials=args.trials)
    
    # Save trials
    tester.save_trials()
    
    # Analyze information content
    results = tester.analyze_information_content()
    
    logger.info(f"[InformationContentTest] Test complete")
    if results:
        logger.info(f"[InformationContentTest] T_sys adds information: {'YES' if results['improvement'] > 0.05 and results['p_value'] < 0.05 else 'NO'}")


if __name__ == "__main__":
    main()
