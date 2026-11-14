"""Hugging Face Transformers transport for the existing LLM service contract."""

from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar, Mapping


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass
class TransformersBackend:
    """Lazy, reusable single-model causal-language-model backend optimized for Colab GPU."""

    model_name: str = "Qwen/Qwen2.5-3B-Instruct"  # Updated for Colab T4 GPU
    device: str = "auto"
    dtype: str = "auto"  # Changed to auto for better GPU compatibility
    max_context_tokens: int = 4096
    default_max_new_tokens: int = 256  # Increased for better reasoning

    _tokenizer: Any = field(default=None, init=False, repr=False)
    _model: Any = field(default=None, init=False, repr=False)
    _resolved_device: str = field(default="unloaded", init=False)

    # Avoid duplicate model allocations when a coordinator/service is constructed twice.
    _cache: ClassVar[dict[tuple[str, str, str], tuple[Any, Any, str]]] = {}
    _cache_lock: ClassVar[threading.Lock] = threading.Lock()

    def _load(self) -> None:
        if self._model is not None:
            return

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        use_cuda = torch.cuda.is_available() and self.device != "cpu"
        requested_device = "cuda" if use_cuda else "cpu"
        cache_key = (self.model_name, requested_device, self.dtype)
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._tokenizer, self._model, self._resolved_device = cached
                return

            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Updated for Colab GPU compatibility
            load_kwargs: dict[str, Any] = {}
            if use_cuda:
                load_kwargs["torch_dtype"] = "auto"
                load_kwargs["device_map"] = "auto"
            else:
                load_kwargs["torch_dtype"] = torch.float32

            try:
                model = AutoModelForCausalLM.from_pretrained(self.model_name, **load_kwargs)
            except TypeError as exc:
                # Compatibility with Transformers releases predating the `dtype` keyword.
                if "dtype" not in str(exc):
                    raise
                load_kwargs["torch_dtype"] = load_kwargs.pop("dtype")
                model = AutoModelForCausalLM.from_pretrained(self.model_name, **load_kwargs)

            if not use_cuda:
                model.to("cpu")
            model.eval()
            resolved = self._model_device(model, requested_device)
            self._cache[cache_key] = (tokenizer, model, resolved)
            self._tokenizer, self._model, self._resolved_device = tokenizer, model, resolved

    @staticmethod
    def _model_device(model: Any, fallback: str) -> str:
        try:
            return str(model.device)
        except Exception:
            return fallback

    def invoke(self, request: Any) -> Any:
        # Imported here to avoid a module-level circular import.
        from .llm_service import LLMResponse

        import torch

        started = time.perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat()
        prompt = str(request.prompt)
        prompt_fingerprint = _fingerprint(prompt)
        generation_parameters = {
            "do_sample": False,
            "max_new_tokens": max(1, min(int(request.max_tokens or self.default_max_new_tokens), self.default_max_new_tokens)),
        }
        provenance: Mapping[str, Any] = getattr(request, "metadata", {}) or {}
        base_metadata: dict[str, Any] = {
            "timestamp": timestamp,
            "backend": "transformers",
            "model": self.model_name,
            "device": self._resolved_device,
            "cuda_available": bool(torch.cuda.is_available()),
            "prompt_fingerprint": prompt_fingerprint,
            "prompt_hash": prompt_fingerprint,
            "generation_parameters": generation_parameters,
            "deterministic": True,
            "reasoning_cycle_id": provenance.get("reasoning_cycle_id") or provenance.get("cycle_id"),
            "intent_id": provenance.get("intent_id"),
            "goal_provenance": provenance.get("goal_provenance"),
            "provenance": dict(provenance),
        }

        try:
            self._load()
            base_metadata["device"] = self._resolved_device
            messages = [{"role": "user", "content": prompt}]
            if getattr(self._tokenizer, "chat_template", None):
                formatted_prompt = self._tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
            else:
                formatted_prompt = prompt

            encoded = self._tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_context_tokens,
            )
            input_ids = encoded["input_ids"]
            attention_mask = encoded["attention_mask"]
            model_device = getattr(self._model, "device", None)
            if model_device is not None:
                input_ids = input_ids.to(model_device)
                attention_mask = attention_mask.to(model_device)

            with torch.inference_mode():
                generated_ids = self._model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    pad_token_id=self._tokenizer.pad_token_id or self._tokenizer.eos_token_id,
                    **generation_parameters,
                )

            input_token_count = int(input_ids.shape[-1])
            completion_ids = generated_ids[0, input_token_count:]
            output_token_count = int(completion_ids.shape[-1])
            text = self._tokenizer.decode(completion_ids, skip_special_tokens=True).strip()
            latency_ms = (time.perf_counter() - started) * 1000.0
            base_metadata.update({
                "output_fingerprint": _fingerprint(text),
                "output_hash": _fingerprint(text),
                "input_tokens": input_token_count,
                "output_tokens": output_token_count,
                "total_tokens": input_token_count + output_token_count,
                "latency_ms": latency_ms,
                "success": True,
                "error": None,
                "exception_type": None,
                "exception_message": None,
            })
            return LLMResponse(text=text, model=self.model_name, success=True, metadata=base_metadata)
        except Exception as exc:
            base_metadata.update({
                "latency_ms": (time.perf_counter() - started) * 1000.0,
                "success": False,
                "error": str(exc),
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "input_tokens": None,
                "output_tokens": None,
                "output_fingerprint": None,
            })
            return LLMResponse(
                text="", model=self.model_name, success=False, error=str(exc), metadata=base_metadata
            )
