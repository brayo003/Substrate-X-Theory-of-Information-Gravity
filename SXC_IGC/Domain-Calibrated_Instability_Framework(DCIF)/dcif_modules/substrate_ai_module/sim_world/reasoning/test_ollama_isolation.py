"""
Minimal Ollama isolation test to diagnose hanging issue.

Tests each model with repeated medium-length prompts to identify:
- Model-specific issues
- Infrastructure issues  
- Integration layer issues
"""

import requests
import time
import json

OLLAMA_BASE_URL = "http://localhost:11434"

MODELS = [
    "qwen2.5-coder:1.5b",
    "gemma2:2b",
    "deepseek-coder:latest"
]

MEDIUM_PROMPT = """You are Aria, a villager in a medieval village.

Current Situation:
- Location: village_center
- Hunger: 0.82
- Food inventory: 0.0

What should you do? Answer in one sentence."""

def test_model(model_name, num_calls=5):
    """Test a single model with repeated calls."""
    print(f"\n{'='*60}")
    print(f"Testing model: {model_name}")
    print(f"{'='*60}")
    
    results = []
    
    for i in range(num_calls):
        print(f"\n  Call {i+1}/{num_calls}...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model_name,
                    "prompt": MEDIUM_PROMPT,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 100
                    }
                },
                timeout=30
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "call": i+1,
                    "success": True,
                    "elapsed_seconds": elapsed,
                    "response_length": len(data.get('response', '')),
                    "response_preview": data.get('response', '')[:50]
                }
                print(f"    ✓ Success in {elapsed:.2f}s")
                print(f"      Response: {result['response_preview']}...")
            else:
                result = {
                    "call": i+1,
                    "success": False,
                    "elapsed_seconds": elapsed,
                    "error": f"HTTP {response.status_code}",
                    "response_preview": response.text[:50]
                }
                print(f"    ✗ HTTP error: {response.status_code}")
        
        except requests.Timeout:
            elapsed = time.time() - start_time
            result = {
                "call": i+1,
                "success": False,
                "elapsed_seconds": elapsed,
                "error": "Timeout",
                "response_preview": None
            }
            print(f"    ✗ Timeout after {elapsed:.2f}s")
        
        except Exception as e:
            elapsed = time.time() - start_time
            result = {
                "call": i+1,
                "success": False,
                "elapsed_seconds": elapsed,
                "error": str(e),
                "response_preview": None
            }
            print(f"    ✗ Exception: {e}")
        
        results.append(result)
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    print(f"\n  Summary: {successful}/{num_calls} successful")
    
    if successful > 0:
        avg_time = sum(r["elapsed_seconds"] for r in results if r["success"]) / successful
        print(f"  Average time: {avg_time:.2f}s")
    
    return results

def main():
    print("="*60)
    print("OLLAMA ISOLATION TEST")
    print("="*60)
    
    # Check Ollama availability
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            available_models = [m.get('name', '') for m in data.get('models', [])]
            print(f"\nAvailable models: {available_models}")
        else:
            print(f"\n✗ Ollama not available (HTTP {response.status_code})")
            return
    except Exception as e:
        print(f"\n✗ Ollama not available: {e}")
        return
    
    # Test each model
    all_results = {}
    for model in MODELS:
        results = test_model(model, num_calls=3)
        all_results[model] = results
    
    # Final analysis
    print("\n" + "="*60)
    print("FINAL ANALYSIS")
    print("="*60)
    
    for model, results in all_results.items():
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        success_rate = successful / total if total > 0 else 0
        
        print(f"\n{model}:")
        print(f"  Success rate: {success_rate*100:.0f}%")
        
        if successful > 0:
            avg_time = sum(r["elapsed_seconds"] for r in results if r["success"]) / successful
            print(f"  Average time: {avg_time:.2f}s")
        
        if successful < total:
            failures = [r for r in results if not r["success"]]
            print(f"  Failure patterns:")
            for f in failures:
                print(f"    Call {f['call']}: {f.get('error', 'Unknown')}")
    
    # Diagnosis
    print("\n" + "="*60)
    print("DIAGNOSIS")
    print("="*60)
    
    all_successful = all(all(r["success"] for r in results) for results in all_results.values())
    
    if all_successful:
        print("✓ All models stable - issue is in integration layer")
    elif any(all(r["success"] for r in results) for results in all_results.values()):
        print("⚠️ Some models stable - issue is model-specific")
    else:
        print("✗ All models unstable - issue is infrastructure (Ollama/HTTP)")

if __name__ == "__main__":
    main()
