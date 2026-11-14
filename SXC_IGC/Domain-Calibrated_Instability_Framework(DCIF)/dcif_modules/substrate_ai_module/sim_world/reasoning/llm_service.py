"""
LLM Service - Local inference layer for Ollama and Transformers

This module provides a dedicated local inference service supporting multiple backends:
- Ollama (HTTP API)
- Transformers (Hugging Face models on GPU)

It handles model selection, prompt sending, response receiving, timeout,
retry logic, and error handling. No business logic or planning logic.
"""

from __future__ import annotations

import json
import requests
import time
from dataclasses import dataclass, field
from typing import Any, Mapping, Literal


@dataclass(frozen=True, slots=True)
class LLMRequest:
    """Request to LLM service."""
    prompt: str
    model: str = "qwen2.5-coder:1.5b"
    temperature: float = 0.7
    max_tokens: int = 512
    timeout: int = 30


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """Response from LLM service."""
    text: str
    model: str
    success: bool
    error: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class LLMService:
    """Local inference service supporting Ollama and Transformers backends."""
    
    # Backend selection
    backend: Literal["ollama", "transformers"] = "ollama"
    
    # Ollama configuration
    default_model: str = "qwen2.5-coder:1.5b"
    default_timeout: int = 120
    max_retries: int = 3
    retry_delay: float = 1.0
    base_url: str = "http://localhost:11434"
    
    # Transformers configuration
    transformers_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    transformers_device: str = "auto"
    transformers_dtype: str = "auto"
    
    # Backend instances
    _transformers_backend: Any = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Initialize the selected backend."""
        if self.backend == "transformers":
            try:
                from .transformers_backend import TransformersBackend
                self._transformers_backend = TransformersBackend(
                    model_name=self.transformers_model,
                    device=self.transformers_device,
                    dtype=self.transformers_dtype
                )
            except ImportError:
                print("[LLM_SERVICE] Transformers backend requested but dependencies not available")
                self.backend = "ollama"
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is available via HTTP API."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_model_available(self, model: str) -> bool:
        """Check if model is available in Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                for m in models:
                    if model in m.get('name', ''):
                        return True
            return False
        except Exception:
            return False
    
    def invoke(self, request: LLMRequest) -> LLMResponse:
        """
        Invoke LLM with given request using the selected backend.
        
        Args:
            request: LLMRequest with prompt and parameters
            
        Returns:
            LLMResponse with text, model, success status, and error if any
        """
        # Route to appropriate backend
        if self.backend == "transformers" and self._transformers_backend is not None:
            return self._transformers_backend.invoke(request)
        else:
            return self._invoke_ollama(request)
    
    def _invoke_ollama(self, request: LLMRequest) -> LLMResponse:
        """Invoke Ollama backend (existing implementation)."""
        # Check Ollama availability
        if not self._check_ollama_available():
            return LLMResponse(
                text="",
                model=request.model,
                success=False,
                error="Ollama is not available. Please install and start Ollama."
            )
        
        # Check model availability
        model = request.model or self.default_model
        if not self._check_model_available(model):
            return LLMResponse(
                text="",
                model=model,
                success=False,
                error=f"Model {model} is not available."
            )
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                response = self._send_request(request)
                if response.success:
                    return response
                # Retry on failure
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return LLMResponse(
                        text="",
                        model=model,
                        success=False,
                        error=f"LLM invocation failed after {self.max_retries} retries: {str(e)}"
                    )
                time.sleep(self.retry_delay * (attempt + 1))
        
        return LLMResponse(
            text="",
            model=model,
            success=False,
            error=f"LLM invocation failed after {self.max_retries} retries"
        )
    
    def _send_request(self, request: LLMRequest) -> LLMResponse:
        """Send request to Ollama via HTTP API."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": request.model,
                    "prompt": request.prompt,
                    "stream": False,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    }
                },
                timeout=request.timeout or self.default_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return LLMResponse(
                    text=data.get('response', ''),
                    model=request.model,
                    success=True,
                    metadata={
                        "backend": "ollama",
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens,
                        "response_length": len(data.get('response', '')),
                        "eval_count": data.get('eval_count', 0),
                        "prompt_eval_count": data.get('prompt_eval_count', 0)
                    }
                )
            else:
                return LLMResponse(
                    text="",
                    model=request.model,
                    success=False,
                    error=f"Ollama returned error code {response.status_code}: {response.text}"
                )
        except requests.Timeout:
            return LLMResponse(
                text="",
                model=request.model,
                success=False,
                error=f"LLM invocation timed out after {request.timeout} seconds"
            )
        except Exception as e:
            return LLMResponse(
                text="",
                model=request.model,
                success=False,
                error=f"LLM invocation failed: {str(e)}"
            )
