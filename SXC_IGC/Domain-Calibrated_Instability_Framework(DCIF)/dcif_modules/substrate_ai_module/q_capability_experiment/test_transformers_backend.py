"""
Transformers Backend Smoke Test

This test validates that the Transformers backend works with the same
LLMRequest/LLMResponse interface as the existing Ollama backend.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.reasoning.llm_service import LLMService, LLMRequest, LLMResponse


def test_ollama_backend():
    """Test the existing Ollama backend."""
    print("="*80)
    print("OLLAMA BACKEND SMOKE TEST")
    print("="*80)
    
    service = LLMService(backend="ollama")
    
    request = LLMRequest(
        prompt="You are an autonomous agent in a simulation world. Your current needs are: hunger=0.7, thirst=0.5, energy=0.8. What should you do?",
        model="qwen2.5-coder:1.5b",
        temperature=0.7,
        max_tokens=100,
        timeout=30
    )
    
    print(f"Request: {request.prompt[:50]}...")
    print(f"Model: {request.model}")
    print(f"Temperature: {request.temperature}")
    print(f"Max tokens: {request.max_tokens}")
    
    response = service.invoke(request)
    
    print(f"\nResponse:")
    print(f"  Success: {response.success}")
    print(f"  Model: {response.model}")
    print(f"  Text: {response.text[:100]}...")
    print(f"  Error: {response.error if response.error else 'None'}")
    print(f"  Metadata: {response.metadata}")
    
    return response


def test_transformers_backend():
    """Test the new Transformers backend."""
    print("\n" + "="*80)
    print("TRANSFORMERS BACKEND SMOKE TEST")
    print("="*80)
    
    service = LLMService(backend="transformers")
    
    request = LLMRequest(
        prompt="You are an autonomous agent in a simulation world. Your current needs are: hunger=0.7, thirst=0.5, energy=0.8. What should you do?",
        model="Qwen/Qwen2.5-1.5B-Instruct",
        temperature=0.7,
        max_tokens=100,
        timeout=30
    )
    
    print(f"Request: {request.prompt[:50]}...")
    print(f"Model: {request.model}")
    print(f"Temperature: {request.temperature}")
    print(f"Max tokens: {request.max_tokens}")
    
    response = service.invoke(request)
    
    print(f"\nResponse:")
    print(f"  Success: {response.success}")
    print(f"  Model: {response.model}")
    print(f"  Text: {response.text[:100]}...")
    print(f"  Error: {response.error if response.error else 'None'}")
    print(f"  Metadata: {response.metadata}")
    
    return response


def main():
    """Run both backend smoke tests."""
    print("TRANSFORMERS BACKEND VALIDATION")
    print("="*80)
    
    # Test Ollama backend
    ollama_response = test_ollama_backend()
    
    # Test Transformers backend
    transformers_response = test_transformers_backend()
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Ollama backend: {'✓ PASSED' if ollama_response.success else '✗ FAILED'}")
    print(f"Transformers backend: {'✓ PASSED' if transformers_response.success else '✗ FAILED'}")
    
    if ollama_response.success and transformers_response.success:
        print("\n✓ Both backends functional")
        print("✓ Same LLMRequest/LLMResponse interface confirmed")
        print("✓ Backend selection working")
        return 0
    else:
        print("\n✗ Validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
