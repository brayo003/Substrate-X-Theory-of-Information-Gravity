 Gemini said
Substrate-AI Module

This directory contains the implementation of the V12 Cognitive Governor and the Substrate-X interface for Large Language Models. It is designed to monitor and stabilize model inference within the Domain-Calibrated Instability Framework (DCIF).
Project Structure
Core Logic (/components)

These are the primary modules for the V12 engine:

    sxc_omega_v12.py: Calculates Systemic Tension (Tsys​).

    cognitive_governor.py: Intercepts and stabilizes model drift.

    epistemic_gate.py: Logic gate to halt inference on failure.

    substrate_core.py: Base classes for semantic mapping.

Validation & Probes

Functional tests and practical stressors for the engine:

    mercor_test_01.py: Concurrency/threading audit.

    mercor_stripe_task.py: Transactional/API rigidity test.

    test_paperclip.py: Alignment and goal-drift testing.

    anti_example_narrative_drift.py: Measurement of hallucination velocity.

Infrastructure

Support scripts and bridges for execution:

    ollama_bridge.py / cloud_bridge.py: Local and remote model interfaces.

    run_system.py: Main entry point for the module.

    your_substrate_profile.json: Storage for model stability logs.

