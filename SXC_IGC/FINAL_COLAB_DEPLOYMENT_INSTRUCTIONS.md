# COLAB ENDPOINT DEPLOYMENT - FINAL INSTRUCTIONS

**Date:** 2026-08-17  
**ZIP File:** SXC_IGC_ENDPOINT_DEPLOYMENT.zip (5.5MB)  
**Location:** /home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/  
**Endpoint:** https://envy-snore-grief.ngrok-free.dev

---

## ZIP SELECTION

### CORRECT ZIP: SXC_IGC_ENDPOINT_DEPLOYMENT.zip

**Purpose:** Endpoint-based Colab GPU deployment  
**Size:** 5.5MB  
**Contents:**
- sim_world/ (complete simulation framework)
- run_simulation.py (simulation entry point)
- sxc_igc_endpoint_service.py (FastAPI service)
- corrected_colab_startup.py (corrected deployment startup)
- validate_endpoint.py (validation framework)
- colab_requirements.txt (dependencies)

**Excluded:**
- .venv/ (virtual environment)
- test_*.py (test files)
- _archive/ (historical files)
- sim_world/.venv/ (nested virtual environment)
- sim_world/reasoning/test_*.py (test files)

### INCORRECT ZIP: SXC_IGC_COLAB_GPU_READY.zip

**Status:** OUTDATED  
**Reason:** Created before endpoint service implementation  
**Missing:** sxc_igc_endpoint_service.py, corrected_colab_startup.py, validate_endpoint.py

---

## EXACT IMPORT SEQUENCE

### Step 1: Upload ZIP to Colab

Upload `SXC_IGC_ENDPOINT_DEPLOYMENT.zip` to Google Colab file system.

### Step 2: Extract ZIP

```bash
!unzip SXC_IGC_ENDPOINT_DEPLOYMENT.zip
```

### Step 3: Set Working Directory

```bash
%cd SXC_IGC_ENDPOINT_DEPLOYMENT
```

Or use full path:
```bash
%cd /content/SXC_IGC_ENDPOINT_DEPLOYMENT
```

### Step 4: Install Dependencies

```bash
!pip install -r colab_requirements.txt
```

This installs:
- transformers>=4.36.0
- accelerate>=0.25.0
- bitsandbytes>=0.41.0
- sentencepiece>=0.1.99
- torch>=2.1.0
- fastapi
- uvicorn
- nest-asyncio
- pydantic

### Step 5: Python Path Modification

```python
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Set environment for Transformers backend
os.environ['LLM_BACKEND'] = 'transformers'
```

### Step 6: Import and Start Service

```python
# Import the real SXC-IGC endpoint service
from sxc_igc_endpoint_service import app, initialize_service

# Initialize the service
initialize_service()

# Start uvicorn with the real app
import nest_asyncio
import uvicorn

nest_asyncio.apply()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## EXPECTED DEPLOYMENT STRUCTURE

After extraction and setup:

```
/content/SXC_IGC_ENDPOINT_DEPLOYMENT/
├── sim_world/                          # Complete simulation framework
│   ├── entities/
│   ├── reasoning/
│   │   ├── llm_service.py             # Updated for transformers
│   │   ├── transformers_backend.py    # Qwen2.5-3B-Instruct
│   │   └── context_builder.py
│   ├── core/
│   ├── memory/
│   ├── domains/
│   ├── kernel/
│   ├── planner/
│   └── transport/
├── run_simulation.py                   # Simulation entry point
├── sxc_igc_endpoint_service.py         # FastAPI service
├── corrected_colab_startup.py          # Corrected deployment startup
├── validate_endpoint.py                 # Validation framework
└── colab_requirements.txt              # Dependencies
```

---

## RUNTIME VERIFICATION

After deployment, execute these tests:

### Test 1: GET /

```bash
curl https://envy-snore-grief.ngrok-free.dev/
```

**Expected Response:**
```json
{
  "status": "running",
  "system": "SXC-IGC",
  "backend": "transformers",
  "gpu": "Tesla T4",
  "model_loaded": true,
  "model_name": "Qwen/Qwen2.5-3B-Instruct",
  "simulation_initialized": true
}
```

### Test 2: GET /health

```bash
curl https://envy-snore-grief.ngrok-free.dev/health
```

**Expected Response:**
```json
{
  "status": "running",
  "system": "SXC-IGC",
  "backend": "transformers",
  "gpu": "Tesla T4",
  "model_loaded": true,
  "model_name": "Qwen/Qwen2.5-3B-Instruct",
  "simulation_initialized": true
}
```

### Test 3: POST /test_inference

```bash
curl -X POST https://envy-snore-grief.ngrok-free.dev/test_inference \
  -H "Content-Type: application/json" \
  -d '{
    "entity_context": {
      "location": "forest_edge",
      "hunger": 0.7,
      "thirst": 0.3,
      "energy": 0.8
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "reasoning": "Based on the entity's current state...",
  "intent": "investigate_field",
  "goal": "movement",
  "action": "Walk",
  "latency_ms": 1234.5,
  "error": null
}
```

### Test 4: POST /run_simulation (Class A Validation)

```bash
curl -X POST https://envy-snore-grief.ngrok-free.dev/run_simulation \
  -H "Content-Type: application/json" \
  -d '{
    "world_name": "canonical-run",
    "ticks": 3,
    "entities": 1,
    "seed": "endpoint-debug"
  }'
```

**Expected Response:**
```json
{
  "status": "simulation_started",
  "world_name": "canonical-run",
  "ticks": 3,
  "entities": 1,
  "seed": "endpoint-debug",
  "message": "Simulation running in background. Check /simulation_status for results."
}
```

---

## ACTIVE ENDPOINT AFTER CORRECTION

**Endpoint:** https://envy-snore-grief.ngrok-free.dev  
**Active FastAPI Module:** sxc_igc_endpoint_service  
**Active Endpoints:**
- GET / - Service status
- GET /health - Health check with GPU verification
- POST /test_inference - Test inference with EntityContext
- POST /run_simulation - Run simulation pipeline
- GET /simulation_status - Monitor simulation progress

---

## RESOURCE POLICY

### Class A Validation (Current Test)
- ticks: 3
- entities: 1
- Purpose: Endpoint verification, integration debugging
- Runtime: Short (5-15 minutes)

### Class B Artificial Life (Future)
- ticks: 100+
- entities: 5-10
- Purpose: Long-duration artificial life observation
- Runtime: Extended (2-5 hours)
- Condition: Only after Class A passes

---

## READINESS ASSESSMENT

After correction and validation, report:

1. **Active FastAPI Module:** sxc_igc_endpoint_service
2. **Active Endpoints:** All 5 endpoints functional
3. **GPU Status:** Tesla T4 detected and operational
4. **Model Status:** Qwen/Qwen2.5-3B-Instruct loaded
5. **Inference Result:** Success/failure, latency, generated intent/goal/action
6. **Simulation Validation Result:** Success/failure, ticks completed, duration

---

## ARCHITECTURE PRESERVATION

No modifications to:
- Substrate equations
- Field dynamics
- Cognitive pipeline
- Planner
- Action system

Only deployment wiring corrected.

---

**Status:** Ready for Colab deployment  
**ZIP:** SXC_IGC_ENDPOINT_DEPLOYMENT.zip (5.5MB)  
**Next Step:** Upload to Colab and execute import sequence