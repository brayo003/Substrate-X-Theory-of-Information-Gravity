# Substrate AI – V12 Cognitive Governor

A real-time stability monitor for AI models based on the Substrate-X Information Gravity framework.

## What It Does

Instead of just measuring *what* an AI outputs, V12 tracks *how* it gets there:

- **T_sys** – cognitive stress (0 = calm, 1+ = unstable)
- **Phase** – NOMINAL (stable) or FIREWALL (about to fail)
- **Intervention** – triggers when tension is too high

## Core Components

| File | Purpose |
|------|---------|
| `components/sxc_omega_v12.py` | V12 engine |
| `cognitive_governor.py` | Wraps any LLM, monitors stress |
| `epistemic_gate.py` | Decides when to trust the output |
| `problem_analyzer.py` | Predicts tension from prompt features |

## Validation

| Test | What It Shows |
|------|---------------|
| `test_paperclip.py` | Detects existential risk |
| `test_real_hle.py` | Predicts HLE failures |
| `demonstrate_hle_failures.py` | Prevents overconfident wrong answers |

## Run It

```bash
pip install -r requirements.txt
python3 run_system.py

Results

    Claude Opus fractures on metacognition (T_sys = 2.73)

    Gemini remains stable (T_sys = 0.00)

Philosophy

V12 answers: "Is it safe to trust this output right now?"
